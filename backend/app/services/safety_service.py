"""
Medical Safety Service.
Inspects incoming patient messages for clinical red flags and emergency symptoms.
If urgent signs are detected, halts standard diagnostic questioning and provides immediate emergency guidance.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Emergency red-flag keywords and clinical triggers
EMERGENCY_TRIGGERS: List[Dict[str, Any]] = [
    {
        "category": "cardiovascular",
        "keywords": ["chest pain", "crushing chest", "heart attack", "radiating pain to arm", "left arm pain", "crushing pain"],
        "flag": "Severe chest pain or potential acute coronary event"
    },
    {
        "category": "respiratory",
        "keywords": ["gasping for air", "cannot breathe", "severe shortness of breath", "choking", "turning blue", "severe dyspnea"],
        "flag": "Severe respiratory distress or cyanosis"
    },
    {
        "category": "neurological",
        "keywords": ["unconscious", "passed out", "fainted", "loss of consciousness", "stroke", "facial drooping", "slurred speech", "sudden paralysis", "seizure"],
        "flag": "Loss of consciousness, acute stroke symptoms, or seizure"
    },
    {
        "category": "hemorrhagic",
        "keywords": ["severe bleeding", "coughing up blood", "vomiting blood", "uncontrolled bleeding", "profuse blood"],
        "flag": "Severe acute hemorrhage or hemoptysis"
    },
    {
        "category": "anaphylaxis",
        "keywords": ["throat closing", "swollen tongue", "anaphylaxis", "cannot swallow air", "severe allergy"],
        "flag": "Possible acute anaphylactic reaction"
    },
    {
        "category": "mental_health",
        "keywords": ["suicide", "kill myself", "self-harm", "want to die", "end my life"],
        "flag": "Immediate mental health crisis"
    }
]


def check_emergency_symptoms(message: str) -> Dict[str, Any]:
    """
    Evaluate user message for emergency red-flag symptoms.

    Returns:
        Dict with keys:
            is_emergency (bool): True if red flag detected.
            red_flags (List[str]): Identified warning flags.
            message (str): Urgent warning text for patient.
            continue_chat (bool): False if emergency care is required.
    """
    msg_lower = message.lower().strip()
    detected_flags = []

    for trigger in EMERGENCY_TRIGGERS:
        for kw in trigger["keywords"]:
            if kw in msg_lower:
                detected_flags.append(trigger["flag"])
                break

    if detected_flags:
        logger.warning("Clinical emergency red flag detected in patient message: %s", detected_flags)
        return {
            "is_emergency": True,
            "red_flags": detected_flags,
            "message": (
                "CRITICAL MEDICAL WARNING: The symptoms described may indicate an urgent or life-threatening condition. "
                "Please do not rely solely on this assistant. Seek immediate emergency medical evaluation (e.g., call 911 or visit the nearest emergency department)."
            ),
            "continue_chat": True
        }

    return {
        "is_emergency": False,
        "red_flags": [],
        "message": "",
        "continue_chat": True
    }
