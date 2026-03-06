"""
Redis client management.

Provides async Redis client for caching, rate limiting, and pub/sub.
"""

import redis.asyncio as redis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get the Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def cache_get(key: str) -> str | None:
    """Get a value from cache."""
    client = await get_redis()
    try:
        return await client.get(key)
    except Exception:
        logger.warning("redis_cache_get_failed", key=key)
        return None


async def cache_set(key: str, value: str, ttl: int | None = None) -> None:
    """Set a value in cache with optional TTL."""
    client = await get_redis()
    ttl = ttl or settings.redis_cache_ttl
    try:
        await client.set(key, value, ex=ttl)
    except Exception:
        logger.warning("redis_cache_set_failed", key=key)


async def cache_delete(key: str) -> None:
    """Delete a value from cache."""
    client = await get_redis()
    try:
        await client.delete(key)
    except Exception:
        logger.warning("redis_cache_delete_failed", key=key)
