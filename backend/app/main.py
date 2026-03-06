"""
TrendForge — Real-Time AI Marketing Intelligence & Ad Generation System

Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import RateLimitMiddleware
from app.db.session import init_db, async_engine
from app.db.redis import get_redis

settings = get_settings()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # --- Startup ---
    setup_logging()
    logger.info(
        "trendforge_starting",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )

    # Initialise DB (creates tables + pgvector extension on first run)
    await init_db()
    logger.info("database_initialised")

    # Warm-up Redis connection
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("redis_connected")
    except Exception as exc:
        logger.warning("redis_connection_failed", error=str(exc))

    logger.info("trendforge_ready")

    yield

    # --- Shutdown ---
    logger.info("trendforge_shutting_down")

    # Close async engine
    await async_engine.dispose()
    logger.info("database_disconnected")

    # Close Redis
    try:
        redis = await get_redis()
        await redis.close()
        logger.info("redis_disconnected")
    except Exception:
        pass

    logger.info("trendforge_stopped")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="TrendForge API",
    description=(
        "Real-Time AI Marketing Intelligence & Ad Generation System. "
        "Collect trends, match them to brands, and generate high-converting "
        "platform-specific ad campaigns using a multi-agent AI pipeline."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)


# Request ID / timing middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Attach request_id and log request timing."""
    import uuid
    import time

    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
        request_id=request_id,
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
register_exception_handlers(app)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_v1_router)


# ---------------------------------------------------------------------------
# Health check / meta
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"])
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "trendforge-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/deep", tags=["meta"])
async def deep_health_check():
    """Deep health check — verifies DB and Redis connectivity."""
    checks = {"database": "unknown", "redis": "unknown"}

    # DB check
    try:
        from sqlalchemy import text
        from app.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as exc:
        checks["database"] = f"unhealthy: {exc}"

    # Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as exc:
        checks["redis"] = f"unhealthy: {exc}"

    overall = "healthy" if all(v == "healthy" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/", tags=["meta"])
async def root():
    return {
        "service": "TrendForge API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Docs disabled in production",
    }
