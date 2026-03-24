# Mycelium AI Framework — Architecture

## Biological Analogy

In nature:
- **Mycelium** = underground network that processes nutrients, routes signals, manages state
- **Ants** = above-ground eyes and hands that sense the world and execute tasks
- **Pheromone trails** = shared memory that lets the colony function as one organism

In this framework:
- **Mycelium** = reasoning brain that routes, plans, delegates (never sees, never executes)
- **Dynamic Ants** = eyes and hands that see (vision) and execute (tools)
- **Shared Memory (QMD)** = pheromone trails — every ant writes findings, the colony reads them

## Chain of Command

```
                    ┌─────────────────────────────┐
                    │     SHARED MEMORY (QMD)     │
                    │  #mission  #mission-complete │
                    │  #lesson   #pain-point       │
                    │  #shortcut #green-leaf        │
                    └──────────┬──────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
  ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
  │  Mycelium   │      │   Scout     │      │ Army Ants   │
  │  (Brain)    │      │ (Researcher)│      │ (Builders)  │
  │ mimo-v2-pro │      │step-3.5-flash│     │ mimo-v2-pro │
  │ 1M context  │      │ fast/cheap  │      │ 1M context  │
  │ NO vision   │      │ web access  │      │ NO vision   │
  └──────┬──────┘      └─────────────┘      └──────┬──────┘
         │                                          │
         │                                   ┌──────▼──────┐
         │                                   │ Dynamic Ants│
         │                                   │  (Workers)  │
         │                                   │ mimo-v2-omni│
         │                                   │ vision+tools│
         │                                   └──────┬──────┘
         │                                          │
         └──────────────────────────────────────────┘
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

### Layer 2: Scout — The Sensor (step-3.5-flash:free)

**Model**: `kilocode/stepfun/step-3.5-flash:free` (256K context, fast, cheap)
**Why**: Scout needs speed, not depth. It probes, finds, reports. It doesn't execute.

**Role**: Constantly improves the colony's capabilities and finds revenue.

**Responsibilities**:
- Monitor free model landscape daily (new models, deprecations, benchmarks)
- Test new models and update benchmarks with PROOF
- Find better tools, APIs, integrations
- Hunt for revenue opportunities ("green leaves")
- Write all findings to shared memory immediately
- NEVER execute — only research and report

**Key rule**: Never propose a downgrade. Only propose upgrades with evidence.

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

## Shared Memory Protocol — The Colony's Nervous System

**Every agent reads and writes shared memory. This is non-negotiable.**

### What Goes In Shared Memory

| Tag | Purpose | Written By | Read By |
|-----|---------|-----------|---------|
| `#mission` | Active work in progress | Dynamic Ants, Army Ants | Mycelium, Scout |
| `#mission-complete` | Finished work with results | Dynamic Ants | Mycelium, Scout |
| `#pain-point` | Something that broke or blocked | Any agent | All agents |
| `#lesson` | Durable knowledge gained | Any agent | All agents |
| `#shortcut` | Efficiency trick discovered | Dynamic Ants | All agents |
| `#green-leaf` | Revenue opportunity found | Scout | Mycelium |
| `#benchmark` | Model performance data | Scout | Mycelium, Army Ants |
| `#durable-state` | Current system state snapshot | Mycelium | All agents |

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
