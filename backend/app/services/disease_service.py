"""
Disease prediction service — uses the Scikit-Learn Logistic Regression model
from disease_prediction_model.zip to predict diseases from symptom input.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any
import numpy as np
import pandas as pd

from app.core.model_loader import registry
from app.schemas.prediction_schema import DiseasePrediction, DiseasePredictionResponse

logger = logging.getLogger(__name__)


def normalize_symptom(symptom: str) -> str:
    """Normalize user symptom string to match feature column format."""
    s = str(symptom).strip().lower()
    s = s.replace(" ", "_").replace("-", "_").replace("/", "_")
    return s


def format_disease_title(disease_name: str) -> str:
    """Format raw disease class name for clinical display."""
    d = str(disease_name).strip()
    acronyms = {"gerd": "GERD", "aids": "AIDS", "uti": "Urinary Tract Infection"}
    if d.lower() in acronyms:
        return acronyms[d.lower()]
    return d.title()


def get_available_symptoms() -> List[Dict[str, str]]:
    """Return all 133 supported symptoms formatted for UI selection."""
    symptoms = registry.disease_symptoms
    return [
        {
            "value": sym,
            "label": sym.replace("_", " ").title()
        }
        for sym in symptoms
    ]


DISEASE_ICD9_MAP: Dict[str, str] = {
    "(vertigo) paroymsal  positional vertigo": "386.11",
    "acne": "706.1",
    "aids": "042",
    "alcoholic hepatitis": "571.1",
    "allergy": "995.3",
    "arthritis": "716.90",
    "bronchial asthma": "493.90",
    "cervical spondylosis": "721.0",
    "chicken pox": "052.9",
    "chronic cholestasis": "576.2",
    "common cold": "460",
    "dengue": "065.4",
    "diabetes": "250.00",
    "dimorphic hemmorhoids(piles)": "455.6",
    "drug reaction": "995.20",
    "fungal infection": "110.9",
    "gastroenteritis": "558.9",
    "gerd": "530.81",
    "heart attack": "410.90",
    "hepatitis a": "070.1",
    "hepatitis b": "070.30",
    "hepatitis c": "070.51",
    "hepatitis d": "070.52",
    "hepatitis e": "070.53",
    "hypertension": "401.9",
    "hyperthyroidism": "242.90",
    "hypoglycemia": "251.2",
    "hypothyroidism": "244.9",
    "impetigo": "684",
    "jaundice": "782.4",
    "malaria": "084.6",
    "migraine": "346.90",
    "osteoarthristis": "715.90",
    "paralysis (brain hemorrhage)": "431",
    "peptic ulcer diseae": "533.90",
    "pneumonia": "486",
    "psoriasis": "696.1",
    "tuberculosis": "011.90",
    "typhoid": "002.0",
    "urinary tract infection": "599.0",
    "varicose veins": "454.9",
}


def get_icd9_code(disease_name: str) -> str:
    """Return corresponding ICD-9 code for a given disease name."""
    raw = str(disease_name).strip().lower()
    return DISEASE_ICD9_MAP.get(raw, "799.9")


def predict_disease_from_symptoms(symptoms: List[str], top_k: int = 5) -> DiseasePredictionResponse:
    """
    Perform disease prediction using the trained Scikit-Learn Logistic Regression model.

    Args:
        symptoms: List of symptom string names provided by patient.
        top_k: Number of top disease predictions to return (1-10).

    Returns:
        DiseasePredictionResponse containing matched/unmatched symptoms and top_k predictions.
    """
    if not registry.disease_model or not registry.disease_label_encoder:
        raise RuntimeError("Disease prediction model is not loaded in registry.")

    all_symptoms = registry.disease_symptoms
    input_vector = pd.DataFrame(0, index=[0], columns=all_symptoms)

    matched: List[str] = []
    unmatched: List[str] = []

    for sym in symptoms:
        norm = normalize_symptom(sym)
        if norm in input_vector.columns:
            input_vector.loc[0, norm] = 1
            matched.append(norm)
        else:
            unmatched.append(sym)

    if not matched:
        raise ValueError("None of the provided symptoms were recognized by the AI model.")

    # Model inference
    probabilities = registry.disease_model.predict_proba(input_vector)[0]

    # Top-K sorting
    top_indices = np.argsort(probabilities)[::-1][:top_k]

    predictions: List[DiseasePrediction] = []
    for idx in top_indices:
        raw_name = registry.disease_label_encoder.inverse_transform([idx])[0]
        prob = float(probabilities[idx])
        predictions.append(
            DiseasePrediction(
                disease=format_disease_title(raw_name),
                probability=round(prob, 4),
                percentage=round(prob * 100, 1),
                icd9_code=get_icd9_code(raw_name)
            )
        )

    return DiseasePredictionResponse(
        matched_symptoms=[m.replace("_", " ").title() for m in matched],
        unmatched_symptoms=unmatched,
        top_prediction=predictions[0],
        predictions=predictions,
        model_used="Scikit-Learn Logistic Regression (symptom_to_disease_classifier)"
    )
