# Mycelium AI Framework — Architecture

## Biological Map

In nature, mycelium is a fungal network that:
- Connects organisms underground (trees, plants, bacteria)
- Routes nutrients to where they're needed
- Sends scouts (hyphae) to explore new territory
- Bundles transport cables (rhizomorphs) for long-distance communication
- Grows stronger with every successful connection

**Our framework mirrors this exactly:**

| Biology | Framework | Role |
|---------|-----------|------|
| **Mycelium** | Core orchestrator | Routes, reasons, delegates. Never executes, never sees. |
| **Hyphae** | Skill harness | Individual skills that plug into the network. Each hypha is a capability. |
| **Rhizomorph** | Shared instant memory | The transport cable between all parts. Every skill reads/writes here. |
| **Scout ants** | Research swarm | Fan out in parallel, find food (tools) and leaves (revenue). |
| **Worker ants** | Executors | Eyes and hands. See (vision) and do (tools). |

## Core Architecture

```
┌──────────────────────────────────────────────────────┐
│                    MYCELIUM CORE                     │
│              (Orchestrator / Brain)                   │
│                                                      │
│  • Routes missions to correct Hyphae                 │
│  • Reasons about colony state via Rhizomorph         │
│  • Never executes. Never sees. Only routes.          │
└──────────────┬───────────────────────┬───────────────┘
               │                       │
               ▼                       ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │    RHIZOMORPH    │    │   SCOUT SWARM        │
    │ (Shared Instant  │    │ (parallel research)  │
    │     Memory)      │    │                      │
    │                  │    │  🔧 Tool Scouts      │
    │  • QMD (long)    │    │  🌿 Leaf Scouts      │
    │  • LCM (session) │    │  📊 Benchmark Scouts │
    │  • Tags: #mission │   │  🔌 Integration Scouts│
    │    #lesson       │    └──────────┬───────────┘
    │    #pain-point   │               │
    │    #green-leaf   │    findings written
    └────────┬─────────┘    to Rhizomorph
             │
             │  skills plug in here
             ▼
    ┌──────────────────────────────────────┐
    │            HYPHAE (Skills)           │
    │                                      │
    │  Each hypha = one skill/capability   │
    │  • Rust native skills                │
    │  • OpenClaw skills (SKILL.md)        │
    │  • MCP servers (wrapped as hyphae)   │
    │  • Any language (wrapped as hyphae)  │
    │                                      │
    │  Plug-and-play. Swap when better     │
    │  arrives. Never locked in.           │
    └──────────────────┬───────────────────┘
                       │
                       │  mycelium delegates to
                       ▼
    ┌──────────────────────────────────────┐
    │         ANT COLONY (Workers)         │
    │                                      │
    │  Army Ants (coordinators)            │
    │    → build teams from Hyphae         │
    │    → match role to skill             │
    │                                      │
    │  Dynamic Ants (executors)            │
    │    → eyes (vision model)             │
    │    → hands (tools/Hyphae)            │
    │    → write results to Rhizomorph     │
    └──────────────────────────────────────┘
```

## The Three Pillars

### 1. Mycelium (Core Orchestrator)

The brain. Routes, reasons, delegates. Never executes, never sees.

- Receives missions (from Jon, heartbeat, or external triggers)
- Reads Rhizomorph for colony state
- Routes to correct Hyphae for execution
- Monitors quality, prevents downgrades
- Writes decisions to Rhizomorph

**Model**: mimo-v2-pro:free (1M context, text+reasoning, NO vision)
**Why**: The brain needs memory, not eyes.

### 2. Hyphae (Skill Harness)

Each hypha is a skill that plugs into the mycelium network. Skills are the integration layer — NOT MCP, NOT custom protocols.

**What can be a hypha:**
- Rust native skills (fast, compiled)
- OpenClaw skills (SKILL.md format)
- MCP servers (wrapped as hyphae)
- Any CLI tool (wrapped as hyphae)
- Any language (subprocess adapter)

**Rules:**
- Hyphae are pluggable — add, remove, swap without touching core
- Each hypha declares its capabilities in a manifest
- Mycelium discovers hyphae at runtime
- If a better skill system emerges, swap it — never locked in
- Hyphae read/write Rhizomorph (shared memory)

### 3. Rhizomorph (Shared Instant Memory)

The transport cable. In nature, rhizomorphs are cord-like bundles of hyphae that transport nutrients over long distances. In our system: the fast shared memory layer that connects all parts.

**Components:**
- **LCM** — session-level memory. Compacts as sessions grow. Recent context, lossless.
- **QMD** — long-term curated memory. Lessons, benchmarks, revenue. Never polluted.
- **Tags** — `#mission`, `#lesson`, `#pain-point`, `#shortcut`, `#green-leaf`, `#benchmark`

**Rules:**
- Every hypha reads Rhizomorph before starting work
- Every hypha writes discoveries back to Rhizomorph
- LCM handles session noise — don't dump everything into QMD
- Only valuable knowledge rises to QMD
- Rhizomorph is instant — no delays, no bottlenecks

## Scout Swarm

Scouts fan out in parallel, each searching for something specific. They write findings to Rhizomorph. The ones that find nothing die silently.

| Scout | Hunts For | Writes To |
|-------|-----------|-----------|
| 🔧 Tool Scout | Better tools, APIs, workflows | `#lesson`, `#shortcut` |
| 🌿 Leaf Scout | Revenue, clients, products | `#green-leaf` |
| 📊 Benchmark Scout | Model performance, new releases | `#benchmark` |
| 🔌 Integration Scout | New skills, connections | `#lesson` |

**Rules:**
- Parallel by default
- Ephemeral (spawn, search, report, die)
- Narrow focus (one thing per scout)
- Cheapest model (step-3.5-flash:free)
- Write everything to Rhizomorph immediately

## Model Assignment

| Role | Model | Why |
|------|-------|-----|
| Mycelium (brain) | mimo-v2-pro:free | 1M context, needs memory not eyes |
| Scout swarm | step-3.5-flash:free | Fast, cheap, narrow focus |
| Army Ants (coordinators) | mimo-v2-pro:free | 1M context for registry state |
| Dynamic Ants (workers) | mimo-v2-omni:free | Vision+tools — the eyes and hands |

**Fallback chain**: mimo-v2-omni → mimo-v2-pro → step-3.5-flash → glm-4.5-air → gpt-5-mini

**Rules:**
- Free only. We make money, not spend it.
- Never downgrade. Only upgrade with proof.
- Scout benchmarks monthly minimum.

## Colony Health

The colony is healthy when:
- Missions completing (Rhizomorph has recent `#mission-complete`)
- Pain points addressed (not accumulating)
- Leaf scouts finding opportunities (`#green-leaf` entries exist)
- Benchmarks current (`#benchmark` entries < 7 days old)

The colony is SICK when:
- Missions go stale (>30 min, no update)
- Pain points accumulate without resolution
- No revenue hunt in 24h
- No benchmarks in 7 days

## The Rust Goal

This framework is designed to be rebuilt in Rust:
- Mycelium core → Rust (fast, safe, single binary)
- Hyphae → Rust skills + adapters for existing skills
- Rhizomorph → SQLite (LCM) + filesystem (QMD)
- Scout swarm → async Rust tasks
- Ant colony → async Rust with tokio

The Python/TypeScript prototype proves the architecture.
The Rust build makes it production-grade.
