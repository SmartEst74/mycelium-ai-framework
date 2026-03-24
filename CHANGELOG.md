# Changelog

All notable changes to the Mycelium AI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-24

### Added
- Initial architecture: 4-layer chain of command (Mycelium → Scout Swarm → Army → Dynamic)
- Biological model assignment: brain routes, ants see and execute
- Named memory tools: **QMD** (long-term, curated) and **LCM** (session-level, well-organised, feeds into QMD)
- Memory funnel model: LCM compacts sessions → only valuable knowledge rises to QMD
- Scout Swarm: 4 scout types running in parallel (Tool, Leaf, Benchmark, Integration)
- The Food Chain: scouts find food → ants get stronger → scouts find leaves → brain grows → colony grows
- 178 agency-agent roles from msitarzewski/agency-agents
- Shared memory protocol (QMD integration)
- Model assignment matrix with fallback chains
- Skill & MCP integration architecture (skills and MCP are first-class plugin systems)
- Immutable rules: never spend money, never downgrade models
- Python core module (core/mycelium.py)
- Configuration: models.yaml, rules.yaml
- Documentation: ARCHITECTURE.md, SCOUT-SWARM.md, SKILL-MCP-INTEGRATION.md, ROADMAP.md
- Registry: 178 roles across 18 departments

### Architecture Decisions
- Mycelium uses mimo-v2-pro (1M context, no vision — needs memory, not eyes)
- Dynamic Ants use mimo-v2-omni (vision+tools — the eyes and hands)
- Scout Swarm uses step-3.5-flash (fast/cheap — many in parallel, each narrow-focused)
- Army Ants use mimo-v2-pro (1M context for registry state)
- Scouts are ephemeral — spawn, search, report, die. No permanent scouts.
- Skills and MCP are first-class plugin systems — Mycelium orchestrates them, never replaces them
- Free tier only. Revenue first. No exceptions.
