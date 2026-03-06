"""
V1 API router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.brands import router as brands_router
from app.api.v1.endpoints.trends import router as trends_router
from app.api.v1.endpoints.campaigns import router as campaigns_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(brands_router)
api_v1_router.include_router(trends_router)
api_v1_router.include_router(campaigns_router)
