"""
Risk Factor Engine.
Analyzes patient demographics, lifestyle, and medical history to identify
clinical risk factors that provide context for diagnostic reasoning.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional
from app.services.clinical_context_service import PatientProfile

logger = logging.getLogger(__name__)


def evaluate_risk_factors(profile: PatientProfile) -> List[str]:
    """
    Identify clinical risk factors from the patient profile.
    These risk factors serve as contextual Bayesian priors, never as hard diagnosis rules.
    """
    risk_factors: List[str] = []

    # 1. Age-based clinical considerations
    if profile.age is not None:
        if profile.age < 18:
            risk_factors.append(f"Pediatric patient (age {profile.age}) - higher susceptibility to acute viral gastroenteritis and dehydration")
        elif profile.age >= 65:
            risk_factors.append(f"Elderly patient (age {profile.age}) - increased baseline cardiovascular and atypical presentation risk")
        elif profile.age >= 50:
            risk_factors.append(f"Age {profile.age} - moderate baseline cardiovascular risk screening recommended")

    # 2. Weight & BMI considerations
    if profile.weight_kg is not None and profile.height_cm is not None and profile.height_cm > 0:
        height_m = profile.height_cm / 100.0
        bmi = profile.weight_kg / (height_m ** 2)
        if bmi >= 30.0:
            risk_factors.append(f"Obesity (BMI {bmi:.1f}) - elevated risk for GERD, hypertension, and cardiovascular strain")
        elif bmi >= 25.0:
            risk_factors.append(f"Overweight (BMI {bmi:.1f}) - potential contributor to reflux or metabolic factors")

    # 3. Medical history & comorbid conditions
    history_lower = [h.lower().strip() for h in profile.medical_history]
    if any("hypertension" in h or "high blood pressure" in h for h in history_lower):
        risk_factors.append("Known history of Hypertension")
    if any("diabetes" in h or "sugar" in h for h in history_lower):
        risk_factors.append("Known history of Diabetes Mellitus (atypical symptom perception risk)")
    if any("heart" in h or "coronary" in h or "cardiac" in h for h in history_lower):
        risk_factors.append("Pre-existing Cardiovascular / Ischemic Heart Disease")
    if any("gerd" in h or "reflux" in h or "acidity" in h or "ulcer" in h for h in history_lower):
        risk_factors.append("Documented history of Acid Reflux / Peptic Disease")

    # 4. Habits
    if profile.smoking is True:
        risk_factors.append("Active or previous tobacco smoking history")

    return risk_factors
