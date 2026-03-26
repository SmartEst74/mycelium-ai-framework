# Contributing

## Principles

1. **Read shared memory first.** Every agent and contributor must search QMD before starting work.
2. **Write discoveries back.** If you learn something useful, tag it and write it to memory.
3. **Free models only.** Never introduce a dependency on paid APIs without approval.
4. **Prove improvements.** Any performance claim needs a benchmark result.

## Process

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Ensure `scripts/validate-write.sh` passes for any new files
5. Run benchmarks if you changed memory or orchestration logic
6. Submit a PR

## Code Standards

- Python: follow PEP 8
- All scripts must be executable with `python3` (no exotic dependencies)
- Documentation in markdown, one idea per file

## Memory Tags

When writing to the colony memory, use these tags:

| Tag | Meaning |
|-----|---------|
| #lesson | Reusable knowledge, patterns, decisions |
| #pain-point | Blockers, gotchas, friction |
| #shortcut | Efficiency patterns, better defaults |
| #green-leaf | Revenue opportunities, leads |
| #benchmark | Performance test results |
| #durable-state | System configuration, architecture |
| #mission | Active work in progress |
| #mission-complete | Finished deliverable |
