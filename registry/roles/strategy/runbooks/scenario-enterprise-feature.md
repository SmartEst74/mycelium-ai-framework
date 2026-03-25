# 🏢 Runbook: Enterprise Feature Development

> **Mode**: NEXUS-Sprint | **Duration**: 6-12 weeks | **Agents**: 20-30

---

## Scenario

You're adding a major feature to an existing enterprise product. Compliance, security, and quality gates are non-negotiable. Multiple stakeholders need alignment. The feature must integrate seamlessly with existing systems.

## Agent Roster

### Core Team
| Agent | Role |
|-------|------|
| Agents Orchestrator | Pipeline controller |
| Project Shepherd | Cross-functional coordination |
| Senior Project Manager | Spec-to-task conversion |
| Sprint Prioritizer | Backlog management |
| UX Architect | Technical foundation |
| UX Researcher | User validation |
| UI Designer | Component design |
| Frontend Developer | UI implementation |
| Backend Architect | API and system integration |
| Senior Developer | Complex implementation |
| DevOps Automator | CI/CD and deployment |
| Evidence Collector | Visual QA |
| API Tester | Endpoint validation |
| Reality Checker | Final quality gate |
| Performance Benchmarker | Load testing |

### Compliance & Governance
| Agent | Role |
|-------|------|
| Legal Compliance Checker | Regulatory compliance |
| Brand Guardian | Brand consistency |
| Finance Tracker | Budget tracking |
| Executive Summary Generator | Stakeholder reporting |

### Quality Assurance
| Agent | Role |
|-------|------|
| Test Results Analyzer | Quality metrics |
| Workflow Optimizer | Process improvement |
| Experiment Tracker | A/B testing |

## Execution Plan

### Phase 1: Requirements & Architecture (Week 1-2)

```
Week 1: Stakeholder Alignment
├── Project Shepherd → Stakeholder analysis + communication plan
├── UX Researcher → User research on feature need
├── Legal Compliance Checker → Compliance requirements scan
├── Senior Project Manager → Spec-to-task conversion
└── Finance Tracker → Budget framework

Week 2: Technical Architecture
├── UX Architect → UX foundation + component architecture
├── Backend Architect → System architecture + integration plan
├── UI Designer → Component design + design system updates
├── Sprint Prioritizer → RICE-scored backlog
├── Brand Guardian → Brand impact assessment
└── Quality Gate: Architecture Review (Project Shepherd + Reality Checker)
```

### Phase 2: Foundation (Week 3)

```
├── DevOps Automator → Feature branch pipeline + feature flags
├── Frontend Developer → Component scaffolding
├── Backend Architect → API scaffold + database migrations
├── Infrastructure Maintainer → Staging environment setup
└── Quality Gate: Foundation verified (Evidence Collector)
```

### Phase 3: Build (Week 4-9)

```
Sprint 1-3 (Week 4-9):
├── Agents Orchestrator → Dev↔QA loop management
├── Frontend Developer → UI implementation (task by task)
├── Backend Architect → API implementation (task by task)
├── Senior Developer → Complex/premium features
├── Evidence Collector → QA every task (screenshots)
├── API Tester → Endpoint validation every API task
├── Experiment Tracker → A/B test setup for key features
│
├── Bi-weekly:
│   ├── Project Shepherd → Stakeholder status update
│   ├── Executive Summary Generator → Executive briefing
│   └── Finance Tracker → Budget tracking
│
└── Sprint Reviews with stakeholder demos
```

### Phase 4: Hardening (Week 10-11)

```
Week 10: Evidence Collection
├── Evidence Collector → Full screenshot suite
├── API Tester → Complete regression suite
├── Performance Benchmarker → Load test at 10x traffic
├── Legal Compliance Checker → Final compliance audit
├── Test Results Analyzer → Quality metrics dashboard
└── Infrastructure Maintainer → Production readiness

Week 11: Final Judgment
├── Reality Checker → Integration testing (default: NEEDS WORK)
├── Fix cycle if needed (2-3 days)
├── Re-verification
└── Executive Summary Generator → Go/No-Go recommendation
```

### Phase 5: Rollout (Week 12)

```
├── DevOps Automator → Canary deployment (5% → 25% → 100%)
├── Infrastructure Maintainer → Real-time monitoring
├── Analytics Reporter → Feature adoption tracking
├── Support Responder → User support for new feature
├── Feedback Synthesizer → Early feedback collection
└── Executive Summary Generator → Launch report
```

## Stakeholder Communication Cadence

| Audience | Frequency | Agent | Format |
|----------|-----------|-------|--------|
| Executive sponsors | Bi-weekly | Executive Summary Generator | SCQA summary (≤500 words) |
| Product team | Weekly | Project Shepherd | Status report |
| Engineering team | Daily | Agents Orchestrator | Pipeline status |
| Compliance team | Monthly | Legal Compliance Checker | Compliance status |
| Finance | Monthly | Finance Tracker | Budget report |

## Quality Requirements

| Requirement | Threshold | Verification |
|-------------|-----------|-------------|
| Code coverage | > 80% | Test Results Analyzer |
| API response time | P95 < 200ms | Performance Benchmarker |
| Accessibility | WCAG 2.1 AA | Evidence Collector |
| Security | Zero critical vulnerabilities | Legal Compliance Checker |
| Brand consistency | 95%+ adherence | Brand Guardian |
| Spec compliance | 100% | Reality Checker |
| Load handling | 10x current traffic | Performance Benchmarker |

## Risk Management

| Risk | Probability | Impact | Mitigation | Owner |
|------|------------|--------|-----------|-------|
| Integration complexity | High | High | Early integration testing, API Tester in every sprint | Backend Architect |
| Scope creep | Medium | High | Sprint Prioritizer enforces MoSCoW, Project Shepherd manages changes | Sprint Prioritizer |
| Compliance issues | Medium | Critical | Legal Compliance Checker involved from Day 1 | Legal Compliance Checker |
| Performance regression | Medium | High | Performance Benchmarker tests every sprint | Performance Benchmarker |
| Stakeholder misalignment | Low | High | Bi-weekly executive briefings, Project Shepherd coordination | Project Shepherd |

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
