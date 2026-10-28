from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str
    timestamp: str


router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Service health check")
@router.get("/", response_model=HealthResponse, include_in_schema=False)
async def get_health() -> HealthResponse:
    """Return health status and runtime metadata for the backend service."""
    return HealthResponse(
        status="ok",
        service="devpath-ai-backend",
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

