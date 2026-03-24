# Changelog

## 2026-03-24 — Architecture Naming (Jon's Design)

### Renamed
- **Hyphae** = skill harness (was: no formal name)
- **Rhizomorph** = shared instant memory (was: "shared memory" / "pheromone trails")
- **Mycelium** = core orchestrator (unchanged)

### Added
- `hyphae/` — skill harness directory with README
- `rhizomorph/` — shared memory directory with README
- Biological mapping: Mycelium (core) → Rhizomorph (memory) → Hyphae (skills) → Ants (workers)

### Updated
- `docs/ARCHITECTURE.md` — full rewrite with Hyphae/Rhizomorph/Mycelium
- `README.md` — simplified, correct naming

### Design Decisions
- Skills ARE the integration layer (not MCP, not custom protocols)
- Hyphae are pluggable — Rust native, OpenClaw, MCP, CLI, any language
- Rhizomorph = QMD + LCM + tag protocol
- If better skill/memory system emerges, swap it — never locked in

## 2026-03-24 — Previous

- 178 agency-agent roles cataloged
- Scout swarm architecture
- Model assignment matrix (corrected: brain needs memory, ants need vision)
- Shared memory protocol (tags)
- Pushed to SmartEst74/mycelium-ai-framework
