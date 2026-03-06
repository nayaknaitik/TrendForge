"""
Rate limiting middleware using Redis sliding window algorithm.

Implements per-user and per-IP rate limiting with configurable windows.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter backed by Redis.
    
    Falls back to in-memory tracking if Redis is unavailable.
    """

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis = redis_client
        self._fallback: dict[str, list[float]] = {}

    def _get_client_key(self, request: Request) -> str:
        """Extract rate limit key from request (user ID or IP)."""
        # Prefer authenticated user ID
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"ratelimit:user:{user_id}"
        
        # Fall back to IP
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
        return f"ratelimit:ip:{ip}"

    async def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Check rate limit using Redis sorted set sliding window."""
        now = time.time()
        window_start = now - window

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)  # Remove expired
        pipe.zadd(key, {str(now): now})  # Add current request
        pipe.zcard(key)  # Count requests in window
        pipe.expire(key, window)  # Set TTL
        results = await pipe.execute()

        request_count = results[2]
        remaining = max(0, limit - request_count)
        return request_count <= limit, remaining

    def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Fallback in-memory rate limiting."""
        now = time.time()
        if key not in self._fallback:
            self._fallback[key] = []

        # Clean old entries
        self._fallback[key] = [t for t in self._fallback[key] if t > now - window]
        self._fallback[key].append(now)

        count = len(self._fallback[key])
        remaining = max(0, limit - count)
        return count <= limit, remaining

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)

        key = self._get_client_key(request)
        limit = settings.rate_limit_per_minute
        window = 60  # 1 minute

        try:
            if self.redis:
                allowed, remaining = await self._check_rate_limit_redis(key, limit, window)
            else:
                allowed, remaining = self._check_rate_limit_memory(key, limit, window)
        except Exception:
            logger.warning("rate_limit_check_failed", key=key)
            # Fail open: allow request if rate limiter is broken
            allowed, remaining = True, limit

        if not allowed:
            logger.warning("rate_limit_exceeded", key=key)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please retry later.",
                    "retry_after_seconds": window,
                },
                headers={"Retry-After": str(window)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
