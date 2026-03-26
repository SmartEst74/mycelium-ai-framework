---
mission: model-selection
project: mycelium-ai-framework
curated: 2026-03-26T01:42:29.322745+00:00
event_count: 6
agents: [scout-models]
tags: [domain:model-selection, role:scout, type:benchmark, type:lesson, type:mission, type:pain-point]
---

# Mission: model-selection

## Summary

- **Project:** mycelium-ai-framework
- **Started:** 2026-03-26T01:42:29.315939+00:00
- **Completed:** 2026-03-26T01:42:29.319520+00:00
- **Events:** 6
- **Agents:** scout-models

## Lessons Learned

- **[scout-models]** mimo-v2-omni:free is the ONLY free model with vision+tool calling
- **[scout-models]** OpenRouter free models are unreliable — rate-limited, return null content

## Pain Points

- **[scout-models]** Fallback chain broke when OpenRouter models returned null — automated tasks failed silently

## Benchmarks

- **Models tested:** 8 free models, 2 passed full test suite (by scout-models)

## Event Timeline

| Seq | Time | Agent | Type | Summary |
|-----|------|-------|------|---------|
| 13 | 2026-03-26T01:42:29 | scout-models | mission.start | {"mission": "model-selection", "project": "mycelium-ai-framework", "objective":  |
| 14 | 2026-03-26T01:42:29 | scout-models | memory.write | {"lesson": "mimo-v2-omni:free is the ONLY free model with vision+tool calling",  |
| 15 | 2026-03-26T01:42:29 | scout-models | memory.write | {"lesson": "OpenRouter free models are unreliable — rate-limited, return null co |
| 16 | 2026-03-26T01:42:29 | scout-models | memory.write | {"pain_point": "Fallback chain broke when OpenRouter models returned null — auto |
| 17 | 2026-03-26T01:42:29 | scout-models | memory.write | {"metric": "Models tested", "value": "8 free models, 2 passed full test suite"} |
| 18 | 2026-03-26T01:42:29 | scout-models | mission.complete | {"mission": "model-selection", "status": "success", "summary": "mimo-v2-omni:fre |
