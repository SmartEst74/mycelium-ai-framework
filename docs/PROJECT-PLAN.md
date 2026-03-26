# Mycelium Claw — Project Plan

> The colony's nervous system. Living, learning, visible.

## Overview

Mycelium Claw extends the Lossless Claw Memory (LCM) plugin with a mycelial event bus and a living visualisation dashboard called **Spore**. Agents emit events as they work, the mycelium routes signals between them, and Jon can see and steer the colony in real time.

**Architecture:** See [MYCELIUM-CLAW-PLAN.md](./MYCELIUM-CLAW-PLAN.md) for the full architecture document.

**Repo:** `SmartEst74/mycelium-claw` (forked from `Martian-Engineering/lossless-claw`, MIT)

**Tech stack:** TypeScript, Node.js, SQLite (WAL), WebSocket (`ws` package), zero build step frontend (vanilla HTML/CSS/JS)

**Dependencies:** 1 npm package (`ws`). Everything else is Node.js stdlib.

---

## Sprint Overview

| Sprint | Focus | Duration | Deliverable |
|--------|-------|----------|-------------|
| Sprint 1 | Foundation — schema, tools, event bus | Days 1–2 | Agents can emit/query events. Database schema live. |
| Sprint 2 | Routing — subscriptions, signals, router | Days 3–4 | Pub/sub working. Jon can inject signals. |
| Sprint 3 | Spore — server, API, WebSocket | Days 5–6 | Live HTTP/WS server. Events stream in real-time. |
| Sprint 4 | Spore — frontend dashboard | Days 7–9 | Browser-based colony visualisation. |
| Sprint 5 | SRE — health, retention, security | Days 10–11 | Production-ready observability. |
| Sprint 6 | Integration — docs, testing, polish | Days 12–14 | Full documentation. Integration tests. Grant-ready demo. |

---

## Sprint 1: Foundation (Days 1–2)

### Day 1 — Schema & Event Store

**Goal:** The database can store and retrieve events. That's it.

| Issue | Title | Estimate |
|-------|-------|----------|
| #1 | Fork LCM to mycelium-claw, configure repo | 2h |
| #2 | Design & implement schema: 4 tables (hyphae, signals, mycorrhizae, colonies) | 3h |
| #3 | Implement HyphaeStore — event CRUD with prepared statements | 3h |

**Acceptance criteria:**
- [ ] Repo `SmartEst74/mycelium-claw` exists with CI configured
- [ ] 4 tables created on plugin load via migration
- [ ] Can insert/query events by type, tag, source, thread
- [ ] Unit tests pass for HyphaeStore operations

### Day 2 — Core Tools

**Goal:** Agents can emit events and query the network.

| Issue | Title | Estimate |
|-------|-------|----------|
| #4 | Implement hypha:emit tool — agent emits event | 2h |
| #5 | Implement hypha:query tool — agent queries events | 2h |
| #6 | Register tools in plugin index | 1h |
| #7 | Integration test: emit → store → query cycle | 2h |

**Acceptance criteria:**
- [ ] Agent can call `hypha:emit` with type, tag, content, metadata
- [ ] Agent can call `hypha:query` by mode (recent, tag, source, type, thread, tags, missions, count)
- [ ] Both tools appear in OpenClaw tool list
- [ ] Integration test validates full emit→query round-trip

---

## Sprint 2: Routing (Days 3–4)

### Day 3 — Signals & Subscriptions

**Goal:** Jon can talk to the colony. Agents can subscribe to patterns.

| Issue | Title | Estimate |
|-------|-------|----------|
| #8 | Implement signal:inject tool — Jon injects signal | 2h |
| #9 | Implement mycorrhiza:subscribe tool — agent subscribes to pattern | 2h |
| #10 | Implement colony:register tool — agent registry | 2h |
| #11 | Build Router — pattern matching & subscriber notification | 3h |

