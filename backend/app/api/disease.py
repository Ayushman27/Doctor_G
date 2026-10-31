"""Disease prediction API router."""

import logging
from fastapi import APIRouter, HTTPException
from app.core.model_loader import registry
from app.schemas.prediction_schema import SymptomPredictionRequest, DiseasePredictionResponse
from app.services.disease_service import get_available_symptoms, predict_disease_from_symptoms

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/disease", tags=["Disease Prediction"])


@router.get("/symptoms", tags=["Disease Prediction"])
async def get_symptoms():
    """
    Get all 133 supported symptoms formatted for UI select/search.
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI models not initialised.")
    return {
        "symptoms": get_available_symptoms(),
        "total": len(registry.disease_symptoms)
    }


@router.post("/predict", response_model=DiseasePredictionResponse, tags=["Disease Prediction"])
async def predict_disease(request: SymptomPredictionRequest) -> DiseasePredictionResponse:
    """
    Predict disease based on symptom indicators using Scikit-Learn Logistic Regression model.
    """
    if not registry.is_loaded() or not registry.disease_model:
        raise HTTPException(status_code=503, detail="Disease prediction model unavailable.")

    try:
        result = predict_disease_from_symptoms(
            symptoms=request.symptoms,
            top_k=request.top_k
        )
        return result
    except ValueError as exc:
        logger.warning("Disease prediction validation error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Disease prediction error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Disease prediction failed: {exc}") from exc
