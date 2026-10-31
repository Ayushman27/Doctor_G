"""
Dynamic Symptom-Specific Question Engine.
Selects targeted, clinically relevant follow-up questions one-at-a-time based on:
- Patient symptoms
- Patient profile (age, sex, weight)
- Top candidate diseases from ML model
- Previous questions and answers
- Information gain and safety priority
Enforces MAX_FOLLOWUP_QUESTIONS = 5 and avoids repetition.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

MAX_FOLLOWUP_QUESTIONS = 5

# Comprehensive Clinical Question Bank keyed by symptom/differential focus
QUESTION_BANK: List[Dict[str, Any]] = [
    # --- DIARRHEA / LOOSE MOTION QUESTIONS ---
    {
        "id": "diarrhea_duration",
        "symptoms": ["diarrhoea", "vomiting"],
        "diseases": ["Gastroenteritis", "Typhoid", "Peptic Ulcer Disease"],
        "question": "How long have you had the loose motions (e.g., since yesterday, 2-3 days)?",
        "category": "symptom_characterization",
        "safety_priority": 3,
        "quick_replies": ["Since yesterday", "2-3 days", "More than 5 days"],
        "reason": "Acute onset within 24-48 hours points to viral or foodborne gastroenteritis, whereas chronic duration suggests inflammatory or malabsorptive etiology."
    },
    {
        "id": "diarrhea_frequency",
        "symptoms": ["diarrhoea"],
        "diseases": ["Gastroenteritis", "Typhoid"],
        "question": "Approximately how many episodes of loose motion have you had in the last 24 hours?",
        "category": "symptom_severity",
        "safety_priority": 4,
        "quick_replies": ["1 to 3 times", "4 to 6 times", "More than 6 times"],
        "reason": "High stool frequency increases acute volume depletion and electrolyte loss."
    },
    {
        "id": "diarrhea_blood",
        "symptoms": ["diarrhoea"],
        "diseases": ["Gastroenteritis", "Peptic Ulcer Disease"],
        "question": "Have you noticed any visible blood or black/tarry color in your stool?",
        "category": "safety_screening",
        "safety_priority": 5,
        "quick_replies": ["No blood", "Yes, visible red blood", "Black or tarry stool"],
        "reason": "Presence of blood (dysentery) distinguishes invasive bacterial infection or mucosal ulceration from benign watery viral gastroenteritis."
    },
    {
        "id": "gi_fever_vomiting",
        "symptoms": ["diarrhoea"],
        "diseases": ["Gastroenteritis", "Typhoid"],
        "question": "Are you experiencing any vomiting or high fever alongside the loose motions?",
        "category": "associated_symptoms",
        "safety_priority": 4,
        "quick_replies": ["Yes, vomiting only", "Yes, fever only", "Both vomiting and fever", "Neither"],
        "reason": "Concomitant vomiting limits oral rehydration and alongside fever strongly suggests infectious gastroenteritis."
    },
    {
        "id": "gi_hydration",
        "symptoms": ["diarrhoea", "vomiting"],
        "diseases": ["Gastroenteritis"],
        "question": "Are you able to keep fluids down, and have you felt any severe dizziness or dry mouth?",
        "category": "safety_screening",
        "safety_priority": 5,
        "quick_replies": ["Keeping fluids down fine", "Mild thirst only", "Feeling dizzy / struggling to drink"],
        "reason": "Screens for clinical dehydration requiring oral rehydration salts or intravenous hydration."
    },
    {
        "id": "gi_food_exposure",
        "symptoms": ["diarrhoea", "vomiting", "stomach_pain"],
        "diseases": ["Gastroenteritis", "Typhoid"],
        "question": "Did symptoms start after eating outside food, or did anyone else sharing the food fall ill?",
        "category": "epidemiology",
        "safety_priority": 2,
        "quick_replies": ["Ate outside food recently", "Home food only", "Others also unwell"],
        "reason": "Foodborne toxin ingestion manifests with rapid onset after contaminated meals."
    },

    # --- CHEST PAIN / DISCOMFORT QUESTIONS ---
    {
        "id": "chest_onset_timing",
        "symptoms": ["chest_pain"],
        "diseases": ["GERD", "Heart Attack", "Peptic Ulcer Disease"],
        "question": "Regarding the chest discomfort, when did it start, and does it seem related to eating meals?",
        "category": "symptom_characterization",
        "safety_priority": 4,
        "quick_replies": ["Started after eating", "Started during physical exertion", "Started at rest randomly"],
        "reason": "Post-prandial onset points towards gastroesophageal reflux (GERD) or dyspepsia rather than acute coronary syndrome."
    },
    {
        "id": "chest_position_posture",
        "symptoms": ["chest_pain"],
        "diseases": ["GERD", "Heart Attack", "Pneumonia"],
        "question": "Does the chest discomfort get worse when lying flat, bending forward, or after heavy meals?",
        "category": "differential_value",
        "safety_priority": 4,
        "quick_replies": ["Worse when lying down", "Relieved when standing up", "No change with position"],
        "reason": "Postural aggravation with recumbency is a classic clinical indicator of gastroesophageal acid reflux (GERD)."
    },
    {
        "id": "chest_breathing_pleuritic",
        "symptoms": ["chest_pain"],
        "diseases": ["Pneumonia", "Bronchial Asthma", "GERD"],
        "question": "Does the discomfort become sharper when taking a deep breath, coughing, or moving your torso?",
        "category": "differential_value",
        "safety_priority": 3,
        "quick_replies": ["Yes, sharper with deep breath", "No change with breathing"],
        "reason": "Pleuritic chest pain (sharper with inhalation) suggests pulmonary/pleural or musculoskeletal etiology rather than ischemic heart disease."
    },
    {
        "id": "chest_safety_radiation",
        "symptoms": ["chest_pain"],
        "diseases": ["Heart Attack", "Hypertension", "GERD"],
        "question": "Do you have severe crushing pressure, difficulty breathing, heavy sweating, or pain spreading to your arm, shoulder, or jaw?",
        "category": "safety_screening",
        "safety_priority": 5,
        "quick_replies": ["No, none of these warning signs", "Yes, mild arm/jaw aching", "Yes, severe pressure / cannot breathe"],
        "reason": "Critical cardinal red-flag screening for acute myocardial ischemia or angina."
    },
    {
        "id": "chest_quality",
        "symptoms": ["chest_pain"],
        "diseases": ["GERD", "Heart Attack"],
        "question": "How would you describe the feeling: is it a burning sensation rising in the chest, or a heavy crushing tightness?",
        "category": "symptom_characterization",
        "safety_priority": 4,
        "quick_replies": ["Burning sensation / heartburn", "Ache / soreness", "Heavy tightness"],
        "reason": "Retrosternal burning (pyrosis) strongly favors acid reflux, whereas heavy pressure warrants cardiac vigilance."
    },

    # --- RESPIRATORY & SYSTEMIC QUESTIONS ---
    {
        "id": "respiratory_dyspnea",
        "symptoms": ["cough", "breathlessness"],
        "diseases": ["Bronchial Asthma", "Pneumonia", "Heart Attack"],
        "question": "Are you experiencing wheezing, whistling sounds when breathing, or tightness in the chest?",
        "category": "differential_value",
        "safety_priority": 4,
        "quick_replies": ["Yes, wheezing sound", "Tightness only", "No wheezing"],
        "reason": "Expiratory wheezing suggests bronchospasm/asthma, whereas localized crackles suggest pneumonia."
    },
    {
        "id": "fever_nature",
        "symptoms": ["high_fever", "fever"],
        "diseases": ["Typhoid", "Malaria", "Dengue", "Pneumonia"],
        "question": "Has the fever been continuous and rising, or does it come and go with severe shivering and shaking chills?",
        "category": "differential_value",
        "safety_priority": 4,
        "quick_replies": ["Continuous fever", "Recurring chills and sweating", "Mild low-grade fever"],
        "reason": "Shaking chills (rigors) with diaphoretic defervescence characterize malaria and acute pyogenic infections."
    }
]


def select_next_question(
    symptoms: List[str],
    candidate_diseases: List[Dict[str, Any]],
    questions_asked: List[str],
    patient_profile: Any = None,
    symptom_details: Dict[str, Any] = None
) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
    """
    Select the highest information-gain question that has not been asked yet.
    Returns:
        (question_text, clinical_rationale, quick_replies) or (None, None, None) if limit reached.
    """
    if len(questions_asked) >= MAX_FOLLOWUP_QUESTIONS:
        logger.info("Maximum follow-up question limit (%d) reached.", MAX_FOLLOWUP_QUESTIONS)
        return None, None, None

    asked_lower = [q.lower().strip() for q in questions_asked]
    candidate_names = [c.get("disease", "").lower() for c in candidate_diseases[:4]]

    scored_questions: List[Tuple[float, Dict[str, Any]]] = []

    for entry in QUESTION_BANK:
        q_text = entry["question"]
        if q_text.lower().strip() in asked_lower or entry["id"].lower() in asked_lower:
            continue

        # Check if already asked in similar phrasing
        if any(entry["id"] in a or q_text[:30].lower() in a for a in asked_lower):
            continue

        score = 0.0

        # 1. Symptom Match (relevance)
        symptom_matches = sum(1 for s in entry["symptoms"] if s in symptoms)
        score += symptom_matches * 3.0

        # 2. Candidate Disease Match (differential value)
        disease_matches = sum(1 for d in entry["diseases"] if d.lower() in candidate_names)
        score += disease_matches * 2.5

        # 3. Safety Priority Weight
        score += entry.get("safety_priority", 1) * 1.5

        # If question has chest pain and chest pain is present, boost priority to screen early
        if "chest_pain" in symptoms and "chest" in entry["id"]:
            score += 2.0

        # If loose motion is present and question addresses diarrhea, boost priority
        if "diarrhoea" in symptoms and "diarrhea" in entry["id"]:
            score += 2.0

        scored_questions.append((score, entry))

    if not scored_questions:
        return None, None, None

    # Sort descending by score
    scored_questions.sort(key=lambda x: x[0], reverse=True)
    best_entry = scored_questions[0][1]

    logger.info("Selected next clinical question: '%s' (Score: %.2f)", best_entry["id"], scored_questions[0][0])
    return best_entry["question"], best_entry["reason"], best_entry.get("quick_replies")
