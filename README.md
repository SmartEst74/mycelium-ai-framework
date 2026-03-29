# 🍄 Mycelium AI Framework

**A multi-agent orchestration framework with proven colonial memory — agents that learn faster together than alone.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 22+](https://img.shields.io/badge/Node.js-22+-green.svg)](https://nodejs.org)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange.svg)](https://openclaw.ai)

## The Problem

AI agents lose all knowledge between sessions. Every time an agent starts a task, it begins from scratch — re-researching the same tools, re-learning the same lessons, re-discovering the same dead ends.

This is not a tool problem. It is an **amnesia problem**.

## The Solution

Mycelium gives AI agents **colonial memory** — a shared knowledge base that compounds across sessions, tasks, and agent instances. Like mycelium networks in nature, information flows between connected organisms, creating collective intelligence greater than any individual.

## Proven Results

| Metric | Solo Agent | Colonial Agent | Improvement |
|--------|-----------|----------------|-------------|
| **Execution time** | 100% baseline | 53% | **47% faster** |
| **Token usage** | 100% baseline | 77% | **23% fewer** |
| **Repeat missions** | 100% baseline | 33% | **67% faster** (compound learning) |
| **State reconstruction** | Impossible | Full | Event-sourced replay |

*Results from `benchmarks/colonial_memory_demo.py` — run it yourself.*

## Quick Start

```bash
# Clone
git clone https://github.com/SmartEst74/mycelium-ai-framework.git
cd mycelium-ai-framework

# One-command setup
make setup

# Run the proof
node --experimental-sqlite benchmarks/colonial_memory_bench.mjs

# Run the full E2E demo
node --experimental-sqlite src/cli.mjs mission "Deploy landing page" --capabilities frontend design
```

## Architecture

```
                        HUMAN
                          │
                          ▼
                  ┌───────────────┐
                  │   MYCELIUM    │  Strategic Brain
                  │   (Brain)     │  Decomposes, spawns, coordinates
                  │               │  NEVER executes, NEVER uses vision
                  └───┬───┬───┬───┘
                      │   │   │
            ┌─────────┘   │   └─────────┐
            ▼             ▼             ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │  SCOUT   │ │  ARMY    │ │ DYNAMIC  │
      │  SWARM   │ │  ANTS    │ │  ANTS    │
      │ research │ │ protect  │ │ execute  │
      │ only     │ │ enforce  │ │ build    │
      └─────┬────┘ └─────┬────┘ └─────┬────┘
            │            │            │
            └────────────┼────────────┘
                         ▼
                  ┌───────────────┐
                  │  RHIZOMORPH   │  Shared Memory
                  │               │
                  │  LCM   QMD    │  Session + Durable
                  └───────────────┘
```

### Four Roles (Biological Analogy)

| Biology | Role | What They Do | What They NEVER Do |
|---------|------|-------------|-------------------|
| **Mycelium** | Brain | Decompose missions, spawn workers, coordinate | Execute, use vision, do research |
| **Scout ant** | Sensor | Research, investigate, benchmark models | Execute, build, deploy |
| **Army ant** | Protector | Security scans, warning enforcement, threat detection | Coordinate, build, plan |
| **Worker ant** | Builder | Execute one focused task, self-evaluate | Coordinate, spawn others |

**Army Ants protect the colony** — they don't coordinate workers. In nature, army ants defend the nest and fight threats. In our framework, they scan for vulnerabilities, enforce hard constraints, and track warnings until fully resolved.

### Three-Layer Memory

| Layer | System | Purpose |
|-------|--------|---------|
| **Nervous System** | Event Bus (Rhizomorph) | Raw events from all agents |
| **Context Brain** | LCM (Lossless Claw) | Conversation compaction |
| **Colonial Memory** | QMD | Durable searchable knowledge |

**The Curator** bridges LCM to QMD: extracts tagged knowledge from session summaries and writes it to durable, searchable memory. This is what creates compound learning.

### Why It Compounds

```
Mission 1: Agent researches deployment → writes #lesson to QMD
Mission 2: Agent searches QMD → finds deployment lesson → skips research → 23% faster
Mission 3: Agent searches QMD → finds deployment + config lessons → skips both → 67% faster
Mission N: Agent has full context from all prior work → near-instant
```

## Components

| Component | Description | Status |
|-----------|-------------|--------|
| **Core** | Mycelium orchestrator, model routing | Working |
| **Registry** | 178+ specialized agent roles | Imported |
| **Rhizomorph** | Event bus with replay (exact tag matching) | Proven |
| **Neural Bridge** | Rust SOTA memory substrate (LCM + QMD) | Working |
| **Spore Dashboard** | Real-time WebSocket colony visualizer | Working |
| **Self-Eval** | Agent self-evaluation after every task | Working |
| **Model Config** | Config-driven model assignment (YAML) | Working |
| **Circuit Breaker** | Provider retry + fail-fast protection | Working |
| **Curator** | LCM to QMD knowledge bridge | Prototype |
| **Benchmark** | Solo vs colonial comparison | 47% faster |
| **Enforcement** | Pre-commit hooks, validation | Working |
| **Bootstrap** | Portable knowledge import | Working |
| **CI/CD** | GitHub Actions (Node + Rust tests) | Working |

## Neural Bridge (Rust)

The `neural-bridge/` crate is the SOTA memory substrate — a Rust skill that fuses the best of LCM (session compaction) and QMD (durable knowledge) into a single high-performance layer.

**Subsystems:**

| Module | Purpose |
|--------|---------|
| `hyphae` | Event store with exact tag matching, meta-tag auto-updates |
| `router` | Signal routing, agent registration, heartbeat, health |
| `taxonomy` | Tag scoring (frequency × recency), co-occurrence relationships |
| `consolidator` | Hot → Warm → Cold → Frozen tier lifecycle |
| `crystallizer` | Promotes #lesson/#benchmark/#pain-point to durable Crystals |
| `spore` | Real-time WebSocket broadcast for dashboard |

```bash
# Run Rust tests
cd neural-bridge && cargo test

# Start the spore server (ws://localhost:9001)
cargo run --bin spore-server

# CLI commands
cargo run --bin neural-bridge -- emit --tag '#lesson' --agent worker-1 --payload 'Use batch inserts'
cargo run --bin neural-bridge -- health
cargo run --bin neural-bridge -- taxonomy
cargo run --bin neural-bridge -- crystallize
```

## Spore Dashboard

Real-time colony visualization at `dashboard/index.html`. Connects to the neural-bridge spore server via WebSocket.

```bash
make dashboard
```

Shows: colony health, live event stream, taxonomy/meta-tags, crystals (durable knowledge), and consolidation tiers. Supports commands: `health`, `recent`, `taxonomy`, `crystals`, `tiers`, `inject tag:payload`.

## Agent Roles

178+ specialized roles across 14 departments, sourced from agency-agents:

| Department | Count | Examples |
|------------|-------|----------|
| Engineering | 23 | Backend Architect, SRE, Code Reviewer |
| Marketing | 27 | SEO Strategist, Content Writer, Growth Hacker |
| Design | 8 | UX Architect, UI Designer, Visual Storyteller |
| Sales | 8 | Deal Strategist, Discovery Coach, Proposal Writer |
| Specialized | 27 | Data Scientist, Prompt Engineer, Workflow Architect |
| Testing | 8 | QA, Penetration Tester, Accessibility Auditor |
| Product | 5 | Product Manager, Growth Analyst |
| Other | 72 | Strategy, Support, Academic, Spatial, Game Dev |

Each role includes memory integration instructions (search QMD before work, write results after).

## Model Assignment

| Role | Model | Rationale |
|------|-------|-----------|
| Mycelium (brain) | mimo-v2-pro:free | 1M context — needs memory + reasoning |
| Scouts (research) | step-3.5-flash:free | Fast, cheap — probes and reports |
| Army Ants (protect) | mimo-v2-omni:free | Vision for scanning, tools for fixing |
| Workers (execute) | mimo-v2-omni:free | Vision + tools — eyes and hands |

**Rule:** Free only. Never downgrade. Only upgrade with proof (3+ benchmark data points). Benchmark monthly.

## Self-Improvement Loop

Every task follows: RUN → EVALUATE → RECORD → IMPROVE

After every task, agents self-evaluate (Accuracy, Efficiency, Completeness, Reusability on 1-5 scale). High scores (avg ≥ 4) auto-tag as `#lesson`. Low efficiency auto-tags as `#shortcut`. Low overall (avg < 3) auto-tags as `#pain-point`. Scores accumulate in shared memory — the Benchmark Scout reads patterns and the Crystallizer promotes repeat lessons to durable Crystals.

## Memory Protocol

Every agent follows the Colony Memory Protocol:

1. **Before work** → search QMD for #lesson, #pain-point, #shortcut
2. **During work** → write discoveries immediately with tags
3. **After work** → write outcome with #mission-complete
4. **Handoffs** → write summary tagged with receiving agent's role

**Tags:** #lesson #pain-point #shortcut #green-leaf #benchmark #durable-state #mission #mission-complete

## Enforcement

Rules without enforcement are suggestions. The framework enforces:

- **Pre-commit hook** — blocks commits that violate file placement rules
- **Write validator** — agents call scripts/validate-write.sh before writing
- **Rules YAML** — machine-parseable rules in config/rules.yaml

See docs/ENFORCEMENT.md.

## Documentation

| Document | Description |
|----------|-------------|
| [Deployment](docs/DEPLOYMENT.md) | **Start here** — get a colony running in 10 minutes |
| [Self-Improvement](docs/SELF-IMPROVEMENT.md) | The MiniMax-inspired learning loop |
| [Architecture](docs/ARCHITECTURE.md) | Full system architecture with all four roles |
| [Colonial Memory](docs/COLONIAL-MEMORY-ARCHITECTURE.md) | LCM + QMD integration spec |
| [Event Bus](docs/EVENT-BUS.md) | Event sourcing and replay design |
| [Enforcement](docs/ENFORCEMENT.md) | Rules and validation system |
| [SRE](docs/SRE-RELIABILITY.md) | Reliability practices |
| [Lessons](docs/LESSONS.md) | Hard-won lessons from real use |
| [Roadmap](docs/ROADMAP.md) | Development phases |

## Contributing

See CONTRIBUTING.md. Key principles:

1. Every agent reads shared memory before work
2. Every agent writes discoveries back
3. Free models only
4. Prove improvements with benchmarks

## License

MIT

---

**Mycelium**: The underground network that makes the forest work.
