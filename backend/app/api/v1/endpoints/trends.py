"""
Trends API endpoints.

GET  /trends              — List active trends (with filters)
GET  /trends/{id}         — Get trend details
POST /trends/refresh      — Trigger trend ingestion
GET  /trends/match/{brand_id} — Get trends matched to a brand
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.models import Trend
from app.schemas.schemas import (
    PlatformType,
    TrendFilter,
    TrendListResponse,
    TrendResponse,
)
from app.services.scraper.social_scraper import ScraperAggregator
from app.services.trends.processor import TrendProcessor
from app.services.ai_agents.orchestrator import AgentOrchestrator
from app.services.brand.brand_service import BrandService

router = APIRouter(prefix="/trends", tags=["trends"])
logger = get_logger(__name__)


@router.get("", response_model=TrendListResponse)
async def list_trends(
    platforms: list[PlatformType] | None = Query(None),
    min_score: float = 0.0,
    category: str | None = None,
    hours_ago: int = 24,
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    List active trends with filtering.
    
    Supports filtering by platform, minimum score, category, and time window.
    Results are sorted by trend_score descending.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

    conditions = [
        Trend.is_active == True,
        Trend.detected_at >= cutoff,
        Trend.trend_score >= min_score,
    ]

    if platforms:
        conditions.append(Trend.platform.in_([p.value for p in platforms]))
    if category:
        conditions.append(Trend.category == category)

    # Count total
    count_query = select(Trend.id).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = len(count_result.all())

    # Fetch page
    query = (
        select(Trend)
        .where(and_(*conditions))
        .order_by(Trend.trend_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    trends = list(result.scalars().all())

    return TrendListResponse(
        trends=[TrendResponse.model_validate(t) for t in trends],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(
    trend_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trend by ID."""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise NotFoundError("Trend", str(trend_id))
    return trend


@router.post("/refresh", response_model=dict)
async def refresh_trends(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger trend ingestion from all configured platforms.
    
    In production, this would be a background task.
    For MVP, runs synchronously with a timeout.
    """
    scraper = ScraperAggregator()
    processor = TrendProcessor()

    try:
        # Fetch raw trends
        raw_trends = await scraper.fetch_all_trending(limit_per_platform=30)

        if not raw_trends:
            return {"message": "No trends fetched", "count": 0}

        # Process trends
        processed = await processor.process_batch(raw_trends)

        # Persist to database
        count = 0
        for trend_data in processed:
            # Upsert logic — skip if external_id already exists
            existing = await db.execute(
                select(Trend).where(
                    Trend.platform == trend_data["platform"],
                    Trend.external_id == trend_data.get("external_id"),
                )
            )
            if existing.scalar_one_or_none():
                continue

            trend = Trend(
                platform=trend_data["platform"],
                external_id=trend_data.get("external_id"),
                source_url=trend_data.get("source_url"),
                title=trend_data["title"],
                description=trend_data.get("description", ""),
                raw_content=trend_data.get("raw_content", {}),
                topics=trend_data.get("topics", []),
                keywords=trend_data.get("keywords", []),
                content_format=trend_data.get("content_format", "text"),
                sentiment_score=trend_data.get("sentiment_score", 0.0),
                sentiment_label=trend_data.get("sentiment_label", "neutral"),
                engagement_score=trend_data.get("engagement_score", 0.0),
                engagement_velocity=trend_data.get("engagement_velocity", 0.0),
                volume=trend_data.get("volume", 0),
                trend_score=trend_data.get("trend_score", 0.0),
                audience_clusters=trend_data.get("audience_clusters", []),
                embedding=trend_data.get("embedding"),
            )
            db.add(trend)
            count += 1

        await db.flush()

        logger.info("trends_refreshed", new_trends=count, total_processed=len(processed))
        return {"message": "Trends refreshed", "new_trends": count, "total_processed": len(processed)}

    finally:
        await scraper.close_all()
        await processor.close()


@router.get("/match/{brand_id}", response_model=list[dict])
async def match_trends_to_brand(
    brand_id: UUID,
    min_relevance: float = Query(default=0.65, ge=0.0, le=1.0),
    limit: int = Query(default=10, le=50),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Find trends most relevant to a specific brand.
    
    Uses the Brand Relevance Agent to score and rank trends.
    """
    # Load brand
    brand_service = BrandService(db)
    brand = await brand_service.get_brand(brand_id, user_id)
    brand_profile = brand_service.serialize_for_agents(brand)

    # Load recent active trends
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    result = await db.execute(
        select(Trend)
        .where(Trend.is_active == True, Trend.detected_at >= cutoff)
        .order_by(Trend.trend_score.desc())
        .limit(limit * 3)  # Fetch extra since some will be filtered
    )
    trends = list(result.scalars().all())

    if not trends:
        return []

    # Serialize trends for agent
    trend_dicts = []
    for t in trends:
        trend_dicts.append({
            "id": str(t.id),
            "platform": t.platform,
            "title": t.title,
            "description": t.description,
            "topics": t.topics,
            "keywords": t.keywords,
            "category": t.category,
            "content_format": t.content_format,
            "sentiment_score": t.sentiment_score,
            "sentiment_label": t.sentiment_label,
            "engagement_score": t.engagement_score,
            "engagement_velocity": t.engagement_velocity,
            "trend_score": t.trend_score,
            "audience_clusters": t.audience_clusters,
        })

    # Score against brand using AI
    orchestrator = AgentOrchestrator()
    matched = await orchestrator.batch_score_trends(
        brand_profile=brand_profile,
        trends=trend_dicts,
        min_relevance=min_relevance,
    )

    return matched[:limit]
