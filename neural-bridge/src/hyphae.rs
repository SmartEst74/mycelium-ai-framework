//! HyphaeStore — Append-only event log operations.
//!
//! The colony's nervous system. Every action, every signal, every state
//! change is recorded here. Events are immutable once written.

use crate::error::{BridgeError, Result};
use crate::store::NeuralStore;
use crate::types::*;
use chrono::Utc;
use rusqlite::params;
use uuid::Uuid;

/// Operations on the hyphae event log.
pub struct HyphaeStore<'a> {
    store: &'a NeuralStore,
}

impl<'a> HyphaeStore<'a> {
    pub fn new(store: &'a NeuralStore) -> Self {
        Self { store }
    }

    /// Emit a new event into the colony's nervous system.
    pub fn emit(
        &self,
        event_type: &str,
        source: &str,
        content: &str,
        tag: Option<&str>,
        target: Option<&str>,
        metadata: serde_json::Value,
        session_key: Option<&str>,
        parent_ref: Option<&str>,
    ) -> Result<Hypha> {
        let id = Uuid::now_v7().to_string();
        let now = Utc::now();

        self.store.conn().execute(
            "INSERT INTO hyphae (id, event_type, tag, source, target, content, metadata, session_key, parent_ref, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            params![
                id,
                event_type,
                tag,
                source,
                target,
                content,
                serde_json::to_string(&metadata)?,
                session_key,
                parent_ref,
                now.to_rfc3339(),
            ],
        )?;

        // Update meta-tag frequency if tag present
        if let Some(t) = tag {
            self.store.conn().execute(
                "INSERT INTO meta_tags (tag, frequency, last_seen, relevance_score)
                 VALUES (?1, 1, ?2, 0.5)
                 ON CONFLICT(tag) DO UPDATE SET
                    frequency = frequency + 1,
                    last_seen = ?2",
                params![t, now.to_rfc3339()],
            )?;
        }

