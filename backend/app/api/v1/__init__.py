"""API v1 router configuration."""
from fastapi import APIRouter
from app.api.v1 import health, repomind

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(repomind.router, prefix="/repomind", tags=["RepoMind"])
