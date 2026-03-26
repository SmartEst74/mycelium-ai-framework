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
                       JON (Human)
                          │
                          ▼
                  ┌───────────────┐
                  │   MYCELIUM    │  Orchestrator
                  │   (Brain)     │  Routes, reasons, delegates
                  └───────┬───────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │  SCOUT   │ │  ARMY    │ │ DYNAMIC  │
      │  SWARM   │ │  ANT     │ │  ANTS    │
      │ research │ │coordinate│ │ execute  │
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
| **Rhizomorph** | Event bus with replay | Proven |
| **Curator** | LCM to QMD knowledge bridge | Prototype |
| **Benchmark** | Solo vs colonial comparison | 47% faster |
| **Enforcement** | Pre-commit hooks, validation | Working |
| **Bootstrap** | Portable knowledge import | Working |

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
| Mycelium (brain) | mimo-v2-pro:free | 1M context — needs memory |
| Scouts (research) | step-3.5-flash:free | Fast, cheap — probes and reports |
| Coordinators | mimo-v2-pro:free | 1M context for registry + mission state |
| Workers (execute) | mimo-v2-omni:free | Vision + tools — eyes and hands |

**Rule:** Free only. Never downgrade. Benchmark monthly.

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
| Hypothesis | Scientific framing, experimental design, grant pitch |
| Architecture | Full system architecture |
| Event Bus | Event sourcing and replay design |
| Colonial Memory | LCM + QMD integration spec |
| Enforcement | Rules and validation system |
| SRE | Reliability practices |
| Lessons | 17 hard-won lessons from real use |
| Roadmap | Development phases |

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