**Acceptance criteria:**
- [ ] Jon can inject a signal with content and context
- [ ] Agent can subscribe to patterns: `*`, `mission:*`, exact tags
- [ ] Router matches emitted events against subscriptions
- [ ] Matching subscribers receive notification

### Day 4 — Signal Routing & Colony Lifecycle

**Goal:** Signals flow through the network. Agents register and update status.

| Issue | Title | Estimate |
|-------|-------|----------|
| #12 | Implement signal routing — Mycelium routes signals to agents | 3h |
| #13 | Wire colony lifecycle — dormant → growing → active → retracting → dead | 2h |
| #14 | Agent integration: emit events on spawn/task/complete | 2h |
| #15 | Integration test: signal injection → routing → delivery | 2h |

**Acceptance criteria:**
- [ ] Signal injected by Jon gets routed to the right agent
- [ ] Agent registration/update through colony:register
- [ ] Agents emit lifecycle events automatically
- [ ] Full signal flow tested end-to-end

---

## Sprint 3: Spore Server (Days 5–6)

### Day 5 — HTTP Server & WebSocket

**Goal:** Spore is a live server. Events stream to connected clients.

| Issue | Title | Estimate |
|-------|-------|----------|
| #16 | Spore HTTP server — static file serving + token auth | 3h |
| #17 | WebSocket handler — connection, auth, live event stream | 3h |
| #18 | REST API: GET /api/hyphae (paginated query) | 2h |

**Acceptance criteria:**
- [ ] Spore binds to localhost with token authentication
- [ ] WebSocket connections receive events in real-time
- [ ] REST endpoint returns paginated events
- [ ] Auth rejects unauthenticated requests

### Day 6 — REST API & Reconnect

**Goal:** Full API surface. Clients reconnect cleanly.

| Issue | Title | Estimate |
|-------|-------|----------|
| #19 | REST API: GET /api/colonies, /api/tags, /api/signals | 2h |
| #20 | WebSocket reconnect + event replay from last-seen ID | 3h |
| #21 | REST API: POST /api/signals — inject signal from Spore UI | 2h |
| #22 | GET /health endpoint — JSON metrics | 1h |

**Acceptance criteria:**
- [ ] All REST endpoints functional
- [ ] WebSocket client reconnects and replays missed events
- [ ] Signal injection from dashboard works
- [ ] Health endpoint returns system metrics

---

## Sprint 4: Spore Frontend (Days 7–9)

### Day 7 — Dashboard Shell & Event Timeline

**Goal:** Browser loads, shows live event timeline.

| Issue | Title | Estimate |
|-------|-------|----------|
| #23 | Spore HTML shell — layout, dark theme, responsive grid | 2h |
| #24 | Event timeline component — live list with auto-scroll | 3h |
| #25 | Event filtering by type, tag, source | 2h |

**Acceptance criteria:**
- [ ] Dashboard loads in browser, connects via WebSocket
- [ ] Events appear in real-time timeline
- [ ] Filtering works by type, tag, and source

### Day 8 — Tag Cloud & Network Visualisation

**Goal:** Visual overview of what the colony is doing.

| Issue | Title | Estimate |
|-------|-------|----------|
| #26 | Tag cloud component — dynamic tags with counts | 2h |
| #27 | Agent panel — colonies list with status indicators | 2h |
| #28 | Network graph — SVG visualisation of agent relationships | 3h |

**Acceptance criteria:**
- [ ] Tag cloud updates in real-time as events arrive
- [ ] Agent panel shows all registered colonies with status
- [ ] SVG network graph shows agent→event relationships

### Day 9 — Signal Injection & Detail Views

**Goal:** Jon can interact with the colony through the dashboard.

| Issue | Title | Estimate |
|-------|-------|----------|
| #29 | Signal injection UI — input box that routes to mycelium | 2h |
| #30 | Event detail view — click event to see metadata, thread | 2h |
| #31 | Agent detail view — click agent to see history, current task | 2h |
| #32 | Theme polish & responsive layout | 1h |

