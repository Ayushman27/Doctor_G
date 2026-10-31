"""
RAG Query Builder.
Constructs targeted clinical queries tailored for specific RAG evaluation intents:
- QUESTION_GENERATION
- DIFFERENTIAL_ASSESSMENT
- RED_FLAG_SCREENING
- TEST_SELECTION
- TEST_INTERPRETATION
- TREATMENT_INFORMATION
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from enum import Enum


class RAGQueryType(str, Enum):
    QUESTION_GENERATION = "QUESTION_GENERATION"
    DIFFERENTIAL_ASSESSMENT = "DIFFERENTIAL_ASSESSMENT"
    RED_FLAG_SCREENING = "RED_FLAG_SCREENING"
    TEST_SELECTION = "TEST_SELECTION"
    TEST_INTERPRETATION = "TEST_INTERPRETATION"
    TREATMENT_INFORMATION = "TREATMENT_INFORMATION"


def build_clinical_rag_query(
    query_type: RAGQueryType,
    symptoms: List[str],
    patient_profile: Optional[Dict[str, Any]] = None,
    candidate_conditions: Optional[List[str]] = None,
    test_results: Optional[List[Dict[str, Any]]] = None,
    current_message: str = "",
) -> str:
    """Build enriched clinical RAG query string."""
    prof_parts = []
    if patient_profile:
        age = patient_profile.get("age")
        sex = patient_profile.get("sex")
        weight = patient_profile.get("weight_kg")
        if age:
            prof_parts.append(f"{age}-year-old")
        if sex:
            prof_parts.append(f"{sex}")
        if weight:
            prof_parts.append(f"{weight} kg")

    profile_str = " ".join(prof_parts) if prof_parts else "patient"
    symptoms_str = ", ".join([s.replace("_", " ") for s in symptoms]) if symptoms else "unspecified symptoms"
    conditions_str = ", ".join(candidate_conditions) if candidate_conditions else ""

    if query_type == RAGQueryType.QUESTION_GENERATION:
        query = (
            f"Clinical questioning evaluation for {profile_str} presenting with {symptoms_str}. "
            f"Candidate conditions: {conditions_str}. "
            "High-value discriminating questions, severity assessment, duration, red flag screening."
        )
    elif query_type == RAGQueryType.RED_FLAG_SCREENING:
        query = (
            f"Urgent red flag screening for {profile_str} with {symptoms_str}. "
            "Life-threatening warning signs, emergency symptoms, acute complications."
        )
    elif query_type == RAGQueryType.DIFFERENTIAL_ASSESSMENT:
        query = (
            f"Differential diagnosis evidence for {profile_str} presenting with {symptoms_str}. "
            f"Primary candidate conditions: {conditions_str}. {current_message}"
        )
    elif query_type == RAGQueryType.TEST_SELECTION:
        query = (
            f"Diagnostic test selection for {profile_str} presenting with {symptoms_str}. "
            f"Suspected conditions: {conditions_str}. Relevant lab tests, imaging, investigations."
        )
    elif query_type == RAGQueryType.TEST_INTERPRETATION:
        tests_str = ", ".join([f"{t.get('test_name')}: {t.get('value')}" for t in (test_results or [])])
        query = (
            f"Lab result interpretation for {profile_str} with {symptoms_str}. "
            f"Test results: {tests_str}. Clinical significance, diagnostic criteria."
        )
    elif query_type == RAGQueryType.TREATMENT_INFORMATION:
        query = (
            f"Evidence-based treatment information for {profile_str} with {symptoms_str}. "
            f"Confirmed / suspected conditions: {conditions_str}. Supportive care, clinical guidelines."
        )
    else:
        query = f"{profile_str} presenting with {symptoms_str}. {current_message}"

    return query.strip()
