# 🍄 Mycelium AI Framework

**A multi-agent orchestration framework inspired by mycelium networks and ant colonies.**

## Biological Model

In nature, mycelium doesn't see — it *routes underground*. The ants are the eyes and hands that sense the world and execute tasks. Pheromone trails are recent signals that guide behavior. The mycelium network is accumulated knowledge that persists across seasons.

**Scouts fan out in parallel**, each searching for something specific:
- 🔧 **Tool Scouts** — find food (new tools, improvements) to strengthen the ants
- 🌿 **Leaf Scouts** — find leaves (revenue opportunities) to feed the mycelium
- 📊 **Benchmark Scouts** — test models, ensure quality never degrades
- 🔌 **Integration Scouts** — find new skills, MCP servers, connections

The ones that find something write pheromone trails (shared memory). The ones that find nothing die silently. No cost to the colony.

### Memory Tools

A funnel, not a partition:

```
  Session grows → LCM compacts → only valuable knowledge rises → QMD
```

| Tool | Role | What lives there |
|------|------|-----------------|
| **LCM** | Session brain — short-term, well-organised. Compacts perfectly as conversations grow. `lcm_grep`, `lcm_describe`, `lcm_expand` for retrieval. | Everything from the session: conversations, investigations, partial work, temporary state |
| **QMD** | Colony brain — long-term, curated. Never polluted with noise. | Only durable, reusable knowledge: lessons, benchmarks, revenue opportunities, system state |

**The rule:** Don't dump noise into QMD. Let LCM do its job. Only promote to QMD when something is genuinely reusable across sessions.

### The Memory Integration Skill (Private Repo)

The private repo holds the **sellable product**: the memory integration skill. NOT memories — those stay local (QMD, LCM, filesystem). The repo contains the skill that teaches any OpenClaw instance how to wire memory systems into a self-improving colony.

```
LOCAL (fast, immediate):
  QMD  ← long-term curated knowledge
  LCM  ← session compaction, feeds QMD
  fs   ← daily logs, workspace files

PRIVATE REPO (sellable):
  SKILL.md, templates/, memory-protocol, examples
  → How to wire QMD + LCM into a self-improving colony
```

**Revenue model:** Sell on ClawHub. One-time install that makes any OpenClaw deployment dramatically more capable — no repeated mistakes, no cold starts, compounding memory.

```
Brain (Mycelium)       → mimo-v2-pro:free  → 1M context, NO vision — needs memory, not eyes
Scouts (Swarm)         → step-3.5-flash    → Many in parallel, fast/cheap, narrow focus
Coordinators (Army)    → mimo-v2-pro:free  → 1M context for registry state
Workers (Dynamic Ants) → mimo-v2-omni:free → Vision+tools — the EYES and HANDS
```

## Chain of Command

```
         ┌──────────────────────────────────────────────┐
         │            COLONY MEMORY                     │
         │  ┌──────────────────┬────────────────────┐   │
         │  │ QMD (long-term)  │  LCM (recent)      │   │
         │  │ files, logs,     │  compacted context, │   │
         │  │ transcripts,     │  grep/describe/     │   │
         │  │ daily memory     │  expand             │   │
         │  └────────┬─────────┴─────────┬──────────┘   │
         │  📋 #mission    ✅ #mission-complete          │
         │  ⚠️ #pain-point 💡 #shortcut                  │
         │  🌿 #green-leaf 📊 #benchmark                 │
         └────────────────┬─────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
Mycelium            SCOUT SWARM           Army Ants
(Brain)           (many in parallel)     (Coordinators)
mimo-v2-pro       step-3.5-flash         mimo-v2-pro
1M context                             1M context
NO vision                              NO vision
    │            🔧 Tool Scouts               │
    │            🌿 Leaf Scouts               │
    │            📊 Benchmark Scouts          │
    │            🔌 Integration Scouts        │
    │                                        │
    │                                  ┌─────▼──────┐
    │                                  │ Dynamic Ants│
    │                                  │  (Workers)  │
    │                                  │ mimo-v2-omni│
    │                                  │ vision+tools│
    │                                  └─────┬──────┘
    │                                        │
    └────────────────────────────────────────┘
           ALL FEED INTO SHARED MEMORY
```

## Features

