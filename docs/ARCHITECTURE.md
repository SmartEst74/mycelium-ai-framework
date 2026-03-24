# Mycelium AI Framework — Architecture

## Biological Analogy

In nature:
- **Mycelium** = underground network that processes nutrients, routes signals, manages state
- **Ants** = above-ground eyes and hands that sense the world and execute tasks
- **Pheromone trails** = recent signals that guide ant behavior before being absorbed into the network
- **Mycelium network itself** = long-term memory — accumulated knowledge that persists across seasons

In this framework:
- **Mycelium** = reasoning brain that routes, plans, delegates (never sees, never executes)
- **Dynamic Ants** = eyes and hands that see (vision) and execute (tools)
- **LCM** = pheromone trails — recent conversation context, compacted but lossless, with retrieval tools
- **QMD** = mycelium network — long-term searchable memory across files, transcripts, and daily logs

## Chain of Command

```
                    ┌─────────────────────────────────────┐
                    │         COLONY MEMORY               │
                    │  ┌─────────────────┬─────────────┐  │
                    │  │  QMD (long-term) │ LCM (recent)│  │
                    │  │  files, logs,    │ compacted   │  │
                    │  │  transcripts,    │ context,    │  │
                    │  │  daily memory    │ grep/describe│  │
                    │  └────────┬────────┴──────┬──────┘  │
                    │           │               │         │
                    │  #mission  #mission-complete        │
                    │  #lesson   #pain-point               │
                    │  #shortcut #green-leaf                │
                    └───────────┬──────────────────────────┘
                                │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
  ┌──────▼──────┐   ┌─────────▼──────────┐   ┌──────▼──────┐
  │  Mycelium   │   │   SCOUT SWARM      │   │ Army Ants   │
  │  (Brain)    │   │ (many in parallel)  │   │ (Builders)  │
  │ mimo-v2-pro │   │ step-3.5-flash      │   │ mimo-v2-pro │
  │ 1M context  │   │                     │   │ 1M context  │
  │ NO vision   │   │  🔧 Tool Scouts     │   │ NO vision   │
  │             │   │  🌿 Leaf Scouts     │   │             │
  │             │   │  📊 Benchmark Scouts │   │             │
  │             │   │  🔌 Integration Scouts│  │             │
  └──────┬──────┘   └─────────┬──────────┘   └──────┬──────┘
         │                    │                      │
         │                    │ writes findings      │ builds teams
         │                    │ to memory            │
         │                    ▼                      │
         │           ┌────────────────┐        ┌─────▼──────┐
         │           │ Shared Memory  │        │ Dynamic Ants│
         │           │ (pheromone     │        │  (Workers)  │
         │           │  trails)       │        │ mimo-v2-omni│
         │           └────────────────┘        │ vision+tools│
         │                                     └─────┬──────┘
         │                                           │
         └───────────────────────────────────────────┘
                    ALL FEED INTO SHARED MEMORY
```

## Layer Details

### Layer 1: Mycelium — The Brain (mimo-v2-pro:free)

**Model**: `xiaomi/mimo-v2-pro:free` (1M context, text+reasoning, NO vision)
**Why**: The brain doesn't need eyes — it needs memory. 1M context holds the full colony state: registry, benchmarks, active missions, model landscape, revenue pipeline.

**Role**: Central reasoning and routing. Never executes. Never sees.

**Responsibilities**:
- Receives missions from Jon or heartbeat
- Reads shared memory for colony state (active missions, pain points, recent completions)
- Delegates to Scout for research and improvement
- Delegates to Army Ants for execution
- Monitors quality, prevents downgrades
- Maintains benchmarks and model selection
- Routes to best available model based on task type
- Writes mission plans and decisions to shared memory

**Key rule**: Mycelium NEVER does the work itself. It delegates. It routes. It reasons.

### Layer 2: Scout Swarm — The Search Party (step-3.5-flash:free)

