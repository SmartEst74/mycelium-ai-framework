# Skill & MCP Integration — Mycelium AI Framework

## Core Principle

Mycelium does NOT replace skills or MCP. It **orchestrates** them.

```
                    ┌─────────────────────────────────┐
                    │          MYCELIUM BRAIN         │
                    │       (mimo-v2-pro, routing)     │
                    └──────────┬──────────────────────┘
                               │ delegates
              ┌────────────────┼────────────────┐
              │                │                │
        ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
        │   Scout   │   │ Army Ants │   │   Skills  │
        │ (research)│   │(coord)    │   │  (ClawHub)│
        └───────────┘   └─────┬─────┘   └─────┬─────┘
                              │               │
                        ┌─────▼─────┐   ┌─────▼─────┐
                        │  Dynamic  │   │    MCP    │
                        │   Ants    │   │   Tools   │
                        │(execution)│   │ (external)│
                        └───────────┘   └───────────┘
```

## Skill Layer (AgentSkills)

Skills are the **plugin system** for capabilities. Mycelium wraps them, never replaces them.

### What Skills Provide
- **Instructions** — how to perform a task (SKILL.md)
- **Tools** — what capabilities are available
- **Configuration** — how to set up and use
- **Documentation** — usage examples and edge cases

### How Mycelium Uses Skills
1. **Registry** — Mycelium maintains a skill registry (from ClawHub or local)
2. **Selection** — Army Ants pick the right skill for a mission
3. **Loading** — Dynamic Ants load skills on-demand (progressive disclosure)
4. **Execution** — Ants execute using skill instructions + tools
5. **Feedback** — Results and lessons flow back to shared memory

### Skill Compatibility Rules
- Every skill must have a `SKILL.md` file
- Skills declare their capabilities in metadata
- Skills can define their own tool requirements
- Skills are loaded per-agent, not globally (progressive disclosure)
- Skills MUST be pluggable — any user can add their own
- Mycelium does NOT bake skill logic into the framework

### Example: ClawHub Skills
```yaml
# A Dynamic Ant assigned to "web development" might load:
skills:
  - name: "github"
    source: "clawhub.com/skills/github"
    capabilities: [issues, prs, ci, code-review]
  - name: "browser"
    source: "clawhub.com/skills/browser"
    capabilities: [web-scraping, ui-automation, screenshots]
```

## MCP Layer (Model Context Protocol)

MCP provides **external tool integration**. Mycelium uses MCP where tools need to talk to external systems.

### What MCP Provides
- **Tool definitions** — standardized interface for external tools
- **Server communication** — JSON-RPC over stdio/HTTP
- **Capability discovery** — tools declare what they can do
- **Security boundaries** — tools run in isolated contexts

### How Mycelium Uses MCP
1. **Discovery** — Scout discovers new MCP servers/tools
2. **Registration** — Army Ants register available MCP tools
3. **Binding** — Dynamic Ants bind MCP tools to their task context
4. **Execution** — Ants call MCP tools during task execution
5. **Reporting** — MCP tool results flow back through shared memory

### MCP Compatibility Rules
- Mycelium supports MCP as a first-class tool integration path
- Dynamic Ants can call MCP servers for external tool access
- MCP tools are treated like any other tool in the capability matrix
- Security: MCP tools run in sandboxed contexts, never in the brain
- Skill discovery includes MCP tool discovery
- If a skill defines MCP tool requirements, the ant must have access

### Example: MCP Tool Usage
```yaml
# A Dynamic Ant using MCP for GitHub operations:
ant:
  role: "engineering-code-reviewer"
  model: "mimo-v2-omni:free"
  tools:
    - type: mcp
      server: "github-mcp"
      capabilities: [create-review, list-prs, get-file]
    - type: skill
      name: "github"
      capabilities: [branch-management, issue-triage]
```

## Integration Architecture

### Three Plugin Systems, One Framework

| Layer | System | Purpose | Mycelium Role |
|-------|--------|---------|---------------|
| **Skills** | AgentSkills/ClawHub | Capability packages | Wraps and orchestrates |
| **Tools** | MCP | External integrations | Selects and binds |
| **Models** | Provider APIs | AI reasoning | Routes to best model |

### Plugin Discovery Flow

```
Scout discovers new plugin (skill or MCP)
    │
    ▼
Scout writes #benchmark to shared memory
    │
    ▼
Mycelium reads and evaluates
    │
    ├── Is it a skill? → Register in skill registry
    ├── Is it MCP? → Register in tool registry
    └── Both? → Register in both
    │
    ▼
Army Ants can now select it for missions
    │
    ▼
Dynamic Ants load and execute with it
```

### What Users Can Plugin

1. **Skills** (AgentSkills format)
   - Drop a SKILL.md + supporting files
   - Mycelium auto-discovers
   - Available to all agents immediately

2. **MCP Servers** (standard MCP protocol)
   - Configure MCP server connection
   - Mycelium discovers capabilities
   - Available to Dynamic Ants on demand

3. **Models** (any provider)
   - Add provider config in models.yaml
   - Scout benchmarks it
   - Available in model selection

4. **Agent Roles** (agency-agents format)
   - Add role definition to registry/roles/
   - Army Ants can select it
   - Immediate availability

## Anti-Patterns

❌ **Don't**: Bake skill logic into the mycelium brain
✅ **Do**: Delegate to skills and let them handle their domain

❌ **Don't**: Replace MCP with custom tool system
✅ **Do**: Use MCP as the standard tool integration path

❌ **Don't**: Lock users into specific skills or tools
✅ **Do**: Support any skill/MCP plugin from any source

❌ **Don't**: Make the brain do what a skill does better
✅ **Do**: Route to the right skill for each job
