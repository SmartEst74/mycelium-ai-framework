# 🍄 Mycelium AI Framework

**A multi-agent orchestration framework inspired by mycelium networks.**

## Chain of Command

```
Mycelium (Brain) → Scout (Researcher) → Army (Team Builder) → Dynamic (Worker)
```

- **Mycelium**: Central reasoning brain. Never executes. Delegates everything.
- **Scout**: Researcher. Finds better models, tools, opportunities. Never executes.
- **Army Ants**: Team builders. Select agency-agent roles, match best model, spawn workers.
- **Dynamic Ants**: Focused workers. One task, one role, one model, one report. Ephemeral.

## Features

- **179 specialized agent roles** from [agency-agents](https://github.com/msitarzewski/agency-agents)
- **Model assignment matrix** — best free model matched to each task type
- **Immutable rules** — never spend money, never downgrade models
- **Self-improving** — Scout continuously finds better tools and opportunities
- **Revenue-focused** — every decision asks "does this make money?"

## Quick Start

```python
from core.mycelium import Mycelium, ArmyAnt, DynamicAnt

brain = Mycelium()
army = ArmyAnt(brain)

# Build a team for a mission
team = army.build_team("Build a landing page", ["frontend", "design", "copywriting"])

# Each team member is a Dynamic Ant with a specialized role
for member in team:
    ant = DynamicAnt(member["role"], member["model"], member["task"])
    result = ant.execute()
```

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

1. **NEVER** spend money without explicit approval
2. **NEVER** downgrade models without proof
3. Primary model MUST have: vision + tools + reasoning
4. Free tier only. We make money, not spend it.
5. Keep benchmarks current — test monthly minimum

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

## License

MIT. Agent roles from [agency-agents](https://github.com/msitarzewski/agency-agents) under their respective license.
