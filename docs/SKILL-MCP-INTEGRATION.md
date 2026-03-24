# Hyphae Integration Architecture

## The Rule: Skills Are the Integration Layer

Mycelium does NOT rebuild skills. It orchestrates them.

Skills (Hyphae) are the primary integration layer. NOT MCP, NOT custom protocols. Skills.

If someone has an MCP server — wrap it as a hypha. If a better protocol than Skills emerges — swap it in. Never locked in.

## Hyphae Types

### Rust Native Hyphae
- Fastest, compiled
- Full access to Rhizomorph (read/write memory)
- Auto-discovered from `hyphae/` directory
- Each has `Cargo.toml` + `hypha.toml` manifest

### OpenClaw Skills (SKILL.md)
- Standard format, already widely used
- Drop in a `SKILL.md` + files, auto-discovered
- Mycelium reads the manifest and routes accordingly
- No recompilation needed

### MCP Servers (Wrapped as Hyphae)
- MCP server runs as subprocess
- Hypha adapter discovers tools via MCP protocol
- Dynamic Ants bind MCP tools on demand
- The MCP server stays as-is — we don't rewrite it

### CLI Tools (Wrapped as Hyphae)
- Any command-line tool
- Hypha adapter wraps stdin/stdout
- Tool declares capabilities in manifest
- Mycelium routes tasks to it

## Discovery

Mycelium discovers hyphae at startup:
1. Scan `hyphae/` directory
2. Read each `hypha.toml` or `SKILL.md`
3. Build capability map
4. Route missions to matching hyphae

## Rules

1. **Never rewrite existing skills** — wrap them as hyphae
2. **Never lock to one protocol** — Skills, MCP, CLI, all supported
3. **Swap when better arrives** — the Rhizomorph interface stays the same
4. **Each hypha reads/writes Rhizomorph** — shared memory is mandatory
5. **Mycelium routes, never executes** — hyphae do the work
