"""
RAG Ingestion Pipeline
Loads medical documents, cleans, splits into chunks with metadata,
generates embeddings using sentence-transformers, and stores in FAISS vectorstore.
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

from app.core.config import settings
from rag.config import (
    DOCUMENTS_DIR,
    VECTORSTORE_DIR,
    FAISS_INDEX_PATH,
    METADATA_PKL_PATH,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)

logger = logging.getLogger(__name__)

# Global model cache to avoid re-loading sentence-transformers repeatedly
_embedding_model_cache = None


def get_embedding_model():
    """Load and cache the sentence-transformer embedding model."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        model_name = getattr(settings, "embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Loading embedding model: %s", model_name)
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model_cache = SentenceTransformer(model_name)
        except Exception as exc:
            logger.warning("Failed to load sentence_transformers (%s). Falling back to mock embeddings for offline testing.", exc)
            _embedding_model_cache = "MOCK"
    return _embedding_model_cache


def get_embeddings(texts: List[str]) -> np.ndarray:
    """Generate dense embedding vectors for a list of text strings."""
    model = get_embedding_model()
    if model == "MOCK":
        # Deterministic pseudo-embeddings for testing fallback
        logger.info("Using fallback mock embeddings.")
        np.random.seed(42)
        embeddings = np.random.randn(len(texts), 384).astype("float32")
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / (norms + 1e-10)

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # L2 Normalize for cosine similarity via inner product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return (embeddings / (norms + 1e-10)).astype("float32")


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    """Split text string into overlapping chunks."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def load_documents_from_dir(doc_dir: Path = DOCUMENTS_DIR) -> List[Dict[str, Any]]:
    """Load all medical JSON documents from the documents directory."""
    all_chunks: List[Dict[str, Any]] = []
    if not doc_dir.is_dir():
        logger.warning("Documents directory missing: %s", doc_dir)
        return all_chunks

    for json_file in doc_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                docs = json.load(f)
                if not isinstance(docs, list):
                    docs = [docs]
                for doc in docs:
                    content = doc.get("content", "")
                    title = doc.get("title", json_file.stem)
                    source = doc.get("source", "Medical Reference")
                    url = doc.get("url", "")
                    disease = doc.get("disease", "")
                    section = doc.get("section", "")
                    source_type = doc.get("source_type", "medical_reference")

                    # Chunk content
                    chunks = chunk_text(content)
                    for idx, chunk in enumerate(chunks):
                        all_chunks.append({
                            "chunk_id": f"{json_file.stem}_{disease}_{idx}",
                            "content": chunk,
                            "title": title,
                            "source": source,
                            "url": url,
                            "disease": disease,
                            "section": section,
                            "source_type": source_type,
                        })
        except Exception as exc:
            logger.error("Error loading RAG document %s: %s", json_file.name, exc)

    logger.info("Loaded and chunked %d total medical passages from %s.", len(all_chunks), doc_dir)
    return all_chunks


def build_and_save_vectorstore() -> Tuple[bool, int]:
    """
    Ingest medical documents, compute embeddings, build FAISS index, and save persistent vectorstore.
    Returns (success_boolean, num_chunks_indexed).
    """
    chunks = load_documents_from_dir()
    if not chunks:
        logger.warning("No document chunks available for RAG ingestion.")
        return False, 0

    texts = [c["content"] for c in chunks]
    embeddings = get_embeddings(texts)

    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    # Attempt FAISS index build
    try:
        import faiss
        dimension = embeddings.shape[1]
        # IndexFlatIP uses Inner Product (cosine similarity on normalized vectors)
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        logger.info("Saved FAISS index to %s (dimension=%d, total=%d).", FAISS_INDEX_PATH, dimension, index.ntotal)
    except Exception as exc:
        logger.warning("FAISS build failed or faiss not installed (%s). Saving numpy matrix index fallback.", exc)
        np.save(str(VECTORSTORE_DIR / "embeddings.npy"), embeddings)

    # Save metadata pkl
    with open(METADATA_PKL_PATH, "wb") as f:
        pickle.dump(chunks, f)

    logger.info("Saved RAG metadata (%d chunks) to %s.", len(chunks), METADATA_PKL_PATH)
    return True, len(chunks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running RAG Ingestion Pipeline...")
    success, count = build_and_save_vectorstore()
    logger.info("Ingestion completed: success=%s, chunks=%d", success, count)
