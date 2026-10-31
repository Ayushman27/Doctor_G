"""
Clinical Context Service.
Maintains structured patient profile, symptom details, medical history,
risk factors, and red flags throughout the conversational diagnostic session.
"""

from __future__ import annotations

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PatientProfile(BaseModel):
    age: Optional[int] = Field(default=None, description="Patient age in years")
    sex: Optional[str] = Field(default=None, description="Patient biological sex ('male', 'female', 'other')")
    weight_kg: Optional[float] = Field(default=None, description="Weight in kilograms")
    height_cm: Optional[float] = Field(default=None, description="Height in centimeters")
    medical_history: List[str] = Field(default_factory=list, description="Pre-existing medical conditions")
    medications: List[str] = Field(default_factory=list, description="Current regular medications")
    allergies: List[str] = Field(default_factory=list, description="Known drug or food allergies")
    smoking: Optional[bool] = Field(default=None, description="Tobacco/smoking history")
    pregnancy_status: Optional[bool] = Field(default=None, description="Pregnancy status if applicable")


class ClinicalContext(BaseModel):
    patient_profile: PatientProfile = Field(default_factory=PatientProfile)
    symptoms: List[str] = Field(default_factory=list, description="Canonical primary symptoms")
    symptom_details: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Detailed attributes per symptom")
    associated_symptoms: List[str] = Field(default_factory=list, description="Associated secondary symptoms")
    risk_factors: List[str] = Field(default_factory=list, description="Identified clinical risk factors")
    red_flags: List[str] = Field(default_factory=list, description="Identified urgent red flags")
    interview_stage: str = Field(default="profile_collection", description="Current interview stage")
    current_profile_target: Optional[str] = Field(default="age", description="Next profile field requested ('age', 'sex', 'weight', None)")
    answers_history: List[Dict[str, str]] = Field(default_factory=list, description="Question and answer log")


def parse_age(text: str, is_explicit: bool = False) -> Optional[int]:
    """Extract patient age from text response."""
    cleaned = text.strip().lower()
    if is_explicit:
        # Match direct number or phrase e.g. "22", "22 years", "i am 22", "age 45"
        match = re.search(r"\b(\d{1,3})\b", cleaned)
        if match:
            val = int(match.group(1))
            if 0 <= val <= 120:
                return val
    else:
        # Require explicit age context e.g. "22 years old", "age 22", "22 yo"
        match = re.search(r"\b(?:age(?:\s+is|\s*:)?\s*(\d{1,3})|(\d{1,3})\s*(?:years?\s+old|yrs?\s+old|yo|y\.o\.))\b", cleaned)
        if match:
            val_str = match.group(1) or match.group(2)
            if val_str:
                val = int(val_str)
                if 0 <= val <= 120:
                    return val
    return None


def parse_sex(text: str) -> Optional[str]:
    """Extract patient biological sex from text response."""
    cleaned = text.strip().lower()
    if re.search(r"\b(female|woman|girl)\b", cleaned) or cleaned in ["f", "female"]:
        return "female"
    if re.search(r"\b(male|man|boy)\b", cleaned) or cleaned in ["m", "male"]:
        return "male"
    if re.search(r"\b(other|non-binary|prefer not to say)\b", cleaned):
        return "other"
    return None


def parse_weight(text: str, is_explicit: bool = False) -> Optional[float]:
    """Extract patient weight in kg from text response."""
    cleaned = text.strip().lower()
    # Check for lbs/pounds first
    match_lbs = re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs|pounds|pound)\b", cleaned)
    if match_lbs:
        lbs = float(match_lbs.group(1))
        return round(lbs * 0.453592, 1)

    # Check for explicit kg units
    match_kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilo|kilos|kilogram|kilograms)\b", cleaned)
    if match_kg:
        val = float(match_kg.group(1))
        if 2.0 <= val <= 350.0:
            return val

    # If it is an explicit prompt for weight (e.g. user answered "65" or "32"), accept plain number
    if is_explicit:
        match_num = re.search(r"^\s*(\d+(?:\.\d+)?)\s*$", cleaned)
        if match_num:
            val = float(match_num.group(1))
            if 2.0 <= val <= 350.0:
                return val

    return None


def extract_patient_profile_update(text: str, target_field: Optional[str]) -> Dict[str, Any]:
    """
    Parse an answer specifically for the currently prompted profile field.
    """
    updates = {}
    if target_field == "age":
        age_val = parse_age(text, is_explicit=True)
        if age_val is not None:
            updates["age"] = age_val
    elif target_field == "sex":
        sex_val = parse_sex(text)
        if sex_val is not None:
            updates["sex"] = sex_val
    elif target_field == "weight":
        wt_val = parse_weight(text, is_explicit=True)
        if wt_val is not None:
            updates["weight_kg"] = wt_val

    return updates


def get_next_profile_prompt(profile: PatientProfile) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
    """
    Determine the next missing profile field to ask for.
    Returns:
        (field_name, prompt_question, quick_reply_options)
    """
    if profile.age is None:
        return "age", "Before I assess your symptoms, I need a few basic details.\n\nHow old are you?", None
    if profile.sex is None:
        return "sex", "What is your biological sex?", ["Male", "Female", "Other"]
    if profile.weight_kg is None:
        return "weight", "What is your approximate weight in kg?", ["50 kg", "65 kg", "75 kg", "85 kg"]

    return None, None, None
