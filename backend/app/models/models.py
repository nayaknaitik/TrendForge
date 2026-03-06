"""
SQLAlchemy models — core domain entities.

Database Schema Design:
─────────────────────────
users             ← Authentication & authorization
brands            ← Brand profiles (1:many per user)
trends            ← Ingested social media trends
trend_metrics     ← Time-series engagement data
campaigns         ← Generated campaign strategies
ad_copies         ← Individual ad variations
brand_trend_match ← Relevance scores between brands and trends

Vector columns use pgvector for semantic search.
All tables use UUID primary keys for distributed-friendly IDs.
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


# ── Utility ─────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ── User ────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tier: Mapped[str] = mapped_column(
        Enum("free", "pro", "enterprise", name="user_tier"),
        default="free",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    brands: Mapped[list["Brand"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# ── Brand Profile ───────────────────────────────────────────────────────

class Brand(Base):
    """
    A brand profile containing all context needed for AI agents
    to generate relevant, on-brand content.
    """
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    industry: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Brand positioning
    target_audience: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"age_range": "25-34", "interests": ["tech", "fitness"], "platforms": ["instagram", "twitter"]}

    brand_tone: Mapped[str] = mapped_column(
        Enum("professional", "casual", "witty", "bold", "inspirational", "edgy", name="brand_tone"),
        default="professional",
    )
    brand_positioning: Mapped[str] = mapped_column(Text, nullable=True)
    # Example: "Premium DTC fitness brand for urban millennials"

    product_details: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"products": [{"name": "ProFit Band", "price": 49.99, "category": "wearable"}]}

    marketing_goals: Mapped[list] = mapped_column(JSONB, default=list)
    # Example: ["brand_awareness", "lead_generation", "sales_conversion"]

    brand_guidelines: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"colors": ["#FF5733"], "forbidden_words": ["cheap"], "hashtags": ["#FitLife"]}

    # Vector embedding of brand profile for semantic matching
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="brands")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


# ── Trend ───────────────────────────────────────────────────────────────

class Trend(Base):
    """
    A trending topic or content piece ingested from social media APIs.
    
    Trend Scoring Algorithm:
    ────────────────────────
    score = (engagement_velocity * 0.35)
          + (volume_normalized * 0.25)
          + (sentiment_magnitude * 0.15)
          + (recency_decay * 0.25)
    
    Where recency_decay = exp(-λ * hours_since_detection)
    λ = 0.1 (half-life ≈ 7 hours)
    """
    __tablename__ = "trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    
    # Source identification
    platform: Mapped[str] = mapped_column(
        Enum("twitter", "reddit", "instagram", "facebook", name="platform_type"),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(String(256), nullable=True)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=True)

    # Content
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    raw_content: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Classification
    category: Mapped[str] = mapped_column(String(128), nullable=True)
    topics: Mapped[list] = mapped_column(JSONB, default=list)
    # Example: ["AI", "productivity", "remote work"]

    keywords: Mapped[list] = mapped_column(JSONB, default=list)
    # Example: ["chatgpt", "automation", "workflow"]

    content_format: Mapped[str] = mapped_column(
        Enum("text", "meme", "thread", "carousel", "video", "image", "poll", name="content_format"),
        default="text",
    )

    # Sentiment
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)  # -1.0 to 1.0
    sentiment_label: Mapped[str] = mapped_column(
        Enum("very_negative", "negative", "neutral", "positive", "very_positive", name="sentiment_label"),
        default="neutral",
    )

    # Engagement metrics
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_velocity: Mapped[float] = mapped_column(Float, default=0.0)  # Change rate per hour
    volume: Mapped[int] = mapped_column(Integer, default=0)  # Number of posts/mentions
    
    # Composite trend score (calculated)
    trend_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    # Audience insights
    audience_clusters: Mapped[list] = mapped_column(JSONB, default=list)
    # Example: [{"cluster": "tech_enthusiasts", "percentage": 0.45}, ...]

    # Vector embedding for semantic search
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True)

    # Lifecycle
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_trends_platform_score", "platform", "trend_score"),
        Index("ix_trends_detected_at", "detected_at"),
        UniqueConstraint("platform", "external_id", name="uq_trend_platform_external"),
    )


class TrendMetrics(Base):
    """Time-series engagement tracking for trends."""
    __tablename__ = "trend_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    trend_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trends.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)

    __table_args__ = (
        Index("ix_trend_metrics_trend_ts", "trend_id", "timestamp"),
    )


# ── Brand-Trend Matching ───────────────────────────────────────────────

class BrandTrendMatch(Base):
    """
    Relevance score between a brand and a trend.
    
    Brand-to-Trend Matching Algorithm:
    ────────────────────────────────────
    relevance = (cosine_similarity(brand_embedding, trend_embedding) * 0.40)
              + (audience_overlap_score * 0.25)
              + (industry_match_score * 0.20)
              + (tone_compatibility_score * 0.15)
    
    Threshold: relevance >= 0.65 to be shown to user
    """
    __tablename__ = "brand_trend_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    trend_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trends.id", ondelete="CASCADE"), nullable=False
    )

    # Scoring breakdown
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_similarity: Mapped[float] = mapped_column(Float, default=0.0)
    audience_overlap: Mapped[float] = mapped_column(Float, default=0.0)
    industry_match: Mapped[float] = mapped_column(Float, default=0.0)
    tone_compatibility: Mapped[float] = mapped_column(Float, default=0.0)

    # Agent reasoning
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    is_relevant: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        UniqueConstraint("brand_id", "trend_id", name="uq_brand_trend"),
        Index("ix_brand_trend_relevance", "brand_id", "relevance_score"),
    )


# ── Campaign ────────────────────────────────────────────────────────────

class Campaign(Base):
    """
    A generated marketing campaign strategy tied to a brand and optionally a trend.
    """
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    trend_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trends.id", ondelete="SET NULL"), nullable=True
    )

    # Campaign details
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    objective: Mapped[str] = mapped_column(
        Enum(
            "brand_awareness", "engagement", "lead_generation",
            "sales_conversion", "app_installs", "traffic",
            name="campaign_objective",
        ),
        nullable=False,
    )
    
    # Strategy (generated by Campaign Strategist Agent)
    strategy: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {
    #   "angle": "leverage AI productivity trend for fitness positioning",
    #   "hook_strategy": "contrast AI automation with physical fitness discipline",
    #   "target_platforms": ["instagram", "twitter"],
    #   "content_pillars": ["transformation", "discipline", "tech-fitness balance"],
    #   "campaign_duration_days": 7
    # }

    # Performance estimate (from Performance Heuristic Agent)
    estimated_engagement: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {
    #   "predicted_engagement_rate": 0.045,
    #   "confidence_level": "medium",
    #   "reasoning": "Trend has high velocity + brand tone alignment is strong"
    # }

    status: Mapped[str] = mapped_column(
        Enum("draft", "generating", "ready", "active", "paused", "completed", name="campaign_status"),
        default="draft",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="campaigns")
    brand: Mapped["Brand"] = relationship(back_populates="campaigns")
    ad_copies: Mapped[list["AdCopy"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


# ── Ad Copy ─────────────────────────────────────────────────────────────

class AdCopy(Base):
    """
    An individual ad variation generated by the Copy Generator Agent.
    Multiple copies per campaign, each tailored to a specific platform.
    """
    __tablename__ = "ad_copies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )

    # Platform targeting
    platform: Mapped[str] = mapped_column(
        Enum("twitter", "reddit", "instagram", "facebook", "linkedin", "tiktok", name="ad_platform"),
        nullable=False,
    )

    # Content
    hook: Mapped[str] = mapped_column(Text, nullable=False)  # Opening line / attention grab
    body: Mapped[str] = mapped_column(Text, nullable=False)  # Main copy
    cta: Mapped[str] = mapped_column(String(256), nullable=False)  # Call to action
    hashtags: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Format-specific fields
    format_type: Mapped[str] = mapped_column(
        Enum("single_post", "thread", "carousel", "story", "reel_script", "ad_copy", name="ad_format"),
        default="single_post",
    )
    
    # For carousels/threads: ordered slides/posts
    slides: Mapped[list] = mapped_column(JSONB, default=list)
    # Example: [{"slide_num": 1, "headline": "...", "body": "..."}, ...]

    # Performance heuristic
    predicted_engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    variation_label: Mapped[str] = mapped_column(String(64), nullable=True)
    # Example: "version_a", "version_b", "aggressive", "subtle"

    # Export
    exported: Mapped[bool] = mapped_column(Boolean, default=False)
    export_format: Mapped[str] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="ad_copies")

    __table_args__ = (
        Index("ix_ad_copies_campaign_platform", "campaign_id", "platform"),
    )
