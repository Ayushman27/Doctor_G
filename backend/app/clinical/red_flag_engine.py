"""
Deterministic Safety & Red-Flag Engine.
Evaluates message and patient context for acute danger signs independently of the LLM.
Triggers immediate transition to URGENT_EVALUATION upon emergency clusters.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Danger sign clusters
ACUTE_RED_FLAG_TRIGGERS = [
    {
        "category": "cardiovascular_critical",
        "keywords": [
            "crushing chest", "chest pressure", "chest pain and shortness of breath",
            "chest pain and cannot breathe", "pain radiating to left arm", "pain radiating to arm",
            "pain radiating to jaw", "pain spreading to jaw", "pain spreading to arm"
        ],
        "flag": "Acute chest pressure with associated radiation, diaphoresis, or dyspnea (suspected acute coronary syndrome)"
    },
    {
        "category": "respiratory_critical",
        "keywords": [
            "gasping for air", "cannot breathe", "severe shortness of breath", "turning blue", "stridor", "suffocating"
        ],
        "flag": "Acute severe respiratory distress or hypoxic compromise"
    },
    {
        "category": "neurological_critical",
        "keywords": [
            "facial drooping", "slurred speech", "sudden weakness in arm", "sudden paralysis",
            "passed out", "loss of consciousness", "fainted", "unconscious"
        ],
        "flag": "Acute neurological focal deficit or syncopal episode (suspected stroke/TIA or syncope)"
    },
    {
        "category": "hemorrhagic_critical",
        "keywords": [
            "vomiting blood", "coughing up blood", "black tarry stool", "profuse rectal bleeding",
            "blood in stool", "bloody stool", "uncontrolled bleeding"
        ],
        "flag": "Significant gastrointestinal hemorrhage or active hemoptysis"
    },
    {
        "category": "anaphylaxis_critical",
        "keywords": [
            "throat closing", "swollen tongue", "anaphylaxis", "severe allergy and cannot breathe"
        ],
        "flag": "Acute airway compromise / severe anaphylactic reaction"
    }
]


def evaluate_clinical_red_flags(
    message: str,
    symptoms: List[str],
    symptom_details: Optional[Dict[str, Any]] = None,
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Deterministically check for emergency warning flags in input text and clinical state.

    Returns:
        {
            "is_emergency": bool,
            "red_flags": List[str],
            "urgent_message": str,
            "stage_override": "URGENT_EVALUATION" or None
        }
    """
    msg_lower = message.lower().strip()
    detected_flags: List[str] = []

    # 1. Direct keyword scanning against danger clusters
    for trigger in ACUTE_RED_FLAG_TRIGGERS:
        for kw in trigger["keywords"]:
            if kw in msg_lower:
                if trigger["flag"] not in detected_flags:
                    detected_flags.append(trigger["flag"])
                break

    # 2. Contextual combinations (e.g. chest symptoms + dyspnea / sweating / syncope)
    has_chest = "chest_pain" in symptoms or any(w in msg_lower for w in ["chest pain", "chest pressure", "chest discomfort", "chest tightness"])
    has_dyspnea = "breathlessness" in symptoms or any(w in msg_lower for w in ["breath", "shortness of breath", "difficulty breathing", "breathless"])
    has_sweat = "sweating" in symptoms or any(w in msg_lower for w in ["sweat", "sweats", "sweating", "cold sweat", "diaphoresis"])
    has_syncope = any(w in msg_lower for w in ["faint", "fainted", "dizzy", "passed out", "lightheaded"])

    if has_chest and (has_dyspnea or has_sweat or has_syncope):
        comb_flag = "Chest discomfort reported in combination with dyspnea, sweating, or presyncope"
        if comb_flag not in detected_flags:
            detected_flags.append(comb_flag)

    # 3. Elderly high-risk combination check
    if age is not None and age >= 65 and has_chest and (has_dyspnea or has_sweat):
        elderly_flag = f"Elderly patient (age {age}) presenting with cardiac symptoms and autonomic features"
        if elderly_flag not in detected_flags:
            detected_flags.append(elderly_flag)

    is_emergency = len(detected_flags) > 0

    urgent_message = ""
    stage_override = None
    if is_emergency:
        stage_override = "URGENT_EVALUATION"
        urgent_message = (
            "EMERGENCY SAFETY ESCALATION:\n"
            f"Some of the symptoms you described (including: {', '.join(detected_flags)}) "
            "can indicate a severe medical condition requiring immediate emergency care.\n\n"
            "Please do NOT wait for online assessment. Seek emergency medical attention immediately "
            "at the nearest emergency department or call emergency services (e.g. 911)."
        )

    return {
        "is_emergency": is_emergency,
        "red_flags": detected_flags,
        "urgent_message": urgent_message,
        "stage_override": stage_override
    }