**Model**: `kilocode/stepfun/step-3.5-flash:free` (256K context, fast, cheap)
**Why**: Scouts need speed, not depth. They probe, find, report. They don't execute.

**Biological basis**: In nature, a mycelium colony sends hundreds of scouts. They fan out in every direction, each searching for something specific. The ones that find something write pheromone trails back to the colony. The ones that find nothing simply die. No cost. No ceremony.

**Not one scout — a SWARM.** Scouts run in parallel, each with a narrow focus.

**Scout Types:**

| Scout | Hunts For | Feeds | Memory Tag |
|-------|-----------|-------|-----------|
| 🔧 **Tool Scout** | New tools, APIs, improvements, better workflows | Dynamic Ants (stronger tools) | `#lesson`, `#shortcut` |
| 🌿 **Leaf Scout** | Revenue opportunities, clients, products, consulting leads | Mycelium brain (resources to grow) | `#green-leaf` |
| 📊 **Benchmark Scout** | Model performance, new releases, degradations | Mycelium brain (routing quality) | `#benchmark` |
| 🔌 **Integration Scout** | New skills (ClawHub), MCP servers, API integrations | Army Ants (broader capability) | `#lesson`, `#shortcut` |

**Scout Rules:**
1. Parallel by default — never one scout when ten can run faster
2. Ephemeral — spawn, search, report, die. No permanent scouts.
3. Narrow focus — each scout searches ONE thing
4. Write everything — every finding goes to shared memory immediately
5. No execution — scouts NEVER do the work. They find it. Others do it.
6. No cost — scouts use the cheapest model (step-3.5-flash)
7. No ceremony — if a scout finds nothing, it dies silently

**The Food Chain:**
```
Scouts find FOOD (tools) → strengthens ANTS → better execution
Scouts find LEAVES (revenue) → feeds MYCELIUM → brain grows
Stronger brain → better routing → stronger teams → more results
                                    ▲
                                    │
                             COLONY GROWS
```

**Scaling**: As many scouts as needed. Daily heartbeat: 3-5. Active revenue hunt: 10-20. Model assessment: 5-10. Emergency: as many as the problem requires.

**See [docs/SCOUT-SWARM.md](SCOUT-SWARM.md) for the full Scout Swarm specification.**

### Layer 3: Army Ants — The Coordinators (mimo-v2-pro:free)

**Model**: `xiaomi/mimo-v2-pro:free` (1M context, text+reasoning)
**Why**: Army Ants need the full registry (178 roles), model benchmarks, and mission context to build teams. They don't need vision — they delegate vision to Dynamic Ants.

**Role**: Build execution teams from agency-agent registry.

**Responsibilities**:
- Receive mission from Mycelium
- Read shared memory for relevant lessons, pain points, shortcuts
- Select appropriate agency-agent roles from registry
- Match best model to each role based on benchmarks
- Decide parallel vs serial execution
- Spawn Dynamic Ants for each task
- Monitor progress, re-route if blocked
- Write team composition and progress to shared memory
- Report results to Mycelium

**Key rule**: Use agency-agent registry. Don't reinvent roles. Write everything to memory.

### Layer 4: Dynamic Ants — The Eyes and Hands (mimo-v2-omni:free)

**Model**: `xiaomi/mimo-v2-omni:free` (262K context, vision+tools+reasoning)
**Why**: This is the ONLY free model with vision+tools. The ants ARE the eyes that see the world and the hands that execute tasks. They feed back to the superior brain through shared memory.

**Role**: Single-task focused execution with full sensory capability.

**Responsibilities**:
- Take one specific task from Army Ant
- Apply agency-agent persona/role
- USE VISION to see the web, UIs, documents, images
- USE TOOLS to execute (write code, scrape web, edit files)
- Write progress to shared memory at each step:
  - Started → `#mission` with task description
  - Pain point → `#pain-point` with what broke
  - Shortcut found → `#shortcut` with the trick
  - Completed → `#mission-complete` with result
- Report result back to Army Ant
- Die after completion (ephemeral)

