"""Model information API router."""

from fastapi import APIRouter, HTTPException
from app.core.model_loader import registry
from app.schemas.prediction_schema import ModelInfoResponse

router = APIRouter()


@router.get("/models/info", response_model=ModelInfoResponse, tags=["Models"])
async def get_model_info() -> ModelInfoResponse:
    """
    Returns model metadata, evaluation metrics, version info,
    and a summary of the feature set.
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI models are not loaded.")

    feature_summary = {
        "total_original_features": len(registry.original_features),
        "total_processed_features": len(registry.feature_metadata.get("processed_features", [])),
        "numerical_features_count": len(registry.numerical_features),
        "categorical_features_count": len(registry.categorical_features),
        "original_feature_names": registry.original_features,
    }

    return ModelInfoResponse(
        metadata=registry.metadata,
        metrics=registry.metrics,
        version=registry.version,
        feature_summary=feature_summary,
    )
