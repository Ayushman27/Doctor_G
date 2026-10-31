"""
RAG Configuration module.
Defines document paths, chunking strategy, embedding parameters, and retriever thresholds.
"""

from pathlib import Path

# Base directories
RAG_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = RAG_DIR / "documents"
PROCESSED_DIR = RAG_DIR / "processed"
VECTORSTORE_DIR = RAG_DIR / "vectorstore"

# File paths
FAISS_INDEX_PATH = VECTORSTORE_DIR / "index.faiss"
METADATA_PKL_PATH = VECTORSTORE_DIR / "metadata.pkl"

# Chunking Configuration (tokens/characters)
DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120

# Embedding Model
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Retriever Parameters
DEFAULT_TOP_K = 5
DEFAULT_SCORE_THRESHOLD = 0.4
