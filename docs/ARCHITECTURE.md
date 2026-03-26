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
| **Mycelium** | Core orchestrator | Decomposes missions, reasons about colony state, spawns workers directly. Never executes leaf work. |
| **Hyphae** | Skill harness | Individual skills that plug into the network. Each hypha is a capability. |
| **Rhizomorph** | Shared instant memory | The transport cable between all parts. Every skill reads/writes here. |
| **Scout ants** | Research swarm | Fan out in parallel, investigate, benchmark models. Research only — never execute. |
| **Dynamic ants** | Builders / Executors | Execute one focused task each. Eyes and hands. The heavy lifters. |
| **Army ants** | Protectors | Security, threat detection, warning enforcement. Safeguard the colony. Never coordinate, never build. |

## Core Architecture

```
┌──────────────────────────────────────────────────────┐
│                    MYCELIUM CORE                     │
│              (Strategic Brain)                        │
│                                                      │
│  • Receives missions from human, heartbeat, or hooks │
│  • Reads Rhizomorph for colony state                 │
│  • Decomposes missions into concrete worker tasks    │
│  • Spawns workers directly — no intermediary         │
│  • Spawns Army Ants for protection sweeps            │
│  • Never executes leaf work. Never uses vision.      │
└──────┬──────────────────┬───────────────────┬────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│  SCOUT SWARM │  │  RHIZOMORPH  │  │  ARMY ANT SWARM  │
│ (Research)   │  │ (Memory)     │  │ (Protection)     │
│              │  │              │  │                  │
│ • Investigate│  │ • LCM (sess) │  │ • Disk health    │
│ • Benchmark  │  │ • QMD (long) │  │ • Security scan  │
│ • Report     │  │ • Tags       │  │ • Warning enforce│
│ • Never exec │  │ • Stream     │  │ • Threat detect  │
└──────┬───────┘  └──────┬───────┘  └────────┬─────────┘
       │ findings         │                    │ threats
       │ written          │                    │ reported
       ▼                  ▼                    ▼
┌──────────────────────────────────────────────────────┐
│              DYNAMIC ANT COLONY (Workers)            │
│                                                      │
│  Each ant = one focused task                         │
│  • Build, deploy, code, design, test                 │
│  • Self-evaluate after every task (1-5 each)         │
│  • Write results + scores to Rhizomorph              │
│  • Spawned directly by Mycelium, not by Army Ants    │
│                                                      │
│  These do the heavy lifting. The colony's builders.  │
└──────────────────────────────────────────────────────┘
```

## The Three Pillars

### 1. Mycelium (Core Orchestrator)

The brain. Decomposes missions, reasons about colony state, spawns workers directly. Never executes leaf work, never uses vision.

- Receives missions (from human, heartbeat, or external triggers)
- Reads Rhizomorph for colony state — lessons, pain points, active missions
- **Decomposes missions** into concrete worker tasks — this is its primary job
- Spawns workers directly for straightforward tasks (90% of work)
- Spawns Army Ants for periodic protection sweeps
- Spawns Scouts when research is needed before execution
- Monitors quality, enforces hard constraints, prevents downgrades
- Writes decisions to Rhizomorph

**Dispatch flow:**
```
Human → Mycelium
         ├─ (optional) Scout: "Research X, report back"
         ├─ Mycelium: decompose into N concrete tasks
         ├─ Worker 1: do task A
         ├─ Worker 2: do task B
         ├─ Worker 3: do task C
         └─ Army Ant: scan what workers built, enforce quality
```

**When to spawn an Army Ant instead of a Worker:**
- Security scan needed
- Warning/error must be tracked until resolved
- System health check (disk, services, configs)
- Threat detection or permission audit

**Model**: mimo-v2-pro:free (1M context, text+reasoning, NO vision)
**Why**: The brain needs memory and reasoning, not eyes. Workers see.

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

Scouts fan out in parallel, each searching for something specific. They research and report — never execute. They write findings to Rhizomorph. The ones that find nothing die silently.

| Scout | Hunts For | Writes To |
|-------|-----------|-----------|
| 🔧 Tool Scout | Better tools, APIs, workflows | `#lesson`, `#shortcut` |
| 🌿 Leaf Scout | Revenue, clients, products | `#green-leaf` |
| 📊 Benchmark Scout | Model performance, new free models | `#benchmark`, `#lesson` |
| 🔌 Integration Scout | New skills, connections | `#lesson` |
| 🔍 Security Scout | Vulnerabilities, misconfigs | `#pain-point` |

**Model benchmarking protocol:**
The Benchmark Scout periodically tests candidate models against standardised tasks:
1. Check provider catalog for new free models
2. Run the same benchmark task on each candidate
3. Score: correctness (1-5), token cost, speed, reasoning quality
4. Report to Mycelium: "Model X beats Model Y for role Z"
5. Mycelium updates assignments if confirmed by 3+ data points

