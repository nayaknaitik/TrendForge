"""
Campaigns API endpoints.

POST /campaigns/generate      — Generate a campaign from trend + brand
GET  /campaigns               — List user campaigns
GET  /campaigns/{id}          — Get campaign detail + ad copies
DELETE /campaigns/{id}        — Delete campaign
POST /campaigns/{id}/export   — Export campaign assets
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.models import Campaign, AdCopy, Brand
from app.schemas.schemas import (
    CampaignGenerateRequest,
    CampaignResponse,
    CampaignListResponse,
    AdCopyResponse,
)
from app.services.campaign.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
logger = get_logger(__name__)


@router.post("/generate", response_model=CampaignResponse, status_code=201)
async def generate_campaign(
    request: CampaignGenerateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a full campaign for a brand + trend combination.

    Runs the AI multi-agent pipeline:
      1. Classify the trend
      2. Score brand relevance
      3. Create campaign strategy
      4. Generate platform-specific ad copies
      5. Predict engagement performance
    """
    # Verify brand belongs to user
    result = await db.execute(
        select(Brand).where(Brand.id == request.brand_id, Brand.user_id == user_id)
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise NotFoundError("Brand", str(request.brand_id))

    campaign_service = CampaignService(db)
    campaign = await campaign_service.generate_campaign(
        brand_id=request.brand_id,
        trend_id=request.trend_id,
        user_id=user_id,
        target_platforms=request.target_platforms,
        objective=request.objective,
    )

    # Load ad copies for response
    ad_result = await db.execute(
        select(AdCopy).where(AdCopy.campaign_id == campaign.id)
    )
    ad_copies = list(ad_result.scalars().all())

    response = CampaignResponse.model_validate(campaign)
    response.ad_copies = [AdCopyResponse.model_validate(a) for a in ad_copies]

    logger.info(
        "campaign_generated",
        campaign_id=str(campaign.id),
        brand_id=str(request.brand_id),
        ad_copies=len(ad_copies),
    )
    return response


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    status: str | None = None,
    brand_id: UUID | None = None,
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List campaigns for the authenticated user."""
    conditions = [Campaign.user_id == user_id]

    if status:
        conditions.append(Campaign.status == status)
    if brand_id:
        conditions.append(Campaign.brand_id == brand_id)

    from sqlalchemy import and_

    # Count
    count_result = await db.execute(
        select(Campaign.id).where(and_(*conditions))
    )
    total = len(count_result.all())

    # Fetch page
    query = (
        select(Campaign)
        .where(and_(*conditions))
        .order_by(Campaign.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    campaigns = list(result.scalars().all())

    return CampaignListResponse(
        campaigns=[CampaignResponse.model_validate(c) for c in campaigns],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific campaign with its ad copies."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign", str(campaign_id))
    if campaign.user_id != user_id:
        raise AuthorizationError("Not authorized to access this campaign")

    # Load ad copies
    ad_result = await db.execute(
        select(AdCopy).where(AdCopy.campaign_id == campaign_id)
    )
    ad_copies = list(ad_result.scalars().all())

    response = CampaignResponse.model_validate(campaign)
    response.ad_copies = [AdCopyResponse.model_validate(a) for a in ad_copies]
    return response


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a campaign and its ad copies."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign", str(campaign_id))
    if campaign.user_id != user_id:
        raise AuthorizationError("Not authorized to delete this campaign")

    # Delete ad copies first
    ad_result = await db.execute(
        select(AdCopy).where(AdCopy.campaign_id == campaign_id)
    )
    for ad in ad_result.scalars().all():
        await db.delete(ad)

    await db.delete(campaign)
    await db.flush()

    logger.info("campaign_deleted", campaign_id=str(campaign_id))


@router.post("/{campaign_id}/export", response_model=dict)
async def export_campaign(
    campaign_id: UUID,
    export_format: str = Query(default="json", regex="^(json|csv|pdf)$"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Export a campaign's ad copies in the requested format.

    Supported formats: json, csv, pdf.
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign", str(campaign_id))
    if campaign.user_id != user_id:
        raise AuthorizationError("Not authorized to export this campaign")

    # Load ad copies
    ad_result = await db.execute(
        select(AdCopy).where(AdCopy.campaign_id == campaign_id)
    )
    ad_copies = list(ad_result.scalars().all())

    if export_format == "json":
        export_data = {
            "campaign": {
                "id": str(campaign.id),
                "campaign_name": campaign.campaign_name,
                "campaign_angle": campaign.campaign_angle,
                "status": campaign.status,
                "strategy": campaign.strategy,
                "estimated_engagement": campaign.estimated_engagement,
                "created_at": campaign.created_at.isoformat(),
            },
            "ad_copies": [
                {
                    "platform": ad.platform,
                    "format": ad.ad_format,
                    "hook": ad.hook,
                    "body": ad.body,
                    "cta": ad.cta,
                    "hashtags": ad.hashtags,
                    "predicted_engagement_rate": ad.predicted_engagement_rate,
                    "slides": ad.slides,
                }
                for ad in ad_copies
            ],
        }
        return {"format": "json", "data": export_data}

    elif export_format == "csv":
        # Return CSV-ready rows
        rows = []
        for ad in ad_copies:
            rows.append({
                "platform": ad.platform,
                "format": ad.ad_format,
                "hook": ad.hook,
                "body": ad.body,
                "cta": ad.cta,
                "hashtags": ", ".join(ad.hashtags) if ad.hashtags else "",
                "engagement_rate": ad.predicted_engagement_rate,
            })
        return {"format": "csv", "rows": rows, "campaign_name": campaign.campaign_name}

    else:
        # PDF export placeholder — integrate with e.g. WeasyPrint in production
        return {
            "format": "pdf",
            "message": "PDF export coming soon. Use JSON or CSV for now.",
            "campaign_name": campaign.campaign_name,
        }
