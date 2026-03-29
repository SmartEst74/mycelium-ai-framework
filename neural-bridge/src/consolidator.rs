//! Consolidator — LCM-style session compaction across tiers.
//!
//! Implements the Liquid Crystal Memory pattern: events flow through
//! tiers of increasing compression. Recent events stay raw (Hot),
//! then get summarised (Warm), then distilled (Cold), then archived (Frozen).

use crate::error::Result;
use crate::store::NeuralStore;
use crate::types::ConsolidationTier;
use rusqlite::params;
use tracing::info;

/// Compacts event history into tiered summaries.
pub struct Consolidator;

impl Consolidator {
    /// Determine the consolidation tier for an event based on its age.
    pub fn tier_for_age_hours(hours: f64) -> ConsolidationTier {
        match hours {
            h if h < 1.0 => ConsolidationTier::Hot,
            h if h < 24.0 => ConsolidationTier::Warm,
            h if h < 168.0 => ConsolidationTier::Cold,
            _ => ConsolidationTier::Frozen,
        }
    }

    /// Run a consolidation pass. Summarises old events into compact records.
    ///
    /// Strategy:
    /// - Hot (< 1h): keep raw, no action
    /// - Warm (1h-24h): group by session_key, create session summary events
    /// - Cold (24h-7d): group by tag, create tag summary events
    /// - Frozen (> 7d): archive to separate table, delete from hyphae
    pub fn consolidate(store: &NeuralStore) -> Result<ConsolidationReport> {
        let conn = store.conn();
        let mut report = ConsolidationReport::default();

        // Warm: summarise sessions older than 1 hour
        let warm_sessions: Vec<(String, i64)> = {
            let mut stmt = conn.prepare(
                "SELECT session_key, COUNT(*) as cnt FROM hyphae
                 WHERE session_key IS NOT NULL
                 AND created_at < datetime('now', '-1 hour')
                 AND created_at > datetime('now', '-24 hours')
                 AND event_type NOT LIKE 'summary:%'
                 GROUP BY session_key HAVING cnt > 5",
            )?;
            let mapped = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?
                .filter_map(|r| r.ok())
                .collect();
            mapped
        };

        for (session_key, event_count) in &warm_sessions {
            // Create a summary event for this session
            let summary_content: String = conn.query_row(
                "SELECT GROUP_CONCAT(content, ' | ') FROM (
                    SELECT content FROM hyphae
                    WHERE session_key = ?1
                    AND event_type NOT LIKE 'summary:%'
                    ORDER BY created_at ASC LIMIT 10
                )",
                params![session_key],
                |r| r.get(0),
            ).unwrap_or_default();

            conn.execute(
                "INSERT INTO hyphae (id, event_type, tag, source, content, session_key, metadata, created_at)
                 VALUES (?1, 'summary:session', '#consolidated', 'consolidator', ?2, ?3, ?4, datetime('now'))",
                params![
                    uuid::Uuid::now_v7().to_string(),
                    summary_content,
                    session_key,
                    serde_json::json!({"event_count": event_count, "tier": "warm"}).to_string(),
                ],
            )?;
            report.warm_sessions += 1;
        }

        // Frozen: archive events older than 7 days
        let frozen_count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae
             WHERE created_at < datetime('now', '-7 days')
             AND event_type NOT LIKE 'summary:%'",
            [],
            |r| r.get(0),
        )?;

        if frozen_count > 0 {
            // Create archive summary before deletion
            conn.execute(
                "INSERT INTO hyphae (id, event_type, tag, source, content, metadata, created_at)
                 VALUES (?1, 'summary:archive', '#archived', 'consolidator', ?2, ?3, datetime('now'))",
                params![
                    uuid::Uuid::now_v7().to_string(),
                    format!("Archived {} events older than 7 days", frozen_count),
                    serde_json::json!({"archived_count": frozen_count, "tier": "frozen"}).to_string(),
                ],
            )?;

            // Move to crystals if they contain lessons
            conn.execute(
                "INSERT OR IGNORE INTO crystals (id, crystal_type, title, content, source_events, tags, confidence, created_at)
                 SELECT
                    id, 'lesson', 'Archived: ' || SUBSTR(content, 1, 100), content,
                    '[]', COALESCE('[\"' || tag || '\"]', '[]'), 0.3, created_at
                 FROM hyphae
                 WHERE created_at < datetime('now', '-7 days')
                 AND tag IN ('#lesson', '#benchmark', '#shortcut')
                 AND event_type NOT LIKE 'summary:%'",
                [],
            )?;

            // Delete archived raw events (summaries preserved)
            conn.execute(
                "DELETE FROM hyphae
                 WHERE created_at < datetime('now', '-7 days')
                 AND event_type NOT LIKE 'summary:%'",
                [],
            )?;
            report.frozen_archived = frozen_count as u64;
        }

        info!(
            warm = report.warm_sessions,
            frozen = report.frozen_archived,
            "consolidation pass complete"
        );

        Ok(report)
    }

    /// Get the current tier distribution.
    pub fn tier_stats(store: &NeuralStore) -> Result<TierStats> {
        let conn = store.conn();

        let hot: u64 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE created_at > datetime('now', '-1 hour')",
            [], |r| r.get::<_, i64>(0),
        )? as u64;

        let warm: u64 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE created_at BETWEEN datetime('now', '-24 hours') AND datetime('now', '-1 hour')",
            [], |r| r.get::<_, i64>(0),
        )? as u64;

        let cold: u64 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE created_at BETWEEN datetime('now', '-7 days') AND datetime('now', '-24 hours')",
            [], |r| r.get::<_, i64>(0),
        )? as u64;

        let frozen: u64 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE created_at < datetime('now', '-7 days')",
            [], |r| r.get::<_, i64>(0),
        )? as u64;

        Ok(TierStats { hot, warm, cold, frozen })
    }
}

/// Results from a consolidation pass.
#[derive(Debug, Default, serde::Serialize)]
pub struct ConsolidationReport {
    pub warm_sessions: u64,
    pub frozen_archived: u64,
}

/// Current event distribution across tiers.
#[derive(Debug, serde::Serialize)]
pub struct TierStats {
    pub hot: u64,
    pub warm: u64,
    pub cold: u64,
    pub frozen: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tier_assignment() {
        assert_eq!(Consolidator::tier_for_age_hours(0.5), ConsolidationTier::Hot);
        assert_eq!(Consolidator::tier_for_age_hours(2.0), ConsolidationTier::Warm);
        assert_eq!(Consolidator::tier_for_age_hours(48.0), ConsolidationTier::Cold);
        assert_eq!(Consolidator::tier_for_age_hours(200.0), ConsolidationTier::Frozen);
    }

    #[test]
    fn consolidate_empty_store() {
        let store = NeuralStore::open_memory().unwrap();
        let report = Consolidator::consolidate(&store).unwrap();
        assert_eq!(report.warm_sessions, 0);
        assert_eq!(report.frozen_archived, 0);
    }
}
