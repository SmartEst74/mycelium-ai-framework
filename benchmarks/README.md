# Colonial Memory Benchmark

## Purpose

Demonstrate measurable advantage of colonial memory (shared, persistent, multi-agent) over solo agents (isolated, ephemeral, no memory).

## How to Run

```bash
cd benchmarks/
python3 run_benchmark.py --mode solo --missions 5
python3 run_benchmark.py --mode colonial --missions 5
python3 run_benchmark.py --compare
```

## Benchmark Tasks

Each benchmark runs a series of "missions" — tasks that require research, evaluation, and reporting.

### Task: "Find the best free AI model for code generation"

**Why this task?**
- Requires web research (searching, reading docs)
- Requires evaluation (comparing multiple options)
- Requires reasoning (judging quality, trade-offs)
- Has a known correct answer (community consensus exists)
- Can be objectively scored

### What We Measure

| Metric | Description | Why It Matters |
|--------|-------------|----------------|
| **Time** | Wall-clock seconds to complete | Speed advantage |
| **Quality** | Accuracy of final recommendation | Effectiveness |
| **Redundancy** | % of work duplicated from previous missions | Memory efficiency |
| **Lessons Used** | # of prior lessons applied in later missions | Compound learning |
| **Token Cost** | Total tokens consumed across all missions | Economic efficiency |

### Expected Outcomes

```
Solo Mode (no memory):
  Mission 1: 180s, 50k tokens, discovers 5 models, picks best
  Mission 2: 175s, 48k tokens, discovers same 5 models, picks best (DUPLICATE)
  Mission 3: 182s, 51k tokens, discovers same 5 models, picks best (DUPLICATE)
  Mission 4: 178s, 49k tokens, discovers same 5 models, picks best (DUPLICATE)
  Mission 5: 180s, 50k tokens, discovers same 5 models, picks best (DUPLICATE)
  Total: 895s, 248k tokens, 0 lessons learned

Colonial Mode (shared memory):
  Mission 1: 180s, 50k tokens, scouts discover 5 models, writes lessons
  Mission 2: 90s, 20k tokens, reads prior lessons, verifies model, picks best
  Mission 3: 85s, 18k tokens, reads prior lessons, checks for updates
  Mission 4: 80s, 15k tokens, reads prior lessons, confirms recommendation
  Mission 5: 75s, 12k tokens, nearly instant — all knowledge exists
  Total: 510s, 115k tokens, 15+ lessons learned

Advantage: 43% faster, 54% fewer tokens, infinite lesson retention
```

## Architecture

```
benchmarks/
├── README.md              # This file
├── run_benchmark.py       # Main benchmark runner
├── tasks/
│   └── code_model_eval.py # Task: evaluate code generation models
├── modes/
│   ├── solo.py            # Solo agent (no memory)
│   └── colonial.py        # Colonial agent (shared memory)
├── metrics/
│   └── reporter.py        # Collects and reports metrics
└── results/               # Benchmark results (git-ignored)
    ├── solo/
    └── colonial/
```

## Grant Application Data

After running benchmarks, results are saved to `results/` as JSON.
Use `run_benchmark.py --compare` to generate a comparison table
suitable for grant applications.

---

*Mycelium AI Framework — Colonial Memory Benchmark*
*Version: 1.0 — 2026-03-25*
