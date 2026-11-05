"""
Pydantic schemas for patient data input.

Fields are derived from feature_metadata.json original_features list.
All categorical values use Optional[str] so the frontend can send
null/None for unknown values — the preprocessor handles missing data.

Field names MUST match the original feature names used during training.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ------------------------------------------------------------------ #
#  Patient Data Model                                                  #
# ------------------------------------------------------------------ #

class PatientData(BaseModel):
    # ---- Patient Information ----------------------------------------
    race: Optional[str] = Field(None, description="Patient race")
    gender: Optional[str] = Field(None, description="Patient gender")
    age: Optional[str] = Field(None, description="Patient age bracket e.g. [50-60)")
    weight: Optional[str] = Field(None, description="Patient weight bracket in lbs")

    # ---- Admission Information ---------------------------------------
    admission_type_id: Optional[int] = Field(None, ge=1, le=8, description="Admission type (1-8)")
    admission_source_id: Optional[int] = Field(None, ge=1, le=26, description="Admission source (1-26)")
    time_in_hospital: Optional[int] = Field(None, ge=1, le=14, description="Days in hospital (1-14)")
    payer_code: Optional[str] = Field(None, description="Insurance/payer code")
    medical_specialty: Optional[str] = Field(None, description="Admitting physician specialty")

    # ---- Laboratory Information -------------------------------------
    num_lab_procedures: Optional[int] = Field(None, ge=0, le=132, description="Number of lab procedures")
    num_procedures: Optional[int] = Field(None, ge=0, le=6, description="Number of procedures (non-lab)")
    num_medications: Optional[int] = Field(None, ge=0, le=81, description="Number of distinct medications")
    max_glu_serum: Optional[str] = Field(None, description="Maximum glucose serum test result")
    A1Cresult: Optional[str] = Field(None, description="HbA1c test result")

    # ---- Clinical Counts --------------------------------------------
    number_outpatient: Optional[int] = Field(None, ge=0, description="Outpatient visits in prior year")
    number_emergency: Optional[int] = Field(None, ge=0, description="Emergency visits in prior year")
    number_inpatient: Optional[int] = Field(None, ge=0, description="Inpatient visits in prior year")
    number_diagnoses: Optional[int] = Field(None, ge=1, le=16, description="Number of diagnoses entered")

    # ---- Diagnoses (ICD-9 codes) ------------------------------------
    diag_1: Optional[str] = Field(None, description="Primary diagnosis (ICD-9 code)")
    diag_2: Optional[str] = Field(None, description="Secondary diagnosis (ICD-9 code)")
    diag_3: Optional[str] = Field(None, description="Tertiary diagnosis (ICD-9 code)")

    # ---- Medication Information — Dosage Changes --------------------
    metformin: Optional[str] = Field("No", description="Metformin dosage change")
    repaglinide: Optional[str] = Field("No", description="Repaglinide dosage change")
    nateglinide: Optional[str] = Field("No", description="Nateglinide dosage change")
    chlorpropamide: Optional[str] = Field("No", description="Chlorpropamide dosage change")
    glimepiride: Optional[str] = Field("No", description="Glimepiride dosage change")
    acetohexamide: Optional[str] = Field("No", description="Acetohexamide dosage change")
    glipizide: Optional[str] = Field("No", description="Glipizide dosage change")
    glyburide: Optional[str] = Field("No", description="Glyburide dosage change")
    tolbutamide: Optional[str] = Field("No", description="Tolbutamide dosage change")
    pioglitazone: Optional[str] = Field("No", description="Pioglitazone dosage change")
    rosiglitazone: Optional[str] = Field("No", description="Rosiglitazone dosage change")
    acarbose: Optional[str] = Field("No", description="Acarbose dosage change")
    miglitol: Optional[str] = Field("No", description="Miglitol dosage change")
    troglitazone: Optional[str] = Field("No", description="Troglitazone dosage change")
    tolazamide: Optional[str] = Field("No", description="Tolazamide dosage change")
    examide: Optional[str] = Field("No", description="Examide dosage change")
    citoglipton: Optional[str] = Field("No", description="Citoglipton dosage change")
    insulin: Optional[str] = Field("No", description="Insulin dosage change")

    # Combination medications
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    # Using aliases to handle hyphenated field names
    glyburide_metformin: Optional[str] = Field("No", alias="glyburide-metformin", description="Glyburide-Metformin change")
    glipizide_metformin: Optional[str] = Field("No", alias="glipizide-metformin", description="Glipizide-Metformin change")
    glimepiride_pioglitazone: Optional[str] = Field("No", alias="glimepiride-pioglitazone", description="Glimepiride-Pioglitazone change")
    metformin_rosiglitazone: Optional[str] = Field("No", alias="metformin-rosiglitazone", description="Metformin-Rosiglitazone change")
    metformin_pioglitazone: Optional[str] = Field("No", alias="metformin-pioglitazone", description="Metformin-Pioglitazone change")

    # ---- Treatment Status -------------------------------------------
    change: Optional[str] = Field("No", description="Was there a change in diabetic medications?")
    diabetesMed: Optional[str] = Field("No", description="Were any diabetes medications prescribed?")

    def to_feature_dict(self) -> dict:
        """
        Convert this schema to a dict with original hyphenated feature names
        as expected by the preprocessor.
        """
        d = self.model_dump(by_alias=True)
        return d


# ------------------------------------------------------------------ #
#  API Request Wrappers                                               #
# ------------------------------------------------------------------ #

class PredictRequest(BaseModel):
    patient_data: PatientData
    condition: Optional[str] = Field(None, description="Medical condition for drug candidate lookup")


class AnalysisRequest(BaseModel):
    patient_data: PatientData
    condition: Optional[str] = Field("", description="Medical condition for drug candidate lookup (auto-detected if empty)")
    top_k: int = Field(5, ge=1, le=20, description="Number of drug candidates to return")
