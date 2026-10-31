"""
RAG Service Coordinator.
Interfaces FastAPI endpoints and conversational services with Advanced Hybrid RAG Retriever.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from rag.hybrid_retriever import hybrid_retriever
from rag.query_builder import RAGQueryType

logger = logging.getLogger(__name__)


def retrieve_medical_evidence(
    symptoms: List[str],
    candidate_diseases: List[Dict[str, Any]],
    current_message: str = "",
    patient_profile: Optional[Dict[str, Any]] = None,
    query_type: RAGQueryType = RAGQueryType.DIFFERENTIAL_ASSESSMENT,
    test_results: Optional[List[Dict[str, Any]]] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve grounded medical evidence chunks using Advanced Hybrid RAG
    (Vector Search + BM25 + Metadata Filtering + RRF + Cross-Encoder Reranking).
    """
    disease_names = [d.get("disease", "") for d in candidate_diseases if d.get("disease")]

    return hybrid_retriever.retrieve_hybrid_evidence(
        query_type=query_type,
        symptoms=symptoms,
        patient_profile=patient_profile,
        candidate_conditions=disease_names,
        test_results=test_results,
        current_message=current_message,
        top_k=top_k
    )
