# Self-Improvement Protocol

Inspired by [MiniMax's autonomous self-improvement](https://huggingface.co/blog/MiniMaxAI/self-improvement) — where models improve through 100+ rounds of self-evaluation without human intervention.

## The Loop

Every task follows: RUN → EVALUATE → RECORD → IMPROVE

```
┌─────────────────────────────────────┐
│            RUN TASK                 │
│   Worker executes one focused task  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         SELF-EVALUATE               │
│  Score 1-5 on each dimension:      │
│  • Accuracy (correct output?)      │
│  • Efficiency (shortest path?)     │
│  • Completeness (everything done?) │
│  • Reusability (learned something?)│
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│          RECORD TO MEMORY           │
│  • Score >= 4 all → #lesson        │
│  • Score < 3 any → #pain-point     │
│  • Efficiency < 4 → #shortcut      │
│  • Always: #mission-complete       │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│           IMPROVE                   │
│  Scout reads accumulated scores    │
│  Spots patterns across sessions    │
│  Reports to Mycelium               │
│  Mycelium updates:                 │
│  • Model assignments               │
│  • Agent behaviour                 │
│  • Default approaches              │
└─────────────┬───────────────────────┘
              │
              └──────── RUN AGAIN (compounding)
```

## What Gets Tracked

| Metric | Per Model | Per Task Type | Aggregated |
|--------|-----------|---------------|------------|
| Token cost | ✅ | ✅ | Scout reads |
| Correctness | ✅ | ✅ | Scout reads |
| Speed | ✅ | ✅ | Scout reads |
| Reusable patterns | — | ✅ | All agents read |

## How It Compounds

1. **Session 1**: Agent tries model A for code gen. Scores 4/5. Records to memory.
2. **Session 5**: Agent tries model B for code gen. Scores 5/5, uses 30% fewer tokens. Records to memory.
3. **Session 10**: Benchmark Scout reads accumulated scores. Reports: "Model B is better for code gen."
4. **Action**: Mycelium updates SOUL.md. Model B is now the default for code gen.
5. **Session 20+**: Every agent starts from Model B. No more wasted tokens on Model A.

The colony learns. Every agent benefits from every other agent's experience.

## Scout Benchmark Protocol

When the Benchmark Scout runs (periodic or triggered):

1. Check provider catalog for new free models
2. Pick 3-5 standardised benchmark tasks:
   - Code generation (write a function, score correctness)
   - Reasoning (logic puzzle, score accuracy)
   - Research (summarise an article, score completeness)
   - Tool use (call a function, score format)
3. Run each task on each candidate model
4. Score: correctness, token cost, speed
5. Report: "Model X scored [scores] vs Model Y scored [scores] for [task type]"
6. Mycelium needs 3+ data points before changing assignments

## Model Assignment Rules

- **Free only**. No spending money on models until revenue exists.
- **Never downgrade** without proof that the new model is worse.
- **Upgrade with evidence**: 3+ benchmark data points confirming improvement.
- **Assignments live in SOUL.md**: every agent reads them at startup.
- **Fallback chain maintained**: if primary model fails, fall back gracefully.

## Example Self-Eval Entry in Memory

```
[dynamic-code] #lesson — Task: build API endpoint. Score: A=5 E=4 C=5 R=5.
Pattern: Always check HTTP method before parsing body. Saves 2-3 retries per task.
Model: mimo-v2-omni:free, 342 tokens, ~8s.
```

```
[dynamic-deploy] #pain-point — Task: deploy to server. Score: A=2 E=2 C=3 R=2.
Failed: SSH key not in known_hosts, wasted 3 retries.
Fix: Always `ssh-keyscan` before first deploy attempt.
```

These entries compound. Next time an agent deploys, it reads the #pain-point and does `ssh-keyscan` first. The colony remembers what the individual forgot.
