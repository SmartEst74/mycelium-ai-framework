//! SporeStream — Real-time WebSocket event broadcast for observability.
//!
//! Streams colony events to the Spore dashboard. Every emit, every signal,
//! every health check is visible in real-time.

use crate::types::*;
use chrono::Utc;
use crossbeam_channel::Receiver;
use serde::Serialize;
use std::sync::Arc;
use tokio::sync::broadcast;

/// The Spore broadcast channel capacity.
const SPORE_CHANNEL_CAPACITY: usize = 1024;

/// Manages real-time event streaming to WebSocket clients.
pub struct SporeStream {
    tx: broadcast::Sender<String>,
}

impl SporeStream {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(SPORE_CHANNEL_CAPACITY);
        Self { tx }
    }

    /// Get a new receiver for WebSocket clients.
    pub fn subscribe(&self) -> broadcast::Receiver<String> {
        self.tx.subscribe()
    }

    /// Broadcast a hypha event to all connected Spore clients.
    pub fn broadcast_hypha(&self, hypha: &Hypha) {
        let event = SporeEvent {
            event_id: hypha.id.clone(),
            event_type: hypha.event_type.clone(),
            source: hypha.source.clone(),
            tag: hypha.tag.clone(),
            summary: if hypha.content.len() > 200 {
                format!("{}...", &hypha.content[..197])
            } else {
                hypha.content.clone()
            },
            timestamp: hypha.created_at,
            colony_health: None,
        };

        if let Ok(json) = serde_json::to_string(&event) {
            let _ = self.tx.send(json);
        }
    }

    /// Broadcast a colony health update.
    pub fn broadcast_health(&self, health: &ColonyHealth) {
        let event = SporeEvent {
            event_id: format!("health-{}", Utc::now().timestamp_millis()),
            event_type: "colony:health".into(),
            source: "neural-bridge".into(),
            tag: None,
            summary: format!("Colony {:?}: {} agents, {} missions", health.status, health.active_agents, health.completed_missions),
            timestamp: health.checked_at,
            colony_health: Some(health.clone()),
        };

        if let Ok(json) = serde_json::to_string(&event) {
            let _ = self.tx.send(json);
        }
    }

    /// Broadcast a raw JSON message.
    pub fn broadcast_raw(&self, message: &str) {
        let _ = self.tx.send(message.to_string());
    }

    /// Start the bridge between crossbeam channel (sync) and tokio broadcast (async).
    /// This runs in a background task, forwarding events from the SignalRouter
    /// to all connected Spore WebSocket clients.
    pub fn start_bridge(self: Arc<Self>, rx: Receiver<Hypha>) -> tokio::task::JoinHandle<()> {
        tokio::spawn(async move {
            loop {
                match rx.recv() {
                    Ok(hypha) => self.broadcast_hypha(&hypha),
                    Err(_) => break,
                }
            }
        })
    }

    /// Number of active subscribers.
    pub fn subscriber_count(&self) -> usize {
        self.tx.receiver_count()
    }
}

impl Default for SporeStream {
    fn default() -> Self {
        Self::new()
    }
}

/// Message types the Spore dashboard can send to the server.
#[derive(Debug, Serialize, serde::Deserialize)]
#[serde(tag = "type")]
pub enum SporeCommand {
    /// Request current colony health.
    #[serde(rename = "health")]
    Health,
    /// Request recent events.
    #[serde(rename = "recent")]
    Recent { limit: Option<u32> },
    /// Request meta-tag taxonomy.
    #[serde(rename = "taxonomy")]
    Taxonomy,
    /// Inject a signal.
    #[serde(rename = "inject")]
    Inject { content: String, priority: Option<String> },
    /// Request crystal knowledge.
    #[serde(rename = "crystals")]
    Crystals { crystal_type: Option<String> },
    /// Request consolidation tier stats.
    #[serde(rename = "tiers")]
    Tiers,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn broadcast_and_subscribe() {
        let stream = SporeStream::new();
        let mut rx = stream.subscribe();

        let hypha = Hypha {
            id: "test-1".into(),
            event_type: "mission:start".into(),
            tag: Some("#mission".into()),
            source: "mycelium".into(),
            target: None,
            content: "Deploy landing page".into(),
            metadata: serde_json::json!({}),
            session_key: None,
            parent_ref: None,
            version: 1,
            created_at: Utc::now(),
        };

        stream.broadcast_hypha(&hypha);

        let msg = rx.try_recv().unwrap();
        let parsed: SporeEvent = serde_json::from_str(&msg).unwrap();
        assert_eq!(parsed.event_type, "mission:start");
        assert_eq!(parsed.source, "mycelium");
    }
}
