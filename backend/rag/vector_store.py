"""
Persistent Vector Store Service (ChromaDB + FAISS / Fallback).
Persists medical embeddings and metadata across application restarts.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from rag.config import VECTORSTORE_DIR, FAISS_INDEX_PATH, METADATA_PKL_PATH
from rag.embedding_service import embed_texts, embed_query

logger = logging.getLogger(__name__)

CHROMA_DIR = VECTORSTORE_DIR / "chromadb"


class PersistentVectorStore:
    """Vector database manager supporting ChromaDB with FAISS / matrix fallbacks."""

    def __init__(self, collection_name: str = "medical_knowledge"):
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.faiss_index = None
        self.metadata: List[Dict[str, Any]] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize or load vector database from disk."""
        if self._initialized:
            return True

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        # Try ChromaDB persistent storage first
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            logger.info("ChromaDB vector store initialized at %s with %d documents.", CHROMA_DIR, self.collection.count())
        except Exception as exc:
            logger.info("ChromaDB persistent client notice: %s. Using FAISS/pickle fallback vectorstore.", exc)

        # Load metadata pickle
        if METADATA_PKL_PATH.exists():
            try:
                with open(METADATA_PKL_PATH, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info("Loaded vector store metadata: %d documents.", len(self.metadata))
            except Exception as exc:
                logger.error("Failed loading vectorstore metadata: %s", exc)

        # Load FAISS index if available
        if FAISS_INDEX_PATH.exists():
            try:
                import faiss
                self.faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
                logger.info("Loaded FAISS vector index with %d vectors.", self.faiss_index.ntotal)
            except Exception as exc:
                logger.debug("FAISS index load note: %s", exc)

        # Fallback numpy embeddings matrix
        npy_path = VECTORSTORE_DIR / "embeddings.npy"
        if npy_path.exists():
            try:
                self.embeddings_matrix = np.load(str(npy_path))
                logger.info("Loaded numpy embeddings fallback matrix shape %s.", self.embeddings_matrix.shape)
            except Exception as exc:
                logger.error("Failed loading numpy embeddings matrix: %s", exc)

        self._initialized = True
        return len(self.metadata) > 0

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Store documents and vector embeddings into persistent store."""
        if not documents:
            return 0

        self.metadata = documents
        texts = [doc.get("content", "") for doc in documents]
        vectors = embed_texts(texts)

        # Save metadata pkl
        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
        with open(METADATA_PKL_PATH, "wb") as f:
            pickle.dump(documents, f)

        # Try inserting into ChromaDB
        if self.collection is not None:
            try:
                ids = [doc.get("chunk_id", f"doc_{i}") for i, doc in enumerate(documents)]
                metadatas = [
                    {
                        "title": doc.get("title", ""),
                        "source": doc.get("source", ""),
                        "disease": doc.get("disease", ""),
                        "section": doc.get("section", ""),
                        "age_group": doc.get("age_group", "all"),
                    }
                    for doc in documents
                ]
                self.collection.add(
                    ids=ids,
                    embeddings=vectors.tolist(),
                    documents=texts,
                    metadatas=metadatas
                )
                logger.info("Added %d documents to ChromaDB collection.", len(documents))
            except Exception as exc:
                logger.warning("ChromaDB document addition error (%s).", exc)

        # Build FAISS index
        try:
            import faiss
            dim = vectors.shape[1]
            idx = faiss.IndexFlatIP(dim)
            idx.add(vectors)
            faiss.write_index(idx, str(FAISS_INDEX_PATH))
            self.faiss_index = idx
        except Exception:
            np.save(str(VECTORSTORE_DIR / "embeddings.npy"), vectors)
            self.embeddings_matrix = vectors

        return len(documents)

    def search(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Vector similarity search returning top-k matched metadata passages with scores."""
        if not self._initialized:
            self.initialize()

        if not self.metadata:
            return []

        q_vec = embed_query(query).reshape(1, -1)
        results: List[Dict[str, Any]] = []

        # 1. Search ChromaDB if available
        if self.collection is not None and self.collection.count() > 0:
            try:
                query_kwargs: Dict[str, Any] = {
                    "query_embeddings": q_vec.tolist(),
                    "n_results": min(top_k * 2, self.collection.count())
                }
                if filters:
                    query_kwargs["where"] = filters

                res = self.collection.query(**query_kwargs)
                if res and res.get("ids") and res["ids"][0]:
                    matched_ids = res["ids"][0]
                    distances = res.get("distances", [[]])[0]
                    for idx_i, doc_id in enumerate(matched_ids):
                        score = 1.0 - (distances[idx_i] if idx_i < len(distances) else 0.0)
                        # find in metadata list
                        for item in self.metadata:
                            if item.get("chunk_id") == doc_id:
                                match_copy = item.copy()
                                match_copy["vector_score"] = round(max(0.0, min(1.0, float(score))), 4)
                                results.append(match_copy)
                                break
                    if results:
                        return results[:top_k]
            except Exception as exc:
                logger.debug("ChromaDB query fallback: %s", exc)

        # 2. Search FAISS index
        if self.faiss_index is not None:
            scores, indices = self.faiss_index.search(q_vec, min(top_k * 2, len(self.metadata)))
            for score_val, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                match_copy = self.metadata[idx].copy()
                match_copy["vector_score"] = round(max(0.0, min(1.0, float(score_val))), 4)
                results.append(match_copy)
                if len(results) >= top_k:
                    break
            return results

        # 3. Search Numpy Matrix fallback
        if self.embeddings_matrix is not None:
            scores = np.dot(self.embeddings_matrix, q_vec.T).squeeze()
            top_indices = np.argsort(scores)[::-1][: top_k * 2]
            for idx in top_indices:
                score_val = float(scores[idx])
                match_copy = self.metadata[idx].copy()
                match_copy["vector_score"] = round(max(0.0, min(1.0, score_val)), 4)
                results.append(match_copy)
                if len(results) >= top_k:
                    break
            return results

        return results


vector_store = PersistentVectorStore()
