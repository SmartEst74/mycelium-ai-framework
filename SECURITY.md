# Security Policy

## Model Constraints

- **Free models only.** We never use paid models in production without explicit approval.
- **No API keys in code.** All secrets via environment variables or config files excluded from git.
- **No external data exfiltration.** Agents write to local memory only. No network calls from memory layer.

## Agent Constraints

- **Mycelium never executes.** The orchestrator only delegates. It never touches files, APIs, or systems directly.
- **Scouts never execute.** Research only. They report findings, never take action.
- **Enforcement is real.** Pre-commit hooks and validation scripts block violations at the git level.

## Reporting

Open an issue on GitHub for security concerns.
