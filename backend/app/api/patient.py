"""Patient prediction API router."""

import logging
from fastapi import APIRouter, HTTPException
from app.core.model_loader import registry
from app.schemas.patient_schema import PredictRequest, AnalysisRequest
from app.schemas.prediction_schema import PredictionResult, AnalysisResponse, ClinicalGuidance, DietPlan
from app.services.patient_service import build_patient_feature_dict
from app.services.prediction_service import predict_risk
from app.services.drug_service import get_drug_candidates
from app.services.clinical_rules import get_clinical_guidance

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/patient/predict", response_model=PredictionResult, tags=["Patient"])
async def predict_patient(request: PredictRequest) -> PredictionResult:
    """
    Perform patient risk stratification using the XGBoost model.
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI model is currently unavailable. Please contact the system administrator.")

    try:
        feature_dict = build_patient_feature_dict(request.patient_data)
        result = predict_risk(feature_dict)
        return result
    except ValueError as exc:
        logger.warning("Patient prediction validation error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Patient prediction error: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction failed. Please check your input data.") from exc


@router.post("/analysis", response_model=AnalysisResponse, tags=["Analysis"])
async def full_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """
    Combined endpoint:
      1. Patient Risk Prediction (XGBoost) -> Risk Class + Probabilities
      2. Severity Mapping -> LOW (Mild Risk), MEDIUM (Moderate Risk), HIGH (Critical Risk)
      3. Disease & Cause Analysis -> Clinical rules engine
      4. Diet & Lifestyle Guidance -> Recommended vs Foods to avoid
      5. Historical Drug Candidates -> Ranked from drug_summary.pkl
    """
    if not registry.is_loaded():
        raise HTTPException(status_code=503, detail="AI model is currently unavailable. Please contact the system administrator.")

    try:
        # Step 1: Risk prediction
        feature_dict = build_patient_feature_dict(request.patient_data)
        prediction = predict_risk(feature_dict)

        # Step 2: Severity mapping from risk class
        severity_map = {
            "LOW": "Mild Readmission & Complication Risk",
            "MEDIUM": "Moderate Severity & Hospitalization Risk",
            "HIGH": "High Severity / Critical Risk"
        }
        severity_str = severity_map.get(prediction.risk_label, "Moderate Severity")

        # Step 3: Clinical Guidance (Disease, Causes, Test Insights, Diet, Action Guidelines)
        patient_dict = request.patient_data.model_dump() if hasattr(request.patient_data, "model_dump") else dict(request.patient_data)
        guidance_raw = get_clinical_guidance(condition=request.condition, patient_data=patient_dict)

        guidance = ClinicalGuidance(
            disease_name=guidance_raw["disease_name"],
            severity=severity_str,
            causes=guidance_raw["causes"],
            test_insights=guidance_raw.get("test_insights", []),
            diet_plan=DietPlan(
                recommended=guidance_raw["diet_plan"]["recommended"],
                avoid=guidance_raw["diet_plan"]["avoid"],
            ),
            what_to_do=guidance_raw.get("what_to_do", []),
            what_not_to_do=guidance_raw.get("what_not_to_do", []),
            lifestyle_advice=guidance_raw["lifestyle_advice"],
        )

        # Determine condition for drug candidate ranking
        condition_to_use = (request.condition or "").strip()
        if not condition_to_use:
            raw_disease = guidance_raw["disease_name"]
            if "Diabetes" in raw_disease:
                condition_to_use = "Diabetes"
            elif "Hypertension" in raw_disease:
                condition_to_use = "Hypertension"
            elif "Cardiovascular" in raw_disease:
                condition_to_use = "Heart Failure"
            elif "Respiratory" in raw_disease:
                condition_to_use = "Asthma"
            elif "Renal" in raw_disease:
                condition_to_use = "Kidney Disease"
            elif "Acne" in raw_disease or "Dermat" in raw_disease:
                condition_to_use = "Acne"
            else:
                condition_to_use = "Diabetes"

        # Step 4: Drug candidate ranking
        candidates = get_drug_candidates(
            condition=condition_to_use,
            top_k=request.top_k,
        )

        # Step 5: Assemble combined response
        return AnalysisResponse(
            patient_risk=prediction,
            condition=condition_to_use,
            clinical_guidance=guidance,
            drug_candidates=candidates,
        )

    except ValueError as exc:
        logger.warning("Analysis validation error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Analysis error: %s", exc)
        raise HTTPException(status_code=500, detail="Analysis failed. Please check your input data.") from exc
