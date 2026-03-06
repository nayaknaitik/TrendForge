"""
Brand profile API endpoints.

POST   /brands          — Create brand
GET    /brands          — List brands
GET    /brands/{id}     — Get brand
PATCH  /brands/{id}     — Update brand
DELETE /brands/{id}     — Delete brand
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.schemas import BrandCreate, BrandResponse, BrandUpdate
from app.services.brand.brand_service import BrandService

router = APIRouter(prefix="/brands", tags=["brands"])


def _get_service(db: AsyncSession = Depends(get_db)) -> BrandService:
    return BrandService(db)


@router.post("", response_model=BrandResponse, status_code=201)
async def create_brand(
    data: BrandCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: BrandService = Depends(_get_service),
):
    """Create a new brand profile."""
    brand = await service.create_brand(user_id, data)
    return brand


@router.get("", response_model=list[BrandResponse])
async def list_brands(
    user_id: UUID = Depends(get_current_user_id),
    service: BrandService = Depends(_get_service),
):
    """List all brands for the current user."""
    return await service.list_brands(user_id)


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: BrandService = Depends(_get_service),
):
    """Get a specific brand profile."""
    return await service.get_brand(brand_id, user_id)


@router.patch("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    data: BrandUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: BrandService = Depends(_get_service),
):
    """Update a brand profile."""
    return await service.update_brand(brand_id, user_id, data)


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(
    brand_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: BrandService = Depends(_get_service),
):
    """Delete a brand profile (soft delete)."""
    await service.delete_brand(brand_id, user_id)
