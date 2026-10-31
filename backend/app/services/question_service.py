"""
Intelligent Question Generation Service.
Generates focused follow-up questions to distinguish top competing disease candidates.
Enforces MAX_FOLLOWUP_QUESTIONS = 5 and prevents asking duplicate questions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.core.config import settings
from app.services.llm_service import get_llm_provider

logger = logging.getLogger(__name__)

# Pre-defined high-value clinical fallback questions for key differential diseases
CLINICAL_QUESTIONS_MAP = [
    {
        "diseases": ["Pneumonia", "Bronchial Asthma", "Influenza"],
        "symptom_trigger": ["fever", "cough"],
        "question": "Have you experienced any shortness of breath or difficulty breathing?",
        "reason": "Dyspnea is a hallmark feature distinguishing lower pulmonary involvement (Pneumonia) from uncomplicated viral flu or upper respiratory infection."
    },
    {
        "diseases": ["Pneumonia", "Heart Attack", "GERD"],
        "symptom_trigger": ["cough", "chest_pain"],
        "question": "Does the chest pain get sharper when taking a deep breath or coughing?",
        "reason": "Pleuritic chest pain (sharper with deep breath) strongly points toward lung lining inflammation (Pneumonia) rather than cardiac ischemia."
    },
    {
        "diseases": ["Influenza", "Common Cold", "Dengue"],
        "symptom_trigger": ["fever"],
        "question": "How many days have you had the fever, and is it accompanied by intense muscle or joint aches?",
        "reason": "Sudden high fever with severe muscle aches points toward Influenza or Dengue rather than a gradual common cold."
    },
    {
        "diseases": ["Malaria", "Typhoid", "Dengue"],
        "symptom_trigger": ["fever", "chills"],
        "question": "Do you experience severe shaking chills followed by heavy sweating in recurring cycles?",
        "reason": "Cyclical paroxysms of fever and sweating are key diagnostic hallmarks of Malaria."
    },
    {
        "diseases": ["Gastroenteritis", "GERD", "Peptic Ulcer Disease"],
        "symptom_trigger": ["vomiting", "nausea", "abdominal_pain"],
        "question": "Is the stomach discomfort relieved shortly after eating food or taking antacids?",
        "reason": "Pain relief after food ingestion is typical of peptic ulcer disease, whereas gastroenteritis causes persistent diarrhea and vomiting."
    },
    {
        "diseases": ["Diabetes", "Hypertension", "Hypoglycemia"],
        "symptom_trigger": ["fatigue"],
        "question": "Have you noticed excessive thirst, frequent urination, or sudden unexplained weight loss?",
        "reason": "The triad of polyuria, polydipsia, and weight loss distinguishes Diabetes Mellitus."
    }
]


def load_question_prompt() -> str:
    """Load question generation prompt template."""
    prompt_path = Path(__file__).resolve().parent.parent.parent / "prompts" / "question_generation.txt"
    if prompt_path.is_file():
        return prompt_path.read_text(encoding="utf-8")
    return ""


def generate_followup_question(
    symptoms: List[str],
    candidate_diseases: List[Dict[str, Any]],
    questions_asked: List[str],
    retrieved_evidence: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """
    Select or generate an intelligent, clinical follow-up question.
    Prevents asking duplicate questions.

    Returns:
        Tuple of (question_string, clinical_reason_string)
    """
    max_questions = getattr(settings, "max_followup_questions", 5)

    if len(questions_asked) >= max_questions:
        logger.info("Maximum follow-up question limit (%d) reached.", max_questions)
        return "", "Maximum follow-up question limit reached."

    # Extract top candidate disease titles
    top_disease_names = [c.get("disease", "") for c in candidate_diseases[:3] if c.get("disease")]

    # 1. First attempt via LLM Provider
    prompt_template = load_question_prompt()
    if prompt_template:
        formatted_prompt = prompt_template.format(
            symptoms=", ".join(symptoms),
            candidate_diseases=", ".join(top_disease_names),
            retrieved_evidence="\n".join([f"- {e.get('title', 'Ref')}: {(e.get('summary') or e.get('content') or '')[:150]}" for e in (retrieved_evidence or [])[:3]]),
            questions_asked="\n".join([f"- {q}" for q in questions_asked]) if questions_asked else "None"
        )

        llm = get_llm_provider()
        try:
            res = llm.generate_json(formatted_prompt, system_instruction="Generate a single clinical follow-up question as JSON.")
            q_text = res.get("question", "").strip()
            q_reason = res.get("reason", "").strip()

            if q_text and q_text.lower() not in [q.lower() for q in questions_asked]:
                logger.info("Generated LLM follow-up question: '%s'", q_text)
                return q_text, q_reason
        except Exception as exc:
            logger.warning("LLM question generation failed (%s). Falling back to clinical rule map.", exc)

    # 2. Fallback to clinical rule map
    for entry in CLINICAL_QUESTIONS_MAP:
        q_text = entry["question"]
        if q_text.lower() not in [q.lower() for q in questions_asked]:
            # Check if any candidate disease or symptom overlaps
            disease_match = any(d.lower() in [td.lower() for td in top_disease_names] for d in entry["diseases"])
            symptom_match = any(s in symptoms for s in entry["symptom_trigger"])
            if disease_match or symptom_match:
                logger.info("Selected fallback clinical question: '%s'", q_text)
                return q_text, entry["reason"]

    # 3. Generic safe fallback
    fallback_q = "How long have you been experiencing these symptoms, and have they worsened recently?"
    if fallback_q.lower() not in [q.lower() for q in questions_asked]:
        return fallback_q, "Determining symptom onset and progression aids clinical assessment."

    return "", "No unique follow-up question available."
