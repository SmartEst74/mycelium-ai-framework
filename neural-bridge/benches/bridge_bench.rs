use criterion::{criterion_group, criterion_main, Criterion};
use neural_bridge::hyphae::HyphaeStore;
use neural_bridge::store::NeuralStore;

fn bench_emit(c: &mut Criterion) {
    let store = NeuralStore::open_memory().unwrap();
    let hs = HyphaeStore::new(&store);

    c.bench_function("emit_event", |b| {
        b.iter(|| {
            hs.emit(
                "bench:event", "bench", "benchmark content",
                Some("#benchmark"), None, serde_json::json!({}), None, None,
            ).unwrap();
        });
    });
}

fn bench_query(c: &mut Criterion) {
    let store = NeuralStore::open_memory().unwrap();
    let hs = HyphaeStore::new(&store);

    // Pre-populate
    for i in 0..1000 {
        let tag = if i % 3 == 0 { "#mission" } else if i % 3 == 1 { "#lesson" } else { "#benchmark" };
        hs.emit("bench:event", "bench", &format!("content {}", i), Some(tag), None, serde_json::json!({}), None, None).unwrap();
    }

    c.bench_function("query_by_tag_1000", |b| {
        b.iter(|| {
            hs.query(&neural_bridge::HyphaeQuery {
                tag: Some("#mission".to_string()),
                ..Default::default()
            }).unwrap();
        });
    });
}

criterion_group!(benches, bench_emit, bench_query);
criterion_main!(benches);
