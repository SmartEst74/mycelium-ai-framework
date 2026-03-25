# Enforcement Layer — Mycelium AI Framework

## Why Enforcement?

The Mycelium architecture defines clear chain-of-command and file placement rules. But agents can still violate them — nothing stops an agent from writing project docs to `memory/` or doing leaf work itself instead of delegating.

The enforcement layer makes violations **physically difficult**, not just verbally discouraged.

## Three Layers of Enforcement

### 1. Pre-Commit Git Hook (`scripts/pre-commit`)

**What it does:** Blocks git commits that violate file placement rules.

**What it catches:**
- Project docs (plan, design, SRE, architecture, spec, RFC, roadmap) committed to `memory/`
- Sub-agent modifications to `MEMORY.md` (detected via commit message patterns)

**How to install:**
```bash
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Bypass (emergency only):**
```bash
git commit --no-verify
```

### 2. Write Validator (`scripts/validate-write.sh`)

**What it does:** Advisory check agents should call before writing files.

**Usage:**
```bash
./scripts/validate-write.sh <file-path> [content-type] [workspace-root]
```

**Content types:**
- `lesson` — goes in `memory/YYYY-MM-DD.md` with `#lesson` tag
- `mission` — goes in `memory/YYYY-MM-DD.md` with `#mission` tag
- `project-doc` — goes in project repo, NOT in `memory/`
- `temp` — goes in `/tmp` or `workspace/tmp`, NOT in `memory/`
- `config` — goes in config directory
- `code` — goes in appropriate code directory
- `unknown` — default checks

**Example in agent workflow:**
```bash
# Before writing an SRE plan:
./scripts/validate-write.sh memory/sre-plan.md project-doc
# Output: ❌ REJECTED: Project docs belong in the project repo...

# Correct path:
./scripts/validate-write.sh /project/repo/docs/SRE-PLAN.md project-doc
# Output: ✅ Write approved: /project/repo/docs/SRE-PLAN.md
```

### 3. Hard Rules in `config/rules.yaml`

**What it does:** Documents the enforcement rules as machine-parseable YAML so agents can reference them programmatically.

**Section:** `rules.enforcement`

**Sub-sections:**
- `chain_of_command` — who does what, who doesn't do what
- `file_placement` — where each type of content goes
- `enforcement_hooks` — references to the git hook and validation script

## File Placement Matrix

| Content Type | Correct Location | WRONG Location |
|---|---|---|
| SRE plans | `<project>/docs/SRE-PLAN.md` | `memory/sre-plan.md` |
| Architecture docs | `<project>/docs/ARCHITECTURE.md` | `memory/architecture.md` |
| Design specs | `<project>/docs/specs/` | `memory/specs/` |
| Lessons learned | `memory/YYYY-MM-DD.md` + `#lesson` tag | Project repo |
| Pain points | `memory/YYYY-MM-DD.md` + `#pain-point` tag | Anywhere without tag |
| Active missions | `memory/YYYY-MM-DD.md` + `#mission` tag | Anywhere without tag |
| Revenue opportunities | `memory/YYYY-MM-DD.md` + `#green-leaf` tag | Anywhere without tag |
| Model benchmarks | `memory/YYYY-MM-DD.md` + `#benchmark` tag | Anywhere without tag |
| MEMORY.md | Main agent (Mycelium) only | Sub-agents |
| Temp/research files | `/tmp` or `workspace/tmp` | `memory/` |

## Chain of Command Enforcement

```
Human (Jon)
    ↓ task
Mycelium (main agent)
    ↓ delegation
Scout          General          Sentinel
(research)     (execute)        (QA/review)
    ↓              ↓                ↓
    └──────────────┴────────────────┘
              Shared Memory
```

**Hard rules:**
- Mycelium THINKS, PLANS, ORCHESTRATES. It does NOT execute leaf work.
- Scouts EXPLORE, RESEARCH, INVESTIGATE. They do NOT execute.
- Generals EXECUTE, BUILD, DEPLOY. They do NOT plan strategy.
- Sentinels REVIEW, AUDIT, QA. They do NOT execute.
- All agents write to shared memory. No side-channels.

## When a Violation is Caught

1. **Pre-commit hook:** Read the error, move the file, re-stage, re-commit
2. **Write validator:** Read the error, write to the correct location
3. **If unsure:** Ask Jon. Don't guess.

## Installation for New Colonies

```bash
# 1. Clone the framework
git clone https://github.com/SmartEst74/mycelium-ai-framework.git

# 2. Copy enforcement scripts to your workspace
cp scripts/validate-write.sh <workspace>/scripts/
cp scripts/pre-commit <workspace>/.git/hooks/pre-commit
chmod +x <workspace>/.git/hooks/pre-commit

# 3. Rules are in config/rules.yaml — review and customize
# 4. Update SOUL.md with the enforcement rules from config/rules.yaml
```
