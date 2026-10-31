"""
Pydantic schemas for prediction, drug recommendation, and clinical guidance responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------ #
#  Risk Prediction Response                                           #
# ------------------------------------------------------------------ #

class RiskProbabilities(BaseModel):
    LOW: float = Field(..., ge=0.0, le=1.0)
    MEDIUM: float = Field(..., ge=0.0, le=1.0)
    HIGH: float = Field(..., ge=0.0, le=1.0)


class PredictionResult(BaseModel):
    risk_class: int = Field(..., description="Predicted risk class index (0=LOW, 1=MEDIUM, 2=HIGH)")
    risk_label: str = Field(..., description="Human-readable risk label")
    probabilities: RiskProbabilities
    model_used: str = Field("Tuned XGBoost", description="Model that produced the prediction")
    model_version: str = Field("1.0.0")


# ------------------------------------------------------------------ #
#  Clinical Guidance Response (Diet, Causes, Severity)                 #
# ------------------------------------------------------------------ #

class DietPlan(BaseModel):
    recommended: List[str] = Field(..., description="Recommended foods and nutrients")
    avoid: List[str] = Field(..., description="Foods to avoid or restrict")


class ClinicalGuidance(BaseModel):
    disease_name: str = Field(..., description="Identified disease/condition name")
    severity: str = Field(..., description="Severity derived from XGBoost risk prediction (Mild/Moderate/High)")
    causes: List[str] = Field(..., description="Underlying causes and risk factors")
    test_insights: List[str] = Field(default_factory=list, description="Key insights extracted from patient test data")
    diet_plan: DietPlan = Field(..., description="Structured diet recommendations")
    what_to_do: List[str] = Field(default_factory=list, description="Actions and guidelines patient should perform")
    what_not_to_do: List[str] = Field(default_factory=list, description="Actions, foods, and risks patient should strictly avoid")
    lifestyle_advice: List[str] = Field(..., description="Lifestyle and physical activity guidelines")


# ------------------------------------------------------------------ #
#  Drug Candidate Response                                            #
# ------------------------------------------------------------------ #

class DrugCandidate(BaseModel):
    drug_name: str
    average_rating: float = Field(..., description="Average user rating (0-10)")
    average_effectiveness: float = Field(..., description="Average effectiveness score (0-5)")
    average_side_effect_score: float = Field(..., description="Average side effect score (0-5)")
    average_candidate_score: float = Field(..., description="Composite candidate score (0-1)")
    review_count: int = Field(..., description="Number of reviews")


class DrugRecommendationResponse(BaseModel):
    condition: str
    candidates: List[DrugCandidate]
    disclaimer: str = (
        "These are historical review-based drug candidates and are NOT prescriptions. "
        "A qualified healthcare professional must make all treatment decisions."
    )


# ------------------------------------------------------------------ #
#  Combined Analysis Response                                         #
# ------------------------------------------------------------------ #

class AnalysisResponse(BaseModel):
    patient_risk: PredictionResult
    condition: str
    clinical_guidance: ClinicalGuidance
    drug_candidates: List[DrugCandidate]
    disclaimer: str = (
        "For research and educational decision-support only. "
        "Not a medical diagnosis or prescription."
    )


# ------------------------------------------------------------------ #
#  Health / Model Info Responses                                      #
# ------------------------------------------------------------------ #

class HealthResponse(BaseModel):
    status: str = "healthy"
    model_loaded: bool
    model_version: str


class ModelInfoResponse(BaseModel):
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    version: Dict[str, Any]
    feature_summary: Dict[str, Any]


class ConditionsResponse(BaseModel):
    conditions: List[str]
    total: int


# ------------------------------------------------------------------ #
#  Symptom Disease Prediction Response                              #
# ------------------------------------------------------------------ #

class SymptomPredictionRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of symptoms experienced by patient")
    top_k: int = Field(5, ge=1, le=10, description="Top K disease predictions to return")


class DiseasePrediction(BaseModel):
    disease: str = Field(..., description="Predicted disease name")
    probability: float = Field(..., ge=0.0, le=1.0, description="Model prediction probability (0-1)")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Model confidence percentage (0-100%)")
    icd9_code: Optional[str] = Field(None, description="Corresponding ICD-9 diagnosis code")


class DiseasePredictionResponse(BaseModel):
    matched_symptoms: List[str] = Field(..., description="Symptoms recognized by the model")
    unmatched_symptoms: List[str] = Field(..., description="Symptoms not recognized by the model")
    top_prediction: DiseasePrediction = Field(..., description="Primary disease prediction")
    predictions: List[DiseasePrediction] = Field(..., description="Top K disease predictions")
    model_used: str = Field("Scikit-Learn Logistic Regression (symptom_to_disease_classifier)", description="Model name")
