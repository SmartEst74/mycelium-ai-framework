# Contributing to Mycelium AI Framework

We welcome contributions! This framework is designed to be enterprise-ready from day one.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/mycelium-ai-framework.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `python -m pytest tests/`

## Architecture

Please read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before contributing.

The core principle:
- **Mycelium (brain)** routes and reasons — never executes
- **Scout (sensor)** researches and improves — never executes
- **Army Ants (coordinators)** build teams — never executes
- **Dynamic Ants (workers)** execute — one task, one role, one model
- **Shared Memory (QMD)** is the colony's nervous system — every agent reads/writes it

## Model Assignment (Immutable)

| Role | Model | Why |
|------|-------|-----|
| Mycelium (brain) | mimo-v2-pro | 1M context — needs memory, not eyes |
| Dynamic Ants (workers) | mimo-v2-omni | Vision+tools — the eyes and hands |
| Scout (sensor) | step-3.5-flash | Fast, cheap — probes and reports |
| Army Ants (coordinators) | mimo-v2-pro | 1M context for registry state |

**Rule**: Never downgrade models. Only upgrade with proof (benchmarks).

## Shared Memory Protocol

Every agent MUST read and write shared memory. See the [Shared Memory Protocol](docs/ARCHITECTURE.md#shared-memory-protocol--the-colonys-nervous-system) for tag definitions and rules.

## Code Standards

- Python 3.11+
- Type hints required
- Docstrings for public APIs
- Tests for new features
- YAML config over hardcoded values

## Pull Requests

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests
4. Run the full test suite: `python -m pytest`
5. Submit a PR with a clear description

## Enterprise Features

We're building toward:
- Rust core for performance and safety
- OpenTelemetry integration for observability
- Multi-tenant support
- Role-based access control
- Audit logging
- SSO/SAML integration

If you're an enterprise user, please open an issue describing your requirements.

## License

MIT License. See [LICENSE](LICENSE) for details.
