"""
Centralized model registry — loads all ML artefacts once at startup.
Uses a singleton-style class so every API handler accesses the same
in-memory objects without re-loading from disk.

Future services (SLM, RAG, RL) should extend this registry rather
than creating separate loading mechanisms.
"""

from __future__ import annotations

import gc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd
import xgboost as xgb

from app.core.config import settings

logger = logging.getLogger(__name__)

# Risk class mapping (matches training labels)
RISK_MAPPING: Dict[int, str] = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}


class ModelRegistry:
    """Singleton-style registry that holds all loaded model artefacts."""

    # ------------------------------------------------------------------ #
    #  Artefacts                                                           #
    # ------------------------------------------------------------------ #
    preprocessor: Any = None                   # sklearn ColumnTransformer
    xgboost_model: Optional[xgb.Booster] = None
    random_forest_model: Any = None            # sklearn RandomForestClassifier (optional)
    drug_summary: Optional[pd.DataFrame] = None
    disease_model: Any = None                  # sklearn LogisticRegression
    disease_label_encoder: Any = None          # sklearn LabelEncoder
    disease_symptoms: list = []                # 133 supported symptoms
    disease_metadata_list: list = []           # 41 supported diseases

    metadata: Dict[str, Any] = {}
    feature_metadata: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    version: Dict[str, Any] = {}

    # Derived helpers (populated after loading)
    original_features: list = []
    categorical_features: list = []
    numerical_features: list = []

    _loaded: bool = False

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def initialize(cls) -> None:
        """Load every required artefact from the model directory.

        Raises RuntimeError if any file is missing or fails to load.
        Called once from the FastAPI lifespan context manager.
        """
        if cls._loaded:
            logger.info("ModelRegistry already initialised — skipping reload.")
            return

        model_dir: Path = settings.model_dir
        logger.info("Loading ML artefacts from: %s", model_dir)

        # Validate directory exists
        if not model_dir.is_dir():
            raise RuntimeError(
                f"Model directory not found: {model_dir}. "
                "Please extract patient_ai_models/ into backend/models/."
            )

        # ---- JSON metadata files ----------------------------------------
        cls.metadata = cls._load_json(model_dir / "metadata.json")
        cls.feature_metadata = cls._load_json(model_dir / "feature_metadata.json")
        cls.metrics = cls._load_json(model_dir / "model_metrics.json")
        cls.version = cls._load_json(model_dir / "version.json")

        # Populate derived feature lists
        cls.original_features = cls.feature_metadata.get("original_features", [])
        cls.categorical_features = cls.feature_metadata.get("categorical_features", [])
        cls.numerical_features = cls.feature_metadata.get("numerical_features", [])

        # ---- Preprocessor (sklearn ColumnTransformer) -------------------
        cls.preprocessor = cls._load_joblib(
            model_dir / "preprocessor.pkl", "preprocessor"
        )

        # ---- XGBoost model (Primary Inference Model) --------------------
        xgboost_path = model_dir / "xgboost.json"
        cls._require_file(xgboost_path, "xgboost.json")
        booster = xgb.Booster()
        booster.load_model(str(xgboost_path))
        cls.xgboost_model = booster
        logger.info("XGBoost model loaded (rounds=%d).", booster.num_boosted_rounds())

        # ---- Random Forest (Secondary/Benchmark Model) -------------------
        # Skipped by default to fit within 512MB RAM cloud tiers (e.g. Render free tier).
        # XGBoost is the active inference model used by /patient/predict and /analysis.
        cls.random_forest_model = None
        if getattr(settings, "load_random_forest", False):
            rf_path = model_dir / "random_forest.pkl"
            if rf_path.exists():
                try:
                    cls.random_forest_model = cls._load_joblib(rf_path, "random_forest")
                except Exception as exc:
                    logger.warning("Optional Random Forest loading skipped (%s).", exc)

        # ---- Drug summary DataFrame ------------------------------------
        cls.drug_summary = cls._load_joblib(
            model_dir / "drug_summary.pkl", "drug_summary"
        )
        logger.info(
            "Drug summary loaded: %d rows, %d conditions.",
            len(cls.drug_summary),
            cls.drug_summary["condition_clean"].nunique(),
        )

        # ---- Disease Prediction Model (Symptom Classifier) -------------
        disease_model_dir = model_dir.parent / "disease_prediction_model"
        if disease_model_dir.is_dir():
            cls.disease_model = cls._load_joblib(disease_model_dir / "disease_model.pkl", "disease_model")
            cls.disease_label_encoder = cls._load_joblib(disease_model_dir / "label_encoder.pkl", "label_encoder")
            symptom_data = cls._load_json(disease_model_dir / "symptom_metadata.json")
            cls.disease_symptoms = symptom_data.get("symptoms", [])
            disease_meta = cls._load_json(disease_model_dir / "disease_metadata.json")
            cls.disease_metadata_list = disease_meta.get("diseases", [])
            logger.info("Loaded Disease Prediction Model: %d symptoms, %d diseases.", len(cls.disease_symptoms), len(cls.disease_metadata_list))

        cls._loaded = True
        gc.collect()
        logger.info("ModelRegistry fully initialised.")

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _require_file(path: Path, name: str) -> None:
        if not path.is_file():
            raise RuntimeError(
                f"Required model file missing: {name} (expected at {path})"
            )

    @classmethod
    def _load_json(cls, path: Path) -> Dict[str, Any]:
        cls._require_file(path, path.name)
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        logger.info("Loaded JSON: %s", path.name)
        return data

    @classmethod
    def _load_joblib(cls, path: Path, label: str) -> Any:
        cls._require_file(path, path.name)
        obj = joblib.load(path)
        logger.info("Loaded %s: %s", label, type(obj).__name__)
        return obj


# Module-level singleton instance
registry = ModelRegistry()
