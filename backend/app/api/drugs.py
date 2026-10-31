"""Drug candidate and OpenFDA API router."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from app.core.model_loader import registry
from app.services.drug_service import get_all_conditions, get_drug_candidates
from app.services.openfda_service import fetch_openfda_drug_info, search_openfda_by_condition
from app.schemas.prediction_schema import ConditionsResponse, DrugRecommendationResponse

router = APIRouter()


@router.get("/drugs/conditions", response_model=ConditionsResponse, tags=["Drugs"])
async def list_conditions() -> ConditionsResponse:
    """
    Returns all medical conditions available in the drug summary dataset.
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI models are not loaded.")

    conditions = get_all_conditions()
    return ConditionsResponse(conditions=conditions, total=len(conditions))


@router.get("/drugs/recommendations", response_model=DrugRecommendationResponse, tags=["Drugs"])
async def get_recommendations(
    condition: str = Query(..., description="Medical condition name"),
    top_k: int = Query(5, ge=1, le=20, description="Number of candidates to return"),
) -> DrugRecommendationResponse:
    """
    Returns the top-k historical drug candidates for a given condition,
    ranked by composite candidate score.
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI models are not loaded.")

    candidates = get_drug_candidates(condition=condition, top_k=top_k)

    return DrugRecommendationResponse(
        condition=condition,
        candidates=candidates,
    )


@router.get("/drugs/openfda/info", tags=["OpenFDA Drug Information"])
async def get_openfda_drug_info(
    drug_name: str = Query(..., description="Brand or generic drug name")
) -> Dict[str, Any]:
    """
    Query the official US Food & Drug Administration (OpenFDA) API for drug label information,
    including indications, usage, active ingredients, and safety warnings.
    """
    info = fetch_openfda_drug_info(drug_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"No OpenFDA label records found for '{drug_name}'.")
    return info


@router.get("/drugs/openfda/search", tags=["OpenFDA Drug Information"])
async def search_openfda_drugs(
    condition: str = Query(..., description="Medical condition or indication keyword"),
    limit: int = Query(3, ge=1, le=10)
) -> Dict[str, Any]:
    """
    Search OpenFDA for official FDA-labeled drug products indicated for a given condition.
    """
    results = search_openfda_by_condition(condition=condition, limit=limit)
    return {
        "condition": condition,
        "results": results,
        "total": len(results)
    }
