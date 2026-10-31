"""
Cross-Encoder Evidence Reranker.
Reranks candidate evidence passages against query context to score relevance precisely.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

_reranker_model_cache = None


def get_reranker_model():
    """Load and cache CrossEncoder reranking model."""
    global _reranker_model_cache
    if _reranker_model_cache is None:
        try:
            from sentence_transformers import CrossEncoder
            logger.info("Loading CrossEncoder reranker model: cross-encoder/ms-marco-MiniLM-L-6-v2")
            _reranker_model_cache = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as exc:
            logger.info("CrossEncoder load note (%s). Using similarity score fallback reranker.", exc)
            _reranker_model_cache = "FALLBACK"
    return _reranker_model_cache


def rerank_evidence(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Rerank candidate document chunks using Cross-Encoder scores.
    Returns top_k highest-quality evidence passages.
    """
    if not candidates:
        return []

    model = get_reranker_model()

    if model != "FALLBACK":
        try:
            pairs = [(query, doc.get("content", "")) for doc in candidates]
            scores = model.predict(pairs)
            for idx, score in enumerate(scores):
                candidates[idx]["cross_encoder_score"] = float(score)
                # Map raw score to 0..1 scale
                sigmoid_score = 1.0 / (1.0 + float(np.exp(-score))) if hasattr(score, "__iter__") else float(score)
                candidates[idx]["final_score"] = round(float(candidates[idx].get("rrf_score", score)), 4)

            sorted_docs = sorted(candidates, key=lambda x: x.get("cross_encoder_score", 0.0), reverse=True)
            return sorted_docs[:top_k]
        except Exception as exc:
            logger.warning("CrossEncoder rerank failed (%s). Using fallback score sort.", exc)

    # Fallback score ranking (uses rrf_score or vector_score)
    sorted_docs = sorted(
        candidates,
        key=lambda x: (x.get("rrf_score", 0.0) * 0.6 + x.get("vector_score", 0.0) * 0.4 + x.get("bm25_score", 0.0) * 0.4),
        reverse=True
    )
    for doc in sorted_docs:
        raw_sc = doc.get("rrf_score", doc.get("vector_score", 0.5))
        doc["final_score"] = round(float(raw_sc), 4)

    return sorted_docs[:top_k]