**Key rule**: One task. One role. One model. One report. Write to memory. Done.

## Shared Memory — The Colony's Nervous System

Two memory systems form a funnel, not a partition:

```
  Session grows
       │
       ▼
  ┌─────────┐
  │   LCM   │  Short-term, well-organised memory
  │         │  Compacts perfectly as sessions grow
  │         │  grep / describe / expand for retrieval
  └────┬────┘
       │
       │  Only truly valuable knowledge
       │  rises here (lessons, benchmarks,
       │  revenue, durable state)
       ▼
  ┌─────────┐
  │   QMD   │  Long-term memory
  │         │  Curated, searchable, persistent
  │         │  Never polluted with noise
  └─────────┘
```

**LCM** is the session brain — it captures everything, compacts it losslessly, and keeps recent context well-organised so nothing important is lost mid-conversation. As sessions grow, LCM summarises perfectly. No need to dump every thought into permanent storage.

**QMD** is the colony brain — only high-value, durable knowledge lives here. Lessons, benchmarks, revenue opportunities, system state. It stays clean because LCM already handles the rest.

**The rule:** Don't fill QMD with noise. Let LCM do its job. Only promote to QMD when something is genuinely reusable across sessions.

### The Memory Integration Skill (Private Repo)

The private repo holds the **sellable product**: the memory integration skill that teaches any OpenClaw instance how to wire QMD + LCM into a self-improving colony.

**Memories stay LOCAL.** Always. QMD, LCM, filesystem — fast, immediate, no git overhead. The private repo does NOT store memories. It stores the **skill** that makes memory work.

```
LOCAL (fast, immediate, every agent reads/writes here):
  ┌──────────────────────────────────────┐
  │  QMD   — long-term curated knowledge│
  │  LCM   — session compaction         │
  │  fs    — daily logs, workspace files│
  └──────────────────────────────────────┘

PRIVATE REPO (sellable product):
  ┌──────────────────────────────────────┐
  │  SKILL.md        — install guide    │
  │  templates/      — MEMORY.md,       │
  │                    AGENTS.md, SOUL   │
  │  memory-protocol — how to wire      │
  │                    QMD + LCM funnel  │
  │  examples/       — working configs  │
  └──────────────────────────────────────┘
```

**What the skill sells:**
- How to set up QMD + LCM as complementary memory systems
- The memory funnel: LCM compacts → valuable knowledge rises to QMD
- Tag protocol: `#lesson`, `#mission`, `#pain-point`, `#shortcut`, `#green-leaf`
- Colony memory rules: every agent reads memory first, writes discoveries back
- HEARTBEAT.md template for autonomous colony monitoring
- Working config examples for OpenClaw

**Anyone who installs the skill gets:**
- Self-improving memory that compounds over time
- No repeated mistakes (lessons persist in QMD)
- No cold starts (agents read memory before working)
- Autonomous heartbeat monitoring
- The same pattern that powers this colony

**Revenue model:** Sell the skill on ClawHub or as a standalone package. It's a one-time setup that makes any OpenClaw deployment dramatically more capable.

### Shared Memory Tags

Every agent reads and writes shared memory. This is non-negotiable.

### What Goes Where

| Tag | Goes To | Why |
|-----|---------|-----|
| `#lesson` | QMD | Durable knowledge, reusable across sessions |
| `#benchmark` | QMD | Model performance data, long-lived |
| `#green-leaf` | QMD | Revenue opportunity, needs to persist |
| `#durable-state` | QMD | System snapshot, survives restarts |
| `#mission` | LCM | Active work — compacted when done |
| `#mission-complete` | LCM | Finished work — absorbed into session summary |
| `#pain-point` | LCM→QMD | If recurring, promote to QMD as `#lesson` |
| `#shortcut` | LCM→QMD | If proven, promote to QMD as `#lesson` |

### Memory Rules

