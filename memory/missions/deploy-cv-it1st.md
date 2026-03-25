---
mission: deploy-cv-it1st
project: cv-quicklinks
curated: 2026-03-25T20:43:25.411072+00:00
event_count: 7
agents: [scout-deploy]
tags: [domain:deployment, role:scout, type:benchmark, type:lesson, type:mission, type:pain-point]
---

# Mission: deploy-cv-it1st

## Summary

- **Project:** cv-quicklinks
- **Started:** 2026-03-25T20:43:25.397720+00:00
- **Completed:** 2026-03-25T20:43:25.402231+00:00
- **Events:** 7
- **Agents:** scout-deploy

## Lessons Learned

- **[scout-deploy]** When git auth fails on remote server, use tar pipe instead of SCP
- **[scout-deploy]** git credential cache used wrong GitHub account — run 'gh auth setup-git' first
- **[scout-deploy]** Nginx on hummingbot serves multiple sites — just add a new server block in sites-enabled

## Pain Points

- **[scout-deploy]** SCP hung silently for 30 seconds with no error — had to kill and retry

## Benchmarks

- **First deploy time:** 15 minutes (including nginx config) (by scout-deploy)

## Event Timeline

| Seq | Time | Agent | Type | Summary |
|-----|------|-------|------|---------|
| 1 | 2026-03-25T20:43:25 | scout-deploy | mission.start | {"mission": "deploy-cv-it1st", "project": "cv-quicklinks", "objective": "Deploy  |
| 2 | 2026-03-25T20:43:25 | scout-deploy | memory.write | {"lesson": "When git auth fails on remote server, use tar pipe instead of SCP",  |
| 3 | 2026-03-25T20:43:25 | scout-deploy | memory.write | {"pain_point": "SCP hung silently for 30 seconds with no error — had to kill and |
| 4 | 2026-03-25T20:43:25 | scout-deploy | memory.write | {"lesson": "git credential cache used wrong GitHub account — run 'gh auth setup- |
| 5 | 2026-03-25T20:43:25 | scout-deploy | memory.write | {"lesson": "Nginx on hummingbot serves multiple sites — just add a new server bl |
| 6 | 2026-03-25T20:43:25 | scout-deploy | memory.write | {"metric": "First deploy time", "value": "15 minutes (including nginx config)"} |
| 7 | 2026-03-25T20:43:25 | scout-deploy | mission.complete | {"mission": "deploy-cv-it1st", "status": "success", "summary": "cv.it1st.com liv |
