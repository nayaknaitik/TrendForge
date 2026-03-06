"""
TrendForge Core Configuration.

All settings are loaded from environment variables with sensible defaults.
Uses pydantic-settings for type-safe configuration with validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ─────────────────────────────────────────────────────────────
    app_name: str = "TrendForge"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # ── Server ──────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Database ────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://trendforge:trendforge@localhost:5432/trendforge"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # ── Redis ───────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300  # 5 minutes default

    # ── Auth ────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-64"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── AI / LLM ────────────────────────────────────────────────────────
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    default_llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ── Social API Keys ─────────────────────────────────────────────────
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "TrendForge/0.1 (by /u/trendforge)"
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_access_token: str = ""

    # ── Rate Limiting ───────────────────────────────────────────────────
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # ── Object Storage ──────────────────────────────────────────────────
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "trendforge-assets"

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field
    @property
    def async_database_url(self) -> str:
        """Ensure async driver is used."""
        url = self.database_url
        if "postgresql://" in url and "asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        return url


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
