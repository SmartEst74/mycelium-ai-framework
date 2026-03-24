# Hyphae — Skill Harness

Each hypha is a skill that plugs into the mycelium network.

## What Is a Hypha?

In biology, hyphae are the individual filamentous threads that form the mycelium network. In this framework, each hypha is a single skill/capability that connects to the core.

## Supported Skill Formats

| Format | Description | Discovery |
|--------|-------------|-----------|
| Rust native | Compiled Rust skill, fastest | Auto-discovered from `hyphae/` |
| OpenClaw SKILL.md | Standard skill format | Read SKILL.md manifest |
| MCP server | Wrapped as hypha | MCP adapter discovers tools |
| CLI tool | Wrapped as hypha | Subprocess adapter |

## Hypha Manifest

Each hypha declares its capabilities:

```yaml
name: my-skill
version: "0.1.0"
type: rust | openclaw | mcp | cli
capabilities:
  - read_file
  - write_file
  - execute_command
model_hint: mimo-v2-omni:free  # optional: which model works best
bounds:
  - filesystem
  - network
```

## Creating a Hypha

### Rust Native
```
hyphae/
  my-skill/
    Cargo.toml
    src/
      lib.rs
    hypha.toml
```

### OpenClaw Skill
```
hyphae/
  my-skill/
    SKILL.md
    references/
    scripts/
```

### MCP Server
```
hyphae/
  my-skill/
    hypha.toml          # declares MCP connection
    mcp-server/         # the MCP server code
```

## Rules

1. Every hypha reads Rhizomorph before starting work
2. Every hypha writes discoveries back to Rhizomorph
3. Hyphae are pluggable — swap when better arrives
4. Never locked in to one skill format
5. Mycelium discovers hyphae at runtime
