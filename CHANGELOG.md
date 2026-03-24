# Changelog

All notable changes to the Mycelium AI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-24

### Added
- Initial architecture: 4-layer chain of command (Mycelium → Scout → Army → Dynamic)
- Biological model assignment: brain routes, ants see and execute
- 178 agency-agent roles from msitarzewski/agency-agents
- Shared memory protocol (QMD integration)
- Model assignment matrix with fallback chains
- Immutable rules: never spend money, never downgrade models
- Python core module (core/mycelium.py)
- Configuration: models.yaml, rules.yaml
- Documentation: ARCHITECTURE.md
- Registry: 178 roles across 18 departments

### Architecture Decisions
- Mycelium uses mimo-v2-pro (1M context, no vision — needs memory, not eyes)
- Dynamic Ants use mimo-v2-omni (vision+tools — the eyes and hands)
- Scout uses step-3.5-flash (fast/cheap — probes and reports)
- Army Ants use mimo-v2-pro (1M context for registry state)
- Free tier only. Revenue first. No exceptions.
