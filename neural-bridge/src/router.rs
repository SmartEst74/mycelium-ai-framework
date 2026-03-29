//! SignalRouter — Pub/sub with pattern matching across agents.
//!
//! Handles signal injection (human → colony), subscription management,
//! and real-time notification dispatch.

use crate::error::{BridgeError, Result};
use crate::store::NeuralStore;
use crate::types::*;
use chrono::Utc;
use crossbeam_channel::{Receiver, Sender};
use dashmap::DashMap;
use rusqlite::params;
use std::sync::Arc;
use uuid::Uuid;

/// A handler that receives matched events.
type EventHandler = Box<dyn Fn(&Hypha) + Send + Sync>;

/// Routes signals and events to subscribed agents.
pub struct SignalRouter {
    handlers: Arc<DashMap<String, EventHandler>>,
    broadcast_tx: Sender<Hypha>,
    broadcast_rx: Receiver<Hypha>,
}

impl SignalRouter {
    pub fn new() -> Self {
        let (tx, rx) = crossbeam_channel::unbounded();
        Self {
            handlers: Arc::new(DashMap::new()),
            broadcast_tx: tx,
            broadcast_rx: rx,
        }
    }

    /// Inject a signal from a human or system into the colony.
    pub fn inject_signal(
        &self,
        store: &NeuralStore,
        signal_type: SignalType,
        source: &str,
        content: &str,
        metadata: serde_json::Value,
        priority: Priority,
        expires_at: Option<chrono::DateTime<Utc>>,
    ) -> Result<Signal> {
        let id = Uuid::now_v7().to_string();
        let now = Utc::now();

        store.conn().execute(
            "INSERT INTO signals (id, signal_type, source, content, metadata, priority, expires_at, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                id,
                serde_json::to_string(&signal_type)?,
                source,
                content,
                serde_json::to_string(&metadata)?,
                priority as i32,
                expires_at.map(|e| e.to_rfc3339()),
                now.to_rfc3339(),
            ],
        )?;

