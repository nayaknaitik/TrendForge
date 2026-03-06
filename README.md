# TrendForge — Real-Time AI Marketing Intelligence & Ad Generation

<div align="center">

**Turn viral trends into revenue-generating ad campaigns in seconds.**

[![CI](https://github.com/YOUR_ORG/trendforge/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/trendforge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## Overview

TrendForge is a production-grade SaaS platform that continuously monitors social media for emerging trends, matches them to brand profiles using AI, and generates platform-optimized ad campaigns — all in real time.

### How It Works

```
Social Media APIs  ──►  Trend Processor  ──►  AI Agent Pipeline  ──►  Ad Campaigns
(Twitter, Reddit,       (scoring, NLP,        (5 specialized         (platform-specific
 Meta)                   embeddings)           agents)                copy & strategy)
```

**AI Agent Pipeline:**

| Agent | Purpose |
|---|---|
| **TrendClassifier** | Categorizes trends by topic, sentiment, audience |
| **BrandRelevance** | Scores trend-brand fit using multi-factor weighted model |
| **CampaignStrategist** | Creates campaign angle, hooks, content pillars |
| **CopyGenerator** | Writes platform-specific ad copy with character-limit awareness |
| **PerformanceHeuristic** | Predicts engagement & recommends optimizations |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| **Frontend** | Next.js 14 (App Router), React 18, Tailwind CSS 3.4, Framer Motion |
| **Database** | PostgreSQL 16 + pgvector, Redis 7 |
| **AI** | OpenAI GPT-4o, Anthropic Claude (switchable) |
| **Infra** | Docker, Nginx, GitHub Actions CI/CD |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose v2+
- (Optional) Node.js 20+, Python 3.11+ for local development

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_ORG/trendforge.git
cd trendforge
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker

```bash
docker compose up -d
```

Services will be available at:

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Nginx (unified) | http://localhost:80 |

### 3. Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

> Requires PostgreSQL and Redis running locally. See `.env.example` for connection strings.

---

## Project Structure

```
trendforge/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST endpoints (auth, brands, trends, campaigns)
│   │   ├── core/                 # Config, security, rate limiting, logging
│   │   ├── db/                   # Session, Redis client
│   │   ├── models/               # SQLAlchemy models (7 tables)
│   │   ├── schemas/              # Pydantic v2 request/response schemas
│   │   └── services/
│   │       ├── ai_agents/        # 5 AI agents + orchestrator
│   │       ├── brand/            # Brand CRUD + embedding
│   │       ├── campaign/         # Campaign generation pipeline
│   │       ├── scraper/          # Multi-platform social scraper
│   │       └── trends/           # Trend processing & scoring
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/        # Trends, Brands, Campaigns, Analytics, Settings
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx          # Landing page
│   │   └── lib/                  # API client, utilities
│   ├── Dockerfile
│   └── package.json
├── infrastructure/
│   └── nginx/nginx.conf
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── ARCHITECTURE.md
```

---

## API Reference

All endpoints are prefixed with `/api/v1`. Authentication uses JWT Bearer tokens.

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get access + refresh tokens |
| POST | `/auth/refresh` | Refresh access token |

### Brands

| Method | Endpoint | Description |
|---|---|---|
| POST | `/brands` | Create brand profile |
| GET | `/brands` | List user's brands |
| GET | `/brands/{id}` | Get brand details |
| PATCH | `/brands/{id}` | Update brand |
| DELETE | `/brands/{id}` | Delete brand |

### Trends

| Method | Endpoint | Description |
|---|---|---|
| GET | `/trends` | List trends (filterable) |
| GET | `/trends/{id}` | Get trend details |
| POST | `/trends/refresh` | Trigger trend scraping |
| GET | `/trends/match/{brand_id}` | AI-powered brand-trend matching |

### Campaigns

| Method | Endpoint | Description |
|---|---|---|
| POST | `/campaigns/generate` | Generate campaign via AI pipeline |
| GET | `/campaigns` | List campaigns |
| GET | `/campaigns/{id}` | Get campaign with ad copies |
| DELETE | `/campaigns/{id}` | Delete campaign |
| POST | `/campaigns/{id}/export` | Export (JSON/CSV/PDF) |

Full interactive docs at **`/docs`** (Swagger UI) or **`/redoc`** (ReDoc).

---

## Database Schema

7 core tables with UUID primary keys:

- **users** — Auth, profiles
- **brands** — Brand profiles with pgvector embeddings (1536-dim)
- **trends** — Scraped & scored trends with embeddings
- **trend_metrics** — Time-series engagement data
- **brand_trend_matches** — AI-computed relevance scores
- **campaigns** — Generated campaign strategies
- **ad_copies** — Platform-specific ad variations

---

## Scoring Algorithms

**Trend Score:**
```
score = (velocity_norm × 0.35) + (volume_norm × 0.25) + (sentiment_magnitude × 0.15) + (recency_decay × 0.25)
recency_decay = exp(-0.1 × hours_since_first_seen)
```

**Brand-Trend Relevance:**
```
relevance = (semantic × 0.40) + (audience × 0.25) + (industry × 0.20) + (tone × 0.15)
threshold ≥ 0.65 to qualify
```

---

## Scaling Strategy

| Phase | Users | Key Changes |
|---|---|---|
| **1** | 0–10k | Single Postgres, app-level caching |
| **2** | 10k–50k | Read replicas, dedicated worker pool, CDN |
| **3** | 50k–100k+ | Connection pooling (PgBouncer), sharding, event-driven arch |

See [ARCHITECTURE.md](ARCHITECTURE.md) for full scaling roadmap.

---

## Environment Variables

See [.env.example](.env.example) for the complete list. Key variables:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `JWT_SECRET_KEY` | ✅ | Secret for JWT signing |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `ANTHROPIC_API_KEY` | ⬜ | Anthropic API key (optional) |
| `TWITTER_BEARER_TOKEN` | ⬜ | Twitter API v2 bearer token |
| `REDDIT_CLIENT_ID` | ⬜ | Reddit OAuth2 client ID |
| `META_ACCESS_TOKEN` | ⬜ | Meta Graph API token |

---

## Contributing

```bash
# Backend
cd backend
ruff check .            # lint
ruff format .           # format
pytest tests/ -v        # test

# Frontend
cd frontend
npm run lint            # lint
npx tsc --noEmit        # type-check
npm run build           # build
```

---

## License

MIT