1. **Every Dynamic Ant writes `#mission` when starting work**
2. **Every Dynamic Ant writes `#mission-complete` when done** (with: what was done, what worked, what didn't)
3. **Every Dynamic Ant writes `#pain-point` if something blocks progress**
4. **Every Dynamic Ant writes `#shortcut` if it finds a better way**
5. **Every agent reads shared memory BEFORE starting work** (avoid repeating mistakes)
6. **Mycelium reads shared memory on every heartbeat** (colony status)
7. **Scout writes `#benchmark` after every model test**
8. **Scout writes `#green-leaf` for every revenue opportunity**

### Instant Colony Visibility

The colony is healthy when:
- `#mission` entries have recent timestamps (work is happening)
- `#mission-complete` entries outnumber `#mission` (work is finishing)
- `#pain-point` entries are being addressed (not accumulating)
- `#green-leaf` entries exist (revenue is being hunted)
- `#benchmark` entries are recent (model quality is being monitored)

The colony is SICK when:
- `#mission` entries go stale (>30 min with no update)
- `#pain-point` entries accumulate without `#lesson` resolutions
- No `#green-leaf` entries in 24h (revenue hunt stopped)
- No `#benchmark` entries in 7 days (model quality unchecked)

## Model Assignment Matrix (Corrected)

| Role | Model | Context | Capabilities | Why |
|------|-------|---------|-------------|-----|
| **Mycelium** (Brain) | mimo-v2-pro:free | 1M | text, reasoning | Needs memory, not eyes |
| **Scout** (Researcher) | step-3.5-flash:free | 256K | text, tools | Needs speed, not depth |
| **Army Ants** (Coordinators) | mimo-v2-pro:free | 1M | text, reasoning | Needs registry context |
| **Dynamic Ants** (Workers) | mimo-v2-omni:free | 262K | vision, tools, reasoning | Needs eyes and hands |

**Fallback chain** (if primary unavailable):
mimo-v2-omni → mimo-v2-pro → step-3.5-flash → glm-4.5-air → gpt-5-mini

**RULE: Never downgrade models. Only upgrade with proof.**
**RULE: Free models only. We make money, not spend it.**

## Agency-Agent Registry

178 specialized agent roles from `msitarzewski/agency-agents`:

| Department | Count | Key Roles |
|-----------|-------|-----------|
| Engineering | 23 | Full-Stack, Backend, Frontend, DevOps, AI/ML |
| Marketing | 27 | Growth Hacker, SEO Strategist, Content, Social |
| Specialized | 27 | Data Analyst, API Designer, Security, Performance |
| Testing | 8 | QA Lead, E2E Tester, Performance Tester |
| Sales | 8 | Outbound Strategist, Pipeline Analyst, Coach |
| Design | 8 | UX Architect, UI Designer, Brand Guardian |
| Product | 5 | Product Manager, Strategist, Analyst |
| Strategy | 3 | Business Strategist, Competitive Analyst |
| Project Mgmt | 6 | Studio Producer, Scrum Master |
| Support | 6 | Customer Success, Technical Support |
| Paid Media | 7 | PPC Strategist, Programmatic Buyer |
| Academic | 5 | Research, Writing, Teaching |
| Game Dev | 5 | Game Designer, Unity Developer |
| Spatial | 6 | XR Developer, VisionOS Engineer |
| Examples | 6 | Demo/Example agents |

## Money-Making Missions (Green Leaves)

Scout continuously searches for:
1. **IT1st services** — Automations, bots, integrations for businesses
2. **Fiverr/Upwork** — Sellable skills and deliverables
3. **Content** — Blog posts, guides, tools that attract leads
4. **Consulting** — AI integration consulting using colony experience
5. **Products** — Sellable tools, templates, frameworks
6. **Arbitrage** — Price differences, free credits, grants

## Implementation

This framework is implemented as:
- `core/` — Mycelium brain logic
- `scout/` — Research and improvement modules
- `army/` — Team building and orchestration
- `dynamic/` — Worker creation and management
- `registry/` — Agency-agent role registry (178 roles)
- `config/` — Model assignments, benchmarks, rules
