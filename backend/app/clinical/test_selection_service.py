"""
Diagnostic Test Selection & Lab Result Analysis Service.
Suggests clinically relevant investigations using non-prescriptive wording ("A clinician may consider...").
Parses and interprets patient-provided laboratory or test values with clinical context.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from rag.query_builder import RAGQueryType
from rag.hybrid_retriever import hybrid_retriever

logger = logging.getLogger(__name__)

# Standard clinical test mapping based on symptom patterns
CLINICAL_TEST_MAPPING = [
    {
        "symptoms": ["diarrhoea", "vomiting", "stomach_pain", "abdominal_pain"],
        "test": "Stool Routine & Culture",
        "reason": "Evaluates for bacterial pathogens, viral antigen, ova, parasites, or leukocyte presence in acute severe enteritis.",
        "relevant_condition": "Gastroenteritis / Dysentery"
    },
    {
        "symptoms": ["diarrhoea", "fatigue", "vomiting"],
        "test": "Serum Electrolytes & Renal Function (BUN/Creatinine)",
        "reason": "Screens for volume depletion, hypokalemia, hyponatremia, and prerenal azotemia resulting from fluid loss.",
        "relevant_condition": "Dehydration / Electrolyte Imbalance"
    },
    {
        "symptoms": ["chest_pain", "breathlessness", "sweating"],
        "test": "12-Lead ECG & Cardiac Enzymes (Troponin-I/T)",
        "reason": "Evaluates myocardial ischemia, ST-segment abnormalities, and cardiac biomarker elevation.",
        "relevant_condition": "Acute Coronary Syndrome / Angina"
    },
    {
        "symptoms": ["cough", "high_fever", "breathlessness"],
        "test": "Chest X-Ray (PA View) & Complete Blood Count (CBC)",
        "reason": "Assesses pulmonary parenchymal infiltrates, consolidation, pleural effusion, and leukocytosis.",
        "relevant_condition": "Pneumonia / Lower Respiratory Infection"
    },
    {
        "symptoms": ["high_fever", "chills", "headache"],
        "test": "Malaria Blood Smear / Rapid Diagnostic Test (RDT) & Dengue NS1 Antigen",
        "reason": "Identifies Plasmodium parasites or flavivirus antigen in acute febrile illness.",
        "relevant_condition": "Malaria / Dengue / Febrile Illness"
    },
    {
        "symptoms": ["chest_pain", "stomach_pain"],
        "test": "Upper GI Endoscopy / H. pylori Stool Antigen Test",
        "reason": "Visualizes esophageal/gastric mucosa for peptic ulceration or erosive esophagitis.",
        "relevant_condition": "GERD / Peptic Ulcer Disease"
    }
]


def recommend_diagnostic_tests(
    symptoms: List[str],
    patient_profile: Dict[str, Any],
    candidate_conditions: List[Dict[str, Any]],
    red_flags: List[str],
    rag_evidence: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Determine whether diagnostic tests may be clinically relevant.

    Returns:
        List of dicts:
        [
            {
                "test_name": "Stool Routine & Culture",
                "reason": "A clinician may consider evaluating for bacterial pathogens...",
                "relevant_condition": "Gastroenteritis",
                "evidence_sources": [...]
            }
        ]
    """
    if not symptoms:
        return []

    recommended: List[Dict[str, Any]] = []

    # 1. Match symptom patterns against clinical test bank
    for entry in CLINICAL_TEST_MAPPING:
        matches = [s for s in entry["symptoms"] if s in symptoms]
        if matches:
            sources = [e.get("source", "Clinical Guidelines") for e in (rag_evidence or [])[:2]]
            recommended.append({
                "test_name": entry["test"],
                "reason": f"A clinician may consider {entry['test'].lower()} to evaluate for {entry['reason'].lower()}",
                "relevant_condition": entry["relevant_condition"],
                "evidence_sources": sources
            })

    # Deduplicate by test name
    unique_tests = []
    seen = set()
    for test in recommended:
        if test["test_name"] not in seen:
            seen.add(test["test_name"])
            unique_tests.append(test)

    return unique_tests[:3]


def analyze_patient_test_results(
    test_results: List[Dict[str, Any]],
    symptoms: List[str],
    patient_profile: Dict[str, Any],
    candidate_conditions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Interpret laboratory/test results in the context of patient symptoms and profile.
    """
    if not test_results:
        return {"interpretation": "No laboratory test results provided.", "findings": []}

    rag_evidence = hybrid_retriever.retrieve_hybrid_evidence(
        query_type=RAGQueryType.TEST_INTERPRETATION,
        symptoms=symptoms,
        patient_profile=patient_profile,
        candidate_conditions=[c.get("disease", "") for c in candidate_conditions],
        test_results=test_results,
        top_k=3
    )

    findings = []
    for t in test_results:
        t_name = t.get("test_name", "Laboratory Test")
        val = t.get("value", "")
        findings.append(f"{t_name} reported as '{val}' within current clinical presentation.")

    sources = [e.get("source", "Reference") for e in rag_evidence]

    return {
        "interpretation": f"Laboratory findings ({', '.join(findings)}) were evaluated alongside symptoms ({', '.join(symptoms)}).",
        "findings": findings,
        "evidence_sources": sources
    }