        Ok(Signal {
            id,
            signal_type,
            source: source.to_string(),
            content: content.to_string(),
            metadata,
            priority,
            expires_at,
            created_at: now,
        })
    }

    /// Subscribe an agent to a pattern. Returns subscription ID.
    pub fn subscribe(
        &self,
        store: &NeuralStore,
        agent_id: &str,
        pattern: &str,
        filter_tags: Vec<String>,
        handler: impl Fn(&Hypha) + Send + Sync + 'static,
    ) -> Result<String> {
        let id = Uuid::now_v7().to_string();

        store.conn().execute(
            "INSERT INTO mycorrhizae (id, agent_id, pattern, filter_tags, active)
             VALUES (?1, ?2, ?3, ?4, 1)",
            params![
                id,
                agent_id,
                pattern,
                serde_json::to_string(&filter_tags)?,
            ],
        )?;

        self.handlers.insert(id.clone(), Box::new(handler));
        Ok(id)
    }

    /// Unsubscribe by ID.
    pub fn unsubscribe(&self, store: &NeuralStore, subscription_id: &str) -> Result<()> {
        let updated = store.conn().execute(
            "UPDATE mycorrhizae SET active = 0 WHERE id = ?1",
            params![subscription_id],
        )?;
        if updated == 0 {
            return Err(BridgeError::SubscriptionNotFound(subscription_id.to_string()));
        }
        self.handlers.remove(subscription_id);
        Ok(())
    }

    /// Register an agent in the colony.
    pub fn register_agent(
        &self,
        store: &NeuralStore,
        agent_id: &str,
        agent_type: AgentType,
        role: &str,
        model: &str,
        capabilities: Vec<String>,
    ) -> Result<Colony> {
        let now = Utc::now();
        store.conn().execute(
            "INSERT INTO colonies (agent_id, agent_type, role, model, capabilities, status, last_heartbeat, registered_at)
             VALUES (?1, ?2, ?3, ?4, ?5, 'active', ?6, ?6)
             ON CONFLICT(agent_id) DO UPDATE SET
                status = 'active',
                last_heartbeat = ?6,
                model = ?4,
                capabilities = ?5",
            params![
                agent_id,
                serde_json::to_string(&agent_type)?,
                role,
                model,
                serde_json::to_string(&capabilities)?,
                now.to_rfc3339(),
            ],
        )?;

        Ok(Colony {
            agent_id: agent_id.to_string(),
            agent_type,
            role: role.to_string(),
            model: model.to_string(),
            capabilities,
            status: AgentStatus::Active,
            last_heartbeat: now,
            registered_at: now,
        })
    }

    /// Record agent heartbeat.
    pub fn heartbeat(&self, store: &NeuralStore, agent_id: &str) -> Result<()> {
        let updated = store.conn().execute(
            "UPDATE colonies SET last_heartbeat = datetime('now'), status = 'active' WHERE agent_id = ?1",
            params![agent_id],
        )?;
        if updated == 0 {
            return Err(BridgeError::AgentNotRegistered(agent_id.to_string()));
        }
        Ok(())
    }

    /// Notify all matching subscribers of a new event.
    pub fn notify(&self, hypha: &Hypha) {
        // Broadcast for Spore stream
        let _ = self.broadcast_tx.send(hypha.clone());

        // Notify in-process subscribers
        for entry in self.handlers.iter() {
            entry.value()(hypha);
        }
    }

    /// Get the broadcast receiver for Spore streaming.
    pub fn broadcast_receiver(&self) -> Receiver<Hypha> {
        self.broadcast_rx.clone()
    }

    /// List active agents in the colony.
    pub fn active_agents(&self, store: &NeuralStore) -> Result<Vec<Colony>> {
        let mut stmt = store.conn().prepare(
            "SELECT * FROM colonies WHERE status = 'active' ORDER BY registered_at ASC",
        )?;
        let rows = stmt.query_map([], |row| {
            let caps_str: String = row.get("capabilities")?;
            Ok(Colony {
                agent_id: row.get("agent_id")?,
                agent_type: {
                    let s: String = row.get("agent_type")?;
                    serde_json::from_str(&s).unwrap_or(AgentType::DynamicAnt)
                },
                role: row.get("role")?,
                model: row.get("model")?,
                capabilities: serde_json::from_str(&caps_str).unwrap_or_default(),
                status: AgentStatus::Active,
                last_heartbeat: {
                    let s: String = row.get("last_heartbeat")?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
                registered_at: {
                    let s: String = row.get("registered_at")?;
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or_else(|_| Utc::now())
                },
            })
        })?;

        rows.collect::<std::result::Result<Vec<_>, _>>()
            .map_err(BridgeError::Database)
    }

    /// Compute colony health from current state.
    pub fn colony_health(&self, store: &NeuralStore) -> Result<ColonyHealth> {
        let conn = store.conn();

        let active_agents: u32 = conn
            .query_row("SELECT COUNT(*) FROM colonies WHERE status = 'active'", [], |r| r.get(0))?;
        let active_missions: u32 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE tag = '#mission' AND id NOT IN (SELECT parent_ref FROM hyphae WHERE tag = '#mission-complete' AND parent_ref IS NOT NULL)",
            [],
            |r| r.get(0),
        ).unwrap_or(0);
        let completed_missions: u32 = conn
            .query_row("SELECT COUNT(*) FROM hyphae WHERE tag = '#mission-complete'", [], |r| r.get(0))?;
        let pain_points: u32 = conn
            .query_row("SELECT COUNT(*) FROM hyphae WHERE tag = '#pain-point'", [], |r| r.get(0))?;
        let green_leaves: u32 = conn
            .query_row("SELECT COUNT(*) FROM hyphae WHERE tag = '#green-leaf'", [], |r| r.get(0))?;
        let recent_benchmarks: u32 = conn.query_row(
            "SELECT COUNT(*) FROM hyphae WHERE tag = '#benchmark' AND created_at > datetime('now', '-7 days')",
            [],
            |r| r.get(0),
        )?;
        let event_rate: f64 = conn.query_row(
            "SELECT CAST(COUNT(*) AS REAL) / MAX(1, (julianday('now') - julianday(MIN(created_at))) * 1440) FROM hyphae WHERE created_at > datetime('now', '-1 hour')",
            [],
            |r| r.get(0),
        ).unwrap_or(0.0);

        let status = if pain_points > completed_missions * 2 {
            HealthStatus::Critical
        } else if pain_points > completed_missions {
            HealthStatus::Unhealthy
        } else if active_agents == 0 {
            HealthStatus::Degraded
        } else {
            HealthStatus::Healthy
        };

        Ok(ColonyHealth {
            status,
            active_agents,
            active_missions,
            completed_missions,
            pain_points,
            green_leaves,
            recent_benchmarks,
            event_rate_per_min: event_rate,
            oldest_stale_mission_mins: None,
            checked_at: Utc::now(),
        })
    }
}

impl Default for SignalRouter {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU32, Ordering};

    fn test_store() -> NeuralStore {
        NeuralStore::open_memory().unwrap()
    }

    #[test]
    fn inject_and_query_signal() {
        let store = test_store();
        let router = SignalRouter::new();

        let sig = router
            .inject_signal(
                &store,
                SignalType::Directive,
                "jon",
                "Focus on CV deployment",
                serde_json::json!({}),
                Priority::High,
                None,
            )
            .unwrap();

        assert!(!sig.id.is_empty());
        assert_eq!(sig.priority, Priority::High);
    }

    #[test]
    fn register_and_heartbeat_agent() {
        let store = test_store();
        let router = SignalRouter::new();

        let colony = router
            .register_agent(&store, "scout-1", AgentType::Scout, "researcher", "step-3.5-flash", vec!["research".into()])
            .unwrap();

        assert_eq!(colony.agent_id, "scout-1");
        assert_eq!(colony.status, AgentStatus::Active);

        router.heartbeat(&store, "scout-1").unwrap();

        let agents = router.active_agents(&store).unwrap();
        assert_eq!(agents.len(), 1);
    }

    #[test]
    fn subscribe_and_notify() {
        let store = test_store();
        let router = SignalRouter::new();
        let counter = Arc::new(AtomicU32::new(0));
        let c = counter.clone();

        router
            .subscribe(&store, "test-agent", "mission:*", vec![], move |_| {
                c.fetch_add(1, Ordering::SeqCst);
            })
            .unwrap();

        let hypha = Hypha {
            id: "test-1".into(),
            event_type: "mission:start".into(),
            tag: Some("#mission".into()),
            source: "mycelium".into(),
            target: None,
            content: "test".into(),
            metadata: serde_json::json!({}),
            session_key: None,
            parent_ref: None,
            version: 1,
            created_at: Utc::now(),
        };

        router.notify(&hypha);
        assert_eq!(counter.load(Ordering::SeqCst), 1);
    }
}
