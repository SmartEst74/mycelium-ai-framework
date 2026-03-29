//! Neural Bridge CLI — command-line interface for the colony brain.
//!
//! Commands:
//!   emit      Emit an event into the hyphae store
//!   query     Query events by filters
//!   health    Check colony health
//!   taxonomy  Show meta-tag taxonomy
//!   consolidate  Run LCM consolidation pass
//!   crystallize  Run QMD crystallization pass
//!   serve     Start the Spore WebSocket server

use neural_bridge::*;
use neural_bridge::consolidator::Consolidator;
use neural_bridge::crystallizer::Crystallizer;
use neural_bridge::hyphae::HyphaeStore;
use neural_bridge::store::NeuralStore;
use neural_bridge::taxonomy::TaxonomyEngine;
use std::env;
use tracing_subscriber::EnvFilter;

fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive("neural_bridge=info".parse().unwrap()))
        .json()
        .init();

    let args: Vec<String> = env::args().collect();
    let cmd = args.get(1).map(|s| s.as_str()).unwrap_or("help");

    let db_path = env::var("NEURAL_BRIDGE_DB").unwrap_or_else(|_| DEFAULT_DB_PATH.to_string());
    let store = NeuralStore::open(&db_path).expect("failed to open neural bridge database");

    match cmd {
        "emit" => {
            let event_type = args.get(2).expect("usage: neural-bridge emit <type> <source> <content> [tag]");
            let source = args.get(3).expect("missing source");
            let content = args.get(4).expect("missing content");
            let tag = args.get(5).map(|s| s.as_str());

            let hs = HyphaeStore::new(&store);
            let h = hs.emit(event_type, source, content, tag, None, serde_json::json!({}), None, None)
                .expect("emit failed");
            println!("{}", serde_json::to_string_pretty(&h).unwrap());
        }

        "query" => {
            let mut q = HyphaeQuery::default();
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--type" => { q.event_type = args.get(i + 1).cloned(); i += 2; }
                    "--tag" => { q.tag = args.get(i + 1).cloned(); i += 2; }
                    "--source" => { q.source = args.get(i + 1).cloned(); i += 2; }
                    "--limit" => { q.limit = args.get(i + 1).and_then(|s| s.parse().ok()); i += 2; }
                    _ => { i += 1; }
                }
            }

            let hs = HyphaeStore::new(&store);
            let events = hs.query(&q).expect("query failed");
            for e in &events {
                println!("[{}] {} @ {} by {} {}",
                    &e.id[..8], e.event_type, e.created_at.format("%H:%M:%S"),
                    e.source, e.tag.as_deref().unwrap_or(""));
            }
            println!("\n{} events", events.len());
        }

        "health" => {
            let router = SignalRouter::new();
            let health = router.colony_health(&store).expect("health check failed");
            println!("{}", serde_json::to_string_pretty(&health).unwrap());
        }

        "taxonomy" => {
            TaxonomyEngine::recompute_scores(&store).expect("recompute failed");
            let tags = TaxonomyEngine::list_tags(&store).expect("list failed");
            for t in &tags {
                println!("{:<20} freq={:<5} relevance={:.3} related={:?}",
                    t.tag, t.frequency, t.relevance_score, t.related_tags);
            }
        }

        "consolidate" => {
            let report = Consolidator::consolidate(&store).expect("consolidation failed");
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
        }

        "crystallize" => {
            let report = Crystallizer::crystallize(&store).expect("crystallization failed");
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
        }

        "crystals" => {
            let crystals = Crystallizer::query_crystals(&store, None).expect("query failed");
            for c in &crystals {
                println!("[{:.8}] {:?} ({:.0}%) — {}",
                    c.id, c.crystal_type, c.confidence * 100.0, c.title);
            }
            println!("\n{} crystals", crystals.len());
        }

        "tiers" => {
            let stats = Consolidator::tier_stats(&store).expect("tier stats failed");
            println!("{}", serde_json::to_string_pretty(&stats).unwrap());
        }

        "serve" => {
            let port: u16 = env::var("SPORE_PORT")
                .unwrap_or_else(|_| "9473".to_string())
                .parse()
                .unwrap_or(9473);
            println!("Start Spore server with: spore-server (port {})", port);
            println!("  SPORE_PORT={} spore-server", port);
        }

        _ => {
            println!("Neural Bridge v{} — Colony Brain CLI", VERSION);
            println!();
            println!("Commands:");
            println!("  emit <type> <source> <content> [tag]   Emit an event");
            println!("  query [--type T] [--tag T] [--limit N] Query events");
            println!("  health                                  Colony health");
            println!("  taxonomy                                Meta-tag taxonomy");
            println!("  consolidate                             Run LCM compaction");
            println!("  crystallize                             Run QMD promotion");
            println!("  crystals                                List crystal knowledge");
            println!("  tiers                                   Consolidation tier stats");
            println!();
            println!("Environment:");
            println!("  NEURAL_BRIDGE_DB   Database path (default: {})", DEFAULT_DB_PATH);
            println!("  RUST_LOG           Log level (default: neural_bridge=info)");
        }
    }
}
