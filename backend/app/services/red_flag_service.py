"""
Clinical Red Flag and Emergency Screening Engine.
Identifies danger signs that require urgent clinical evaluation or emergency escalation.
Distinguishes between immediate acute life-threatening clusters (which interrupt normal flow)
and mild/non-acute symptoms that require conversational safety screening.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from app.services.clinical_context_service import ClinicalContext

logger = logging.getLogger(__name__)

# Acute emergency triggers that immediately require emergency care escalation
ACUTE_RED_FLAGS = [
    {
        "category": "cardiovascular_critical",
        "keywords": [
            "crushing chest", "chest pressure and sweating", "chest pain and shortness of breath",
            "chest pain and cannot breathe", "pain radiating to left arm", "pain radiating to arm",
            "pain radiating to jaw", "pain spreading to jaw", "pain spreading to arm"
        ],
        "flag": "Acute chest pressure with associated radiation, diaphoresis, or dyspnea (potential acute coronary syndrome)"
    },
    {
        "category": "respiratory_critical",
        "keywords": [
            "gasping for air", "cannot breathe", "severe shortness of breath", "turning blue", "stridor"
        ],
        "flag": "Acute severe respiratory distress or potential hypoxic event"
    },
    {
        "category": "neurological_critical",
        "keywords": [
            "facial drooping", "slurred speech", "sudden weakness in arm", "sudden paralysis",
            "passed out", "loss of consciousness", "fainted", "unconscious"
        ],
        "flag": "Acute neurological deficit (possible stroke, TIA, or hemodynamic syncope)"
    },
    {
        "category": "hemorrhagic_critical",
        "keywords": [
            "vomiting blood", "coughing up blood", "black tarry stool", "profuse rectal bleeding",
            "uncontrolled bleeding"
        ],
        "flag": "Active severe gastrointestinal hemorrhage or hemoptysis"
    },
    {
        "category": "anaphylaxis_critical",
        "keywords": [
            "throat closing", "swollen tongue", "anaphylaxis", "severe allergy and cannot breathe"
        ],
        "flag": "Acute airway compromise / anaphylactic reaction"
    }
]


def check_clinical_red_flags(
    message: str,
    symptoms: List[str],
    symptom_details: Dict[str, Any],
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate message and clinical context for acute red-flag warning signs.

    Returns:
        Dict with keys:
            is_emergency (bool): True if acute danger sign cluster detected.
            red_flags (List[str]): Identified warning flags.
            urgent_message (str): Compassionate, safe clinical escalation message.
            needs_safety_screening (bool): True if symptoms warrant cautionary screening.
    """
    msg_lower = message.lower().strip()
    detected_flags: List[str] = []

    # 1. Direct keyword scanning for acute clusters
    for trigger in ACUTE_RED_FLAGS:
        for kw in trigger["keywords"]:
            if kw in msg_lower:
                detected_flags.append(trigger["flag"])
                break

    # 2. Contextual combination check (e.g. chest pain + shortness of breath + sweating)
    has_chest = "chest" in msg_lower or "chest_pain" in symptoms
    has_dyspnea = any(w in msg_lower for w in ["breath", "shortness of breath", "difficulty breathing", "breathless"])
    has_sweat = any(w in msg_lower for w in ["sweat", "sweating", "cold sweat", "diaphoresis"])
    has_syncope = any(w in msg_lower for w in ["faint", "fainted", "dizzy", "passed out", "lightheaded"])

    if has_chest and (has_dyspnea or has_sweat or has_syncope):
        flag_desc = "Chest discomfort reported in combination with dyspnea, sweating, or presyncope"
        if flag_desc not in detected_flags:
            detected_flags.append(flag_desc)

    # Elderly high-risk combination check
    if age is not None and age >= 65 and has_chest and (has_dyspnea or has_sweat):
        elderly_flag = f"Elderly patient (age {age}) presenting with cardiac symptoms and autonomic features"
        if elderly_flag not in detected_flags:
            detected_flags.append(elderly_flag)

    # 3. Check for severe GI red flags
    has_blood_stool = any(w in msg_lower for w in ["blood in stool", "bloody stool", "black stool", "tarry stool"])
    if has_blood_stool:
        gi_flag = "Significant blood reported in stool or altered black/tarry stool"
        if gi_flag not in detected_flags:
            detected_flags.append(gi_flag)

    is_emergency = len(detected_flags) > 0

    urgent_message = ""
    if is_emergency:
        urgent_message = (
            "SAFETY ESCALATION: Some of the symptoms you described (including "
            f"{', '.join(detected_flags)}) can sometimes be associated with serious conditions that require urgent medical attention.\n\n"
            "Please do not wait or rely solely on this online research assistant. "
            "Seek immediate in-person medical evaluation at an emergency department or contact your local emergency services (e.g., call 911)."
        )

    # Determine if non-emergency symptoms still need safety screening (e.g. isolated chest discomfort or severe headache)
    needs_safety_screening = ("chest_pain" in symptoms or has_chest or "headache" in symptoms) and not is_emergency

    return {
        "is_emergency": is_emergency,
        "red_flags": detected_flags,
        "urgent_message": urgent_message,
        "needs_safety_screening": needs_safety_screening
    }
