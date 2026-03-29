//! Core domain types for the Neural Bridge.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Unique event identifier — UUIDv7 (time-sortable, globally unique).
pub type EventId = String;

/// Agent identifier within the colony.
pub type AgentId = String;

/// Tag for classification (e.g. `#mission`, `#lesson`, `#pain-point`).
pub type Tag = String;

/// A hypha event — the atomic unit of colony memory.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hypha {
    pub id: EventId,
    pub event_type: String,
    pub tag: Option<Tag>,
    pub source: AgentId,
    pub target: Option<AgentId>,
    pub content: String,
    pub metadata: serde_json::Value,
    pub session_key: Option<String>,
    pub parent_ref: Option<EventId>,
    pub version: u32,
    pub created_at: DateTime<Utc>,
}

/// A signal injection — human or system input to the colony.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Signal {
    pub id: EventId,
    pub signal_type: SignalType,
    pub source: String,
    pub content: String,
    pub metadata: serde_json::Value,
    pub priority: Priority,
    pub expires_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}

/// Signal priority levels.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Priority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
}

/// Types of signals that can be injected.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SignalType {
    Directive,
    Query,
    Override,
    Halt,
    Resume,
}

/// A subscription binding — agent watching a pattern.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mycorrhiza {
    pub id: String,
    pub agent_id: AgentId,
    pub pattern: String,
    pub filter_tags: Vec<Tag>,
    pub active: bool,
    pub created_at: DateTime<Utc>,
}

/// A registered colony member.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Colony {
    pub agent_id: AgentId,
    pub agent_type: AgentType,
    pub role: String,
    pub model: String,
    pub capabilities: Vec<String>,
    pub status: AgentStatus,
    pub last_heartbeat: DateTime<Utc>,
    pub registered_at: DateTime<Utc>,
}

/// Agent types in the colony hierarchy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AgentType {
    Mycelium,
    Scout,
    ArmyAnt,
    DynamicAnt,
}

/// Agent lifecycle status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AgentStatus {
    Spawning,
    Active,
    Idle,
    Terminated,
    Failed,
}

/// Self-evaluation scores from a Dynamic Ant.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelfEval {
    pub agent_id: AgentId,
    pub task_id: EventId,
    pub accuracy: u8,
    pub efficiency: u8,
    pub completeness: u8,
    pub reusability: u8,
    pub notes: String,
    pub created_at: DateTime<Utc>,
}

impl SelfEval {
    /// Average score across all dimensions (1-5 scale).
    pub fn average(&self) -> f32 {
        (self.accuracy + self.efficiency + self.completeness + self.reusability) as f32 / 4.0
    }

    /// Whether this eval indicates a reusable lesson (all >= 4).
    pub fn is_lesson(&self) -> bool {
        self.accuracy >= 4 && self.efficiency >= 4 && self.completeness >= 4 && self.reusability >= 4
    }

    /// Whether this eval indicates a pain point (any < 3).
    pub fn is_pain_point(&self) -> bool {
        self.accuracy < 3 || self.efficiency < 3 || self.completeness < 3 || self.reusability < 3
    }
}

/// Query filters for retrieving hyphae.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct HyphaeQuery {
    pub event_type: Option<String>,
    pub tag: Option<Tag>,
    pub source: Option<AgentId>,
    pub target: Option<AgentId>,
    pub session_key: Option<String>,
    pub parent_ref: Option<EventId>,
    pub since: Option<DateTime<Utc>>,
    pub until: Option<DateTime<Utc>>,
    pub limit: Option<u32>,
    pub offset: Option<u32>,
}

/// Colony health snapshot.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColonyHealth {
    pub status: HealthStatus,
    pub active_agents: u32,
    pub active_missions: u32,
    pub completed_missions: u32,
    pub pain_points: u32,
    pub green_leaves: u32,
    pub recent_benchmarks: u32,
    pub event_rate_per_min: f64,
    pub oldest_stale_mission_mins: Option<f64>,
    pub checked_at: DateTime<Utc>,
}

/// Overall colony health status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum HealthStatus {
    Healthy,
    Degraded,
    Unhealthy,
    Critical,
}

/// Consolidation tier — how aggressively memory is compacted.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConsolidationTier {
    /// Raw events, no compaction. Age < 1 hour.
    Hot,
    /// Summarised per-session. Age 1h-24h.
    Warm,
    /// Distilled lessons only. Age > 24h.
    Cold,
    /// Archived, queryable but compressed. Age > 7d.
    Frozen,
}

/// A crystallised knowledge unit — promoted from events to durable memory.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Crystal {
    pub id: String,
    pub crystal_type: CrystalType,
    pub title: String,
    pub content: String,
    pub source_events: Vec<EventId>,
    pub tags: Vec<Tag>,
    pub confidence: f32,
    pub access_count: u64,
    pub last_accessed: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

/// Types of crystallised knowledge.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CrystalType {
    Lesson,
    Benchmark,
    Shortcut,
    Pattern,
    Warning,
}

/// A meta-tag with computed relevance score.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaTag {
    pub tag: Tag,
    pub frequency: u64,
    pub last_seen: DateTime<Utc>,
    pub relevance_score: f64,
    pub related_tags: Vec<Tag>,
}

/// Real-time event for Spore WebSocket stream.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SporeEvent {
    pub event_id: EventId,
    pub event_type: String,
    pub source: AgentId,
    pub tag: Option<Tag>,
    pub summary: String,
    pub timestamp: DateTime<Utc>,
    pub colony_health: Option<ColonyHealth>,
}
