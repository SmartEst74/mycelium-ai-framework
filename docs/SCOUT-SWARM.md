# Scout Swarm — The Colony's Search Party

## Biological Principle

In nature, a mycelium colony doesn't send one scout. It sends **hundreds**. They fan out in every direction, each searching for something specific:

- **Food scouts** — find nutrients, decaying matter, mineral deposits
- **Leaf scouts** — find fallen leaves, organic material to decompose
- **Trail scouts** — find better paths, shorter routes, safer corridors
- **Threat scouts** — detect competitors, parasites, hostile fungi

The ones that find something **write pheromone trails** back to the colony. The colony reads those trails and routes resources accordingly. The ones that find nothing simply die. No cost to the colony. No ceremony.

**We do the same.**

## Scout Types

### 🔧 Tool Scouts — "Food Finders"

**Mission**: Find new tooling and self-improvements to strengthen the colony.

**What they hunt for:**
- New free models (better, faster, cheaper)
- New APIs and integrations
- Better development tools
- Improved prompt patterns
- More efficient workflows
- New skills on ClawHub
- New MCP servers
- Better deployment methods
- Performance optimizations
- Security improvements

**How they operate:**
- Spawn in parallel (many scouts, each with a narrow search)
- Run quick assessments (cheap model, fast)
- Write findings to shared memory with `#benchmark` or `#lesson`
- Die after reporting (ephemeral)

**What happens with their findings:**
- Mycelium reads `#benchmark` entries
- If a tool is better → update model assignments
- If a workflow is better → update `#shortcut` entries
- If something is broken → write `#pain-point`
- **The colony gets stronger with every successful find**

### 🌿 Leaf Scouts — "Revenue Hunters"

**Mission**: Find leaves (money-making opportunities) to feed the mycelium.

**What they hunt for:**
- Freelance opportunities (Fiverr, Upwork, Toptal)
- Client needs (businesses needing automation)
- Product ideas (tools people will pay for)
- Content opportunities (guides, templates, courses)
- Consulting leads (AI integration, web dev)
- Arbitrage opportunities (price differences, free credits, grants)
- Partnership opportunities (revenue sharing, affiliates)
- Market gaps (underserved niches)

**How they operate:**
- Spawn in parallel (many scouts, each searching a different channel)
- Run quick assessments (is this real? is it viable? can we do it with zero spend?)
- Write findings to shared memory with `#green-leaf`
- Die after reporting (ephemeral)

**What happens with their findings:**
- Mycelium reads `#green-leaf` entries
- Scores opportunities: revenue potential × probability × speed
- Routes highest-scoring opportunities to Army Ants
- Army Ants build teams to execute
- **Revenue feeds the brain, brain grows the colony**

### 📊 Benchmark Scouts — "Quality Inspectors"

**Mission**: Test models and ensure the colony never degrades.

**What they hunt for:**
- New model releases (free tier)
- Model performance changes (improvements or degradations)
- Context window changes
- Tool/vision capability changes
- Rate limit changes
- Cost changes

**How they operate:**
- Run standardized tests against all available models
- Compare against current assignments
- Write results to shared memory with `#benchmark`
- Flag any degradation with `#pain-point`

**What happens with their findings:**
- Mycelium reads `#benchmark` entries
- If model improved → consider upgrade (with proof)
- If model degraded → trigger fallback chain
- If new model found → add to assessment queue
- **Model quality stays current, never degrades silently**

### 🔌 Integration Scouts — "Connection Finders"

**Mission**: Find new ways to connect the colony to the outside world.

**What they hunt for:**
- New skills on ClawHub
- New MCP servers
- New API integrations
- New deployment targets
- New communication channels
- New tool ecosystems

**How they operate:**
- Monitor ClawHub, MCP registries, GitHub trending
- Assess compatibility with mycelium architecture
- Write findings to shared memory with `#lesson` or `#shortcut`
- Die after reporting (ephemeral)

