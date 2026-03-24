# Rhizomorph — Shared Instant Memory

In biology, rhizomorphs are cord-like bundles of hyphae that transport nutrients over long distances. In this framework, the Rhizomorph is the shared memory layer that connects all parts of the colony.

## Architecture

```
┌──────────────────────────────────────────┐
│              RHIZOMORPH                  │
│                                          │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │  LCM (session)  │  │ QMD (long)   │  │
│  │  SQLite DB      │  │ Files on disk│  │
│  │  Compacts       │  │ Curated      │  │
│  │  Recent context │  │ Durable      │  │
│  └────────┬────────┘  └──────┬───────┘  │
│           │                  │           │
│  ┌────────┴──────────────────┴────────┐  │
│  │           TAG PROTOCOL             │  │
│  │  #mission  #lesson  #pain-point   │  │
│  │  #shortcut #green-leaf #benchmark │  │
│  └───────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Components

### LCM (Session Memory)
- SQLite-backed
- Compacts as sessions grow
- Recent context, lossless
- Tools: `lcm_grep`, `lcm_describe`, `lcm_expand`

### QMD (Long-term Memory)
- Markdown files on disk
- Only valuable knowledge: lessons, benchmarks, revenue
- Never polluted with session noise
- Searchable via grep

## Tag Protocol

| Tag | Layer | Purpose |
|-----|-------|---------|
| `#mission` | LCM | Active work |
| `#mission-complete` | LCM→QMD | Finished work with results |
| `#lesson` | QMD | Durable knowledge |
| `#pain-point` | LCM→QMD | Blocker (promote if recurring) |
| `#shortcut` | LCM→QMD | Efficiency trick (promote if proven) |
| `#green-leaf` | QMD | Revenue opportunity |
| `#benchmark` | QMD | Model performance data |

## Memory Rules

1. Every hypha reads Rhizomorph before starting work
2. Every hypha writes discoveries back immediately
3. LCM handles session noise — don't dump everything into QMD
4. Only valuable, reusable knowledge rises to QMD
5. Rhizomorph is instant — no delays, no bottlenecks

## Swappable

If a better memory system than QMD/LCM emerges, swap it in. The Rhizomorph interface stays the same — read, write, search, compact. The implementation can change.
