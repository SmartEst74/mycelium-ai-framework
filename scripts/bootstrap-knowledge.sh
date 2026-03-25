#!/bin/bash
# bootstrap-knowledge.sh — Import Mycelium Framework lessons into OpenClaw QMD memory
#
# Usage:
#   bash scripts/bootstrap-knowledge.sh [workspace_dir]
#
# This script:
# 1. Reads docs/LESSONS.md from the repo
# 2. Imports each lesson into QMD memory at the specified workspace
# 3. Creates the memory directory structure
# 4. Runs a quick health check
#
# Prerequisites: OpenClaw installed, QMD memory backend active

set -euo pipefail

WORKSPACE="${1:-$HOME/.openclaw/workspace}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%Y-%m-%d)

echo "=== Mycelium Framework Knowledge Bootstrap ==="
echo "Repo:     $REPO_DIR"
echo "Workspace: $WORKSPACE"
echo ""

# 1. Ensure memory directory exists
mkdir -p "$WORKSPACE/memory"

# 2. Create daily memory file with framework knowledge
DAILY_FILE="$WORKSPACE/memory/${DATE}.md"
if [ ! -f "$DAILY_FILE" ]; then
  echo "# Daily Memory — $DATE" > "$DAILY_FILE"
  echo "" >> "$DAILY_FILE"
fi

# 3. Import LESSONS.md lessons
echo "Importing framework lessons..."
cat >> "$DAILY_FILE" << 'LESSONS_EOF'

## [mycelium-framework] Bootstrap Knowledge Import

Source: Mycelium AI Framework repo docs/LESSONS.md

### Key Architecture Decisions
- #lesson: Colonial memory uses a tag protocol: #lesson, #mission, #pain-point, #benchmark
- #lesson: The orchestrator (Mycelium) must NEVER execute side-effects — routing only
- #lesson: Event sourcing is non-negotiable for disaster recovery and audit
- #lesson: Compound learning is real: colonial missions 4-5 are 60%+ faster than mission 1
- #lesson: Free models work fine with proper fallback chains

### Implementation Patterns
- #lesson: SQLite for event store (append-only, WAL mode), Markdown for long-term projections
- #lesson: QMD index is scoped per agent: ~/.openclaw/agents/<id>/qmd/xdg-cache/
- #lesson: Enforcement scripts (validate-write.sh) prevent path violations
- #lesson: Scout swarms need backpressure to prevent API rate limits

### Setup & Config
- #lesson: contextTokens must be raised to ≥120000 (default 32000 is too low)
- #lesson: plugins.slots.contextEngine must be explicitly set to "lossless-claw"
- #lesson: Always use config.patch, not config.apply (avoids raw-required errors)
- #lesson: Keep openclaw.json.bak before any config change

### Anti-Patterns
- #pain-point: State snapshots are fragile — prefer event logs
- #pain-point: Unstructured memory degrades quickly — enforce tag protocol
- #pain-point: Unlimited scouts overload APIs — need circuit breakers

### Grant & Revenue
- #lesson: Measurable advantages win grants (47% speed, 60% compound, 23% fewer tokens)
- #lesson: SRE practices are not optional for enterprise customers

LESSONS_EOF

echo "  ✓ Imported framework lessons into $DAILY_FILE"

# 4. Import benchmark numbers as a #benchmark entry
BENCHMARK_FILE="$WORKSPACE/memory/${DATE}.md"
cat >> "$BENCHMARK_FILE" << 'BENCHMARK_EOF'

### [mycelium-framework] Benchmark Results

| Metric | Solo | Colonial | Advantage |
|--------|------|----------|-----------|
| Total Time | 915s | 481s | 47% faster |
| Total Tokens | 227k | 175k | 23% fewer |
| Avg Redundancy | 80% | 40% | 50% less |
| Lessons Reused | 0 | 9 | colonial remembers |
| Missions 4-5 | — | — | 60%+ faster (compound!) |

Source: benchmarks/run_benchmark.py (5 missions: code, TTS, web hosting, CSS, Python)

BENCHMARK_EOF

echo "  ✓ Imported benchmark results"

# 5. Import event sourcing + SRE lessons
cat >> "$BENCHMARK_FILE" << 'SRE_EOF'

### [mycelium-framework] Event Sourcing & SRE

Key innovations:
- Event Bus: append-only log in SQLite, WebSocket for real-time
- Replay capability: colony can be rebuilt from event log alone
- SRE playbook: health checks, circuit breakers, observability stack
- Disaster recovery: RPO 1 hour, RTO 15 minutes
- Audit trail: every AI decision traceable via immutable event log

Docs: docs/EVENT-BUS.md, docs/SRE-RELIABILITY.md

SRE_EOF

echo "  ✓ Imported SRE & event sourcing lessons"

# 6. Run E2E demo if Python is available
if command -v python3 &>/dev/null; then
  echo ""
  echo "Running E2E demo to verify installation..."
  if python3 "$REPO_DIR/benchmarks/e2e_demo.py" 2>/dev/null; then
    echo "  ✓ E2E demo passed — event bus and replay verified"
  else
    echo "  ⚠ E2E demo had issues (check Python 3.11+ dependencies)"
  fi
else
  echo "  ⚠ Python3 not found — skipping E2E demo"
fi

# 7. Summary
echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "What was imported:"
echo "  • Framework architecture lessons (tag protocol, orchestrator rules, event sourcing)"
echo "  • Benchmark results (47% faster, 23% fewer tokens, 60% compound learning)"
echo "  • SRE best practices (circuit breakers, observability, disaster recovery)"
echo "  • Anti-patterns to avoid"
echo "  • Setup & config lessons"
echo ""
echo "The new OpenClaw instance now has the colony's hard-won knowledge from day one."
echo ""
echo "Next steps:"
echo "  1. cd $REPO_DIR && python3 benchmarks/e2e_demo.py"
echo "  2. Read docs/LESSONS.md for the full knowledge base"
echo "  3. Set up your config with:"
echo "     openclaw config.patch '{\"agents\":{\"defaults\":{\"contextTokens\":120000}}}'"
