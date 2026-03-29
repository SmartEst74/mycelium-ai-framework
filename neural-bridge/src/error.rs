//! Error types for the Neural Bridge.

use thiserror::Error;

#[derive(Error, Debug)]
pub enum BridgeError {
    #[error("database error: {0}")]
    Database(#[from] rusqlite::Error),

    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("event not found: {0}")]
    EventNotFound(String),

    #[error("agent not registered: {0}")]
    AgentNotRegistered(String),

    #[error("subscription not found: {0}")]
    SubscriptionNotFound(String),

    #[error("signal expired: {0}")]
    SignalExpired(String),

    #[error("invalid tag: {0}")]
    InvalidTag(String),

    #[error("consolidation failed: {0}")]
    ConsolidationFailed(String),

    #[error("crystallization failed: {0}")]
    CrystallizationFailed(String),

    #[error("io error: {0}")]
    Io(#[from] std::io::Error),

    #[error("websocket error: {0}")]
    WebSocket(#[from] tokio_tungstenite::tungstenite::Error),

    #[error("bridge is shutting down")]
    ShuttingDown,
}

pub type Result<T> = std::result::Result<T, BridgeError>;