**Acceptance criteria:**
- [ ] Jon types in inject box, signal is created and routed
- [ ] Clicking an event shows full detail with thread chain
- [ ] Clicking an agent shows their event history
- [ ] Dashboard works on mobile/tablet

---

## Sprint 5: SRE & Security (Days 10–11)

### Day 10 — Health & Observability

**Goal:** System is observable. You can see what's happening and why.

| Issue | Title | Estimate |
|-------|-------|----------|
| #33 | Metrics collection — events/sec, active agents, signal queue | 3h |
| #34 | Alert thresholds — configurable alerts for anomalous conditions | 2h |
| #35 | Retention/cleanup — auto-archive events older than 30 days | 2h |
| #36 | SQLite backup — automated backup via .backup command | 1h |

**Acceptance criteria:**
- [ ] Health endpoint returns all key metrics
- [ ] Alerts trigger when thresholds are crossed
- [ ] Old events are archived and cleaned up
- [ ] Backup runs on schedule

### Day 11 — Security Hardening

**Goal:** System is secure. No unauthorised access. Data is protected.

| Issue | Title | Estimate |
|-------|-------|----------|
| #37 | Token authentication — shared secret for Spore access | 2h |
| #38 | Content redaction filter — optional regex-based redaction | 2h |
| #39 | Rate limiting — prevent event flooding | 2h |
| #40 | Security audit — review all auth, data handling, injection points | 2h |

**Acceptance criteria:**
- [ ] All Spore endpoints require valid token
- [ ] Sensitive content can be redacted
- [ ] Rate limiting prevents abuse
- [ ] Security audit passes with no critical findings

---

## Sprint 6: Integration & Polish (Days 12–14)

### Day 12 — Testing

**Goal:** Comprehensive test coverage. No regressions.

| Issue | Title | Estimate |
|-------|-------|----------|
| #41 | Unit tests — all store operations, router, pattern matching | 3h |
| #42 | Integration tests — full agent lifecycle with events | 3h |
| #43 | E2E tests — Spore dashboard flow (browser automation) | 2h |

**Acceptance criteria:**
- [ ] Unit test coverage > 80%
- [ ] Integration tests cover all major flows
- [ ] E2E tests validate dashboard works end-to-end

### Day 13 — Documentation

**Goal:** Documentation that impresses an SRE expert.

| Issue | Title | Estimate |
|-------|-------|----------|
| #44 | API documentation — complete REST + WebSocket + tool docs | 3h |
| #45 | SRE runbook — operations manual for Mycelium Claw | 2h |
| #46 | Architecture documentation — diagrams, decisions, trade-offs | 2h |
| #47 | Contributing guide — how to extend the event bus | 1h |

**Acceptance criteria:**
- [ ] API docs cover all endpoints and tools with examples
- [ ] SRE runbook covers deployment, monitoring, incident response
- [ ] Architecture docs include decision records
- [ ] Contributing guide enables external contributors

### Day 14 — Polish & Grant Demo

**Goal:** Production-ready. Grant demo prepared.

| Issue | Title | Estimate |
|-------|-------|----------|
| #48 | Performance benchmarks — event throughput, latency, memory | 2h |
| #49 | Demo preparation — scripted demo of colony coordination | 2h |
| #50 | Grant pitch update — "colony with visible nervous system" | 2h |
| #51 | Final review — SRE checklist, code quality, documentation completeness | 2h |

**Acceptance criteria:**
- [ ] Benchmarks meet targets (< 10ms write, < 50ms WS delivery, < 200ms render)
- [ ] Demo script runs without errors
- [ ] Grant pitch updated with Spore evidence
- [ ] All SRE checklist items green

---

## Architecture Decision Records

