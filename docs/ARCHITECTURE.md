# Mycelium AI Framework — Architecture

## Chain of Command

```
Mycelium (Brain)
  ├── Scout (Researcher)
  │     ├── Better models
  │     ├── Better tools
  │     ├── Better reasoning
  │     ├── Better memory
  │     ├── Better environment control
  │     └── Better money-making (find green leaves)
  │
  ├── Army Ants (Team Builders)
  │     ├── Picks agency-agent roles from registry
  │     ├── Assigns best model for each role
  │     ├── Orchestrates parallel or serial execution
  │     └── Reports results to Mycelium
  │
  └── Dynamic Ants (Workers)
        ├── Focused single-task role
        ├── Best model matched to task
        ├── Agency-agent persona applied
        └── Completes task, reports back to Army
```

## Layer Details

### Layer 1: Mycelium (Reasoning + Control)
- **Role**: Central brain. Never executes side-effects.
- **Responsibilities**: 
  - Receives missions from Jon or heartbeat
  - Delegates to Scout for research and improvement
  - Delegates to Army for execution
  - Monitors quality, prevents downgrades
  - Maintains benchmarks and model selection
  - Routes to best available model based on task type
- **Model**: Best reasoning model available (currently mimo-v2-omni:free)
- **Key rule**: Mycelium NEVER does the work itself. It delegates.

### Layer 2: Scout (Researcher + Improver)
- **Role**: Constantly improves the colony's capabilities
- **Responsibilities**:
  - Monitor free model landscape daily
  - Test new models and update benchmarks
  - Find better tools, APIs, integrations
  - Improve agent control patterns
  - Improve memory and environment control
  - Hunt for revenue opportunities ("green leaves")
  - Report findings to Mycelium
- **Model**: Fast model for research (step-3.5-flash:free or similar)
- **Key rule**: Never propose a downgrade. Only propose upgrades with evidence.

### Layer 3: Army Ants (Team Builders)
- **Role**: Build execution teams from agency-agent registry
- **Responsibilities**:
  - Receive mission from Mycelium
  - Select appropriate agency-agent roles from registry
  - Match best model to each role based on benchmarks
  - Decide parallel vs serial execution
  - Spawn Dynamic Ants for each task
  - Monitor progress, re-route if blocked
  - Report results to Mycelium
- **Model**: Best orchestration model available
- **Key rule**: Use agency-agent registry. Don't reinvent roles.

### Layer 4: Dynamic Ants (Workers)
- **Role**: Single-task focused execution
- **Responsibilities**:
  - Take one specific task from Army Ant
  - Apply agency-agent persona/role
  - Use assigned model (matched to task type)
  - Complete task with full focus
  - Report result back to Army Ant
  - Die after completion (ephemeral)
- **Model**: Best model for the specific task type:
  - Code → qwen3-coder (if available) or best coding model
  - Writing → best creative model
  - Research → fastest model with web access
  - Vision → mimo-v2-omni:free (only free vision model)
- **Key rule**: One task. One role. One model. One report. Done.

## Model Assignment Matrix

| Task Type | Best Free Model | Fallback |
|-----------|----------------|----------|
| Vision + Tools | mimo-v2-omni:free (kilocode) | gpt-5-mini |
| Code Generation | mimo-v2-pro:free (kilocode) | step-3.5-flash:free |
| Reasoning | mimo-v2-omni:free (kilocode) | glm-4.5-air:free |
| Creative Writing | mimo-v2-pro:free (kilocode) | step-3.5-flash:free |
| Fast Research | step-3.5-flash:free (kilocode) | mimo-v2-pro:free |
| Web Scraping | mimo-v2-pro:free (kilocode) | glm-4.5-air:free |

**RULE: Never downgrade models. Only upgrade with proof.**
**RULE: Free models only. No spend. We make money, not spend it.**

## Agency-Agent Registry

179 specialized agent roles from `msitarzewski/agency-agents`:

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
- `registry/` — Agency-agent role registry
- `config/` — Model assignments, benchmarks, rules
