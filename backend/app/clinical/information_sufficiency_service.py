"""
Information Sufficiency Evaluation Service.
Determines whether enough clinical context has been gathered to make a diagnostic support assessment.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

MAX_QUESTION_LIMIT = 5


def evaluate_information_sufficiency(
    symptoms: List[str],
    symptom_details: Dict[str, Any],
    patient_profile: Dict[str, Any],
    questions_asked: List[str],
    answers_history: List[Dict[str, Any]],
    red_flags: List[str]
) -> Dict[str, Any]:
    """
    Evaluate if current clinical conversation data is sufficient for differential assessment.

    Returns:
        {
            "status": "SUFFICIENT_INFORMATION" | "NEED_MORE_INFORMATION",
            "missing_information": List[str],
            "reason": str
        }
    """
    missing: List[str] = []

    # Check basic profile completion
    if patient_profile.get("age") is None:
        missing.append("patient_age")
    if patient_profile.get("sex") is None:
        missing.append("patient_sex")

    num_questions = len(questions_asked)

    # If maximum question limit reached or 3+ detailed answers collected
    if num_questions >= MAX_QUESTION_LIMIT:
        return {
            "status": "SUFFICIENT_INFORMATION",
            "missing_information": [],
            "reason": f"Maximum follow-up question quota ({MAX_QUESTION_LIMIT}) completed."
        }

    if num_questions >= 3 and len(answers_history) >= 3:
        return {
            "status": "SUFFICIENT_INFORMATION",
            "missing_information": [],
            "reason": "Sufficient clinical symptom characterization and safety screening gathered."
        }

    if missing:
        return {
            "status": "NEED_MORE_INFORMATION",
            "missing_information": missing,
            "reason": f"Missing baseline clinical context fields ({', '.join(missing)})."
        }

    return {
        "status": "NEED_MORE_INFORMATION",
        "missing_information": ["symptom_characterization"],
        "reason": "Additional symptom-specific discriminating questions required."
    }
