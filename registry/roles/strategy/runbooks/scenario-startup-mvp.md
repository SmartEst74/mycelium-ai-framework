# 🚀 Runbook: Startup MVP Build

> **Mode**: NEXUS-Sprint | **Duration**: 4-6 weeks | **Agents**: 18-22

---

## Scenario

You're building a startup MVP — a new product that needs to validate product-market fit quickly. Speed matters, but so does quality. You need to go from idea to live product with real users in 4-6 weeks.

## Agent Roster

### Core Team (Always Active)
| Agent | Role |
|-------|------|
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Spec-to-task conversion |
| Sprint Prioritizer | Backlog management |
| UX Architect | Technical foundation |
| Frontend Developer | UI implementation |
| Backend Architect | API and database |
| DevOps Automator | CI/CD and deployment |
| Evidence Collector | QA for every task |
| Reality Checker | Final quality gate |

### Growth Team (Activated Week 3+)
| Agent | Role |
|-------|------|
| Growth Hacker | Acquisition strategy |
| Content Creator | Launch content |
| Social Media Strategist | Social campaign |

### Support Team (As Needed)
| Agent | Role |
|-------|------|
| Brand Guardian | Brand identity |
| Analytics Reporter | Metrics and dashboards |
| Rapid Prototyper | Quick validation experiments |
| AI Engineer | If product includes AI features |
| Performance Benchmarker | Load testing before launch |
| Infrastructure Maintainer | Production setup |

## Week-by-Week Execution

### Week 1: Discovery + Architecture (Phase 0 + Phase 1 compressed)

```
Day 1-2: Compressed Discovery
├── Trend Researcher → Quick competitive scan (1 day, not full report)
├── UX Architect → Wireframe key user flows
└── Senior Project Manager → Convert spec to task list

Day 3-4: Architecture
├── UX Architect → CSS design system + component architecture
├── Backend Architect → System architecture + database schema
├── Brand Guardian → Quick brand foundation (colors, typography, voice)
└── Sprint Prioritizer → RICE-scored backlog + sprint plan

Day 5: Foundation Setup
├── DevOps Automator → CI/CD pipeline + environments
├── Frontend Developer → Project scaffolding
├── Backend Architect → Database + API scaffold
└── Quality Gate: Architecture Package approved
```

### Week 2-3: Core Build (Phase 2 + Phase 3)

```
Sprint 1 (Week 2):
├── Agents Orchestrator manages Dev↔QA loop
├── Frontend Developer → Core UI (auth, main views, navigation)
├── Backend Architect → Core API (auth, CRUD, business logic)
├── Evidence Collector → QA every completed task
├── AI Engineer → ML features if applicable
└── Sprint Review at end of week

Sprint 2 (Week 3):
├── Continue Dev↔QA loop for remaining features
├── Growth Hacker → Design viral mechanics + referral system
├── Content Creator → Begin launch content creation
├── Analytics Reporter → Set up tracking and dashboards
└── Sprint Review at end of week
```

### Week 4: Polish + Hardening (Phase 4)

```
Day 1-2: Quality Sprint
├── Evidence Collector → Full screenshot suite
├── Performance Benchmarker → Load testing
├── Frontend Developer → Fix QA issues
├── Backend Architect → Fix API issues
└── Brand Guardian → Brand consistency audit

Day 3-4: Reality Check
├── Reality Checker → Final integration testing
├── Infrastructure Maintainer → Production readiness
└── DevOps Automator → Production deployment prep

Day 5: Gate Decision
├── Reality Checker verdict
├── IF NEEDS WORK: Quick fix cycle (2-3 days)
├── IF READY: Proceed to launch
└── Executive Summary Generator → Stakeholder briefing
```

### Week 5-6: Launch + Growth (Phase 5)

```
Week 5: Launch
├── DevOps Automator → Production deployment
├── Growth Hacker → Activate acquisition channels
├── Content Creator → Publish launch content
├── Social Media Strategist → Cross-platform campaign
├── Analytics Reporter → Real-time monitoring
└── Support Responder → User support active

Week 6: Optimize
├── Growth Hacker → Analyze and optimize channels
├── Feedback Synthesizer → Collect early user feedback
├── Experiment Tracker → Launch A/B tests
├── Analytics Reporter → Week 1 analysis
└── Sprint Prioritizer → Plan iteration sprint
```

## Key Decisions

| Decision Point | When | Who Decides |
|---------------|------|-------------|
| Go/No-Go on concept | End of Day 2 | Studio Producer |
| Architecture approval | End of Day 4 | Senior Project Manager |
| Feature scope for MVP | Sprint planning | Sprint Prioritizer |
| Production readiness | Week 4 Day 5 | Reality Checker |
| Launch timing | After Reality Checker READY | Studio Producer |

## Success Criteria

| Metric | Target |
|--------|--------|
| Time to live product | ≤ 6 weeks |
| Core features complete | 100% of MVP scope |
| First users onboarded | Within 48 hours of launch |
| System uptime | > 99% in first week |
| User feedback collected | ≥ 50 responses in first 2 weeks |

## Common Pitfalls & Mitigations

| Pitfall | Mitigation |
|---------|-----------|
| Scope creep during build | Sprint Prioritizer enforces MoSCoW — "Won't" means won't |
| Over-engineering for scale | Rapid Prototyper mindset — validate first, scale later |
| Skipping QA for speed | Evidence Collector runs on EVERY task — no exceptions |
| Launching without monitoring | Infrastructure Maintainer sets up monitoring in Week 1 |
| No feedback mechanism | Analytics + feedback collection built into Sprint 1 |

## 💾 Memory Integration

**Recall:** Before starting work, search QMD memory for relevant context. Use:
```bash
exec: qmd search "query" --json -n 5
```
Search for tags: `#lesson`, `#pain-point`, `#green-leaf`, `#benchmark`, `#durable-state`, and project-specific terms. Review `#pain-point` to avoid repeating mistakes. Use `memory_get` to read specific memory files after locating them.

**Remember:** After completing tasks, write outcomes to memory. Use the proper tags:
- `#lesson` — reusable knowledge, patterns, decisions
- `#pain-point` — blockers, gotchas, friction
- `#shortcut` — efficiency patterns, better defaults
- `#green-leaf` — revenue opportunities, leads, monetization
- `#benchmark` — model tests, tool assessments, performance metrics
- `#durable-state` — system state, configuration, architecture decisions
- `#mission` — active work in progress
- `#mission-complete` — finished deliverables

**Handoffs:** When passing work to another agent, write a summary tagged with the receiving agent's role (e.g., `#frontend-developer`) and include a clear `#mission-complete` with the deliverable location. This enables automatic recall without manual copy-paste.

**Rollback:** When QA fails, search memory for the last known-good state (`#durable-state`, prior `#mission-complete`) and revert to it. Capture the failure with a `#pain-point` to prevent recurrence.

**Stream Protocol:** Keep the colony consciousness stream updated. Use:
```bash
exec: bash scripts/stream-write.sh "<your-agent-id>" "<thought>"
```
at major milestones: task start, decisions, blockers, completions. This broadcasts progress to the colony.

**Deliverable Format:** Always produce structured outputs (docs, code, specs). Remember them with tags: `<project>`, `<your-role>`, `<topic>` so future agents can find them.

**Tool Access:** You have access to `memory_get` and can run `qmd search`. Use `scripts/memory-vector write` to push urgent updates to the colony (bypass file buffering).
