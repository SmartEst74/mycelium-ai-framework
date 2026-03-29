//! Crystallizer — QMD-style knowledge promotion.
//!
//! Promotes valuable events from the hyphae stream into durable crystals.
//! Crystals are the colony's long-term memory: lessons, benchmarks,
//! shortcuts, patterns, and warnings.

use crate::error::Result;
use crate::store::NeuralStore;
use crate::types::*;
use chrono::Utc;
use rusqlite::params;
use tracing::info;

/// Promotes high-value hyphae into durable crystal knowledge.
pub struct Crystallizer;

impl Crystallizer {
    /// Run a crystallization pass — promote tagged events to crystals.
    ///
    /// Rules:
    /// - Events tagged #lesson with self-eval >= 4 → Crystal::Lesson
    /// - Events tagged #benchmark → Crystal::Benchmark
    /// - Events tagged #shortcut → Crystal::Shortcut
    /// - Events tagged #pain-point (repeated 3+) → Crystal::Warning
    pub fn crystallize(store: &NeuralStore) -> Result<CrystallizationReport> {
        let conn = store.conn();
        let mut report = CrystallizationReport::default();

        // Promote lessons (high-scoring events)
        let lessons: Vec<(String, String, String)> = {
            let mut stmt = conn.prepare(
                "SELECT id, content, source FROM hyphae WHERE tag = '#lesson' ORDER BY created_at DESC LIMIT 50",
            )?;
            let mapped = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)))?
                .filter_map(|r| r.ok())
                .collect();
            mapped
        };

        for (event_id, content, source) in &lessons {
            // Skip if already crystallized
            let already: i64 = conn.query_row(
                "SELECT COUNT(*) FROM crystals WHERE source_events LIKE ?1",
                params![format!("%{}%", event_id)],
                |r| r.get(0),
            ).unwrap_or(0);
            if already > 0 { continue; }
            let crystal_id = uuid::Uuid::now_v7().to_string();
            let title = if content.len() > 100 {
                format!("{}...", &content[..97])
            } else {
                content.clone()
            };

            conn.execute(
                "INSERT INTO crystals (id, crystal_type, title, content, source_events, tags, confidence, created_at)
                 VALUES (?1, 'lesson', ?2, ?3, ?4, ?5, 0.7, ?6)",
                params![
                    crystal_id,
                    title,
                    content,
                    serde_json::to_string(&vec![event_id])?,
                    serde_json::to_string(&vec!["#lesson"])?,
                    Utc::now().to_rfc3339(),
                ],
            )?;
            report.lessons_promoted += 1;

            info!(source = source.as_str(), "crystallized lesson");
        }

        // Promote benchmarks
        let benchmarks: Vec<(String, String)> = {
            let mut stmt = conn.prepare(
                "SELECT id, content FROM hyphae WHERE tag = '#benchmark' ORDER BY created_at DESC LIMIT 50",
            )?;
            let mapped = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?
                .filter_map(|r| r.ok())
                .collect();
            mapped
        };

        for (event_id, content) in &benchmarks {
            // Skip if already crystallized
            let already: i64 = conn.query_row(
                "SELECT COUNT(*) FROM crystals WHERE source_events LIKE ?1",
                params![format!("%{}%", event_id)],
                |r| r.get(0),
            ).unwrap_or(0);
            if already > 0 { continue; }
            let crystal_id = uuid::Uuid::now_v7().to_string();
            conn.execute(
                "INSERT INTO crystals (id, crystal_type, title, content, source_events, tags, confidence, created_at)
                 VALUES (?1, 'benchmark', ?2, ?3, ?4, '[\"#benchmark\"]', 0.8, ?5)",
                params![
                    crystal_id,
                    &content[..content.len().min(100)],
                    content,
                    serde_json::to_string(&vec![event_id])?,
                    Utc::now().to_rfc3339(),
                ],
            )?;
            report.benchmarks_promoted += 1;
        }

        // Detect repeated pain points → promote as warnings
        let pain_clusters: Vec<(String, i64)> = {
            let mut stmt = conn.prepare(
                "SELECT content, COUNT(*) as cnt FROM hyphae
                 WHERE tag = '#pain-point'
                 GROUP BY content HAVING cnt >= 3
                 ORDER BY cnt DESC LIMIT 20",
            )?;
            let mapped = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?
                .filter_map(|r| r.ok())
                .collect();
            mapped
        };

        for (content, count) in &pain_clusters {
            // Check if already crystallized
            let existing: i64 = conn.query_row(
                "SELECT COUNT(*) FROM crystals WHERE crystal_type = 'warning' AND content = ?1",
                params![content],
                |r| r.get(0),
            )?;

            if existing == 0 {
                let crystal_id = uuid::Uuid::now_v7().to_string();
                conn.execute(
                    "INSERT INTO crystals (id, crystal_type, title, content, source_events, tags, confidence, created_at)
                     VALUES (?1, 'warning', ?2, ?3, '[]', '[\"#pain-point\",\"#warning\"]', ?4, ?5)",
                    params![
                        crystal_id,
                        format!("Recurring issue ({}x): {}", count, &content[..content.len().min(80)]),
                        content,
                        (*count as f64 / 10.0).min(1.0),
                        Utc::now().to_rfc3339(),
                    ],
                )?;
                report.warnings_promoted += 1;
            }
        }

        info!(
            lessons = report.lessons_promoted,
            benchmarks = report.benchmarks_promoted,
            warnings = report.warnings_promoted,
            "crystallization pass complete"
        );

        Ok(report)
    }

    /// Query crystals by type.
    pub fn query_crystals(store: &NeuralStore, crystal_type: Option<CrystalType>) -> Result<Vec<Crystal>> {
        let (sql, param) = match crystal_type {
            Some(ct) => {
                // Serialize to get the snake_case string, then strip quotes
                let serialized = serde_json::to_string(&ct)?;
                let cleaned = serialized.trim_matches('"').to_string();
                (
                    "SELECT * FROM crystals WHERE crystal_type = ?1 ORDER BY confidence DESC, created_at DESC".to_string(),
                    Some(cleaned),
                )
            }
            None => (
                "SELECT * FROM crystals ORDER BY confidence DESC, created_at DESC".to_string(),
                None,
            ),
        };

        let conn = store.conn();
        let mut stmt = conn.prepare(&sql)?;

        let rows = if let Some(ref p) = param {
            stmt.query_map(params![p], Self::row_to_crystal)?
                .filter_map(|r| r.ok())
                .collect()
        } else {
            stmt.query_map([], Self::row_to_crystal)?
                .filter_map(|r| r.ok())
                .collect()
        };

        Ok(rows)
    }

    /// Record crystal access (boosts confidence over time).
    pub fn record_access(store: &NeuralStore, crystal_id: &str) -> Result<()> {
        store.conn().execute(
            "UPDATE crystals SET access_count = access_count + 1, last_accessed = datetime('now'),
             confidence = MIN(1.0, confidence + 0.01)
             WHERE id = ?1",
            params![crystal_id],
        )?;
        Ok(())
    }

    fn row_to_crystal(row: &rusqlite::Row) -> rusqlite::Result<Crystal> {
        let source_str: String = row.get("source_events")?;
        let tags_str: String = row.get("tags")?;
        Ok(Crystal {
            id: row.get("id")?,
            crystal_type: {
                let s: String = row.get("crystal_type")?;
                serde_json::from_str(&format!("\"{}\"", s)).unwrap_or(CrystalType::Lesson)
            },
            title: row.get("title")?,
            content: row.get("content")?,
            source_events: serde_json::from_str(&source_str).unwrap_or_default(),
            tags: serde_json::from_str(&tags_str).unwrap_or_default(),
            confidence: row.get("confidence")?,
            access_count: row.get::<_, i64>("access_count")? as u64,
            last_accessed: {
                let s: String = row.get("last_accessed")?;
                chrono::DateTime::parse_from_rfc3339(&s)
                    .map(|dt| dt.with_timezone(&chrono::Utc))
                    .unwrap_or_else(|_| chrono::Utc::now())
            },
            created_at: {
                let s: String = row.get("created_at")?;
                chrono::DateTime::parse_from_rfc3339(&s)
                    .map(|dt| dt.with_timezone(&chrono::Utc))
                    .unwrap_or_else(|_| chrono::Utc::now())
            },
        })
    }
}

