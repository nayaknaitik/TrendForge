# TrendForge — System Architecture Document

## 1. Executive Summary

TrendForge is a real-time AI marketing intelligence platform that ingests social media trends,
processes them through a multi-agent AI pipeline, and generates platform-specific ad campaigns
tailored to brand profiles.

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Next.js App Router (SSR + Client Components)                    │   │
│  │  ├── Landing Page (SSR, SEO optimized)                          │   │
│  │  ├── Dashboard (Client, WebSocket for real-time)                │   │
│  │  ├── Brand Manager (Client)                                      │   │
│  │  ├── Campaign Studio (Client, streaming AI responses)           │   │
│  │  └── Ad Preview & Export (Client)                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS / WSS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Nginx / Traefik (TLS termination, rate limiting, CORS)         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BACKEND SERVICE LAYER                             │
│                                                                         │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────────────┐      │
│  │ Auth Service    │  │ Brand Service     │  │ Campaign Service   │      │
│  │ (JWT + OAuth2)  │  │ (CRUD + Memory)   │  │ (Gen + Export)     │      │
│  └────────┬───────┘  └────────┬─────────┘  └────────┬───────────┘      │
│           │                   │                      │                   │
│  ┌────────┴───────────────────┴──────────────────────┴───────────┐      │
│  │              FastAPI Application Server                        │      │
│  │  ├── Middleware (auth, rate limit, logging, CORS)             │      │
│  │  ├── Dependency Injection Container                           │      │
│  │  └── Background Task Workers (Celery / ARQ)                   │      │
│  └───────────────────────────┬───────────────────────────────────┘      │
│                               │                                          │
│  ┌────────────────┐  ┌───────┴──────────┐  ┌────────────────────┐      │
│  │ Scraper Service │  │ Trend Processing  │  │ AI Orchestrator    │      │
│  │ (API ingestion) │  │ (NLP pipeline)    │  │ (Multi-agent)      │      │
│  └────────┬───────┘  └────────┬─────────┘  └────────┬───────────┘      │
│           │                   │                      │                   │
└───────────┼───────────────────┼──────────────────────┼──────────────────┘
            │                   │                      │
            ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                     │
│                                                                         │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────────────┐      │
│  │  PostgreSQL     │  │  Redis            │  │  Object Storage    │      │
│  │  + pgvector     │  │  (cache + pubsub) │  │  (S3 / MinIO)      │      │
│  │  (structured +  │  │  (sessions +      │  │  (generated assets)│      │
│  │   vector data)  │  │   rate limits)    │  │                    │      │
│  └────────────────┘  └──────────────────┘  └────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ X/Twitter │ │ Reddit   │ │ Meta     │ │ OpenAI   │ │ Anthropic│    │
│  │ API v2   │ │ API      │ │ Graph API│ │ GPT-4    │ │ Claude   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Key Architectural Decisions

### 3.1 Why FastAPI over Node.js
- **Async-native**: Built on Starlette, handles 10k+ concurrent connections
- **Pydantic v2**: Rust-based validation, 5-17x faster than v1
- **OpenAPI auto-generation**: Reduces API documentation burden
- **Python ML ecosystem**: Direct access to transformers, sentence-transformers, etc.
- **Tradeoff**: Slightly more complex deployment than Node.js monolith

### 3.2 Why pgvector over Pinecone (MVP)
- **Operational simplicity**: One database to manage
- **Cost**: $0 additional at MVP scale (~100k vectors)
- **Performance**: Adequate for <1M vectors with HNSW indexing
- **Migration path**: Abstract vector operations behind interface for future Pinecone migration
- **Tradeoff**: Won't scale past ~10M vectors without sharding

### 3.3 Why LangGraph for Agent Orchestration
- **Deterministic**: State machine-based, not autonomous
- **Observable**: Full execution trace for debugging
- **Composable**: Agents chain explicitly, no hidden coupling
- **Tradeoff**: More boilerplate than raw LLM calls

### 3.4 Why Redis over RabbitMQ
- **Dual-purpose**: Cache + pub/sub + rate limiting + sessions
- **Simplicity**: One fewer service to manage
- **Performance**: Sub-millisecond operations
- **Tradeoff**: Less durable than RabbitMQ for critical message queues (mitigated by PostgreSQL as source of truth)

## 4. Scaling Strategy

### Phase 1: 0-10k users
- Single PostgreSQL instance (pgvector)
- Single Redis instance
- 2-4 FastAPI workers behind Nginx
- Estimated infra cost: ~$200/mo

### Phase 2: 10k-50k users
- PostgreSQL read replicas
- Redis Cluster (3 nodes)
- Migrate vector search to Pinecone
- Celery workers scaled independently
- Estimated infra cost: ~$2,000/mo

### Phase 3: 50k-100k+ users
- PostgreSQL with Citus for sharding
- Dedicated Pinecone pod
- Kubernetes-based auto-scaling
- CDN for generated assets
- Estimated infra cost: ~$8,000/mo

## 5. Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: Structured JSON → Loki or ELK
- **Tracing**: OpenTelemetry → Jaeger
- **Alerting**: Grafana alerting → PagerDuty/Slack
- **AI Observability**: LangSmith for agent trace debugging

## 6. Security Model
- JWT (RS256) + refresh tokens
- API key rotation with vault
- Row-level security in PostgreSQL
- Rate limiting per user tier (Redis sliding window)
- Input sanitization via Pydantic
- CORS whitelist
- CSP headers via Nginx
- Secrets via environment variables (never committed)