**Rules:**
- Parallel by default
- Ephemeral (spawn, search, report, die)
- Narrow focus (one thing per scout)
- Cheapest model (step-3.5-flash:free)
- Write everything to Rhizomorph immediately
- Research only — never execute, never deploy, never modify files

## Army Ants (Colony Protectors)

In real ant colonies, army ants protect the nest, fight threats, and secure territory. In our framework, Army Ants are the colony's immune system.

**What Army Ants do:**
- Scan for vulnerabilities in code workers built
- Detect broken deployments and alert or roll back
- Audit permissions, configs, access control
- Enforce hard constraints (errors/warnings = extreme threats)
- Track warnings until fully resolved — never dismiss, never ignore
- Guard against data leaks, misconfigurations, bad actors

**Warning lifecycle:**
```
Army Ant finds warning:
  1. Writes to Rhizomorph: [army-xxx] #warning — "description"
  2. Attempts fix if trivial
  3. If can't fix → escalates to Mycelium
  4. Warning stays OPEN until next sweep confirms resolved
  5. On resolution: [army-xxx] #warning-resolved — "fixed description"
```

**Parallel deployment:**
The Mycelium spawns Army Ants in parallel, each with one protection domain:
- Army Ant 1: disk + storage health
- Army Ant 2: security scan (permissions, configs, access)
- Army Ant 3: code quality (warnings, errors, lint)
- Army Ant 4: service health (APIs, gateway, crons)

**Rules:**
- Each Army Ant has ONE domain — can't get distracted
- Warnings stay attached until verified clean — no dismissing
- Free model (same as workers) — protection doesn't need heavy reasoning
- Write threats to Rhizomorph immediately for Mycelium awareness

## Dynamic Ants (Colony Builders)

The heavy lifters. Each Dynamic Ant executes one focused task and reports back.

**What Dynamic Ants do:**
- Build, deploy, code, design, test — the actual work
- Self-evaluate after every task (Accuracy 1-5, Efficiency 1-5, Completeness 1-5, Reusability 1-5)
- Write results + self-eval scores to Rhizomorph
- One task, one focus, one report

**Self-evaluation protocol:**
After every task, the Dynamic Ant scores itself and routes the result:
- Score >= 4 on all dimensions → `#lesson` with the reusable pattern
- Score < 3 on any dimension → `#pain-point` with what went wrong
- Efficiency < 4 → find shorter path, record as `#shortcut`

This data feeds the colony's self-improvement loop (see below).

**Model**: mimo-v2-omni:free (vision + tools — the eyes and hands)

## Self-Improvement Loop (MiniMax-Inspired)

Every task follows: RUN → EVALUATE → RECORD → IMPROVE

```
Worker does task
       │
       ▼
Worker self-evaluates (1-5 each)
       │
       ▼
Scores written to Rhizomorph
       │
       ▼
Scout reads accumulated scores
       │
       ▼
Scout reports patterns to Mycelium
       │
       ▼
Mycelium updates model assignments / agent behaviour
       │
       ▼
Next task starts from improved baseline
```

**What gets tracked:**
- Token cost per model per task type
- Correctness scores by model and role
- Speed (response time)
- Reusable patterns discovered by workers

**How it compounds:**
- Session 1: Agent tries model A for code gen, scores 4/5
- Session 5: Agent tries model B for code gen, scores 5/5, uses 30% fewer tokens
- Session 10: Model B is the default for code gen. Model A is reserved for vision tasks.
- The colony learns which model is best for which job — automatically.

**Data source:** Worker self-eval scores accumulate in Rhizomorph over time.
**Analysis:** Benchmark Scout reads scores periodically, spots patterns, reports.
**Action:** Mycelium updates SOUL.md model assignments when 3+ data points confirm a better option.

## Model Assignment

| Role | Model | Why |
|------|-------|-----|
| Mycelium (brain) | mimo-v2-pro:free | 1M context, needs memory not eyes |
| Scout swarm | step-3.5-flash:free | Fast, cheap, narrow focus |
| Army Ants (protectors) | mimo-v2-omni:free | Vision for scanning, tools for fixing |
| Dynamic Ants (workers) | mimo-v2-omni:free | Vision + tools — the eyes and hands |

**Fallback chain**: mimo-v2-omni → mimo-v2-pro → step-3.5-flash → glm-4.5-air → gpt-5-mini

**Rules:**
- Free only. We make money, not spend it.
- Never downgrade. Only upgrade with proof (3+ benchmark data points).
- Benchmark Scout evaluates new models monthly minimum.
- Model assignments live in SOUL.md — every agent reads them.

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
