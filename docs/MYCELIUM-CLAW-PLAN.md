# Mycelium Claw — Architecture & Implementation Plan

> The colony's nervous system. Living, learning, visible.

## 1. Overview

Mycelium Claw extends the Lossless Claw Memory (LCM) plugin with a mycelial event bus and a living visualisation dashboard called **Spore**. Agents emit events as they work, the mycelium routes signals between them, and Jon can see and steer the colony in real time.

**What this is NOT:**
- Not a replacement for LCM (extends it)
- Not a generic message queue (it's colony-aware)
- Not a monitoring dashboard (it's a living network)
- Not a Python/Go system (Node.js only, zero external runtime deps)

## 2. Naming

| Name | What | Fungal Metaphor |
|---|---|---|
| **Mycelium Claw** | The extended LCM plugin (OpenClaw extension) | The living network |
| **Spore** | Web dashboard — the user-facing visualisation | Entry point; spore lands, germinates, spreads |
| **S.P.O.R.E.** | System for Presenting Organism Runtime Events | (acronym, not shouted) |
| **hyphae** | Event table — append-only log of everything | Individual filaments carrying nutrients |
| **signals** | Injection table — Jon's input to the network | External chemical signals reaching the network |
| **mycorrhizae** | Subscription table — who watches what | Symbiotic links between organisms |
| **colonies** | Agent registry — who's alive and what they do | Distinct fungal colonies in the network |
| **sporocarps** | Materialised views / projections | Visible fruiting bodies — derived state |

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                        │
│                                                             │
│  ┌──────────────────┐      ┌────────────────────────────┐  │
│  │  LCM (existing)  │      │  Mycelium Claw (extension) │  │
│  │  ┌────────────┐  │      │  ┌──────────────────────┐  │  │
│  │  │ messages   │  │      │  │ hyphae (events)      │  │  │
│  │  │ summaries  │  │      │  │ signals (injections) │  │  │
│  │  │ contexts   │  │      │  │ mycorrhizae (subs)   │  │  │
│  │  └────────────┘  │      │  │ colonies (agents)    │  │  │
│  │                  │      │  └──────────────────────┘  │  │
│  │  SQLite (WAL)  ◄─────────────────── same DB ──────── │  │
│  └──────────────────┘      └────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    SPORE (web dashboard)              │  │
│  │  HTTP server → serves static HTML/JS/CSS             │  │
│  │  WebSocket → live event stream to browser            │  │
│  │  REST API → query hyphae, signals, colonies          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Agents: Mycelium │ Scout │ Army Ant │ Dynamic Ant         │
└─────────────────────────────────────────────────────────────┘
```

**Key constraint:** Everything runs inside the OpenClaw gateway process or as a child process. No external services (no Redis, no NATS, no Postgres). SQLite + Node.js + `ws` package. That's it.

## 4. Database Schema

All tables live in the existing `~/.openclaw/lcm.db` alongside LCM's tables. Added via LCM's migration system.

### 4.1 hyphae — Event Log

Append-only. Every action, every signal, every state change.

```sql
CREATE TABLE hyphae (
    id TEXT PRIMARY KEY,                    -- ULID (time-sortable, globally unique)
    type TEXT NOT NULL,                     -- event type (see §4.5)
    tag TEXT,                               -- primary tag: #mission, #pain-point, etc.
    source TEXT NOT NULL,                   -- agent id, 'jon', or 'mycelium'
    target TEXT,                            -- null = broadcast, specific = targeted delivery
    content TEXT NOT NULL,                  -- human-readable description
    metadata TEXT DEFAULT '{}',            -- arbitrary JSON (extensible, no migration needed)
    session_key TEXT,                       -- links to LCM conversation for cross-reference
    hypha_ref TEXT REFERENCES hyphae(id),   -- thread linkage: parent event this extends
    version INTEGER DEFAULT 1,             -- schema version for future migrations
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes for common queries
CREATE INDEX idx_hyphae_type ON hyphae(type);
CREATE INDEX idx_hyphae_tag ON hyphae(tag);
CREATE INDEX idx_hyphae_source ON hyphae(source);
CREATE INDEX idx_hyphae_created ON hyphae(created_at);
CREATE INDEX idx_hyphae_ref ON hyphae(hypha_ref);
CREATE INDEX idx_hyphae_session ON hyphae(session_key);
```

**Design notes:**
- ULID for `id` gives time-ordered keys without auto-increment (better for distributed agents)
- `tag` is nullable — not every event needs a tag
- `metadata` is JSON string — extensible without schema changes. New fields go here.
- `hypha_ref` chains events into threads: `mission:start` → `hypha:extend` → `hypha:extend` → `mission:complete`
- Tags are **not in a separate table**. They emerge: `SELECT DISTINCT tag FROM hyphae WHERE tag IS NOT NULL`

### 4.2 signals — Jon's Injections

When Jon talks to the mycelium (not a specific agent), his input lands here.

```sql
CREATE TABLE signals (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,                  -- what Jon said
    context TEXT DEFAULT '{}',             -- additional context Jon provided
    routed_to TEXT,                         -- which hypha/agent mycelium decided to route to
    status TEXT DEFAULT 'pending',          -- pending → routed → processed → archived
    processed_by TEXT,                      -- which agent processed it
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at TEXT
);
```

**Flow:**
1. Jon types in Spore dashboard or sends message to Mycelium
2. Mycelium creates signal row (status=pending)
3. Mycelium analyses content, decides routing, sets `routed_to` and `status=routed`
4. Creates corresponding `hyphae` event (type=`signal:injected`)
5. Target agent picks it up, processes, sets `status=processed`

### 4.3 mycorrhizae — Subscriptions

Who watches what. Pattern-matched, like pub/sub topics.

```sql
CREATE TABLE mycorrhizae (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber TEXT NOT NULL,               -- agent id, 'spore-dashboard', or 'jon'
    pattern TEXT NOT NULL,                  -- glob pattern: 'mission:*', 'pain-point', '*'
    active INTEGER DEFAULT 1,              -- soft delete
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Pattern matching:**
- `*` — everything (Spore dashboard uses this)
- `mission:*` — all mission events
- `pain-point` — only pain-point tagged events
- `scout:*` — events from scout agents

### 4.4 colonies — Agent Registry

Who's in the network. Updated as agents spawn/complete.

```sql
CREATE TABLE colonies (
    id TEXT PRIMARY KEY,                    -- agent id (matches sub-agent session)
    role TEXT NOT NULL,                     -- mycelium | scout | army-ant | dynamic-ant
    status TEXT DEFAULT 'dormant',          -- dormant → growing → active → retracting → dead
    current_task TEXT,                      -- what they're working on (short description)
    hypha_ref TEXT REFERENCES hyphae(id),   -- current mission/event they're attached to
    capabilities TEXT DEFAULT '[]',         -- JSON array: what this agent can do
    metadata TEXT DEFAULT '{}',             -- JSON: model, spawn time, etc.
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Status lifecycle:**
- `dormant` — registered but not spawned
- `growing` — spawned, initialising
- `active` — working on a task
- `retracting` — task complete, cleaning up
- `dead` — finished or failed

### 4.5 Event Types (extensible, not enforced in schema)

These are conventions, not constraints. The `type` column is free-text.

| Category | Types | Description |
|---|---|---|
| **Mission** | `mission:start`, `mission:complete`, `mission:fail`, `mission:blocked` | Top-level work units |
| **Hypha** | `hypha:extend`, `hypha:branch`, `hypha:retract` | Network growth/shrink |
| **Signal** | `signal:injected`, `signal:routed`, `signal:processed` | Jon's input flowing through |
| **Scout** | `scout:spawn`, `scout:finding`, `scout:complete` | Research activities |
| **Agent** | `agent:spawn`, `agent:error`, `agent:complete` | Agent lifecycle |
| **Memory** | `memory:write`, `memory:compact`, `memory:promote` | LCM/QMD pipeline |
| **Health** | `health:check`, `health:alert` | System health |

**Adding new types:** Just emit an event with the new type. No migration. Tags and types are strings that emerge from usage.

### 4.6 Sporocarps — Materialised Views (v2)

Derived state, computed from events. Not in v1 schema.

```sql
-- Example future view
CREATE VIEW active_missions AS
SELECT h.* FROM hyphae h
WHERE h.type = 'mission:start'
AND NOT EXISTS (
    SELECT 1 FROM hyphae h2
    WHERE h2.hypha_ref = h.id
    AND h2.type IN ('mission:complete', 'mission:fail')
);
```

For v1: compute these queries on demand. Materialise later if performance requires it.

## 5. Data Flows

### 5.1 Agent emits event

```
Agent completes task
  → calls tool: hypha:emit { type: 'mission:complete', tag: '#mission', content: '...' }
  → Mycelium Claw inserts into hyphae table
  → Mycelium Claw checks mycorrhizae for matching patterns
  → WebSocket broadcasts to Spore dashboard
  → Subscribed agents notified (via LCM context injection or next prompt)
```

### 5.2 Jon injects signal

```
Jon types in Spore dashboard
  → Spore POST /api/signals { content: '...' }
  → Mycelium Claw inserts into signals table (status=pending)
  → Mycelium (main agent) receives signal as system event
  → Mycelium analyses content, decides routing
  → Sets signal.routed_to, signal.status=routed
  → Emits hyphae event (type='signal:injected')
  → Target agent receives context in next prompt
```

### 5.3 Agent subscribes to events

```
Agent registers subscription
  → calls tool: mycorrhiza:subscribe { pattern: 'pain-point' }
  → Mycelium Claw inserts into mycorrhizae table
  → When matching event occurs, subscriber notified
  → For sub-agents: context injected at next prompt boundary
  → For Spore: WebSocket push
```

### 5.4 Spore dashboard loads

```
Browser opens Spore URL
  → HTTP GET / → serves static SPA
  → WebSocket connects → Spore subscribes to pattern '*'
  → REST GET /api/hyphae?limit=50 → initial event load
  → REST GET /api/colonies → agent list
  → REST GET /api/tags → live tag cloud
  → WebSocket pushes new events in real-time
  → User clicks tag → filters view → can inject signal
```

## 6. Spore Dashboard

**S.P.O.R.E. — System for Presenting Organism Runtime Events**

### 6.1 UI Layout

```
┌────────────────────────────────────────────────────────────┐
│  🍄 SPORE                                    [filter] [⚡] │
├────────────┬───────────────────────────────────────────────┤
│            │                                               │
│  COLONIES  │         NETWORK VIEW                          │
│  (agents)  │                                               │
│            │    ┌─────┐                                    │
│  🧠 mycel  │    │scout├──── finding                       │
│  🔍 scout  │    └──┬──┘                                    │
│  🛡️ army   │       │         ┌──────┐                     │
│  🔨 dyna   │       └─────────│builder├──── complete       │
│            │                 └──────┘                      │
│────────────│                                               │
│  TAGS      │───────────────────────────────────────────────│
│  #mission  │                                               │
│  #lesson   │    EVENT TIMELINE                             │
│  #pain-pt  │    14:50 ✅ scout complete                    │
│  #shortcut │    14:48 🔨 builder: created README.md        │
│            │    14:47 🛡️ protector: sweep passed            │
│────────────│    14:46 🌱 mycelium: spawned scout            │
│            │                                               │
│  💬 INJECT │                                               │
│  [type here and the mycelium routes it...]                │
└────────────┴───────────────────────────────────────────────┘
```

### 6.2 Interaction Model

| Action | What happens |
|---|---|
| Click agent | Show agent detail: role, status, current task, event history |
| Click tag | Filter timeline to that tag. Show tag stats. |
| Click event | Show event detail: content, metadata, thread (hypha_ref chain) |
| Type in inject box | Creates signal. Mycelium routes it. |
| Hover over event | Tooltip with source, timestamp, metadata preview |

### 6.3 Tech Stack

| Component | Technology | Why |
|---|---|---|
| HTTP server | Node.js `http` module | Zero deps, always available |
| WebSocket | `ws` package (npm) | Only external dep, pure JS |
| Frontend | Vanilla HTML/CSS/JS | No build step, no framework, loads instantly |
| Visualisation | SVG or Canvas | Renders network graph natively |
| Auth | Simple token (shared secret from OpenClaw config) | No OAuth complexity for v1 |

**Total dependencies: 1 npm package (`ws`)**

## 7. SRE Plan

### 7.1 Reliability

| Risk | Mitigation |
|---|---|
| SQLite lock contention (WAL + concurrent writes) | LCM already handles `busy_timeout`. Hyphae writes are append-only (low contention). |
| WebSocket connection drops | Auto-reconnect with exponential backoff. Event replay from last-seen ID on reconnect. |
| Event bus overwhelming agents | Backpressure: events are fire-and-forget for emitters. Subscribers buffer or drop (with alert). |
| Spore server crash | Non-critical — agents keep working. Spore reconnects on restart. Events persist in SQLite. |
| Database corruption | SQLite WAL is crash-safe. Backup via `.backup` command (not file copy). |

### 7.2 Observability

**Metrics to track:**

| Metric | Source | Alert threshold |
|---|---|---|
| Events/sec | `SELECT COUNT(*) FROM hyphae WHERE created_at > datetime('now', '-1 minute')` | > 100/sec |
| Active agents | `SELECT COUNT(*) FROM colonies WHERE status = 'active'` | > 20 (resource concern) |
| Signal queue depth | `SELECT COUNT(*) FROM signals WHERE status = 'pending'` | > 10 (routing stalled) |
| WebSocket connections | Spore server internal counter | > 50 |
| DB size | `SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()` | > 1GB |
| Event lag | Time between event creation and WebSocket delivery | > 5 seconds |

**Health endpoint:** `GET /health` returns JSON with above metrics.

**Logging:** All hyphae events ARE the log. Query `hyphae WHERE type = 'health:*'` for health history.

### 7.3 Disaster Recovery

**Scenario: Server crash, LCM database corrupted**

1. Restore from backup: `sqlite3 lcm_backup.db ".backup lcm.db"`
2. Or replay: all events are in `hyphae` table (append-only, WAL-safe)
3. Agents re-register: on next activity, agents emit `agent:spawn` events
4. Spore reconnects: auto-reconnect, replays from last-seen event ID

**Scenario: Spore dashboard down**

- Non-critical. Agents continue working.
- Events still written to SQLite.
- Spore catches up on restart via replay.

**Scenario: WebSocket overwhelmed**

- Server-side: drop oldest events from buffer (with `event:dropped` alert)
- Client-side: reconnect, request replay from last-seen ID

### 7.4 Performance

**Target:** < 10ms event write, < 50ms WebSocket delivery, < 200ms dashboard render.

**Scaling path:**
- v1 (now): SQLite + Node.js, single process. Good for < 1000 events/min, < 20 concurrent agents.
- v2 (if needed): Separate event store (e.g. SQLite replicas, or NATS). Not needed now.
- v3 (if needed): Distributed agents with network transport. Grant-funded future.

**Optimisations:**
- ULID for time-ordered inserts (SQLite B-tree friendly)
- Indexes on `type`, `tag`, `source`, `created_at`
- WebSocket binary frames for large payloads (JSON, not binary)
- Pagination on REST endpoints (cursor-based on ULID)

### 7.5 Retention & Cleanup

| Policy | Implementation |
|---|---|
| Events kept online | 30 days (configurable) |
| Archive old events | `SELECT * FROM hyphae WHERE created_at < datetime('now', '-30 days')` → export to JSON, then delete |
| Signals kept | 90 days (important for audit) |
| Colonies | Prune `dead` agents after 7 days |
| Vacuum | Weekly `VACUUM` to reclaim space |

## 8. Security

### 8.1 Spore Dashboard Auth

- **Shared secret:** Token from OpenClaw config (or generated on first run)
- **Cookie or header:** `Authorization: Bearer <token>` on WebSocket and REST
- **No public access:** Spore binds to `localhost` by default
- **Remote access:** Via SSH tunnel or OpenClaw's existing auth (if gateway proxy)

### 8.2 Data Sensitivity

- Event content may contain sensitive info (file paths, partial code, user messages)
- **Redaction filter:** Optional regex-based redaction on event content before storage
- **Access control:** Only authenticated users can read events or inject signals
- **No encryption at rest for v1** (SQLite file permissions: `0600`, owned by OpenClaw user)

### 8.3 Injection Safety

- Signals are routed by the Mycelium (LLM), not directly executed
- Jon's input is treated as context, not as a command to execute
- Agents receive signals as additional context in their next prompt — they decide what to do

## 9. Plugin Structure

```
~/.openclaw/extensions/mycelium-claw/
├── index.ts                     ← OpenClaw extension entry point
├── openclaw.plugin.json         ← Extension metadata
├── package.json                 ← Dependencies (only: ws)
├── LICENSE                      ← MIT (forked from lossless-claw)
├── README.md
│
├── src/
│   ├── plugin/
│   │   └── index.ts             ← Plugin registration (tools, hooks, routes)
│   ├── db/
│   │   ├── connection.ts        ← SQLite connection (extends LCM's)
│   │   ├── migration.ts         ← Schema migrations (adds our 4 tables)
│   │   └── hyphae.ts            ← Event CRUD operations
│   ├── tools/
│   │   ├── hypha-emit.ts        ← Tool: agent emits event
│   │   ├── signal-inject.ts     ← Tool: Jon injects signal
│   │   ├── mycorrhiza-subscribe.ts ← Tool: subscribe to patterns
│   │   ├── colony-register.ts   ← Tool: register/update agent
│   │   └── hypha-query.ts       ← Tool: query events (for agents)
│   ├── bus/
│   │   ├── router.ts            ← Pattern matching, subscriber notification
│   │   └── backpressure.ts      ← Buffer management, drop policy
│   ├── spore/
│   │   ├── server.ts            ← HTTP + WebSocket server
│   │   ├── api.ts               ← REST endpoints
│   │   ├── ws.ts                ← WebSocket handler
│   │   └── static/              ← Frontend files
│   │       ├── index.html
│   │       ├── app.js
│   │       └── style.css
│   └── sre/
│       ├── health.ts            ← Health checks, metrics
│       ├── retention.ts         ← Cleanup, archival
│       └── backup.ts            ← SQLite backup
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── SRE.md
```

## 10. Implementation Roadmap

### Phase 1: Foundation (this week)
- [ ] Fork `Martian-Engineering/lossless-claw` → `SmartEst74/mycelium-claw`
- [ ] Add 4-table migration to `src/db/migration.ts`
- [ ] Implement `hyphae.ts` (event CRUD)
- [ ] Implement `hypha-emit.ts` tool (agent emits event)
- [ ] Implement `signal-inject.ts` tool (Jon injects signal)
- [ ] Test: agent emits event, event stored, queryable

### Phase 2: Routing (week 2)
- [ ] Implement `router.ts` (pattern matching, subscriber notification)
- [ ] Implement `mycorrhiza-subscribe.ts` tool
- [ ] Implement `colony-register.ts` tool
- [ ] Implement `hypha-query.ts` tool
- [ ] Test: agent subscribes to pattern, matching event triggers notification

### Phase 3: Spore Dashboard (week 2-3)
- [ ] Build HTTP server with auth
- [ ] Build WebSocket handler with replay
- [ ] Build REST API endpoints
- [ ] Build frontend (HTML/CSS/JS)
- [ ] Network visualisation (SVG graph)
- [ ] Tag cloud + filtering
- [ ] Signal injection UI
- [ ] Test: open Spore, see events live, inject signal, see it route

### Phase 4: SRE (week 3)
- [ ] Health endpoint
- [ ] Retention/cleanup job
- [ ] Backup automation
- [ ] Logging integration
- [ ] Performance benchmarks

### Phase 5: Integration (week 3-4)
- [ ] Wire into AGENTS.md colony protocol
- [ ] Update SOUL.md with Spore as the observability layer
- [ ] Update MEMORY.md architecture section
- [ ] Documentation
- [ ] Grant pitch update: "Colony with visible nervous system"

## 11. What This Enables

**For Jon:**
- See what the colony is doing RIGHT NOW (not after the fact)
- Inject context without interrupting (the mycelium routes)
- Click into any work area and drill down
- Watch the memory pipeline (LCM → QMD) working in real time

**For the grant:**
- Visual proof that colonial memory compounds
- Interactive demo of agent coordination
- "Here's a living mycelium network. Watch it learn."
- Demonstrates SRE maturity (observability, recovery, health)

**For the colony:**
- Agents coordinate through events, not polling
- Knowledge flows in real-time (hyphal network)
- Failures visible immediately (health events)
- History replayable (event sourcing)

---

*Plan version: 1.0 — 2026-03-26*
*Status: PLANNING — review before implementation*
*Dependencies: LCM (MIT, forkable), ws (npm), Node.js (required by OpenClaw)*
