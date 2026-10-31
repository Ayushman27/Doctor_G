"""
Embedding Service for Medical RAG.
Generates normalized dense vector representations of queries and medical text passages
using Sentence-Transformers.
"""

from __future__ import annotations

import logging
from typing import List
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

_model_cache = None


def get_embedding_model():
    """Load and cache SentenceTransformer model."""
    global _model_cache
    if _model_cache is None:
        model_name = getattr(settings, "embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Initializing SentenceTransformer embedding service: %s", model_name)
        try:
            from sentence_transformers import SentenceTransformer
            _model_cache = SentenceTransformer(model_name)
        except Exception as exc:
            logger.warning("SentenceTransformer unavailable (%s). Falling back to mock embeddings.", exc)
            _model_cache = "MOCK"
    return _model_cache


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Generate normalized dense vector embeddings for a list of text strings.
    Returns np.ndarray of shape (len(texts), vector_dimension).
    """
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)

    model = get_embedding_model()
    if model == "MOCK":
        np.random.seed(42)
        embeddings = np.random.randn(len(texts), 384).astype(np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / (norms + 1e-10)

    raw_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    norms = np.linalg.norm(raw_embeddings, axis=1, keepdims=True)
    return (raw_embeddings / (norms + 1e-10)).astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """Generate normalized embedding vector for a single query string."""
    embeddings = embed_texts([query])
    return embeddings[0]
