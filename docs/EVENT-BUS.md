# Event Bus & Replay — Rhizomorph's Nervous System

## Why an Event Bus?

The Rhizomorph is not just a shared memory database. It's the colony's nervous system — every event flows through it in real-time, and every agent subscribes to relevant events.

**Without event bus:**
- Agents poll memory (latency, wasted cycles)
- No ordering guarantees
- No replay capability (can't rebuild state)
- Distributed systems patterns impossible

**With event bus:**
- Instant propagation (milliseconds)
- Ordered event stream (causality preserved)
- Full replay for disaster recovery
- Can rebuild colony state from scratch
- Enables CQRS, event sourcing, projections

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      EVENT BUS (WebSocket)                   │
│  • Ordered stream of all Rhizomorph writes                 │
│  • Every write is an event: { type, payload, timestamp }   │
│  • Agents subscribe to tags: #mission, #benchmark, etc.    │
│  • Event persistence: append-only log in LCM               │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ▼                      ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │   LCM (SQLite)   │    │   QMD (Markdown)     │
    │  Append log      │    │  Projections         │
    │  Compaction      │    │  (derived views)     │
    └──────────────────┘    └──────────────────────┘
```

## Event Structure

```json
{
  "id": "evt_abc123",           // unique event ID (UUID or ULID)
  "type": "memory.write",       // event type
  "timestamp": "2026-03-25T20:22:00.000Z",
  "source": "scout-tool",       // agent that emitted
  "payload": {
    "tag": "#benchmark",
    "content": "mimo-v2-omni is 40% faster than previous model",
    "metadata": { ... }
  },
  "version": 1                 // schema version for migrations
}
```

## Event Types

| Type | Description | Consumers |
|------|-------------|-----------|
| `memory.write` | Write to Rhizomorph (LCM→QMD pathway) | All agents (filter by tag) |
| `mission.start` | New mission assigned | Mycelium, Army Ant |
| `mission.complete` | Mission finished with results | Mycelium, Scouts |
| `scout.spawn` | Scout created | Monitoring |
| `scout.done` | Scout completed | Mycelium |
| `agent.error` | Agent failure with context | Mycelium, SRE |
| `health.check` | Periodic health ping | SRE, dashboard |

## Subscription Model

Agents subscribe to tags (like pub/sub):

```javascript
bus.subscribe('#mission', (event) => {
  // React to new mission events
});

bus.subscribe('#benchmark', (event) => {
  // Update model performance database
});

bus.subscribe('#pain-point', (event) => {
  // Mycelium prioritizes blocking issues
});
```

**Filtering**: subscriptions are pattern-matched, efficient (index by tag).

## Replay & Recovery

### Disaster Scenario

Server crash, LCM database corrupted, QMD files lost.

### Recovery Procedure

1. **Replay event log** from earliest available event (or from backup snapshot)
2. **Rebuild projections**:
   - LCM state (current session context)
   - QMD files (curated long-term memory)
3. **Restart agents** — they subscribe and catch up automatically
4. **Colony returns to pre-crash state** — no manual intervention

### Checkpointing

To avoid replaying millions of events:
- **Periodic snapshots** (every 1000 events or hourly)
- **Snapshot includes**:
  - LCM database state
  - QMD file set
  - Last event ID processed
- **Recovery**: load latest snapshot + replay events after that

## Implementation Sketch (Python)

```python
class EventBus:
    def __init__(self, lcm_db_path):
        self.db = sqlite3.connect(lcm_db_path)
        self.subscribers = defaultdict(list)
        self.sequence = 0
    
    def emit(self, event_type, payload, source=None):
        """Write event to log and notify subscribers"""
        event = {
            "id": ulid(),
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat()+"Z",
            "source": source,
            "payload": payload,
            "sequence": self.sequence,
            "version": 1
        }
        self.db.execute("INSERT INTO events VALUES (?,?,?,?,?)",
                       (event["id"], event["sequence"], event["type"],
                        json.dumps(event), datetime.utcnow()))
        self.db.commit()
        self.sequence += 1
        self._notify(event)
    
    def subscribe(self, pattern, callback):
        """Subscribe to events matching pattern (e.g. '#benchmark')"""
        self.subscribers[pattern].append(callback)
    
    def replay(self, from_sequence=0):
        """Replay all events from given sequence"""
        cursor = self.db.execute("SELECT event FROM events WHERE sequence >= ?",
                                (from_sequence,))
        for row in cursor:
            event = json.loads(row[0])
            self._notify(event)
```

## SRE Benefits

### Reliability
- **State reconstruction**: colony can be rebuilt from event log alone
- **Audit trail**: every decision, every write, traceable
- **Debugging**: replay events to reproduce issues

### Observability
- **Event metrics**: events/sec, subscriber latency, backlog
- **Health dashboards**: event bus lag, subscriber health
- **Alerts**: event backlog growing, subscribers failing

### Testing
- **Deterministic tests**: record event sequence, replay to verify behavior
- **Property-based testing**: simulate failures, verify recovery
- **Chaos engineering**: kill agents, replay events to rebuild state

## Production Considerations

- **Event log persistence**: WAL mode in SQLite, fsync on every write (or batch with durability trade-off)
- **Retention policy**: archive old logs to S3/Blob storage after 30 days
- **Backpressure**: slow subscribers buffer events (bounded queue), drop oldest if overwhelmed (with alert)
- **Security**: event payloads may contain sensitive data — encrypt at rest, TLS in transit
- **Schema evolution**: version field allows gradual migration; old events still readable

## Why This Matters for the Grant

Event sourcing + replay is a **proven pattern** in distributed systems (Kafka, EventStore). Applying it to AI agent colonies is novel:

1. **Recovery**: if an agent makes a bad decision, replay events up to that point, fix, continue
2. **Simulation**: run "what-if" scenarios by replaying with modified agents
3. **Compliance**: full audit trail of AI decisions (GDPR, AI Act)
4. **Debuggability**: reproduce and fix issues with exact event sequence

This is **expert-level architecture** that reviewers expect from serious systems.

---

*Related: LCM, QMD, Rhizomorph, SRE practices*
*Version: 1.0 — 2026-03-25*
