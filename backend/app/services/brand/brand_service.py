"""
Brand Memory Service.

Manages brand profiles with:
- CRUD operations
- Vector embedding generation for semantic matching
- Profile serialization for AI agent context
- Embedding-based similarity search across brands
"""

from uuid import UUID

import httpx
import orjson
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.models import Brand
from app.schemas.schemas import BrandCreate, BrandUpdate

logger = get_logger(__name__)
settings = get_settings()


class BrandService:
    """
    Service layer for brand profile management.
    
    Handles:
    - CRUD with database
    - Embedding generation on create/update
    - Serialization to dict format expected by AI agents
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._embedding_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            timeout=30.0,
        )

    async def create_brand(self, owner_id: UUID, data: BrandCreate) -> Brand:
        """Create a new brand profile with embedding."""
        brand = Brand(
            owner_id=owner_id,
            name=data.name,
            industry=data.industry,
            description=data.description,
            target_audience=data.target_audience.model_dump(),
            brand_tone=data.brand_tone.value,
            brand_positioning=data.brand_positioning,
            product_details={"products": [p.model_dump() for p in data.product_details]},
            marketing_goals=[g.value for g in data.marketing_goals],
            brand_guidelines=data.brand_guidelines.model_dump(),
        )

        # Generate embedding from brand profile text
        embedding = await self._generate_brand_embedding(brand)
        if embedding:
            brand.embedding = embedding

        self.db.add(brand)
        await self.db.flush()
        await self.db.refresh(brand)

        logger.info("brand_created", brand_id=str(brand.id), name=brand.name)
        return brand

    async def update_brand(self, brand_id: UUID, owner_id: UUID, data: BrandUpdate) -> Brand:
        """Update a brand profile, regenerating embedding if content changed."""
        brand = await self._get_brand_or_raise(brand_id, owner_id)

        update_data = data.model_dump(exclude_unset=True)
        content_changed = False

        for field, value in update_data.items():
            if value is not None:
                if field == "target_audience":
                    setattr(brand, field, value.model_dump() if hasattr(value, "model_dump") else value)
                elif field == "brand_tone":
                    setattr(brand, field, value.value if hasattr(value, "value") else value)
                elif field == "product_details":
                    setattr(brand, field, {"products": [p.model_dump() if hasattr(p, "model_dump") else p for p in value]})
                elif field == "marketing_goals":
                    setattr(brand, field, [g.value if hasattr(g, "value") else g for g in value])
                elif field == "brand_guidelines":
                    setattr(brand, field, value.model_dump() if hasattr(value, "model_dump") else value)
                else:
                    setattr(brand, field, value)
                content_changed = True

        # Regenerate embedding if content changed
        if content_changed:
            embedding = await self._generate_brand_embedding(brand)
            if embedding:
                brand.embedding = embedding

        await self.db.flush()
        await self.db.refresh(brand)

        logger.info("brand_updated", brand_id=str(brand_id))
        return brand

    async def get_brand(self, brand_id: UUID, owner_id: UUID) -> Brand:
        """Get a brand by ID, verifying ownership."""
        return await self._get_brand_or_raise(brand_id, owner_id)

    async def list_brands(self, owner_id: UUID) -> list[Brand]:
        """List all brands for a user."""
        result = await self.db.execute(
            select(Brand)
            .where(Brand.owner_id == owner_id, Brand.is_active == True)
            .order_by(Brand.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_brand(self, brand_id: UUID, owner_id: UUID) -> None:
        """Soft-delete a brand."""
        brand = await self._get_brand_or_raise(brand_id, owner_id)
        brand.is_active = False
        await self.db.flush()
        logger.info("brand_deleted", brand_id=str(brand_id))

    def serialize_for_agents(self, brand: Brand) -> dict:
        """
        Serialize a brand to the dict format expected by AI agents.
        
        This is the canonical representation used across all agents.
        """
        return {
            "id": str(brand.id),
            "name": brand.name,
            "industry": brand.industry,
            "description": brand.description,
            "target_audience": brand.target_audience,
            "brand_tone": brand.brand_tone,
            "brand_positioning": brand.brand_positioning,
            "product_details": brand.product_details,
            "marketing_goals": brand.marketing_goals,
            "brand_guidelines": brand.brand_guidelines,
        }

    async def _get_brand_or_raise(self, brand_id: UUID, owner_id: UUID) -> Brand:
        """Get brand with ownership check."""
        result = await self.db.execute(
            select(Brand).where(
                Brand.id == brand_id,
                Brand.owner_id == owner_id,
                Brand.is_active == True,
            )
        )
        brand = result.scalar_one_or_none()
        if not brand:
            raise NotFoundError("Brand", str(brand_id))
        return brand

    async def _generate_brand_embedding(self, brand: Brand) -> list[float] | None:
        """
        Generate embedding from brand profile text.
        
        Combines key brand attributes into a paragraph for embedding.
        """
        if not settings.openai_api_key:
            return None

        # Build a rich text representation of the brand
        text = f"""
        Brand: {brand.name}
        Industry: {brand.industry}
        Description: {brand.description or ''}
        Positioning: {brand.brand_positioning or ''}
        Tone: {brand.brand_tone}
        Target Audience: {orjson.dumps(brand.target_audience).decode()}
        Products: {orjson.dumps(brand.product_details).decode()}
        Marketing Goals: {orjson.dumps(brand.marketing_goals).decode()}
        """.strip()

        try:
            response = await self._embedding_client.post(
                "/embeddings",
                json={
                    "input": text[:8000],
                    "model": settings.embedding_model,
                    "dimensions": settings.embedding_dimensions,
                },
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            logger.warning("brand_embedding_failed", error=str(e))
            return None

    async def close(self):
        await self._embedding_client.aclose()
