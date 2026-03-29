//! TaxonomyEngine — Automatic meta-tag classification and relevance scoring.
//!
//! Computes tag co-occurrence, relevance decay, and relationship graphs.
//! Feeds the Spore dashboard with taxonomy visualisation data.

use crate::error::Result;
use crate::store::NeuralStore;
use crate::types::MetaTag;
use chrono::Utc;
use rusqlite::params;

/// Manages the meta-tag taxonomy for the colony.
pub struct TaxonomyEngine;

impl TaxonomyEngine {
    /// Recompute relevance scores for all tags based on frequency and recency.
    ///
    /// Score = frequency_weight * recency_weight
    /// - frequency_weight = log2(frequency + 1) / log2(max_frequency + 1)
    /// - recency_weight = 1.0 / (1.0 + days_since_last_seen)
    pub fn recompute_scores(store: &NeuralStore) -> Result<u64> {
        let conn = store.conn();

        let max_freq: f64 = conn
            .query_row("SELECT COALESCE(MAX(frequency), 1) FROM meta_tags", [], |r| r.get(0))?;

        let mut stmt = conn.prepare(
            "SELECT tag, frequency, last_seen FROM meta_tags",
        )?;

        let tags: Vec<(String, f64, String)> = stmt
            .query_map([], |row| {
                Ok((
                    row.get::<_, String>(0)?,
                    row.get::<_, f64>(1)?,
                    row.get::<_, String>(2)?,
                ))
            })?
            .filter_map(|r| r.ok())
            .collect();

        let now = Utc::now();
        let mut updated = 0u64;

        for (tag, freq, last_seen_str) in &tags {
            let last_seen = chrono::DateTime::parse_from_rfc3339(last_seen_str)
                .map(|dt| dt.with_timezone(&Utc))
                .unwrap_or(now);

            let days_since = (now - last_seen).num_hours() as f64 / 24.0;
            let freq_weight = (freq + 1.0).log2() / (max_freq + 1.0).log2();
            let recency_weight = 1.0 / (1.0 + days_since);
            let score = (freq_weight * recency_weight).clamp(0.0, 1.0);

            conn.execute(
                "UPDATE meta_tags SET relevance_score = ?1 WHERE tag = ?2",
                params![score, tag],
            )?;
            updated += 1;
        }

        Ok(updated)
    }

    /// Compute related tags based on co-occurrence in the same session/thread.
    pub fn compute_relationships(store: &NeuralStore) -> Result<u64> {
        let conn = store.conn();

        // Find tags that co-occur in events with the same session_key or parent thread
        let mut stmt = conn.prepare(
            "SELECT DISTINCT a.tag, b.tag
             FROM hyphae a
             JOIN hyphae b ON (a.session_key = b.session_key OR a.parent_ref = b.parent_ref)
             WHERE a.tag IS NOT NULL AND b.tag IS NOT NULL AND a.tag != b.tag
             AND a.session_key IS NOT NULL",
        )?;

        // Build adjacency map
        let mut relationships: std::collections::HashMap<String, Vec<String>> = std::collections::HashMap::new();
        let pairs: Vec<(String, String)> = stmt
            .query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?
            .filter_map(|r| r.ok())
            .collect();

        for (tag_a, tag_b) in pairs {
            relationships.entry(tag_a).or_default().push(tag_b);
        }

        let mut updated = 0u64;
        for (tag, related) in &relationships {
            // Deduplicate and limit
            let mut unique: Vec<String> = related.clone();
            unique.sort();
            unique.dedup();
            unique.truncate(10);

            conn.execute(
                "UPDATE meta_tags SET related_tags = ?1 WHERE tag = ?2",
                params![serde_json::to_string(&unique).unwrap_or_default(), tag],
            )?;
            updated += 1;
        }

        Ok(updated)
    }

    /// Get all meta-tags ordered by relevance.
    pub fn list_tags(store: &NeuralStore) -> Result<Vec<MetaTag>> {
        let mut stmt = store.conn().prepare(
            "SELECT tag, frequency, last_seen, relevance_score, related_tags
             FROM meta_tags ORDER BY relevance_score DESC",
        )?;

        let rows = stmt.query_map([], |row| {
            let related_str: String = row.get(4)?;
            Ok(MetaTag {
                tag: row.get(0)?,
                frequency: row.get::<_, i64>(1)? as u64,
                last_seen: {
                    let s: String = row.get(2)?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
                relevance_score: row.get(3)?,
                related_tags: serde_json::from_str(&related_str).unwrap_or_default(),
            })
        })?;

        rows.collect::<std::result::Result<Vec<_>, _>>()
            .map_err(crate::error::BridgeError::Database)
    }

    /// Get the top N most relevant tags.
    pub fn top_tags(store: &NeuralStore, n: usize) -> Result<Vec<MetaTag>> {
        let all = Self::list_tags(store)?;
        Ok(all.into_iter().take(n).collect())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hyphae::HyphaeStore;

    fn test_store() -> NeuralStore {
        NeuralStore::open_memory().unwrap()
    }

    #[test]
    fn recompute_scores() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        // Emit events with various tags
        for _ in 0..10 {
            hs.emit("a", "s", "c", Some("#mission"), None, serde_json::json!({}), None, None).unwrap();
        }
        for _ in 0..3 {
            hs.emit("b", "s", "c", Some("#lesson"), None, serde_json::json!({}), None, None).unwrap();
        }
        hs.emit("c", "s", "c", Some("#pain-point"), None, serde_json::json!({}), None, None).unwrap();

        let updated = TaxonomyEngine::recompute_scores(&store).unwrap();
        assert_eq!(updated, 3);

        let tags = TaxonomyEngine::list_tags(&store).unwrap();
        assert_eq!(tags.len(), 3);
        // #mission should have highest relevance (most frequent, just seen)
        assert_eq!(tags[0].tag, "#mission");
    }
}
