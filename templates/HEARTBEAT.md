# HEARTBEAT.md

## On each heartbeat

1. Check runtime state for stalled or high-value work.
2. Check token / usage posture — reduce waste if something is burning spend.
3. Search memory for `#mission` — any missions stalled > 15 min? Re-dispatch or escalate.
4. Search memory for `#pain-point` — any new blockers? Investigate or escalate.
5. If no missions in progress, scan for the next highest-value work and dispatch.

## Army Ant Health Sweep

Spawn Army Ants in parallel for periodic protection:

```
Army Ant 1: Disk + storage health
  → Check disk usage, warn if > 80%
  → Track warning until resolved

Army Ant 2: Security scan
  → Check permissions, configs, access control
  → Report any changes since last sweep

Army Ant 3: Code quality
  → Run linters, check for warnings/errors
  → Track each warning until fixed

Army Ant 4: Service health
  → Check APIs, gateway, cron status
  → Report degraded services immediately
```

Army Ants write threats to memory. Warnings stay OPEN until verified clean.

## Rules

- Do not invent urgency
- Do not pester the human with routine status
- Use memory + live state before asking questions
- If the system is healthy and work exists, move one concrete item instead of waiting
- Prefer the next concrete money-making step over more planning
- Keep the loop lean and cost-aware