/// Results from a crystallization pass.
#[derive(Debug, Default, serde::Serialize)]
pub struct CrystallizationReport {
    pub lessons_promoted: u64,
    pub benchmarks_promoted: u64,
    pub warnings_promoted: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hyphae::HyphaeStore;

    fn test_store() -> NeuralStore {
        NeuralStore::open_memory().unwrap()
    }

    #[test]
    fn crystallize_lessons() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        hs.emit("task:complete", "worker-1", "Use async iterators for streaming", Some("#lesson"), None, serde_json::json!({}), None, None).unwrap();

        let report = Crystallizer::crystallize(&store).unwrap();
        assert_eq!(report.lessons_promoted, 1, "should promote 1 lesson");

        let crystals = Crystallizer::query_crystals(&store, Some(CrystalType::Lesson)).unwrap();
        assert_eq!(crystals.len(), 1);
        assert!(crystals[0].content.contains("async iterators"));
    }

    #[test]
    fn crystallize_is_idempotent() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        hs.emit("a", "s", "lesson content", Some("#lesson"), None, serde_json::json!({}), None, None).unwrap();

        Crystallizer::crystallize(&store).unwrap();
        let report2 = Crystallizer::crystallize(&store).unwrap();
        // Should not re-promote already crystallized events
        assert_eq!(report2.lessons_promoted, 0);
    }
}
