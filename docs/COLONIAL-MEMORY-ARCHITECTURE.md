# Colonial Memory Architecture

## The Problem

Three systems exist but aren't connected into a pipeline:
- **Rhizomorph** (Event Bus) — captures raw agent events in SQLite
- **LCM** (Lossless Claw) — compacts conversations into layered summary DAGs
- **QMD** (Quick Markdown) — indexes markdown files for fast search

Without a bridge, LCM compacts conversations but durable knowledge doesn't
automatically flow into QMD. Agents must manually curate memory files.

## The Solution: Curated Pipeline with Hierarchical Tagging

```
Agents → [Rhizomorph Event Bus] → [LCM Compaction] → [Curator] → [QMD Index]
                                         │                  │
                                    ephemeral noise    durable knowledge
                                    stays compacted    indexed & searchable
```

### Layer 1: Rhizomorph (Nervous System)

The event bus captures everything agents do:
- `mission.start` / `mission.complete` — mission lifecycle
- `memory.write` — knowledge discovery
- `memory.reuse` — compound learning (using prior knowledge)
- `delegation` — agent hierarchy events

**Tagging happens at write time:**

```python
bus.emit("memory.write", {
    "lesson": "Deploy via SCP when git auth unavailable",
    "context": "cv.it1st.com deployment",
}, agent="scout-deploy", tags=[
    "mission:deploy-cv-it1st",
    "project:cv-quicklinks",
    "role:scout",
    "type:lesson",
    "domain:deployment"
])
```

**Tag taxonomy (fixed vocabulary):**

| Prefix | Purpose | Example |
|--------|---------|---------|
| `mission:` | Specific work item | `mission:deploy-cv-it1st` |
| `project:` | Parent project | `project:cv-quicklinks` |
| `role:` | Agent role | `role:scout`, `role:general`, `role:army-ant` |
| `type:` | Knowledge type | `type:lesson`, `type:pain-point`, `type:benchmark` |
| `domain:` | Technical area | `domain:deployment`, `domain:model-selection` |

### Layer 2: LCM (Context Brain)

LCM already does what it's designed for:
- Compacts conversations into layered summaries (depth 0, 1, 2...)
- Preserves source references via `summary_parents`
- Provides `lcm_grep`, `lcm_expand_query` for retrieval

**What LCM contributes to the pipeline:**
- Compacted conversation context (not events — those go to Rhizomorph)
- `lcm_expand_query` can answer "what happened in this conversation?"
- The compaction DAG preserves detail that would otherwise be lost

**What LCM does NOT do:**
- It doesn't know about mission/project hierarchy
- It doesn't tag or categorize knowledge
- It doesn't push to QMD

### Layer 3: QMD (Colonial Memory)

QMD indexes markdown files. The key insight: **use QMD collections as hierarchical namespaces**.

```
memory/
├── missions/
│   ├── deploy-cv-it1st.md        # Mission-specific lessons
│   ├── crypto-income-plan.md     # Mission plan
│   └── mycelium-framework.md     # Active mission
├── projects/
│   ├── cv-quicklinks.md          # Project-level knowledge
│   ├── it1st-services.md         # Revenue project
│   └── mycelium-ai-framework.md  # Open source project
├── lessons/
│   ├── deployment.md             # Cross-mission deployment lessons
│   ├── model-selection.md        # Model comparison lessons
│   └── colony-ops.md             # Agent orchestration lessons
├── benchmarks/
│   ├── model-performance.md      # Model benchmarks
│   └── token-efficiency.md       # Cost optimization benchmarks
└── agents/
    ├── scout-patterns.md         # What scouts do well
    └── general-patterns.md       # What generals do well
```

**QMD collection mapping:**

```
memory-root-main   →  MEMORY.md (global rules, already indexed)
memory-dir-main    →  memory/**/*.md (all memory files, already indexed)
```

The existing collections already cover this! No new collections needed.
The hierarchy comes from **directory structure + frontmatter tags**, not
collection names.

### Layer 4: The Curator (The Missing Bridge)

The curator is a process that:
1. **Watches** Rhizomorph for completed missions
2. **Reads** the LCM compaction for that mission's conversation
3. **Extracts** durable knowledge (lessons, pain points, benchmarks)
4. **Writes** curated markdown to `memory/missions/<name>.md`
5. **QMD auto-indexes** on next `qmd update`

**Implementation: A Python script that runs as a cron job or post-mission hook.**

```python
# curator.py — The Colonial Memory Curator

def curate_mission(mission_id: str, bus: Rhizomorph, lcm_db: str):
    """Extract durable knowledge from a completed mission."""

    # 1. Get all events for this mission from Rhizomorph
    events = bus.get_events_by_tag(f"mission:{mission_id}")

    # 2. Extract lessons, pain points, benchmarks
    lessons = [e for e in events if "type:lesson" in e.tags]
    pain_points = [e for e in events if "type:pain-point" in e.tags]
    benchmarks = [e for e in events if "type:benchmark" in e.tags]

    # 3. Ask LCM for the conversation context
    # (via lcm_expand_query with the mission's conversation)
    summary = lcm_query(f"What was learned in mission {mission_id}?")

    # 4. Write curated markdown
    content = format_mission_memory(mission_id, lessons, pain_points,
                                     benchmarks, summary)
    write_to(f"memory/missions/{mission_id}.md", content)

    # 5. QMD indexes it automatically on next update
    # (or we trigger qmd update explicitly)
```

