"""
Prediction service — wraps the XGBoost inference pipeline.

Flow:
  raw patient dict → DataFrame → preprocessor → XGBoost → PredictionResult
"""

from __future__ import annotations

import logging
from typing import Dict

import numpy as np
import pandas as pd
import xgboost as xgb

from app.core.model_loader import registry, RISK_MAPPING
from app.schemas.prediction_schema import PredictionResult, RiskProbabilities

logger = logging.getLogger(__name__)


def predict_risk(patient_dict: Dict) -> PredictionResult:
    """
    Run the full inference pipeline for one patient.

    Args:
        patient_dict: Raw feature dict with original feature names
                      (as returned by PatientData.to_feature_dict()).

    Returns:
        PredictionResult with risk_class, risk_label, and probabilities.
    """
    if not registry.is_loaded():
        raise RuntimeError("ML models are not loaded. Cannot perform prediction.")

    # Step 1 — Build single-row DataFrame with correct column order
    df = _build_dataframe(patient_dict)

    # Step 2 — Preprocess with saved preprocessor (prevents train/inference mismatch)
    try:
        X_processed = registry.preprocessor.transform(df)
    except Exception as exc:
        logger.error("Preprocessing failed: %s", exc)
        raise ValueError(f"Patient data preprocessing failed: {exc}") from exc

    # Step 3 — XGBoost inference
    try:
        dmatrix = xgb.DMatrix(X_processed)
        probs_array = registry.xgboost_model.predict(dmatrix)
    except Exception as exc:
        logger.error("XGBoost inference failed: %s", exc)
        raise RuntimeError(f"Model inference failed: {exc}") from exc

    # Step 4 — Extract probabilities (shape: [1, 3])
    probs = probs_array[0]  # [p_LOW, p_MEDIUM, p_HIGH]
    predicted_class = int(np.argmax(probs))
    risk_label = RISK_MAPPING[predicted_class]

    logger.info(
        "Prediction complete — class=%d (%s), probs=[%.3f, %.3f, %.3f]",
        predicted_class,
        risk_label,
        probs[0],
        probs[1],
        probs[2],
    )

    return PredictionResult(
        risk_class=predicted_class,
        risk_label=risk_label,
        probabilities=RiskProbabilities(
            LOW=round(float(probs[0]), 4),
            MEDIUM=round(float(probs[1]), 4),
            HIGH=round(float(probs[2]), 4),
        ),
        model_used="Tuned XGBoost",
        model_version=registry.version.get("model_version", "1.0.0"),
    )


def _build_dataframe(patient_dict: Dict) -> pd.DataFrame:
    """
    Construct a one-row DataFrame from the patient feature dict.
    Columns are ordered to match the original training feature list.
    """
    expected_features = registry.original_features

    # Fill any missing features with None so preprocessor can handle them
    row = {feat: patient_dict.get(feat, None) for feat in expected_features}

    df = pd.DataFrame([row])
    return df
