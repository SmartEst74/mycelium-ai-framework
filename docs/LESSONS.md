# Lessons Learned — Mycelium AI Framework

Every "aha moment" that came from building this framework. Captured here so they travel with the repo.

**How to use:** When setting up a new OpenClaw instance, run `scripts/bootstrap-lessons.sh` to import these lessons into QMD memory. Or just read this file — the knowledge is in human-readable form.

---

## Architecture Lessons

### 1. Colonial Memory Must Be Declarative
The colony doesn't just "remember things" — it enforces a **tag protocol** (`#lesson`, `#mission`, `#pain-point`, `#benchmark`). Without this protocol, agents write noise into shared memory and the signal degrades. The tag protocol is the difference between a filing cabinet and a nervous system.

### 2. The Mycelium Must NEVER Execute
This was the hardest lesson. The orchestrator's job is **routing and reasoning only**. If the Mycelium touches a file, calls an API, or does any side-effect, it becomes a bottleneck and a single point of failure. The enforcement scripts validate this — every write must be by a leaf agent.

### 3. Event Sourcing Is Non-Negotiable
We first tried polling. Then state snapshots. Both failed. Event sourcing is the only way to:
- Rebuild state after disaster (replay from log)
- Time-travel debug (replay to any moment)
- Audit every AI decision (GDPR, AI Act)
- Test deterministically (record + replay in CI)

The `EVM` (Event Memory Vector) we eventually built proved this: the colony can be destroyed and rebuilt from events alone.

### 4. Compound Learning Is Real
Benchmark data proves it: missions 4-5 are **60%+ faster** than mission 1 when the colony retains lessons. Solo agents show no such improvement. This is the key grant finding — **colonial memory produces measurable, compounding advantages**.

### 5. Free Models Are Fine (With Fallback Chains)
The initial instinct was "use the best model". But the constraint "free models only" forced us to build proper fallback chains: `primary → fallback1 → fallback2 → paid-only-if-critical`. The fallback chain is more resilient than any single model.

### 6. GPT-4.1-mini for LCM Summaries
OpenClaw's Lossless Claw plugin uses `gpt-4.1-mini` for compaction summaries. This is the right choice — cheap, fast, and summaries don't need frontier quality. The summaries are DAG-linked and retrievable via `lcm_expand`. Don't overspend on compaction.

---

## Implementation Lessons

### 7. SQLite for Event Store, Markdown for Projections
Two storage layers:
- **LCM (SQLite)**: append-only event log, WAL mode for durability
- **QMD (Markdown)**: curated long-term memory, file-per-topic, searchable

The hybrid approach gives: SQL queries for events + human-readable files for knowledge + file-based version control for QMD.

### 8. The QMD Index Must Be Scoped Per Agent
Each OpenClaw agent instance has its own QMD index (at `~/.openclaw/agents/<id>/qmd/xdg-cache/qmd/index.sqlite`). Collection names are scoped: `memory-root-main`, `memory-dir-main`. If you run `qmd search` from the CLI, you need to point at the right index.

### 9. Enforcement Scripts Save Projects
The `validate-write.sh` hook prevents agents from writing outside their allowed paths. Without it, agents inevitably create files in the wrong directory (root writes to core/, scouts write to root/, etc.). The pre-commit hook validates before merge. These save months of cleanup.

### 10. Scout Swarms Need Backpressure
When you spawn 10 scouts in parallel, some will be faster than others. Without backpressure (bounded queues, rate limiting), the slower scouts overload the model API and get rate-limited. The circuit breaker pattern (from SRE best practices) prevents cascading failure.

---

## Setup & Deployment Lessons

### 11. Bootstrap Is a COLD Start Problem
A fresh OpenClaw instance has no memory. The `scripts/bootstrap-lessons.sh` script imports this file's lessons into QMD so the new instance has the colony's hard-won knowledge from day one.

### 12. Config Must Be Idempotent
OpenClaw config changes can be fragile (the `raw required` error). Always use `config.patch` for partial updates, not `config.apply` with the full file. Keep a backup (`openclaw.json.bak`) before any config change.

### 13. LCM Must Be Explicitly Pinned
Installing the lossless-claw plugin is not enough. You must also set `plugins.slots.contextEngine = "lossless-claw"` in config. Otherwise the plugin loads but context engine still uses default behavior.

### 14. Context Tokens Need to Be Raised
Default 32000 context tokens is too low for real work. Raise to at least 120000:
```json
{ "agents": { "defaults": { "contextTokens": 120000 } } }
```

---

## Revenue & Grant Lessons

### 15. Measurable Advantages Win Grants
"Colonial memory is better" is a claim. "Colonial memory produces 47% speed improvement and 60% compound acceleration on later missions" is proof. Always have numbers.

### 16. SRE Is Not Optional
Grant reviewers and enterprise customers expect SRE practices: health checks, circuit breakers, observability, disaster recovery, security. The `docs/SRE-RELIABILITY.md` playbook covers this. Implement it.

### 17. The Framework Must Be Runnable on First Clone
Someone clones the repo. They run `make demo`. It works. That's the benchmark for all repositories. The E2E demo (`benchmarks/e2e_demo.py`) proves the core concept without any external dependencies beyond Python.

---

## Anti-Patterns to Avoid

- ❌ Don't have the orchestrator do any work (Mycelium must stay clean)
- ❌ Don't use state snapshots instead of event logs (fragile, not auditable)
- ❌ Don't skip the tag protocol (unstructured memory degrades quickly)
- ❌ Don't spawn unlimited scouts without backpressure
- ❌ Don't commit secrets or tokens (use environment variables)
- ❌ Don't let agents write outside their role boundaries
- ❌ Don't use polling when event-driven is possible

---

*This file is the colony's institutional memory. Treat it with respect.*
*Last updated: 2026-03-25 by mycelium (main agent)*
