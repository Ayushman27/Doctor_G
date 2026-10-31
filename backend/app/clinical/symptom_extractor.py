"""
Symptom & Duration Extraction Service.
Extracts canonical symptoms and duration mapping from natural language user input.
"""

from __future__ import annotations

import logging
import re
from typing import List, Dict, Any

from app.core.model_loader import registry
from app.services.disease_service import normalize_symptom
from app.services.llm_service import get_llm_provider

logger = logging.getLogger(__name__)

# Duration extraction regex patterns
DURATION_PATTERNS = [
    (r"(?:since\s+)?yesterday", "1 day"),
    (r"(?:for\s+)?(\d+)\s*days?", r"\1 days"),
    (r"(?:for\s+)?(\d+)\s*weeks?", r"\1 weeks"),
    (r"(?:for\s+)?(\d+)\s*hours?", r"\1 hours"),
    (r"(?:for\s+)?(\d+)\s*months?", r"\1 months"),
    (r"today|this morning|just started", "today"),
]

DEFAULT_FALLBACK_SYMPTOMS = [
    "high_fever", "cough", "throat_irritation", "muscle_pain", "stomach_pain",
    "breathlessness", "sweating", "vomiting", "diarrhoea", "chest_pain",
    "abdominal_pain", "headache", "fatigue", "chills", "nausea", "joint_pain",
    "bloody_stool", "tarry_stool", "skin_rash", "itching"
]


def extract_duration_from_text(text: str) -> str:
    """Extract duration string from natural language text."""
    text_lower = text.lower()
    for pattern, replacement in DURATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            if "\\" in replacement:
                return re.sub(pattern, replacement, match.group(0))
            return replacement
    return "unspecified"


def get_supported_symptoms() -> List[str]:
    """Retrieve supported symptoms from registry, initializing if required."""
    if not registry.is_loaded():
        try:
            registry.initialize()
        except Exception as exc:
            logger.warning("Registry init notice in symptom extractor (%s). Using fallback list.", exc)

    syms = registry.disease_symptoms
    return syms if syms else DEFAULT_FALLBACK_SYMPTOMS


def extract_symptoms_and_duration(message: str) -> Dict[str, Any]:
    """
    Extract symptoms list and duration mapping from natural language.
    """
    supported_symptoms = get_supported_symptoms()
    msg_lower = message.lower().strip()

    matched: List[str] = []
    unmatched: List[str] = []

    # Common synonym dictionary
    synonyms = {
        "fever": "high_fever",
        "high fever": "high_fever",
        "coughing": "cough",
        "cough": "cough",
        "throat pain": "throat_irritation",
        "sore throat": "throat_irritation",
        "body ache": "muscle_pain",
        "body pain": "muscle_pain",
        "muscle pain": "muscle_pain",
        "stomach pain": "stomach_pain",
        "abdominal pain": "abdominal_pain",
        "stomach ache": "stomach_pain",
        "tummy pain": "stomach_pain",
        "belly pain": "stomach_pain",
        "shortness of breath": "breathlessness",
        "hard to breathe": "breathlessness",
        "difficulty breathing": "breathlessness",
        "sweating": "sweating",
        "sweat": "sweating",
        "vomit": "vomiting",
        "vomiting": "vomiting",
        "nausea": "nausea",
        "feeling sick": "nausea",
        "lose motion": "diarrhoea",
        "loose motion": "diarrhoea",
        "loose motions": "diarrhoea",
        "lose motions": "diarrhoea",
        "loose stool": "diarrhoea",
        "loose stools": "diarrhoea",
        "diarrhea": "diarrhoea",
        "diarrhoea": "diarrhoea",
        "chest pain": "chest_pain",
        "chest discomfort": "chest_pain",
        "headache": "headache",
        "head ache": "headache",
        "head hurts": "headache",
        "weak": "fatigue",
        "weakness": "fatigue",
        "feeling weak": "fatigue",
        "tired": "fatigue",
        "fatigue": "fatigue",
        "blood in stool": "bloody_stool",
        "bloody stool": "bloody_stool",
        "black stool": "tarry_stool",
    }

    # 1. Check synonym dict first
    for synonym, canon in synonyms.items():
        if synonym in msg_lower:
            if canon not in matched:
                matched.append(canon)

    # 2. Direct keyword scanning against supported symptoms
    for sym in supported_symptoms:
        readable = sym.replace("_", " ")
        if sym in msg_lower or readable in msg_lower:
            if sym not in matched:
                matched.append(sym)

    # If no direct match and text is descriptive, attempt LLM fallback
    skip_llm = len(msg_lower.split()) < 3 or any(w in msg_lower for w in ["hi", "hello", "yes", "no", "male", "female", "kg", "years old"])
    if not matched and not skip_llm:
        try:
            llm = get_llm_provider()
            prompt = (
                f"Extract clinical symptoms from: '{message}'.\n"
                f"Allowed canonical symptoms: {supported_symptoms[:40]}...\n"
                "Return JSON: {'symptoms': ['canonical_name'], 'unmatched': ['other_symptoms']}"
            )
            res = llm.generate_json(prompt, system_instruction="Extract symptoms as JSON.")
            llm_syms = res.get("symptoms", [])
            for s in llm_syms:
                norm = normalize_symptom(s)
                if norm in supported_symptoms and norm not in matched:
                    matched.append(norm)
                else:
                    unmatched.append(s)
        except Exception as exc:
            logger.warning("LLM symptom extraction notice: %s", exc)

    extracted_duration = extract_duration_from_text(message)
    duration_map: Dict[str, str] = {}
    for s in matched:
        duration_map[s] = extracted_duration

    return {
        "symptoms": matched,
        "duration": duration_map,
        "unmatched": unmatched
    }
