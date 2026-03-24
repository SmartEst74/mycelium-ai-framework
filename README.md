# 🍄 Mycelium AI Framework

**A multi-agent orchestration framework inspired by mycelium networks and ant colonies.**

## Biological Model

In nature, mycelium doesn't see — it *routes underground*. The ants are the eyes and hands that sense the world and execute tasks. Pheromone trails are the shared memory that lets the colony function as one organism.

```
Brain (Mycelium)     → mimo-v2-pro:free  → 1M context, NO vision — needs memory, not eyes
Sensor (Scout)       → step-3.5-flash    → Fast, cheap — probes and reports
Coordinators (Army)  → mimo-v2-pro:free  → 1M context for registry state
Workers (Dynamic)    → mimo-v2-omni:free → Vision+tools — the EYES and HANDS
```

## Chain of Command

```
         ┌──────────────────────────────────────┐
         │       SHARED MEMORY (QMD)            │
         │  📋 #mission    ✅ #mission-complete  │
         │  ⚠️ #pain-point 💡 #shortcut          │
         │  🌿 #green-leaf 📊 #benchmark         │
         └────────────────┬─────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
Mycelium              Scout                Army Ants
(Brain)             (Sensor)            (Coordinators)
mimo-v2-pro        step-3.5-flash        mimo-v2-pro
1M context         fast/cheap            1M context
NO vision          web access            NO vision
    │                                         │
    │                                  ┌──────▼──────┐
    │                                  │ Dynamic Ants│
    │                                  │  (Workers)  │
    │                                  │ mimo-v2-omni│
    │                                  │ vision+tools│
    │                                  └──────┬──────┘
    │                                         │
    └─────────────────────────────────────────┘
           ALL FEED INTO SHARED MEMORY
```

## Features

- **178 specialized agent roles** from [agency-agents](https://github.com/msitarzewski/agency-agents)
- **Biologically correct model assignment** — brain routes, ants see and do
- **Shared memory as colony nervous system** — every ant writes findings
- **Immutable rules** — never spend money, never downgrade models
- **Self-improving** — Scout continuously finds better tools and opportunities
- **Revenue-focused** — every decision asks "does this make money?"

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
| `#lesson` | Durable knowledge gained | Any agent |
| `#shortcut` | Efficiency trick discovered | Dynamic Ants |
| `#green-leaf` | Revenue opportunity found | Scout |
| `#benchmark` | Model performance data | Scout |
| `#durable-state` | System snapshot | Mycelium |

**Colony Health Rules:**
- ✅ Healthy: missions completing, pain points addressed, revenue being hunted
- ⚠️ Sick: stale missions (>30 min), accumulating pain points, no revenue hunt in 24h

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

## Why Mycelium?

Mycelium networks in nature:
- Connect trees and share resources underground
- Route nutrients to where they're needed most
- Self-heal when damaged
- Grow stronger over time

This framework does the same for AI agents:
- Connects specialized agents to missions
- Routes the best model to each task
- Self-improves through Scout research
- Gets more capable with every mission
- Shared memory = colony's pheromone trails

## License

MIT. Agent roles from [agency-agents](https://github.com/msitarzewski/agency-agents) under their respective license.
