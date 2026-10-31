"""
Patient service — converts validated Pydantic schemas into feature dicts
suitable for the prediction pipeline.

Responsible for mapping hyphenated alias fields back to their original
feature names that the preprocessor expects.
"""

from __future__ import annotations

from typing import Dict

from app.schemas.patient_schema import PatientData


def build_patient_feature_dict(patient_data: PatientData) -> Dict:
    """
    Convert a PatientData Pydantic model into a flat dict keyed
    by the original training feature names (including hyphenated ones).

    The Pydantic model uses Python-safe underscore aliases for hyphenated
    fields. This function reconstructs the correct hyphenated names.
    """
    # Get alias-keyed dict (hyphenated field names)
    raw = patient_data.model_dump(by_alias=True)

    # Remap any remaining underscore aliases back to hyphenated originals
    alias_to_original = {
        "glyburide_metformin": "glyburide-metformin",
        "glipizide_metformin": "glipizide-metformin",
        "glimepiride_pioglitazone": "glimepiride-pioglitazone",
        "metformin_rosiglitazone": "metformin-rosiglitazone",
        "metformin_pioglitazone": "metformin-pioglitazone",
    }

    feature_dict: Dict = {}
    for key, value in raw.items():
        original_key = alias_to_original.get(key, key)
        feature_dict[original_key] = value

    return feature_dict
