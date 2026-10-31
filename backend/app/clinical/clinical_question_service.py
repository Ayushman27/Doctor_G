"""
Clinical Question Generation Service.
Generates ONE targeted, symptom-specific question at a time using RAG evidence,
patient profile, and differential diagnosis context.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Tuple

from app.services.symptom_question_service import QUESTION_BANK
from app.services.llm_service import get_llm_provider
from rag.query_builder import RAGQueryType
from rag.hybrid_retriever import hybrid_retriever

logger = logging.getLogger(__name__)


def generate_next_clinical_question(
    symptoms: List[str],
    symptom_details: Dict[str, Any],
    patient_profile: Dict[str, Any],
    candidate_conditions: List[Dict[str, Any]],
    questions_asked: List[str],
    previous_answers: List[Dict[str, Any]],
    red_flags: List[str],
    rag_evidence: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Select or generate the next high-value clinical question.

    Returns:
        {
            "question": str,
            "reason": str,
            "symptom_target": str,
            "priority": str,  # 'high', 'medium', 'low'
            "quick_replies": List[str],
            "evidence_sources": List[str]
        }
    """
    if not symptoms:
        return {
            "question": "Hi! Please tell me what symptoms or health problems you are currently experiencing.",
            "reason": "Initial symptom identification mandatory before clinical assessment.",
            "symptom_target": "initial_complaint",
            "priority": "high",
            "quick_replies": ["I have loose motion and stomach pain", "I have chest pain", "I have fever and cough"],
            "evidence_sources": []
        }

    asked_lower = [q.lower().strip() for q in questions_asked]
    candidate_names = [c.get("disease", "").lower() for c in candidate_conditions[:4]]

    # 1. Retrieve RAG evidence for question generation if not passed
    if rag_evidence is None:
        rag_evidence = hybrid_retriever.retrieve_hybrid_evidence(
            query_type=RAGQueryType.QUESTION_GENERATION,
            symptoms=symptoms,
            patient_profile=patient_profile,
            candidate_conditions=candidate_names,
            top_k=3
        )

    # 2. Score and select from clinical question bank matching symptoms
    scored_candidates: List[Tuple[float, Dict[str, Any]]] = []

    for entry in QUESTION_BANK:
        q_text = entry["question"]
        q_id = entry["id"]

        if q_text.lower().strip() in asked_lower or q_id.lower() in asked_lower:
            continue
        if any(q_id in a or q_text[:25].lower() in a for a in asked_lower):
            continue

        # Rule check: Question MUST relate to reported symptoms!
        matching_symptoms = [s for s in entry["symptoms"] if s in symptoms]
        if not matching_symptoms:
            continue

        score = 0.0
        score += len(matching_symptoms) * 4.0

        # Match with candidate conditions
        d_matches = sum(1 for d in entry["diseases"] if d.lower() in candidate_names)
        score += d_matches * 3.0

        # Safety priority weighting (1..5)
        score += entry.get("safety_priority", 1) * 2.0

        # Boost specific acute symptom priorities
        if "chest_pain" in symptoms and "chest" in q_id:
            score += 5.0
        if "diarrhoea" in symptoms and "diarrhea" in q_id:
            score += 5.0

        scored_candidates.append((score, entry))

    if scored_candidates:
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_entry = scored_candidates[0][1]

        target_sym = best_entry["symptoms"][0] if best_entry["symptoms"] else symptoms[0]
        sources = [e.get("source", "Clinical Reference") for e in (rag_evidence or [])[:2]]

        return {
            "question": best_entry["question"],
            "reason": best_entry["reason"],
            "symptom_target": target_sym,
            "priority": "high" if best_entry.get("safety_priority", 1) >= 4 else "medium",
            "quick_replies": best_entry.get("quick_replies", []),
            "evidence_sources": sources
        }

    # 3. Fallback LLM Question Generation guided strictly by symptoms & RAG
    try:
        llm = get_llm_provider()
        evidence_text = "\n".join([f"- {e.get('title')}: {e.get('summary')}" for e in (rag_evidence or [])])
        prompt = (
            f"Patient symptoms: {symptoms}\n"
            f"Patient profile: {patient_profile}\n"
            f"Previous questions asked: {questions_asked}\n"
            f"RAG clinical evidence:\n{evidence_text}\n\n"
            "Generate ONE targeted, high-value clinical follow-up question related ONLY to the reported symptoms.\n"
            "Return JSON with keys 'question', 'reason', 'symptom_target', 'quick_replies'."
        )
        res = llm.generate_json(prompt, system_instruction="You are a clinical interviewer. Return valid JSON.")
        if res.get("question"):
            return {
                "question": res["question"],
                "reason": res.get("reason", f"Characterize reported symptom {symptoms[0]}."),
                "symptom_target": res.get("symptom_target", symptoms[0]),
                "priority": "medium",
                "quick_replies": res.get("quick_replies", ["Yes", "No", "Unsure"]),
                "evidence_sources": [e.get("source", "") for e in (rag_evidence or [])[:2]]
            }
    except Exception as exc:
        logger.warning("LLM question generation fallback note: %s", exc)

    # Generic symptom follow-up default
    sym_readable = symptoms[0].replace("_", " ")
    return {
        "question": f"Regarding your {sym_readable}, could you describe when it started and how severe it feels on a scale of 1 to 10?",
        "reason": f"Assess duration and severity of reported {sym_readable}.",
        "symptom_target": symptoms[0],
        "priority": "medium",
        "quick_replies": ["Mild (1-3)", "Moderate (4-6)", "Severe (7-10)"],
        "evidence_sources": []
    }
