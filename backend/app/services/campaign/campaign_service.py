"""
Campaign Generator Service.

Orchestrates the full campaign lifecycle:
1. Accept user request (brand + trend + objective)
2. Run AI agent pipeline
3. Persist campaign + ad copies to database
4. Return results

This service is the bridge between the API layer and the AI agent system.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.models import AdCopy, Brand, Campaign, Trend
from app.schemas.schemas import CampaignCreate
from app.services.ai_agents.orchestrator import AgentOrchestrator
from app.services.brand.brand_service import BrandService

logger = get_logger(__name__)


class CampaignService:
    """
    Service layer for campaign generation and management.
    
    Bridges:
    - API routes → AI agent pipeline → Database persistence
    """

    def __init__(self, db: AsyncSession, orchestrator: AgentOrchestrator | None = None):
        self.db = db
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.brand_service = BrandService(db)

    async def generate_campaign(self, user_id: UUID, data: CampaignCreate) -> Campaign:
        """
        Generate a complete campaign using the AI pipeline.
        
        Flow:
        1. Load brand and trend from database
        2. Serialize for AI agents
        3. Run orchestrator pipeline
        4. Persist results
        """
        # Load brand
        brand = await self.brand_service.get_brand(data.brand_id, user_id)
        brand_profile = self.brand_service.serialize_for_agents(brand)

        # Load trend (optional — campaigns can exist without a trend)
        trend_data = {}
        if data.trend_id:
            result = await self.db.execute(
                select(Trend).where(Trend.id == data.trend_id)
            )
            trend = result.scalar_one_or_none()
            if not trend:
                raise NotFoundError("Trend", str(data.trend_id))
            trend_data = self._serialize_trend(trend)

        # Create campaign record in "generating" status
        campaign = Campaign(
            user_id=user_id,
            brand_id=data.brand_id,
            trend_id=data.trend_id,
            name=data.name,
            objective=data.objective.value,
            status="generating",
        )
        self.db.add(campaign)
        await self.db.flush()

        try:
            # Run AI pipeline
            target_platforms = [p.value for p in data.target_platforms] if data.target_platforms else None

            result = await self.orchestrator.generate_campaign(
                brand_profile=brand_profile,
                trend_data=trend_data,
                objective=data.objective.value,
                target_platforms=target_platforms,
                num_variations=3,
                custom_instructions=data.custom_instructions,
            )

            if result["status"] == "rejected":
                campaign.status = "draft"
                campaign.strategy = {"rejected": True, "reason": result["reason"]}
                campaign.estimated_engagement = {}
            else:
                campaign.status = "ready"
                campaign.strategy = result.get("strategy", {})

                # Persist ad copies
                for copy_data in result.get("ad_copies", []):
                    perf = copy_data.get("performance", {})
                    ad_copy = AdCopy(
                        campaign_id=campaign.id,
                        platform=copy_data.get("platform", "twitter"),
                        hook=copy_data.get("hook", ""),
                        body=copy_data.get("body", ""),
                        cta=copy_data.get("cta", "Learn more"),
                        hashtags=copy_data.get("hashtags", []),
                        format_type=copy_data.get("format_type", "single_post"),
                        slides=copy_data.get("slides", []),
                        predicted_engagement_rate=perf.get("predicted_engagement_rate", 0.0),
                        variation_label=copy_data.get("variation_label"),
                    )
                    self.db.add(ad_copy)

                # Set estimated engagement from the best performing copy
                if result.get("ad_copies"):
                    best = result["ad_copies"][0]
                    campaign.estimated_engagement = best.get("performance", {})

            await self.db.flush()
            await self.db.refresh(campaign)

            logger.info(
                "campaign_generated",
                campaign_id=str(campaign.id),
                status=campaign.status,
                copies=len(result.get("ad_copies", [])),
            )

        except Exception as e:
            campaign.status = "draft"
            campaign.strategy = {"error": str(e)}
            await self.db.flush()
            logger.error("campaign_generation_failed", campaign_id=str(campaign.id), error=str(e))
            raise

        return campaign

    async def get_campaign(self, campaign_id: UUID, user_id: UUID) -> Campaign:
        """Get a campaign with its ad copies."""
        result = await self.db.execute(
            select(Campaign)
            .options(selectinload(Campaign.ad_copies))
            .where(Campaign.id == campaign_id, Campaign.user_id == user_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise NotFoundError("Campaign", str(campaign_id))
        return campaign

    async def list_campaigns(self, user_id: UUID, brand_id: UUID | None = None) -> list[Campaign]:
        """List campaigns for a user, optionally filtered by brand."""
        query = (
            select(Campaign)
            .options(selectinload(Campaign.ad_copies))
            .where(Campaign.user_id == user_id)
            .order_by(Campaign.created_at.desc())
        )
        if brand_id:
            query = query.where(Campaign.brand_id == brand_id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_campaign(self, campaign_id: UUID, user_id: UUID) -> None:
        """Delete a campaign and its ad copies."""
        campaign = await self.get_campaign(campaign_id, user_id)
        await self.db.delete(campaign)
        await self.db.flush()
        logger.info("campaign_deleted", campaign_id=str(campaign_id))

    def _serialize_trend(self, trend: Trend) -> dict:
        """Serialize a trend for AI agent consumption."""
        return {
            "id": str(trend.id),
            "platform": trend.platform,
            "title": trend.title,
            "description": trend.description,
            "topics": trend.topics,
            "keywords": trend.keywords,
            "category": trend.category,
            "content_format": trend.content_format,
            "sentiment_score": trend.sentiment_score,
            "sentiment_label": trend.sentiment_label,
            "engagement_score": trend.engagement_score,
            "engagement_velocity": trend.engagement_velocity,
            "volume": trend.volume,
            "trend_score": trend.trend_score,
            "audience_clusters": trend.audience_clusters,
        }