- **178 specialized agent roles** from [agency-agents](https://github.com/msitarzewski/agency-agents)
- **Biologically correct model assignment** — brain routes, ants see and do
- **Scout Swarm** — many scouts in parallel, each searching for food or leaves
- **Shared memory as colony nervous system** — every ant writes findings
- **The Food Chain** — scouts find tools → ants get stronger → scouts find leaves → brain grows → colony grows
- **Immutable rules** — never spend money, never downgrade models
- **Self-improving** — Scout Swarm continuously finds better tools and opportunities
- **Revenue-focused** — Leaf Scouts constantly hunt for money-making opportunities

## Quick Start

```python
from core.mycelium import Mycelium, ArmyAnt, DynamicAnt

brain = Mycelium()                    # mimo-v2-pro (brain, 1M context)
army = ArmyAnt(brain)                 # mimo-v2-pro (coordinator, 1M context)

# Build a team for a mission
team = army.build_team("Build a landing page", ["frontend", "design", "copywriting"])

# Each team member is a Dynamic Ant with specialized role
for member in team["team"]:
    ant = DynamicAnt(member["role"], member["model"], member["task"])
    result = ant.execute()            # mimo-v2-omni (eyes+hands, vision+tools)
    # ant writes #mission → #mission-complete to shared memory
```

## Shared Memory Protocol

Every agent reads and writes shared memory (QMD). This is the colony's nervous system.

| Tag | Purpose | Written By |
|-----|---------|-----------|
| `#mission` | Active work started | Dynamic Ants |
| `#mission-complete` | Work finished with results | Dynamic Ants |
| `#pain-point` | Something blocked progress | Any agent |
| `#lesson` | Durable knowledge gained | Tool/Integration Scouts |
| `#shortcut` | Efficiency trick discovered | Tool/Integration Scouts |
| `#green-leaf` | Revenue opportunity found | Leaf Scouts |
| `#benchmark` | Model performance data | Benchmark Scouts |
| `#durable-state` | System snapshot | Mycelium |

**Colony Health Rules:**
- ✅ Healthy: missions completing, pain points addressed, leaf scouts finding opportunities
- ⚠️ Sick: stale missions (>30 min), accumulating pain points, no green-leaf in 24h
- 🍄 Growing: scouts finding food (tools) → ants getting stronger → brain routing better → colony expanding

## Agent Registry

178+ specialized roles across 18 departments:

| Department | Roles | Use Case |
|-----------|-------|----------|
| Engineering | 23 | Full-stack, DevOps, ML, Security |
| Marketing | 27 | Growth, SEO, Content, Social |
| Sales | 8 | Outbound, Pipeline, Coaching |
| Design | 8 | UX, UI, Brand, Visual Storytelling |
| Specialized | 27 | Data, Legal, Compliance, HR |
| Testing | 8 | QA, E2E, Performance, Chaos |
| Product | 5 | PM, Strategy, Analysis |
| Strategy | 3 | Business, Competitive, Innovation |
| + 10 more | 71 | Support, Academic, Game Dev, etc. |

## Model Rules

1. **NEVER** spend money without Jon's explicit approval
2. **NEVER** downgrade models without proof
3. Brain uses mimo-v2-pro (1M context, no vision — needs memory)
4. Ants use mimo-v2-omni (vision+tools — they ARE the eyes and hands)
5. Free tier only. We make money, not spend it.
6. Keep benchmarks current — test monthly minimum

## Skill & MCP Integration

Mycelium does NOT replace skills or MCP. It **orchestrates** them.

- **Skills** (AgentSkills/ClawHub) → Capability packages. Users plugin their own. Mycelium wraps and routes.
- **MCP Tools** (Model Context Protocol) → External integrations. Dynamic Ants bind MCP tools on demand.
- **Models** (any provider) → Routing layer picks the best model for each task.

Anyone can plugin:
- 🧩 **Skills** — Drop a SKILL.md + files, auto-discovered
- 🔌 **MCP Servers** — Configure connection, capabilities discovered
- 🤖 **Models** — Add provider config, Scout benchmarks it
- 🐜 **Agent Roles** — Add role definition to registry

See [docs/SKILL-MCP-INTEGRATION.md](docs/SKILL-MCP-INTEGRATION.md) for the full integration architecture.

## Why Mycelium?

Mycelium networks in nature:
- Connect trees and share resources underground
- Route nutrients to where they're needed most
- Send hundreds of scouts to find food and leaves
- Self-heal when damaged
- Grow stronger with every successful find

This framework does the same for AI agents:
- Connects specialized agents to missions
- Routes the best model to each task
- **Swarms scouts in parallel** — tool scouts find food, leaf scouts find revenue
- Self-improves through Scout discoveries
- Gets more capable with every mission
- Shared memory = colony's pheromone trails

### The Food Chain

```
🔧 Scouts find FOOD (tools, improvements)
   → strengthens ANTS → better execution

🌿 Scouts find LEAVES (revenue, opportunities)
   → feeds MYCELIUM → brain grows

💪 Stronger brain → better routing → stronger teams → more results
   → COLONY GROWS
```

## License

MIT. Agent roles from [agency-agents](https://github.com/msitarzewski/agency-agents) under their respective license.
