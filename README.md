# 🍄 Mycelium AI Framework

**A multi-agent orchestration framework inspired by mycelium networks.**

## What Is It?

Mycelium is a fungal network that connects organisms underground, routes nutrients, and sends scouts to explore. This framework does the same for AI agents.

**Three pillars:**

- **Mycelium** (core) — Orchestrator. Routes, reasons, delegates. Never executes.
- **Hyphae** (skills) — Individual capabilities that plug into the network. Rust skills, OpenClaw skills, MCP servers, any tool. Plug-and-play.
- **Rhizomorph** (memory) — Shared instant memory. Every part reads/writes here. QMD for long-term, LCM for sessions.

## The Biology

| Biology | Framework | What It Does |
|---------|-----------|-------------|
| Mycelium | Core orchestrator | Routes missions, reasons about state |
| Hyphae | Skill harness | Individual skills that plug in |
| Rhizomorph | Shared instant memory | Transport cable between all parts |
| Scout ants | Research swarm | Find tools (food) and revenue (leaves) |
| Worker ants | Executors | Eyes (vision) and hands (tools) |

## How It Works

```
Jon sends mission
       │
       ▼
  ┌─────────┐
  │MYCELIUM │ reads Rhizomorph for colony state
  │ (brain) │ routes to correct Hyphae
  └────┬────┘
       │
       ▼
  ┌─────────┐     ┌──────────────┐
  │RHIZOMORPH│◄───►│ SCOUT SWARM  │
  │(memory)  │     │ (parallel)   │
  │ QMD+LCM  │     │ tools/revenue│
  └────┬─────┘     └──────────────┘
       │
       │  hyphae plug in here
       ▼
  ┌─────────┐
  │ HYPHAE  │ skills, tools, integrations
  │(skills) │ plug-and-play, swap anytime
  └────┬────┘
       │
       ▼
  ┌─────────┐
  │  ANTS   │ army (coordinate) + dynamic (execute)
  │(workers)│ vision + tools → write to Rhizomorph
  └─────────┘
```

## Hyphae (Skills)

The integration layer. NOT MCP, NOT custom protocols. Skills.

**What can be a hypha:**
- Rust native skills (fast, compiled)
- OpenClaw skills (SKILL.md format)
- MCP servers (wrapped as hyphae)
- Any CLI tool (wrapped as hyphae)
- Any language (subprocess adapter)

**Rules:**
- Plug-and-play — add, remove, swap without touching core
- If a better skill system emerges, swap it
- Every hypha reads/writes Rhizomorph

## Rhizomorph (Shared Memory)

The transport cable between all parts. Two layers:

| Layer | What | Why |
|-------|------|-----|
| LCM | Session memory | Compacts as conversations grow. Recent context, lossless. |
| QMD | Long-term memory | Lessons, benchmarks, revenue. Never polluted. |

**Tags:** `#mission` `#lesson` `#pain-point` `#shortcut` `#green-leaf` `#benchmark`

**Rules:**
- Every hypha reads Rhizomorph before starting
- Every hypha writes discoveries back
- LCM handles noise — only valuable knowledge rises to QMD

## Scout Swarm

Scouts fan out in parallel. Write findings to Rhizomorph. Die silently if they find nothing.

| Scout | Hunts For | Writes |
|-------|-----------|--------|
| 🔧 Tool Scout | Better tools, APIs | `#lesson`, `#shortcut` |
| 🌿 Leaf Scout | Revenue, clients | `#green-leaf` |
| 📊 Benchmark Scout | Model quality | `#benchmark` |
| 🔌 Integration Scout | New skills | `#lesson` |

## Models

| Role | Model | Why |
|------|-------|-----|
| Mycelium | mimo-v2-pro:free | 1M context, needs memory not eyes |
| Scouts | step-3.5-flash:free | Fast, cheap |
| Coordinators | mimo-v2-pro:free | 1M context for registry |
| Workers | mimo-v2-omni:free | Vision+tools — eyes and hands |

**Rules:** Free only. Never downgrade. Scout benchmarks monthly.

## Agent Registry

178+ specialized roles from [agency-agents](https://github.com/msitarzewski/agency-agents):

Engineering (23), Marketing (27), Sales (8), Design (8), Specialized (27), Testing (8), Product (5), Strategy (3), Project Management (6), Support (6), Paid Media (7), Academic (5), Game Dev (5), Spatial (6), and more.

## Colony Health

**Healthy:** missions completing, pain points addressed, revenue being hunted, benchmarks current.

**Sick:** stale missions (>30 min), accumulating pain points, no revenue hunt in 24h, no benchmarks in 7 days.

## Enforcement

Rules without enforcement are suggestions. The framework includes:

- **Pre-commit git hook** — blocks commits that put project docs in `memory/`
- **Write validator script** — agents call before writing to check correct location
- **Hard rules in `config/rules.yaml`** — machine-parseable enforcement rules

See [docs/ENFORCEMENT.md](docs/ENFORCEMENT.md) for details.

## Why Mycelium?

- Connects specialized agents to missions
- Routes the best model to each task
- Swarms scouts in parallel
- Self-improves through discoveries
- Gets more capable with every mission
- Shared memory = colony's nervous system

## License

MIT. Agent roles from [agency-agents](https://github.com/msitarzewski/agency-agents) under their respective license.