        Ok(Hypha {
            id,
            event_type: event_type.to_string(),
            tag: tag.map(String::from),
            source: source.to_string(),
            target: target.map(String::from),
            content: content.to_string(),
            metadata,
            session_key: session_key.map(String::from),
            parent_ref: parent_ref.map(String::from),
            version: 1,
            created_at: now,
        })
    }

    /// Query hyphae with flexible filters.
    pub fn query(&self, q: &HyphaeQuery) -> Result<Vec<Hypha>> {
        let mut sql = String::from("SELECT * FROM hyphae WHERE 1=1");
        let mut param_values: Vec<Box<dyn rusqlite::types::ToSql>> = Vec::new();

        if let Some(ref et) = q.event_type {
            sql.push_str(" AND event_type = ?");
            param_values.push(Box::new(et.clone()));
        }
        if let Some(ref tag) = q.tag {
            sql.push_str(" AND tag = ?");
            param_values.push(Box::new(tag.clone()));
        }
        if let Some(ref src) = q.source {
            sql.push_str(" AND source = ?");
            param_values.push(Box::new(src.clone()));
        }
        if let Some(ref tgt) = q.target {
            sql.push_str(" AND target = ?");
            param_values.push(Box::new(tgt.clone()));
        }
        if let Some(ref sk) = q.session_key {
            sql.push_str(" AND session_key = ?");
            param_values.push(Box::new(sk.clone()));
        }
        if let Some(ref pr) = q.parent_ref {
            sql.push_str(" AND parent_ref = ?");
            param_values.push(Box::new(pr.clone()));
        }
        if let Some(ref since) = q.since {
            sql.push_str(" AND created_at >= ?");
            param_values.push(Box::new(since.to_rfc3339()));
        }
        if let Some(ref until) = q.until {
            sql.push_str(" AND created_at <= ?");
            param_values.push(Box::new(until.to_rfc3339()));
        }

        sql.push_str(" ORDER BY created_at ASC");

        if let Some(limit) = q.limit {
            sql.push_str(" LIMIT ?");
            param_values.push(Box::new(limit as i64));
        }
        if let Some(offset) = q.offset {
            sql.push_str(" OFFSET ?");
            param_values.push(Box::new(offset as i64));
        }

        let params_ref: Vec<&dyn rusqlite::types::ToSql> = param_values.iter().map(|p| p.as_ref()).collect();
        let mut stmt = self.store.conn().prepare(&sql)?;
        let rows = stmt.query_map(params_ref.as_slice(), |row| {
            Ok(Hypha {
                id: row.get("id")?,
                event_type: row.get("event_type")?,
                tag: row.get("tag")?,
                source: row.get("source")?,
                target: row.get("target")?,
                content: row.get("content")?,
                metadata: {
                    let s: String = row.get("metadata")?;
                    serde_json::from_str(&s).unwrap_or(serde_json::Value::Object(Default::default()))
                },
                session_key: row.get("session_key")?,
                parent_ref: row.get("parent_ref")?,
                version: row.get("version")?,
                created_at: {
                    let s: String = row.get("created_at")?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
            })
        })?;

        rows.collect::<std::result::Result<Vec<_>, _>>()
            .map_err(BridgeError::Database)
    }

    /// Count events with a specific tag (exact match, not LIKE).
    pub fn count_by_tag(&self, tag: &str) -> Result<u64> {
        let count: i64 = self
            .store
            .conn()
            .query_row("SELECT COUNT(*) FROM hyphae WHERE tag = ?1", params![tag], |r| {
                r.get(0)
            })?;
        Ok(count as u64)
    }

    /// Get a single event by ID.
    pub fn get(&self, id: &str) -> Result<Hypha> {
        let mut stmt = self
            .store
            .conn()
            .prepare("SELECT * FROM hyphae WHERE id = ?1")?;
        stmt.query_row(params![id], |row| {
            Ok(Hypha {
                id: row.get("id")?,
                event_type: row.get("event_type")?,
                tag: row.get("tag")?,
                source: row.get("source")?,
                target: row.get("target")?,
                content: row.get("content")?,
                metadata: {
                    let s: String = row.get("metadata")?;
                    serde_json::from_str(&s).unwrap_or(serde_json::Value::Object(Default::default()))
                },
                session_key: row.get("session_key")?,
                parent_ref: row.get("parent_ref")?,
                version: row.get("version")?,
                created_at: {
                    let s: String = row.get("created_at")?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
            })
        })
        .map_err(|_| BridgeError::EventNotFound(id.to_string()))
    }

    /// Replay all events through a callback (for rebuilding state).
    pub fn replay(&self, mut handler: impl FnMut(Hypha)) -> Result<u64> {
        let mut stmt = self
            .store
            .conn()
            .prepare("SELECT * FROM hyphae ORDER BY created_at ASC")?;
        let mut count = 0u64;
        let rows = stmt.query_map([], |row| {
            Ok(Hypha {
                id: row.get("id")?,
                event_type: row.get("event_type")?,
                tag: row.get("tag")?,
                source: row.get("source")?,
                target: row.get("target")?,
                content: row.get("content")?,
                metadata: {
                    let s: String = row.get("metadata")?;
                    serde_json::from_str(&s).unwrap_or(serde_json::Value::Object(Default::default()))
                },
                session_key: row.get("session_key")?,
                parent_ref: row.get("parent_ref")?,
                version: row.get("version")?,
                created_at: {
                    let s: String = row.get("created_at")?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
            })
        })?;

        for row in rows {
            if let Ok(hypha) = row {
                handler(hypha);
                count += 1;
            }
        }
        Ok(count)
    }

    /// Total event count.
    pub fn count(&self) -> Result<u64> {
        let c: i64 = self
            .store
            .conn()
            .query_row("SELECT COUNT(*) FROM hyphae", [], |r| r.get(0))?;
        Ok(c as u64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_store() -> NeuralStore {
        NeuralStore::open_memory().unwrap()
    }

    #[test]
    fn emit_and_query() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        let h = hs
            .emit(
                "mission:start",
                "mycelium",
                "Deploy landing page",
                Some("#mission"),
                None,
                serde_json::json!({"priority": "high"}),
                None,
                None,
            )
            .unwrap();

        assert!(!h.id.is_empty());
        assert_eq!(h.event_type, "mission:start");
        assert_eq!(h.tag, Some("#mission".to_string()));

        let results = hs
            .query(&HyphaeQuery {
                tag: Some("#mission".to_string()),
                ..Default::default()
            })
            .unwrap();

        assert_eq!(results.len(), 1);
        assert_eq!(results[0].content, "Deploy landing page");
    }

    #[test]
    fn count_by_tag_exact_match() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        hs.emit("a", "s", "c", Some("#mission"), None, serde_json::json!({}), None, None).unwrap();
        hs.emit("b", "s", "c", Some("#mission-complete"), None, serde_json::json!({}), None, None).unwrap();
        hs.emit("c", "s", "c", Some("#mission"), None, serde_json::json!({}), None, None).unwrap();

        // Unlike LIKE-based matching, exact match should NOT cross-match
        assert_eq!(hs.count_by_tag("#mission").unwrap(), 2);
        assert_eq!(hs.count_by_tag("#mission-complete").unwrap(), 1);
    }

    #[test]
    fn replay_preserves_order() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        hs.emit("first", "s", "1", None, None, serde_json::json!({}), None, None).unwrap();
        hs.emit("second", "s", "2", None, None, serde_json::json!({}), None, None).unwrap();
        hs.emit("third", "s", "3", None, None, serde_json::json!({}), None, None).unwrap();

        let mut types = Vec::new();
        hs.replay(|h| types.push(h.event_type.clone())).unwrap();

        assert_eq!(types, vec!["first", "second", "third"]);
    }

    #[test]
    fn meta_tag_updates_on_emit() {
        let store = test_store();
        let hs = HyphaeStore::new(&store);

        hs.emit("a", "s", "c", Some("#lesson"), None, serde_json::json!({}), None, None).unwrap();
        hs.emit("b", "s", "c", Some("#lesson"), None, serde_json::json!({}), None, None).unwrap();

        let freq: i64 = store
            .conn()
            .query_row("SELECT frequency FROM meta_tags WHERE tag = '#lesson'", [], |r| r.get(0))
            .unwrap();
        assert_eq!(freq, 2);
    }
}
