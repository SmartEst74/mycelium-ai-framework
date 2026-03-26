# 🌊 Mycelium AI Framework — Quick Start

Get a multi-agent colony running in 5 minutes.

## What This Is

An architecture for AI agents that **compounds knowledge** instead of starting from scratch every session. Four specialized roles work together:

| Role | Icon | Job |
|------|------|-----|
| **Mycelium** | 🧠 | Brain — plans, decomposes tasks, routes to workers |
| **Scout** | 🔍 | Researcher — explores, reports, never executes |
| **Army Ant** | 🛡️ | Protector — scans for threats, enforces hard constraints |
| **Dynamic Ant** | 🔨 | Builder — executes one task, self-evaluates, reports back |

## The Key Insight

Solo agents forget everything between sessions. Colony agents share a memory system (QMD) so every agent starts with accumulated knowledge. The colony gets smarter over time.

## 5-Minute Setup

### 1. Clone

```bash
git clone https://github.com/SmartEst74/mycelium-ai-framework.git
cd mycelium-ai-framework
```

### 2. Copy Templates

```bash
# Copy to your OpenClaw workspace
cp -r templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp -r templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp -r templates/HEARTBEAT.md ~/.openclaw/workspace/HEARTBEAT.md
```

### 3. Configure Models

Edit `~/.openclaw/workspace/SOUL.md` and replace the model placeholders with your available models:

```
| **Mycelium** (brain) | <your-pro-model>    | Big context for planning |
| **Scout** (sensor)   | <your-fast-model>   | Cheap, fast research     |
| **Army Ant** (protector) | <your-vision-model> | Needs to scan files |
| **Dynamic Ant** (builder) | <your-vision-model> | Needs tools + vision |
```

### 4. Start the Colony

OpenClaw will read `SOUL.md` on startup. The Mycelium agent is now your main session.

### 5. Send Your First Mission

Type a task in Telegram / your OpenClaw channel. Example:

> "Research the current state of web components and write a summary to memory"

The Mycelium will:
1. 🧠 Decompose the task
2. 🔍 Spawn a Scout to research
3. 📝 Write findings to QMD memory
4. ✅ Report back to you

## The Event Bus

Every action the colony takes is recorded as a structured event. Filter by project to see only relevant work.

### Using the Event Bus

```bash
# Emit an event
./scripts/event-bus.sh emit --agent mycelium --role brain --type spawn \
  --project my-project --message "Starting new feature"

# Query events for a project
./scripts/event-bus.sh query --project my-project

# See all events in real-time
./scripts/event-bus.sh stream

# Filter stream by project
./scripts/event-bus.sh stream --project my-project

# Stats
./scripts/event-bus.sh stats
```

### Event Types

| Type | Icon | Meaning |
|------|------|---------|
| `spawn` | 🌱 | New agent spawned |
| `think` | 💭 | Agent reasoning |
| `decide` | ⚡ | Decision made |
| `execute` | 🔨 | Action taken |
| `block` | 🛑 | Blocker encountered |
| `complete` | ✅ | Task finished |
| `protect` | 🛡️ | Army Ant enforcement |
| `research` | 🔍 | Scout research |

### Visualisation (coming soon)

```bash
# ASCII flow diagram
./scripts/event-bus-visualize.sh --project my-project

# Interactive HTML graph
python3 scripts/event-bus-graph.py --project my-project
# Opens events-visual.html in browser
```

## Self-Improvement Loop

Every task follows: RUN → EVALUATE → RECORD → IMPROVE

1. **Before task**: Search QMD for relevant `#lesson` entries
2. **Do the work**: Execute, discover, iterate
3. **Self-evaluate**: Score 1-5 on Accuracy, Efficiency, Completeness, Reusability
4. **Record**: Write outcome + scores to memory with tags
5. **Improve**: Score < 3 → `#pain-point`; Score ≥ 4 on all → `#lesson`

## Memory Tags

| Tag | Purpose | Retention |
|-----|---------|-----------|
| `#lesson` | Reusable knowledge | Permanent |
| `#pain-point` | Friction / gotchas | Until resolved |
| `#shortcut` | Efficiency pattern | Permanent |
| `#mission` | Active work | Until completed |
| `#mission-complete` | Finished work | Archive after review |

## Project Isolation

Each project gets its own ID. Events, memory entries, and missions are tagged by project. Switch contexts without pollution.

```bash
# Work on Project A
./scripts/event-bus.sh emit --agent mycelium --role brain --type think \
  --project project-a --message "Starting deployment prep"

# Work on Project B (separate stream)
./scripts/event-bus.sh emit --agent mycelium --role brain --type think \
  --project project-b --message "Researching pricing strategy"

# Query only Project A
./scripts/event-bus.sh query --project project-a
```

## Architecture

```
         ┌─────────────┐
         │  🧠 MYCELIUM │  (Brain — decompose, route)
         │  mimo-v2-pro │
         └──────┬──────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌───────┐  ┌────────┐  ┌──────────┐
│🔍SCOUT│  │🔨BUILDER│  │🛡️PROTECT│
│flash  │  │omni    │  │omni      │
└───────┘  └────────┘  └──────────┘
    │           │           │
    ▼           ▼           ▼
┌─────────────────────────────┐
│  📦 QMD MEMORY (shared)     │
│  Lessons, shortcuts, state  │
└─────────────────────────────┘
```

## Files

```
├── docs/
│   ├── ARCHITECTURE.md       # Full architecture
│   ├── SELF-IMPROVEMENT.md   # Learning loop protocol
│   └── DEPLOYMENT.md         # Detailed setup guide
├── templates/
│   ├── SOUL.md               # Colony personality (copy to workspace)
│   ├── AGENTS.md             # Operating protocol (copy to workspace)
│   ├── HEARTBEAT.md          # Health checks (copy to workspace)
│   └── cron/                 # Example cron configurations
└── scripts/
    ├── event-bus.sh          # Event recording & querying
    ├── event-bus-visualize.sh # ASCII flow diagrams
    └── event-bus-graph.py    # Interactive HTML visualisation
```

## License

MIT — build, share, improve.

## Contributing

Found a better pattern? Write it as a `#lesson` and open a PR. The colony gets smarter when we share.
