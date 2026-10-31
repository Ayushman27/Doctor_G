"""
Advanced Hybrid RAG Retriever.
Combines Vector Search (ChromaDB) + BM25 Keyword Retrieval + Metadata Filtering + Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from rag.vector_store import vector_store
from rag.bm25_retriever import bm25_retriever
from rag.reranker import rerank_evidence
from rag.query_builder import RAGQueryType, build_clinical_rag_query

logger = logging.getLogger(__name__)


def apply_metadata_filtering(
    candidates: List[Dict[str, Any]],
    patient_profile: Optional[Dict[str, Any]] = None,
    symptoms: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Filter candidate evidence based on patient metadata (e.g. pediatric vs adult filters).
    """
    if not candidates:
        return []

    filtered = []
    age = patient_profile.get("age") if patient_profile else None
    target_age_group = "all"
    if age is not None:
        if age < 18:
            target_age_group = "pediatric"
        elif age >= 65:
            target_age_group = "elderly"
        else:
            target_age_group = "adult"

    for doc in candidates:
        doc_age = doc.get("age_group", "all")
        # Keep document if age group matches or is 'all'
        if doc_age in ["all", target_age_group]:
            filtered.append(doc)
        elif target_age_group == "pediatric" and doc_age == "all":
            filtered.append(doc)

    return filtered if filtered else candidates


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion (RRF) algorithm:
    RRF_Score(d) = 1/(k + rank_vector(d)) + 1/(k + rank_bm25(d))
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    # Process vector search results
    for rank, doc in enumerate(vector_results):
        doc_id = doc.get("chunk_id", f"v_{rank}")
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    # Process BM25 keyword results
    for rank, doc in enumerate(bm25_results):
        doc_id = doc.get("chunk_id", f"b_{rank}")
        if doc_id not in doc_map:
            doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

    # Sort candidates by combined RRF score
    fused: List[Dict[str, Any]] = []
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    for doc_id in sorted_ids:
        doc_copy = doc_map[doc_id].copy()
        doc_copy["rrf_score"] = round(scores[doc_id], 6)
        fused.append(doc_copy)

    return fused


class AdvancedHybridRetriever:
    """Full Advanced Hybrid RAG Retriever implementation."""

    def __init__(self, vector_k: int = 20, bm25_k: int = 20, fusion_k: int = 30, top_k: int = 5):
        self.vector_k = vector_k
        self.bm25_k = bm25_k
        self.fusion_k = fusion_k
        self.top_k = top_k
        self._loaded = False

    def ensure_indexed(self):
        """Ensure vector store and BM25 index are initialized and synchronized."""
        if self._loaded:
            return
        vector_store.initialize()
        if vector_store.metadata:
            bm25_retriever.index_documents(vector_store.metadata)
        self._loaded = True

    def retrieve_hybrid_evidence(
        self,
        query_type: RAGQueryType,
        symptoms: List[str],
        patient_profile: Optional[Dict[str, Any]] = None,
        candidate_conditions: Optional[List[str]] = None,
        test_results: Optional[List[Dict[str, Any]]] = None,
        current_message: str = "",
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Full Hybrid RAG Retrieval Pipeline:
        Vector Search + BM25 -> RRF Fusion -> Metadata Filter -> Cross-Encoder Rerank.
        """
        self.ensure_indexed()

        query_str = build_clinical_rag_query(
            query_type=query_type,
            symptoms=symptoms,
            patient_profile=patient_profile,
            candidate_conditions=candidate_conditions,
            test_results=test_results,
            current_message=current_message
        )

        # 1. Vector Search
        vector_res = vector_store.search(query=query_str, top_k=self.vector_k)

        # 2. BM25 Search
        bm25_res = bm25_retriever.search(query=query_str, top_k=self.bm25_k)

        # 3. Reciprocal Rank Fusion
        fused_candidates = reciprocal_rank_fusion(vector_res, bm25_res)

        # 4. Metadata Filtering
        filtered_candidates = apply_metadata_filtering(fused_candidates, patient_profile, symptoms)

        # 5. Cross-Encoder Reranking
        k_final = top_k or self.top_k
        top_evidence = rerank_evidence(query=query_str, candidates=filtered_candidates[:self.fusion_k], top_k=k_final)

        # Format output payload for front-end/service ingestion
        formatted_results = []
        for item in top_evidence:
            formatted_results.append({
                "chunk_id": item.get("chunk_id", ""),
                "source": item.get("source", "Medical Reference"),
                "title": item.get("title", ""),
                "organization": item.get("organization", "Health Guideline"),
                "author": item.get("author", ""),
                "publication_date": item.get("publication_date", ""),
                "document_type": item.get("document_type", "reference"),
                "chapter": item.get("chapter", ""),
                "section": item.get("section", ""),
                "topic": item.get("topic", ""),
                "disease": item.get("disease", ""),
                "summary": item.get("content", ""),
                "url": item.get("url", ""),
                "score": item.get("final_score", item.get("rrf_score", 0.5)),
            })

        logger.info("Hybrid RAG retrieved %d evidence chunks for query type %s.", len(formatted_results), query_type.value)
        return formatted_results


hybrid_retriever = AdvancedHybridRetriever()
