---

### File: ARCHITECTURE.md
```markdown
# System Architecture

Detailed technical architecture of the Shopify Analytics AI system.

## System Overview
```
┌──────────────────────────────────────────────────────────────┐
│                         Client Layer                          │
│                  (HTTP REST API Requests)                     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      Rails API (Port 3000)                    │
├──────────────────────────────────────────────────────────────┤
│  Controllers:                                                 │
│  - ShopifyAuthController (OAuth flow)                        │
│  - QuestionsController (main endpoint)                       │
│                                                               │
│  Services:                                                    │
│  - AiServiceClient (HTTP client to Python)                   │
│                                                               │
│  Models:                                                      │
│  - Shop (encrypted tokens, OAuth data)                       │
│  - AnalyticsQuery (query history, results)                   │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP POST
                         │ /api/v1/query
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 Python AI Service (Port 8000)                 │
├──────────────────────────────────────────────────────────────┤
│  AgentOrchestrator:                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 1: Intent Classifier                            │   │
│  │ - Classify question into domain                       │   │
│  │ - Extract entities and time ranges                    │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 2: Query Planner                                │   │
│  │ - Determine data sources                              │   │
│  │ - Plan aggregations and filters                       │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 3: ShopifyQL Generator                          │   │
│  │ - Generate analytics query                            │   │
│  │ - Validate query syntax                               │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 4: Query Executor                               │   │
│  │ - Execute query (demo: synthetic data)                │   │
│  │ - Apply NumPy linear regression forecasting           │   │
│  └──────────┬───────────────────────────────────────────┘   │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 5: Insight Synthesizer                          │   │
│  │ - Transform data to business language                 │   │
│  │ - Generate recommendations                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │ Claude API Calls
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               Anthropic Claude API                            │
│              (claude-sonnet-4-20250514)                      │
└──────────────────────────────────────────────────────────────┘