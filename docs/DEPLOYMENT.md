# Deployment Guide — Mycelium on OpenClaw

Get a Mycelium colony running on your OpenClaw instance in under 10 minutes.

## Prerequisites

- [OpenClaw](https://docs.openclaw.ai) installed and running
- Node.js 22+ (for benchmarks)
- At least one free model provider configured (kilocode, github-copilot, etc.)
- Git (optional, for version control)

## Step 1: Clone & Copy Templates

```bash
# Clone the framework
git clone https://github.com/SmartEst74/mycelium-ai-framework.git
cd mycelium-ai-framework

# Copy templates to your OpenClaw workspace
cp templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp templates/HEARTBEAT.md ~/.openclaw/workspace/HEARTBEAT.md
```

## Step 2: Configure Models

Edit `~/.openclaw/workspace/SOUL.md` and replace the model placeholders:

| Placeholder | What to put |
|-------------|-------------|
| `MODEL_BRAIN` | Your best reasoning model (e.g., `kilocode/xiaomi/mimo-v2-pro:free`) |
| `MODEL_SCOUT` | Your cheapest fast model (e.g., `stepfun/step-3.5-flash:free`) |
| `MODEL_WORKER` | Your vision+tools model (e.g., `kilocode/xiaomi/mimo-v2-omni:free`) |
| `FALLBACK_1` | First fallback (e.g., `zhipuai/glm-4.5-air:free`) |
| `FALLBACK_2` | Last resort (e.g., `github-copilot/gpt-5-mini`) |

**Rule**: Free only. You make money, not spend it.

## Step 3: Create Memory Directory

```bash
mkdir -p ~/.openclaw/workspace/memory
```

## Step 4: Set Up Crons

Import the example cron jobs:

```bash
# Heartbeat cycle (every 2 hours)
# Use the OpenClaw cron tool or import the JSON:
cat templates/cron/mycelium-cycle.json

# Army Ant health sweep (every hour)
cat templates/cron/army-ant-checks.json
```

Or set them up manually via OpenClaw's cron tool.

## Step 5: Verify

```bash
# Check OpenClaw status
openclaw status

# Test memory search
# (from an OpenClaw session)
# memory_search("recent lessons")

# Test a Scout spawn
# sessions_spawn({ model: "MODEL_SCOUT", task: "SCOUT. Test: check if kilocode has new free models. Report findings." })
```

## Step 6: First Mission

Send your first mission to the Mycelium:

```
Build a simple landing page for my project.
```

Watch the colony work:
1. Mycelium decomposes into tasks (design, build, deploy)
2. Scouts research if needed
3. Dynamic Ants execute each task
4. Army Ants scan the result
5. Everything writes to memory

## File Structure

After deployment, your workspace should look like:

```
~/.openclaw/workspace/
├── SOUL.md          ← Colony personality + rules + model assignments
├── AGENTS.md        ← Operating protocol + self-improvement loop
├── HEARTBEAT.md     ← Health checks + Army Ant sweep instructions
├── MEMORY.md        ← Global rules and state (auto-updated by main agent)
├── IDENTITY.md      ← Who the agent is
├── USER.md          ← Who the human is
└── memory/          ← Colony memory (lessons, pain points, missions)
    ├── YYYY-MM-DD.md
    └── ...
```

## Customisation

### Adding Army Ant Domains

Edit `HEARTBEAT.md` and add a new Army Ant:

```markdown
Army Ant 5: Database health
  → Check query performance, connection pools
  → Report slow queries or connection exhaustion
```

### Adding Scout Types

Edit the Scout section in your template to add new research domains:

```markdown
| 🔍 Compliance Scout | Regulatory changes, GDPR updates | `#pain-point` |
```

### Changing Heartbeat Frequency

Edit the cron schedule in `mycelium-cycle.json`:
- Every 2 hours: `"everyMs": 7200000` (default)
- Every 30 minutes: `"everyMs": 1800000`
- Every 6 hours: `"everyMs": 21600000`

## Troubleshooting

### Memory search returns empty
- Check that `memory/` directory exists
- Verify QMD backend is active: `openclaw status` should show `[memory-core]`
- Run a memory write test first

### Army Ant warnings not tracked
- Verify the Army Ant writes `#warning` tags to memory
- Check that subsequent sweeps read previous `#warning` entries
- Use `memory_search("#warning")` to see active warnings

### Model not available
- Check provider config: `openclaw status`
- Verify the model string matches your provider format
- Try the fallback chain manually

### Crons not firing
- Check cron status: use the OpenClaw cron tool
- Verify `sessionTarget` is set correctly (`"isolated"` for independent runs)
- Check OpenClaw gateway is running
