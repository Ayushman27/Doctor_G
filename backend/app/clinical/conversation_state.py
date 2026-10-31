"""
Clinical Conversation State Machine.
Defines strict state enums, transitions, and session state container.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ConversationStage(str, Enum):
    INITIAL_COMPLAINT = "INITIAL_COMPLAINT"
    SYMPTOM_EXTRACTION = "SYMPTOM_EXTRACTION"
    PATIENT_PROFILE = "PATIENT_PROFILE"
    SYMPTOM_CHARACTERIZATION = "SYMPTOM_CHARACTERIZATION"
    SAFETY_SCREENING = "SAFETY_SCREENING"
    DIFFERENTIAL_ASSESSMENT = "DIFFERENTIAL_ASSESSMENT"
    INFORMATION_SUFFICIENCY_CHECK = "INFORMATION_SUFFICIENCY_CHECK"
    TEST_CONSIDERATION = "TEST_CONSIDERATION"
    TEST_RESULT_ANALYSIS = "TEST_RESULT_ANALYSIS"
    FINAL_ASSESSMENT = "FINAL_ASSESSMENT"
    TREATMENT_INFORMATION = "TREATMENT_INFORMATION"
    URGENT_EVALUATION = "URGENT_EVALUATION"


VALID_TRANSITIONS = {
    ConversationStage.INITIAL_COMPLAINT: [ConversationStage.SYMPTOM_EXTRACTION, ConversationStage.URGENT_EVALUATION],
    ConversationStage.SYMPTOM_EXTRACTION: [ConversationStage.INITIAL_COMPLAINT, ConversationStage.PATIENT_PROFILE, ConversationStage.URGENT_EVALUATION],
    ConversationStage.PATIENT_PROFILE: [ConversationStage.SYMPTOM_CHARACTERIZATION, ConversationStage.URGENT_EVALUATION],
    ConversationStage.SYMPTOM_CHARACTERIZATION: [ConversationStage.SAFETY_SCREENING, ConversationStage.URGENT_EVALUATION],
    ConversationStage.SAFETY_SCREENING: [ConversationStage.DIFFERENTIAL_ASSESSMENT, ConversationStage.URGENT_EVALUATION],
    ConversationStage.DIFFERENTIAL_ASSESSMENT: [ConversationStage.INFORMATION_SUFFICIENCY_CHECK, ConversationStage.URGENT_EVALUATION],
    ConversationStage.INFORMATION_SUFFICIENCY_CHECK: [ConversationStage.SYMPTOM_CHARACTERIZATION, ConversationStage.TEST_CONSIDERATION, ConversationStage.FINAL_ASSESSMENT, ConversationStage.URGENT_EVALUATION],
    ConversationStage.TEST_CONSIDERATION: [ConversationStage.TEST_RESULT_ANALYSIS, ConversationStage.FINAL_ASSESSMENT, ConversationStage.URGENT_EVALUATION],
    ConversationStage.TEST_RESULT_ANALYSIS: [ConversationStage.FINAL_ASSESSMENT, ConversationStage.URGENT_EVALUATION],
    ConversationStage.FINAL_ASSESSMENT: [ConversationStage.TREATMENT_INFORMATION, ConversationStage.URGENT_EVALUATION],
    ConversationStage.TREATMENT_INFORMATION: [ConversationStage.URGENT_EVALUATION],
    ConversationStage.URGENT_EVALUATION: []
}


def create_initial_state_dict(session_id: str) -> Dict[str, Any]:
    """Create new initial conversation state dict conforming to spec section 28."""
    return {
        "session_id": session_id,
        "conversation_stage": ConversationStage.INITIAL_COMPLAINT.value,
        "initial_complaint": None,
        "patient_profile": {
            "age": None,
            "sex": None,
            "weight": None,
            "height": None
        },
        "symptoms": [],
        "symptom_details": {},
        "duration": {},
        "medical_history": [],
        "medications": [],
        "allergies": [],
        "risk_factors": [],
        "red_flags": [],
        "questions_asked": [],
        "answers": [],
        "ml_predictions": [],
        "rag_queries": [],
        "rag_evidence": [],
        "tests_suggested": [],
        "test_results": [],
        "assessment": None,
        "is_completed": False,
        "messages": []
    }
