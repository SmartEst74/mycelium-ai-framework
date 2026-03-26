# Role-to-Model Mapping

Maps mycelium-ai-framework registry roles to the best available free models.

## Model Assignments

| Model | Capabilities | Context | Cost | Use Case |
|-------|-------------|---------|------|----------|
| `kilocode/xiaomi/mimo-v2-omni:free` | Vision+Tools+Text | 262K | Free | Workers needing vision/UI/design analysis |
| `kilocode/xiaomi/mimo-v2-pro:free` | Text+Tools | 1M | Free | Brain, coordination, large-context reasoning |
| `kilocode/stepfun/step-3.5-flash:free` | Text+Tools | 128K | Free | Fast scouts, quick research, low-latency tasks |
| `openrouter/qwen/qwen3-coder:free` | Text (coding) | 262K | Free* | Code review, refactoring, architecture docs |
| `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text | 128K | Free* | Analysis, writing, strategy |

*OpenRouter free models are rate-limited. Use only when kilocode models can't do the job.

## Role → Model Mapping

### Tier 1: Orchestrator (never executes)

| Agent Role | Model | Reason |
|-----------|-------|--------|
| **Mycelium** (brain) | `kilocode/xiaomi/mimo-v2-pro:free` | 1M context for memory, reasoning, routing |
| **Army Ant** (coordinator) | `kilocode/xiaomi/mimo-v2-pro:free` | 1M context for registry + mission state |
| **agents-orchestrator** | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for multi-agent coordination |

### Tier 2: Scouts (research only, never execute)

| Agent Role | Model | Reason |
|-----------|-------|--------|
| **Scout** (generic) | `kilocode/stepfun/step-3.5-flash:free` | Fastest, cheapest, good enough for research |
| **Tool Scout** | `kilocode/stepfun/step-3.5-flash:free` | Quick web/API probing |
| **Leaf Scout** (revenue) | `kilocode/stepfun/step-3.5-flash:free` | Fast market scanning |
| **Benchmark Scout** | `kilocode/stepfun/step-3.5-flash:free` | Quick model comparison |
| **Integration Scout** | `kilocode/stepfun/step-3.5-flash:free` | Fast skill/tool evaluation |

### Tier 3: Dynamic Ants / Workers (execute tasks)

#### Engineering (23 roles) — Vision+Code capable

| Role | Model | Reason |
|------|-------|--------|
| engineering-backend-architect | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for architecture diagrams, code analysis |
| engineering-frontend-developer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for UI screenshots, design analysis |
| engineering-sre | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for dashboards, monitoring screens |
| engineering-devops-automator | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for CI/CD pipelines, infra diagrams |
| engineering-code-reviewer | `openrouter/qwen/qwen3-coder:free` | Pure code analysis, no vision needed |
| engineering-senior-developer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision + code, generalist |
| engineering-software-architect | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for system design docs |
| engineering-data-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for data flow diagrams |
| engineering-database-optimizer | `openrouter/qwen/qwen3-coder:free` | Pure SQL/code optimization |
| engineering-security-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for security dashboards |
| engineering-rapid-prototyper | `kilocode/xiaomi/mimo-v2-omni:free` | Vision + fast iteration |
| engineering-technical-writer | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text generation, no vision needed |
| engineering-git-workflow-master | `kilocode/stepfun/step-3.5-flash:free` | Fast git commands, lightweight |
| engineering-mobile-app-builder | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for mobile UI screenshots |
| engineering-embedded-firmware-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy, C/embedded |
| engineering-solidity-smart-contract-engineer | `openrouter/qwen/qwen3-coder:free` | Solidity code review |
| engineering-ai-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision + code for ML pipelines |
| engineering-ai-data-remediation-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for data quality dashboards |
| engineering-autonomous-optimization-architect | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for optimization strategies |
| engineering-incident-response-commander | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for incident dashboards |
| engineering-threat-detection-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for threat analysis |
| engineering-feishu-integration-developer | `kilocode/stepfun/step-3.5-flash:free` | API integration, fast |
| engineering-wechat-mini-program-developer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for mini-program UI |

#### Design (8 roles) — Always vision-capable

| Role | Model | Reason |
|------|-------|--------|
| design-ui-designer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision essential for UI analysis |
| design-ux-architect | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for wireframes, user flows |
| design-ux-researcher | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for user research analysis |
| design-brand-guardian | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for brand assets |
| design-visual-storyteller | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for visual content |
| design-whimsy-injector | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for creative design |
| design-image-prompt-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for image analysis |
| design-inclusive-visuals-specialist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for accessibility analysis |

#### Marketing (27 roles) — Text-heavy

| Role | Model | Reason |
|------|-------|--------|
| marketing-content-creator | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text generation |
| marketing-seo-specialist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for SEO analysis |
| marketing-growth-hacker | `kilocode/stepfun/step-3.5-flash:free` | Fast experimentation |
| marketing-social-media-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast content ideas |
| marketing-tiktok-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast trend analysis |
| marketing-linkedin-content-creator | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Professional text generation |
| marketing-twitter-engager | `kilocode/stepfun/step-3.5-flash:free` | Fast, short-form content |
| marketing-podcast-strategist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Long-form content planning |
| marketing-book-co-author | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for book structure |
| marketing-ai-citation-strategist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for AI search optimization |
| marketing-reddit-community-builder | `kilocode/stepfun/step-3.5-flash:free` | Fast community engagement |
| marketing-instagram-curator | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for image content |
| marketing-carousel-growth-engine | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for carousel design |
| marketing-short-video-editing-coach | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for video content |
| marketing-douyin-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-kuaishou-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-weibo-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-zhihu-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-bilibili-content-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-xiaohongshu-specialist | `kilocode/stepfun/step-3.5-flash:free` | Fast platform analysis |
| marketing-wechat-official-account | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text content creation |
| marketing-baidu-seo-specialist | `kilocode/stepfun/step-3.5-flash:free` | Fast SEO analysis |
| marketing-app-store-optimizer | `kilocode/stepfun/step-3.5-flash:free` | Fast ASO analysis |
| marketing-china-ecommerce-operator | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for product images |
| marketing-cross-border-ecommerce | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for product listings |
| marketing-livestream-commerce-coach | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for livestream analysis |
| marketing-private-domain-operator | `kilocode/stepfun/step-3.5-flash:free` | Fast operations |

#### Sales (8 roles) — Text-heavy, fast

| Role | Model | Reason |
|------|-------|--------|
| sales-coach | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Coaching text generation |
| sales-discovery-coach | `kilocode/stepfun/step-3.5-flash:free` | Fast question generation |
| sales-deal-strategist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for deal analysis |
| sales-account-strategist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for account research |
| sales-pipeline-analyst | `kilocode/stepfun/step-3.5-flash:free` | Fast data analysis |
| sales-engineer | `openrouter/qwen/qwen3-coder:free` | Technical sales documentation |
| sales-proposal-strategist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Long-form text generation |
| sales-outbound-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast campaign planning |

#### Testing (8 roles) — Code+Vision

| Role | Model | Reason |
|------|-------|--------|
| testing-api-tester | `openrouter/qwen/qwen3-coder:free` | Code analysis |
| testing-performance-benchmarker | `kilocode/stepfun/step-3.5-flash:free` | Fast benchmarking |
| testing-accessibility-auditor | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for UI accessibility |
| testing-evidence-collector | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for screenshots |
| testing-reality-checker | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for verification |
| testing-test-results-analyzer | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for results |
| testing-tool-evaluator | `kilocode/stepfun/step-3.5-flash:free` | Fast evaluation |
| testing-workflow-optimizer | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for workflow analysis |

#### Product (5 roles) — Large context

| Role | Model | Reason |
|------|-------|--------|
| product-manager | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for product strategy |
| product-sprint-prioritizer | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for backlog analysis |
| product-trend-researcher | `kilocode/stepfun/step-3.5-flash:free` | Fast research |
| product-feedback-synthesizer | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for feedback analysis |
| product-behavioral-nudge-engine | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Behavioral analysis text |

#### Paid Media (7 roles) — Analysis-heavy

| Role | Model | Reason |
|------|-------|--------|
| paid-media-ppc-strategist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for campaign analysis |
| paid-media-paid-social-strategist | `kilocode/stepfun/step-3.5-flash:free` | Fast campaign planning |
| paid-media-auditor | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for audit data |
| paid-media-creative-strategist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for ad creative |
| paid-media-programmatic-buyer | `kilocode/stepfun/step-3.5-flash:free` | Fast bid optimization |
| paid-media-search-query-analyst | `kilocode/stepfun/step-3.5-flash:free` | Fast query analysis |
| paid-media-tracking-specialist | `openrouter/qwen/qwen3-coder:free` | Code for tracking implementation |

#### Specialized (27 roles) — Mixed

| Role | Model | Reason |
|------|-------|--------|
| agents-orchestrator | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for orchestration |
| specialized-mcp-builder | `openrouter/qwen/qwen3-coder:free` | Code-heavy |
| specialized-workflow-architect | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for workflow design |
| specialized-model-qa | `kilocode/stepfun/step-3.5-flash:free` | Fast model testing |
| specialized-developer-advocate | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text content creation |
| specialized-document-generator | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Document writing |
| specialized-salesforce-architect | `openrouter/qwen/qwen3-coder:free` | Code/config heavy |
| specialized-cultural-intelligence-strategist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Analysis text |
| specialized-french-consulting-market | `kilocode/stepfun/step-3.5-flash:free` | Fast market analysis |
| specialized-korean-business-navigator | `kilocode/stepfun/step-3.5-flash:free` | Fast market analysis |
| automation-governance-architect | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for governance |
| blockchain-security-auditor | `openrouter/qwen/qwen3-coder:free` | Code audit |
| compliance-auditor | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for compliance docs |
| corporate-training-designer | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Training content |
| data-consolidation-agent | `openrouter/qwen/qwen3-coder:free` | Data/code heavy |
| government-digital-presales-consultant | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Text-heavy |
| healthcare-marketing-compliance | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for regulations |
| identity-graph-operator | `openrouter/qwen/qwen3-coder:free` | Data/code heavy |
| lsp-index-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy |
| recruitment-specialist | `kilocode/stepfun/step-3.5-flash:free` | Fast candidate matching |
| report-distribution-agent | `kilocode/stepfun/step-3.5-flash:free` | Fast report generation |
| sales-data-extraction-agent | `openrouter/qwen/qwen3-coder:free` | Code/data extraction |
| study-abroad-advisor | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Advisory text |
| supply-chain-strategist | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for supply chain |
| accounts-payable-agent | `openrouter/qwen/qwen3-coder:free` | Code/data processing |
| agentic-identity-trust | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for trust framework |
| zk-steward | `openrouter/qwen/qwen3-coder:free` | Code-heavy (ZK proofs) |

#### Support (6 roles) — Text-heavy

| Role | Model | Reason |
|------|-------|--------|
| support-support-responder | `kilocode/stepfun/step-3.5-flash:free` | Fast response generation |
| support-analytics-reporter | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for data analysis |
| support-infrastructure-maintainer | `kilocode/stepfun/step-3.5-flash:free` | Fast maintenance tasks |
| support-executive-summary-generator | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for summarization |
| support-finance-tracker | `kilocode/stepfun/step-3.5-flash:free` | Fast financial queries |
| support-legal-compliance-checker | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for legal docs |

#### Academic (5 roles) — Text-heavy

| Role | Model | Reason |
|------|-------|--------|
| academic-anthropologist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Research text |
| academic-geographer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for maps |
| academic-historian | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Historical text analysis |
| academic-narratologist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Narrative analysis |
| academic-psychologist | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Behavioral analysis |

#### Game Development (20 roles) — Vision+Code

| Role | Model | Reason |
|------|-------|--------|
| game-designer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for game design |
| technical-artist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for art pipeline |
| level-designer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for level layouts |
| narrative-designer | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | Story/narrative text |
| game-audio-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy |
| blender-addon-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (Python/Blender) |
| godot-gameplay-scripter | `openrouter/qwen/qwen3-coder:free` | Code-heavy (GDScript) |
| godot-multiplayer-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (networking) |
| godot-shader-developer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for shader output |
| unity-architect | `openrouter/qwen/qwen3-coder:free` | Code-heavy (C#) |
| unity-editor-tool-developer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (C#) |
| unity-multiplayer-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (networking) |
| unity-shader-graph-artist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for shader output |
| roblox-avatar-creator | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for 3D design |
| roblox-experience-designer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for experience design |
| roblox-systems-scripter | `openrouter/qwen/qwen3-coder:free` | Code-heavy (Lua) |
| unreal-multiplayer-architect | `openrouter/qwen/qwen3-coder:free` | Code-heavy (C++) |
| unreal-systems-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (C++) |
| unreal-technical-artist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for art pipeline |
| unreal-world-builder | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for world design |

#### Spatial Computing (6 roles) — Vision+Code

| Role | Model | Reason |
|------|-------|--------|
| visionos-spatial-engineer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for spatial UI |
| xr-immersive-developer | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for immersive design |
| xr-interface-architect | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for XR interfaces |
| xr-cockpit-interaction-specialist | `kilocode/xiaomi/mimo-v2-omni:free` | Vision for interaction design |
| macos-spatial-metal-engineer | `openrouter/qwen/qwen3-coder:free` | Code-heavy (Metal/3D) |
| terminal-integration-specialist | `openrouter/qwen/qwen3-coder:free` | Code-heavy (CLI) |

#### Project Management (6 roles) — Large context

| Role | Model | Reason |
|------|-------|--------|
| project-manager-senior | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for project data |
| project-management-project-shepherd | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for project docs |
| project-management-studio-producer | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for production |
| project-management-studio-operations | `kilocode/xiaomi/mimo-v2-pro:free` | Large context for ops |
| project-management-jira-workflow-steward | `openrouter/qwen/qwen3-coder:free` | Jira API/code heavy |
| project-management-experiment-tracker | `kilocode/stepfun/step-3.5-flash:free` | Fast experiment logging |

## Quick Reference

Need vision? → `kilocode/xiaomi/mimo-v2-omni:free`
Need large context? → `kilocode/xiaomi/mimo-v2-pro:free`
Need speed? → `kilocode/stepfun/step-3.5-flash:free`
Need code quality? → `openrouter/qwen/qwen3-coder:free`
Need writing/analysis? → `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