### ADR-001: SQLite over external message bus
**Context:** We need event storage and pub/sub for agent coordination.
**Decision:** Use the existing LCM SQLite database with WAL mode.
**Rationale:** Zero external dependencies. SQLite is crash-safe, already proven by LCM. WAL mode handles concurrent reads/writes. For our scale (< 1000 events/min), this is more than sufficient.
**Consequences:** No horizontal scaling beyond single process. Acceptable for v1. Migration path to NATS/Redis documented if needed.

### ADR-002: Dynamic tags over static taxonomy
**Context:** Agents need to categorise events. Should we enforce a fixed set of tags?
**Decision:** Tags are free-text strings that emerge from usage.
**Rationale:** A rigid taxonomy would break every time a new agent type or event category is introduced. Dynamic tags let the colony self-organise. We can materialise popular tags into views later.
**Consequences:** No schema enforcement on tags. Tag collisions possible (rare). Tag cloud provides visibility.

### ADR-003: Vanilla frontend over framework
**Context:** Spore needs a web dashboard.
**Decision:** Pure HTML/CSS/JS. No React, no build step, no bundler.
**Rationale:** Zero dependencies beyond `ws`. Loads instantly. No build pipeline to maintain. The dashboard is simple enough that a framework adds complexity without value.
**Consequences:** More manual DOM manipulation. Acceptable for the interaction model (timeline, filters, graphs).

### ADR-004: Token auth over OAuth
**Context:** Spore needs authentication.
**Decision:** Shared secret token. Bearer token on HTTP/WS.
**Rationale:** Single-user system (Jon). OAuth adds complexity for zero benefit. Token is generated on first run, stored in OpenClaw config.
**Consequences:** No multi-user support. No permission granularity. Acceptable for v1. Migration path to OAuth documented if needed.

### ADR-005: Extend LCM rather than fork
**Context:** We need event bus features that LCM doesn't provide.
**Decision:** Extend LCM with new tables and tools. Same plugin, same database.
**Rationale:** LCM's migration system supports additive changes. Forking would create a maintenance burden. Extending means we inherit LCM's reliability and OpenClaw integration.
**Consequences:** Mycelium Claw is coupled to LCM's release cycle. Mitigated by upstream tracking in our fork.

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| SQLite lock contention under load | Medium | Low | WAL mode + `busy_timeout`. Hyphae writes are append-only. |
| WebSocket connection storms | Medium | Medium | Connection limiting + rate limiting on auth. |
| LCM upstream breaking changes | High | Medium | Fork pinned to known-good commit. Track upstream with review. |
| Spore frontend complexity creep | Medium | High | Strict scope: vanilla JS, no framework, v1 features only. |
| Grant timeline pressure | High | Medium | Daily milestones. MVP by day 11. Polish by day 14. |
| Security vulnerability in signal injection | High | Low | Signals routed by LLM (not executed). Input validation. Rate limiting. |

---

## Definition of Done

For each issue to be considered done:

1. **Code complete** — all functionality implemented
2. **Tests pass** — unit + integration tests green
3. **Documentation** — relevant docs updated
4. **No regressions** — existing tests still pass
5. **Reviewed** — code quality meets SRE standards
6. **Deployed** — pushed to GitHub, ready for demo

---

## Team

| Role | Responsibility |
|------|---------------|
| **Mycelium** (Jon) | Strategic direction, approval, grant pitch |
| **Dynamic Ant** (AI agent) | Implementation, testing, documentation |
| **Scout** (AI agent) | Research, architecture review, risk assessment |
| **SRE mindset** | Every decision filtered through reliability, observability, recoverability |

---

## Communication

- **Daily standup:** Progress against daily milestones
- **Blocker escalation:** Same-day, no waiting
- **Demo:** End of each sprint (days 2, 4, 6, 9, 11, 14)
- **Retrospective:** After sprint 6, what worked, what to improve

---

*Plan version: 1.0 — 2026-03-26*
*Owner: Jon Smart*
*Status: APPROVED — ready for issue creation*
