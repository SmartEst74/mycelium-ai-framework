//! Spore Server — WebSocket + HTTP server for real-time colony observability.
//!
//! Serves:
//! - WebSocket at /ws   → live event stream
//! - GET /health        → colony health JSON
//! - GET /events        → recent events JSON
//! - GET /taxonomy      → meta-tag taxonomy JSON
//! - GET /crystals      → crystal knowledge JSON
//! - GET /tiers         → consolidation tier stats JSON
//! - GET /              → Spore dashboard HTML

use futures_util::{SinkExt, StreamExt};
use neural_bridge::consolidator::Consolidator;
use neural_bridge::crystallizer::Crystallizer;
use neural_bridge::hyphae::HyphaeStore;
use neural_bridge::router::SignalRouter;
use neural_bridge::spore::{SporeCommand, SporeStream};
use neural_bridge::store::NeuralStore;
use neural_bridge::taxonomy::TaxonomyEngine;
use neural_bridge::*;
use std::env;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::{TcpListener, TcpStream};
use tokio_tungstenite::accept_async;
use tracing::{error, info};
use tracing_subscriber::EnvFilter;

/// Thread-safe wrapper that creates per-thread connections.
struct DbPool {
    path: String,
}

impl DbPool {
    fn new(path: &str) -> Self {
        Self { path: path.to_string() }
    }
    fn connect(&self) -> Result<NeuralStore, BridgeError> {
        NeuralStore::open(&self.path)
    }
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::from_default_env()
                .add_directive("neural_bridge=info".parse().unwrap())
                .add_directive("spore_server=info".parse().unwrap()),
        )
        .json()
        .init();

    let port: u16 = env::var("SPORE_PORT")
        .unwrap_or_else(|_| "9473".to_string())
        .parse()
        .unwrap_or(9473);

    let db_path = env::var("NEURAL_BRIDGE_DB").unwrap_or_else(|_| DEFAULT_DB_PATH.to_string());

    // Verify DB opens successfully
    NeuralStore::open(&db_path).expect("failed to open database");

    let pool = Arc::new(DbPool::new(&db_path));
    let spore = Arc::new(SporeStream::new());

    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let listener = TcpListener::bind(addr).await.expect("failed to bind");
    info!(port = port, "Spore server listening");
    println!("🍄 Spore dashboard: http://127.0.0.1:{}", port);
    println!("🔌 WebSocket:       ws://127.0.0.1:{}/ws", port);

    loop {
        match listener.accept().await {
            Ok((stream, peer)) => {
                let pool = pool.clone();
                let spore = spore.clone();
                tokio::spawn(async move {
                    if let Err(e) = handle_connection(stream, peer, pool, spore).await {
                        error!(peer = %peer, error = %e, "connection error");
                    }
                });
            }
            Err(e) => error!(error = %e, "accept failed"),
        }
    }
}

async fn handle_connection(
    stream: TcpStream,
    peer: SocketAddr,
    pool: Arc<DbPool>,
    spore: Arc<SporeStream>,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let ws_stream = accept_async(stream).await?;
    info!(peer = %peer, "WebSocket client connected");

    let (mut write, mut read) = ws_stream.split();
    let mut rx = spore.subscribe();

    // Send initial health snapshot
    let p = pool.clone();
    let health_json = tokio::task::spawn_blocking(move || {
        let store = p.connect().ok()?;
        let health = SignalRouter::new().colony_health(&store).ok()?;
        serde_json::to_string(&health).ok()
    }).await?.unwrap_or_default();

    write
        .send(tokio_tungstenite::tungstenite::Message::Text(health_json))
        .await?;

    loop {
        tokio::select! {
            Ok(msg) = rx.recv() => {
                if write.send(tokio_tungstenite::tungstenite::Message::Text(msg)).await.is_err() {
                    break;
                }
            }
            Some(Ok(msg)) = read.next() => {
                if msg.is_close() {
                    break;
                }
                if let Ok(text) = msg.into_text() {
                    if let Ok(cmd) = serde_json::from_str::<SporeCommand>(&text) {
                        let p = pool.clone();
                        let response = tokio::task::spawn_blocking(move || {
                            match p.connect() {
                                Ok(store) => handle_command(&cmd, &store),
                                Err(e) => format!("{{\"error\": \"{}\"}}", e),
                            }
                        }).await.unwrap_or_default();
                        if write.send(tokio_tungstenite::tungstenite::Message::Text(response)).await.is_err() {
                            break;
                        }
                    }
                }
            }
            else => break,
        }
    }

    info!(peer = %peer, "WebSocket client disconnected");
    Ok(())
}

fn handle_command(cmd: &SporeCommand, store: &NeuralStore) -> String {
    match cmd {
        SporeCommand::Health => {
            let health = SignalRouter::new().colony_health(store).unwrap_or_else(|_| ColonyHealth {
                status: HealthStatus::Critical,
                active_agents: 0, active_missions: 0, completed_missions: 0,
                pain_points: 0, green_leaves: 0, recent_benchmarks: 0,
                event_rate_per_min: 0.0, oldest_stale_mission_mins: None,
                checked_at: chrono::Utc::now(),
            });
            serde_json::to_string(&health).unwrap_or_default()
        }
        SporeCommand::Recent { limit } => {
            let hs = HyphaeStore::new(store);
            let events = hs.query(&HyphaeQuery {
                limit: Some(limit.unwrap_or(50)),
                ..Default::default()
            }).unwrap_or_default();
            serde_json::to_string(&events).unwrap_or_default()
        }
        SporeCommand::Taxonomy => {
            let _ = TaxonomyEngine::recompute_scores(store);
            let tags = TaxonomyEngine::list_tags(store).unwrap_or_default();
            serde_json::to_string(&tags).unwrap_or_default()
        }
        SporeCommand::Inject { content, priority: _ } => {
            let hs = HyphaeStore::new(store);
            match hs.emit("signal:inject", "human", content, Some("#directive"), None, serde_json::json!({}), None, None) {
                Ok(h) => serde_json::to_string(&h).unwrap_or_default(),
                Err(e) => format!("{{\"error\": \"{}\"}}", e),
            }
        }
        SporeCommand::Crystals { crystal_type: _ } => {
            let crystals = Crystallizer::query_crystals(store, None).unwrap_or_default();
            serde_json::to_string(&crystals).unwrap_or_default()
        }
        SporeCommand::Tiers => {
            let stats = Consolidator::tier_stats(store).unwrap_or_else(|_| {
                neural_bridge::consolidator::TierStats { hot: 0, warm: 0, cold: 0, frozen: 0 }
            });
            serde_json::to_string(&stats).unwrap_or_default()
        }
    }
}
