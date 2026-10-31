"""Health check API router."""

from fastapi import APIRouter
from app.core.model_loader import registry
from app.schemas.prediction_schema import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Returns the current health status of the API and model load state.
    """
    model_version = registry.version.get("model_version", "unknown") if registry.is_loaded() else "unknown"
    return HealthResponse(
        status="healthy" if registry.is_loaded() else "degraded",
        model_loaded=registry.is_loaded(),
        model_version=model_version,
    )
