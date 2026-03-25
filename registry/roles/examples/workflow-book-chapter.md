# Workflow Example: Book Chapter Development

> A focused single-agent workflow for turning rough source material into a strategic first-person chapter draft with explicit revision loops.

## When to Use This

Use this workflow when an author has voice notes, fragments, or strategic notes, but not yet a clean chapter draft. The goal is not generic ghostwriting. The goal is to produce a chapter that strengthens category positioning, preserves the author's voice, and exposes open editorial decisions clearly.

## Agent Used

| Agent | Role |
|-------|------|
| Book Co-Author | Converts source material into a versioned chapter draft with editorial notes and next-step questions |

## Example Activation

```text
Activate Book Co-Author.

Book goal: Build authority around practical AI adoption for Mittelstand companies.
Target audience: Owners and operational leaders of 20-200 person businesses.
Chapter topic: Why most AI projects fail before implementation starts.
Desired draft maturity: First substantial draft.

Raw material:
- Voice memo: "The real failure happens in expectation setting, not tooling."
- Notes: Leaders buy software before defining the operational bottleneck.
- Story fragment: We nearly rolled out the wrong automation in a cabinetmaking workflow because the actual problem was quoting delays, not production throughput.
- Positioning angle: Practical realism over hype.

Produce:
1. Chapter objective and strategic role in the book
2. Any clarification questions you need
3. Chapter 2 - Version 1 - ready for review
4. Editorial notes on assumptions and proof gaps
5. Specific next-step revision requests
```

## Expected Output Shape

The Book Co-Author should respond in five parts:

1. `Target Outcome`
2. `Chapter Draft`
3. `Editorial Notes`
4. `Feedback Loop`
5. `Next Step`

## Quality Bar

- The draft stays in first-person voice
- The chapter has one clear promise and internal logic
- Claims are tied to source material or flagged as assumptions
- Generic motivational language is removed
- The output ends with explicit revision questions, not a vague handoff

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
