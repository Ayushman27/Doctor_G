"""
Medical RAG Retriever.
Queries persistent FAISS vector store to retrieve grounded medical evidence context
based on patient symptoms, candidate diseases, current questions, and conversation history.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.config import settings
from rag.config import (
    FAISS_INDEX_PATH,
    METADATA_PKL_PATH,
    VECTORSTORE_DIR,
    DEFAULT_TOP_K,
    DEFAULT_SCORE_THRESHOLD,
)
from rag.ingestion import get_embeddings, build_and_save_vectorstore

logger = logging.getLogger(__name__)


class MedicalRetriever:
    """Retriever for authoritative medical evidence from FAISS vector store."""

    def __init__(self, top_k: int = DEFAULT_TOP_K, score_threshold: float = DEFAULT_SCORE_THRESHOLD):
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.faiss_index = None
        self.metadata: List[Dict[str, Any]] = []
        self.fallback_embeddings: Optional[np.ndarray] = None
        self._loaded = False

    def load_vectorstore(self) -> bool:
        """Load persistent FAISS index and metadata. Auto-build if missing."""
        if self._loaded:
            return True

        numpy_path = VECTORSTORE_DIR / "embeddings.npy"
        has_vectors = FAISS_INDEX_PATH.exists() or numpy_path.exists()
        if not has_vectors or not METADATA_PKL_PATH.exists():
            logger.info("Vectorstore missing. Triggering auto-ingestion...")
            build_and_save_vectorstore()

        # Load metadata
        if METADATA_PKL_PATH.exists():
            try:
                with open(METADATA_PKL_PATH, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info("Loaded RAG metadata: %d passages.", len(self.metadata))
            except Exception as exc:
                logger.error("Failed loading RAG metadata: %s", exc)

        # Load FAISS index
        if FAISS_INDEX_PATH.exists():
            try:
                import faiss
                self.faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
                logger.info("Loaded FAISS index with %d vectors.", self.faiss_index.ntotal)
            except Exception as exc:
                logger.warning("FAISS read_index failed (%s). Checking fallback matrix.", exc)

        # Fallback numpy matrix if FAISS is unavailable
        if self.faiss_index is None and numpy_path.exists():
            try:
                self.fallback_embeddings = np.load(str(numpy_path))
                logger.info("Loaded fallback matrix with shape %s.", self.fallback_embeddings.shape)
            except Exception as exc:
                logger.error("Failed loading fallback matrix: %s", exc)

        self._loaded = True
        return len(self.metadata) > 0

    def retrieve(
        self,
        symptoms: List[str],
        candidate_diseases: List[str],
        query: str = "",
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant medical evidence chunks for given symptoms and candidate diseases.
        """
        if not self._loaded:
            self.load_vectorstore()

        if not self.metadata:
            logger.warning("No RAG metadata loaded. Returning empty retrieval results.")
            return []

        k = top_k or getattr(settings, "rag_top_k", self.top_k)
        threshold = score_threshold or getattr(settings, "rag_score_threshold", self.score_threshold)

        # Construct enriched search query
        query_parts = []
        if symptoms:
            query_parts.append("Symptoms: " + ", ".join(symptoms))
        if candidate_diseases:
            query_parts.append("Candidate diseases: " + ", ".join(candidate_diseases))
        if query:
            query_parts.append("Context: " + query)
        query_parts.append("distinguishing characteristics diagnostic evaluation red flags clinical features")

        search_query = " | ".join(query_parts)
        query_vec = get_embeddings([search_query])  # Shape: (1, dim)

        results: List[Dict[str, Any]] = []

        if self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query_vec, min(k * 2, len(self.metadata)))
            scores = scores[0]
            indices = indices[0]

            for score, idx in zip(scores, indices):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                score_val = float(score)
                # Map raw score to 0..1 scale if needed
                norm_score = round(max(0.0, min(1.0, score_val)), 4)
                if norm_score >= threshold:
                    chunk_meta = self.metadata[idx].copy()
                    chunk_meta["score"] = norm_score
                    results.append(chunk_meta)
                if len(results) >= k:
                    break

        elif self.fallback_embeddings is not None:
            # Cosine similarity matrix dot product
            scores = np.dot(self.fallback_embeddings, query_vec.T).squeeze()
            top_indices = np.argsort(scores)[::-1][: k * 2]

            for idx in top_indices:
                score_val = float(scores[idx])
                norm_score = round(max(0.0, min(1.0, score_val)), 4)
                if norm_score >= threshold:
                    chunk_meta = self.metadata[idx].copy()
                    chunk_meta["score"] = norm_score
                    results.append(chunk_meta)
                if len(results) >= k:
                    break

        logger.info("Retrieved %d medical evidence documents (k=%d, threshold=%.2f).", len(results), k, threshold)
        return results


# Module instance
retriever = MedicalRetriever()
