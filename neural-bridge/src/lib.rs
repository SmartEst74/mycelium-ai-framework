//! Neural Bridge — SOTA memory substrate for the Mycelium AI colony.
//!
//! Fuses Liquid Crystal Memory (LCM) session compaction with Quantum Memory
//! Dendrite (QMD) long-term curated storage. Provides:
//!
//! - **Hyphae Store**: Append-only event log (the colony's nervous system)
//! - **Signal Router**: Pub/sub with pattern matching across agents
//! - **Taxonomy Engine**: Automatic meta-tag classification and scoring
//! - **Consolidator**: LCM-style session compaction (lossless → lossy tiers)
//! - **Crystallizer**: QMD-style knowledge promotion (lessons, benchmarks)
//! - **Spore Stream**: Real-time WebSocket event broadcast for observability
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────┐
//! │               Neural Bridge                      │
//! │                                                  │
//! │  HyphaeStore ◄── emit() ── Agents               │
//! │       │                                          │
//! │       ├── SignalRouter ── subscribe()/inject()    │
//! │       ├── TaxonomyEngine ── classify()/score()   │
//! │       ├── Consolidator ── compact()/tier()       │
//! │       ├── Crystallizer ── promote()/curate()     │
//! │       └── SporeStream ── broadcast()/ws()        │
//! └─────────────────────────────────────────────────┘
//! ```

pub mod consolidator;
pub mod crystallizer;
pub mod error;
pub mod hyphae;
pub mod router;
pub mod spore;
pub mod store;
pub mod taxonomy;
pub mod types;

pub use error::BridgeError;
pub use hyphae::HyphaeStore;
pub use router::SignalRouter;
pub use spore::SporeStream;
pub use store::NeuralStore;
pub use taxonomy::TaxonomyEngine;
pub use types::*;

/// Bridge version for protocol negotiation.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Default database path.
pub const DEFAULT_DB_PATH: &str = "neural-bridge.db";