**The markdown format (frontmatter + body):**

```markdown
---
mission: deploy-cv-it1st
project: cv-quicklinks
completed: 2026-03-25T17:27:00Z
tags: [deployment, hetzner, nginx, cv-it1st]
---

# Mission: Deploy cv.it1st.com

## What Was Built
Deployed cv-quicklinks to hummingbot (46.225.28.139) at cv.it1st.com.

## Lessons Learned
- When git auth fails on remote, use tar pipe instead of SCP
- Nginx already configured for multiple sites — just add server block
- Node 18 works fine for cv-quicklinks (no need to upgrade)

## Pain Points
- SCP hung silently for 30s — had to kill and retry with tar pipe
- git credential cache used wrong GitHub account (sexyloverman vs SmartEst74)

## Benchmarks
- Deployment time: 15 min (first deploy, including nginx config)
- Expected future deploys: 2 min (just tar + restart)
```

## Tag Hierarchy — How It Works

### Example: Scout discovers a lesson during deployment

```
Agent: scout-deploy
Mission: deploy-cv-it1st
Project: cv-quicklinks

Event:
  type: memory.write
  tags: [mission:deploy-cv-it1st, project:cv-quicklinks, role:scout, type:lesson]
  payload: {"lesson": "Use tar pipe when git auth unavailable on remote"}
```

### Querying by any level of the hierarchy

```python
# All lessons from deployment missions
bus.get_events_by_tag("type:lesson")

# All events from cv-quicklinks project
bus.get_events_by_tag("project:cv-quicklinks")

# All events from a specific mission
bus.get_events_by_tag("mission:deploy-cv-it1st")

# All pain points from scouts
# (requires filtering — Rhizomorph supports AND queries)
```

### QMD cross-referencing

```bash
# Find all deployment-related knowledge
qmd search "deployment" -c memory-dir-main

# Find lessons about git auth
qmd search "git auth credential" -c memory-dir-main

# Find what a specific mission learned
qmd search "deploy-cv-itst lessons" -c memory-dir-main
```

## Compound Learning — The Grant Story

The tag hierarchy enables **measurable compound learning**:

```
Mission 1: Scout discovers 5 lessons, stores tagged
Mission 2: Scout queries "type:lesson domain:deployment" → reuses 3/5
Mission 3: Scout queries → reuses 4/5 (1 new lesson added)
Mission N: Scout reuses all prior lessons, only discovers genuinely new ones
```

**Metrics:**
- `lessons_stored` — how many lessons entered the colonial memory
- `lessons_reused` — how many were found and applied in later missions
- `redundancy_rate` — % of work that duplicated prior knowledge
- `compound_speedup` — time reduction per mission due to prior knowledge

## Architecture Justification (for grants)

### Why not just use LCM?

LCM is a **context** system — it compacts conversations for the current session.
It doesn't provide:
- Mission-level tagging
- Cross-conversation knowledge retrieval
- Structured lesson extraction
- Compound learning metrics

### Why not just use QMD?

QMD is a **search** system — it indexes files for retrieval.
It doesn't provide:
- Real-time event capture (Rhizomorph does this)
- Conversation compaction (LCM does this)
- Automatic knowledge extraction (the Curator does this)

### Why all three together?

The pipeline gives you:
1. **Rhizomorph** captures everything, tags it, makes it auditable
2. **LCM** compacts context so agents don't lose detail in long sessions
3. **QMD** indexes durable knowledge so future agents can find it
4. **Curator** bridges the gap, extracting signal from noise

This is the "colonial memory" — not just one agent remembering, but a
**system of agents building shared institutional knowledge** that compounds
over time.

## Implementation Plan

### Phase 1: Tags in Rhizomorph (DONE)
- Event dataclass has `agent` and `tags` fields ✓
- All Event construction includes these fields ✓
- Query methods support tag-based filtering ✓

### Phase 2: Curator Script (NEXT)
- Write `scripts/curator.py`
- Watch Rhizomorph for completed missions
- Extract lessons/pain-points/benchmarks by tag
- Write curated markdown to `memory/missions/`
- Trigger QMD update

### Phase 3: Colony Memory Protocol Integration (NEXT)
- Update SOUL.md with tag taxonomy
- Update AGENTS.md with curator instructions
- Add curator as a cron job (post-mission hook)

### Phase 4: Benchmark Integration (NEXT)
- Wire curator metrics into benchmark framework
- Measure: lessons_stored, lessons_reused, redundancy_rate
- Show compound learning curve over N missions

### Phase 5: Demo (GRANT DELIVERABLE)
- Run 5 missions with colonial memory enabled
- Run 5 missions without (control)
- Compare: time, tokens, redundancy, compound speedup
- Produce chart showing learning curve