**What happens with their findings:**
- Mycelium reads and evaluates
- If compatible → register in skill/tool registry
- If incompatible → log why for future reference
- **The colony's reach expands with every new connection**

## The Food Chain

```
Scouts find FOOD (tools, improvements)
    │
    ▼
Food strengthens ANTS (Dynamic Ants get better tools)
    │
    ▼
Stronger ants execute BETTER
    │
    ▼
Better execution produces RESULTS
    │
    ▼
Scouts find LEAVES (revenue opportunities)
    │
    ▼
Leaves feed MYCELIUM (brain gets resources to grow)
    │
    ▼
Stronger brain ROUTES BETTER
    │
    ▼
Better routing builds STRONGER TEAMS
    │
    ▼
Stronger teams produce MORE RESULTS
    │
    └──────────► COLONY GROWS ◄──────────┘
                     ▲
                     │
              (cycle repeats)
```

## Scout Swarm Rules

1. **Parallel by default** — Never run one scout when ten can run faster
2. **Ephemeral** — Scouts spawn, search, report, die. No permanent scouts.
3. **Narrow focus** — Each scout searches ONE thing. Breadth comes from many scouts.
4. **Write everything** — Every finding goes to shared memory immediately
5. **No execution** — Scouts NEVER do the work. They find it. Others do it.
6. **No cost** — Scouts use the cheapest/fastest model available (step-3.5-flash)
7. **No ceremony** — If a scout finds nothing, it dies silently. No report needed.

## Shared Memory — Where Scouts Write

Scouts write into the memory funnel:

```
  Session grows → LCM compacts → only valuable knowledge rises → QMD
```

| Memory | What Scouts Write | Why |
|--------|------------------|-----|
| **LCM** | Everything — findings, investigations, partial results, dead ends | LCM compacts it all perfectly. No need to curate on write. |
| **QMD** | Only proven value — `#lesson`, `#green-leaf`, `#benchmark` | Durable knowledge that will be needed again next session |

Scouts don't decide what's valuable. They dump into LCM. The session compaction process surfaces what matters. Only then does it rise to QMD.

Every scout writes to whichever system fits. The colony reads both.

## Shared Memory Tags (Scout-Specific)

| Tag | Scout Type | Purpose |
|-----|-----------|---------|
| `#benchmark` | Benchmark Scout | Model performance data |
| `#green-leaf` | Leaf Scout | Revenue opportunity |
| `#lesson` | Tool Scout | Durable knowledge gained |
| `#shortcut` | Tool/Integration Scout | Efficiency trick found |
| `#pain-point` | Any Scout | Something broken or blocked |

## How Many Scouts?

**As many as needed.** In nature, a healthy colony sends hundreds.

In practice:
- **Daily heartbeat**: 3-5 scouts (routine checks)
- **Active revenue hunt**: 10-20 scouts (parallel search across channels)
- **Model assessment**: 5-10 scouts (test all available models)
- **New integration check**: 3-5 scouts (ClawHub, MCP, GitHub trending)
- **Emergency**: As many as needed (degraded model, broken tool, urgent opportunity)

**The colony scales scouts to match the problem.**

## What Scouts Feed

| Scout Type | Feeds | How |
|-----------|-------|-----|
| Tool Scout | → Dynamic Ants | Better tools = stronger ants |
| Leaf Scout | → Mycelium (brain) | Revenue = resources to grow |
| Benchmark Scout | → Mycelium (brain) | Model data = better routing |
| Integration Scout | → Army Ants | New connections = broader capability |

## Anti-Patterns

❌ **Don't**: Run one scout for everything
✅ **Do**: Run many scouts, each narrow-focused

❌ **Don't**: Make scouts permanent
✅ **Do**: Spawn, search, report, die

❌ **Don't**: Let scouts execute
✅ **Do**: Scouts find, others do

❌ **Don't**: Ignore scout findings
✅ **Do**: Mycelium reads ALL scout reports on every heartbeat

❌ **Don't**: Send scouts without a clear search mission
✅ **Do**: Each scout has ONE specific thing to find
