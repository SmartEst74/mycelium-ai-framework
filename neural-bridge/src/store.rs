//! NeuralStore — SQLite persistence layer for the bridge.
//!
//! Owns the database connection and provides migration, backup, and
//! transaction primitives. All other modules operate through this store.

use crate::error::Result;
use rusqlite::Connection;
use std::path::Path;
use tracing::info;

/// The shared SQLite store backing all bridge subsystems.
pub struct NeuralStore {
    conn: Connection,
}

impl NeuralStore {
    /// Open (or create) the store at the given path.
    pub fn open(path: impl AsRef<Path>) -> Result<Self> {
        let conn = Connection::open(path)?;
        let store = Self { conn };
        store.configure_pragmas()?;
        store.migrate()?;
        Ok(store)
    }

    /// Open an in-memory store (for testing).
    pub fn open_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        let store = Self { conn };
        store.configure_pragmas()?;
        store.migrate()?;
        Ok(store)
    }

    /// Access the raw connection (for subsystem queries).
    pub fn conn(&self) -> &Connection {
        &self.conn
    }

    fn configure_pragmas(&self) -> Result<()> {
        self.conn.execute_batch(
            "PRAGMA journal_mode = WAL;
             PRAGMA busy_timeout = 5000;
             PRAGMA synchronous = NORMAL;
             PRAGMA cache_size = -64000;
             PRAGMA foreign_keys = ON;
             PRAGMA temp_store = MEMORY;",
        )?;
        Ok(())
    }

    fn migrate(&self) -> Result<()> {
        self.conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            );",
        )?;

        let current: i32 = self
            .conn
            .query_row(
                "SELECT COALESCE(MAX(version), 0) FROM schema_version",
                [],
                |r| r.get(0),
            )
            .unwrap_or(0);

        if current < 1 {
            self.migrate_v1()?;
        }

        info!(version = 1, "neural-bridge schema ready");
        Ok(())
    }

    fn migrate_v1(&self) -> Result<()> {
        self.conn.execute_batch(
            "-- Hyphae: append-only event log
            CREATE TABLE IF NOT EXISTS hyphae (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                tag TEXT,
                source TEXT NOT NULL,
                target TEXT,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                session_key TEXT,
                parent_ref TEXT REFERENCES hyphae(id),
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_hyphae_type ON hyphae(event_type);
            CREATE INDEX IF NOT EXISTS idx_hyphae_tag ON hyphae(tag);
            CREATE INDEX IF NOT EXISTS idx_hyphae_source ON hyphae(source);
            CREATE INDEX IF NOT EXISTS idx_hyphae_created ON hyphae(created_at);
            CREATE INDEX IF NOT EXISTS idx_hyphae_parent ON hyphae(parent_ref);
            CREATE INDEX IF NOT EXISTS idx_hyphae_session ON hyphae(session_key);

            -- Signals: human/system injections
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                signal_type TEXT NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                priority INTEGER NOT NULL DEFAULT 1,
                expires_at TEXT,
                consumed_by TEXT,
                consumed_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
            CREATE INDEX IF NOT EXISTS idx_signals_priority ON signals(priority DESC);

            -- Mycorrhizae: subscriptions
            CREATE TABLE IF NOT EXISTS mycorrhizae (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                pattern TEXT NOT NULL,
                filter_tags TEXT NOT NULL DEFAULT '[]',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_myco_agent ON mycorrhizae(agent_id);
            CREATE INDEX IF NOT EXISTS idx_myco_active ON mycorrhizae(active);

            -- Colonies: agent registry
            CREATE TABLE IF NOT EXISTS colonies (
                agent_id TEXT PRIMARY KEY,
                agent_type TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                capabilities TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'spawning',
                last_heartbeat TEXT NOT NULL DEFAULT (datetime('now')),
                registered_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_colony_type ON colonies(agent_type);
            CREATE INDEX IF NOT EXISTS idx_colony_status ON colonies(status);

            -- Self-evaluations
            CREATE TABLE IF NOT EXISTS self_evals (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                task_id TEXT NOT NULL REFERENCES hyphae(id),
                accuracy INTEGER NOT NULL CHECK(accuracy BETWEEN 1 AND 5),
                efficiency INTEGER NOT NULL CHECK(efficiency BETWEEN 1 AND 5),
                completeness INTEGER NOT NULL CHECK(completeness BETWEEN 1 AND 5),
                reusability INTEGER NOT NULL CHECK(reusability BETWEEN 1 AND 5),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_eval_agent ON self_evals(agent_id);
            CREATE INDEX IF NOT EXISTS idx_eval_task ON self_evals(task_id);

            -- Crystals: promoted durable knowledge (QMD layer)
            CREATE TABLE IF NOT EXISTS crystals (
                id TEXT PRIMARY KEY,
                crystal_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_events TEXT NOT NULL DEFAULT '[]',
                tags TEXT NOT NULL DEFAULT '[]',
                confidence REAL NOT NULL DEFAULT 0.5,
                access_count INTEGER NOT NULL DEFAULT 0,
                last_accessed TEXT NOT NULL DEFAULT (datetime('now')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_crystal_type ON crystals(crystal_type);
            CREATE INDEX IF NOT EXISTS idx_crystal_confidence ON crystals(confidence DESC);

            -- Meta-tags: taxonomy with computed scores
            CREATE TABLE IF NOT EXISTS meta_tags (
                tag TEXT PRIMARY KEY,
                frequency INTEGER NOT NULL DEFAULT 1,
                last_seen TEXT NOT NULL DEFAULT (datetime('now')),
                relevance_score REAL NOT NULL DEFAULT 0.5,
                related_tags TEXT NOT NULL DEFAULT '[]'
            );

            -- Record migration
            INSERT INTO schema_version (version) VALUES (1);",
        )?;
        info!("applied migration v1: full neural bridge schema");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn opens_in_memory() {
        let store = NeuralStore::open_memory().unwrap();
        // Verify tables exist
        let count: i32 = store
            .conn()
            .query_row(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('hyphae','signals','mycorrhizae','colonies','self_evals','crystals','meta_tags')",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(count, 7);
    }

    #[test]
    fn migration_is_idempotent() {
        let store = NeuralStore::open_memory().unwrap();
        // Re-opening should not fail
        drop(store);
        let _store2 = NeuralStore::open_memory().unwrap();
    }
}
