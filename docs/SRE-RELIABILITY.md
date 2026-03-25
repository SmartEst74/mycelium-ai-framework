# SRE & Reliability — Mycelium AI Framework

## Philosophy

The colony must be:
- **Self-healing**: recover from failures automatically
- **Observable**: know what's happening, when, and why
- **Resilient**: degrade gracefully, not catastrophically
- **Repeatable**: identical deployments produce identical behavior
- **Auditable**: every decision traceable

This is not optional. Grant reviewers and enterprise customers demand it.

## Core Reliability Patterns

### 1. Event Sourcing + Replay

**See `docs/EVENT-BUS.md`**

All state changes flow through the event bus. The entire colony state can be rebuilt by replaying events from a snapshot.

**Benefits:**
- Disaster recovery (rebuild from backup + recent events)
- Time travel debugging (replay to any point in time)
- Audit trail (immutable log of every AI decision)

### 2. Health Checks & Circuit Breakers

Every agent, every hypha, every external dependency has a health check.

```yaml
health:
  checks:
    - name: "LCM database"
      type: "sqlite"
      path: "/var/lib/mycelium/lcm.db"
      interval: 10s
      timeout: 2s
    - name: "model provider: kilocode"
      type: "http"
      url: "https://api.kilo.ai/health"
      interval: 30s
    - name: "Redis (if used for pub/sub)"
      type: "tcp"
      host: "localhost"
      port: 6379
  circuit_breaker:
    failure_threshold: 3
    recovery_timeout: 30s
    half_open_max_calls: 5
```

**Circuit breaker pattern**:
- 3 failures → circuit opens → agent/dependency marked unhealthy
- Mycelium routes around failures (use fallback models, alternative hyphae)
- After 30s, half-open test → if healthy, close circuit

### 3. Graceful Degradation

When a component fails:
1. Try fallback (model → hypha → alternative approach)
2. If no fallback, **fail quietly** with log, don't crash colony
3. Alert SRE (readable alert with context)

Example: model provider rate-limited → switch to secondary provider → log warning → continue mission.

### 4. Immutable Infrastructure

- **Agents are stateless** — all state in LCM/QMD
- **Deploy as containers** — immutable images, same everywhere
- **Configuration versioned** — git, not manual edits
- **Secrets from vault** — never bake into images

### 5. Observability Stack

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Metrics   │────▶│   Tracing   │────▶│   Logs       │
│ (Prometheus)│     │ (OpenTelemetry)│   │ (Loki/ELK)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Metrics to collect:**
- Agent execution time (p50, p95, p99)
- Event bus lag (events waiting to be processed)
- Memory growth (LCM DB size, QMD file count)
- Error rates by agent/hypha type
- Model call latency and rate limits
- Mission success rate (SLO: >99%)

**Tracing:**
- Distributed trace per mission: mission → scout → hypha → model call
- Trace ID flows through all events
- Visualize in Jaeger/Tempo

**Logs:**
- Structured JSON logs (timestamp, level, agent, mission_id, event_id)
- Centralized, searchable
- Retention: 30 days (compliance) + aggregated metrics

### 6. Deployment Best Practices

#### Blue/Green Deployments

- Deploy new version to green environment
- Run smoke tests (health checks, sample mission)
- Switch 10% traffic → monitor → 100%
- Rollback on SLO breach (5xx errors, latency spike)

#### Canary Releases

For risky changes (new model, new agent type):
- Deploy to 1 node / 5% missions
- Compare SLOs vs control group
- If p95 latency < baseline, error rate < 0.1% → roll out gradually

#### Infrastructure as Code

Everything defined in code:
- Network (VPC, subnets, security groups)
- Compute (K8s pods, horizontal pod autoscaler)
- Storage (LCM SQLite persistent volume, QMD files PVC)
- Config (ConfigMap/SealedSecret)
- Monitoring (PrometheusRule, Alertmanager routes)

### 7. Security

- **Least privilege**: agents run with minimal permissions (no root, restricted filesystem)
- **Network segmentation**: internal event bus on isolated network, no public internet access
- **Secrets management**: Vault/SecretStore, never in git
- **Audit logging**: all agent actions, all model calls, all memory writes
- **Input validation**: sanitize all external data before writing to Rhizomorph

### 8. Capacity Planning & Autoscaling

- **Autoscaling** based on:
  - Queue depth (pending missions)
  - Event bus lag
  - CPU/memory of agent pods

- **Resource limits**:
  - LCM SQLite: <10GB (archive old events to S3)
  - QMD: <100k files (shard by date)
  - Agent memory: 512MB–2GB depending on model

- **Backpressure**: if agents overwhelmed, reject new missions with `429 Too Many Requests` and retry-after header

### 9. Disaster Recovery

**Backup strategy:**
- Hourly snapshots of LCM DB + QMD dir to object storage
- 30-day retention
- Cross-region replication for production

**Recovery procedure:**
1. Deploy fresh cluster (IaC)
2. Restore latest snapshot
3. Replay events from snapshot to latest
4. Start agents (they'll catch up via event bus)
5. Verify health checks pass

**RPO**: 1 hour (last snapshot + events)
**RTO**: 15 minutes (restore + replay)

### 10. Testing Pyramid

```
      /\
     /  \    E2E tests (demos, full mission flows)
    /    \   Integration tests (agent + LCM + model mock)
   /______\  Unit tests (config, utilities, invariants)
```

**Mandatory:**
- E2E test: submit mission, verify #mission-complete written
- Chaos test: kill agent during mission → verify recovery via replay
- Load test: 100 concurrent missions → measure latency, resource use

---

## Grant Reviewer Checklist

Will ask: "How do you ensure reliability in production?"

Answers:
1. **Event sourcing** — full replay capability, state rebuild
2. **Health checks + circuit breakers** — automatic failure handling
3. **Immutable deployments** — reproducible, rollback in seconds
4. **Observability** — metrics/tracing/logs for every mission
5. **SLOs defined** — latency, error rate, availability targets
6. **Disaster recovery** — backups, RTO/RPO documented
7. **Security** — least privilege, audit logs, secrets vault
8. **Capacity planning** — autoscaling, backpressure, resource limits
9. **Testing** — E2E + chaos + load tests in CI
10. **Compliance** — audit trail for every AI decision

---

*This is expert-level SRE. If we implement even 50% of this, we demonstrate serious engineering.*

*Version: 1.0 — 2026-03-25*
