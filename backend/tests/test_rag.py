"""Unit tests for Medical RAG Ingestion and Retriever."""

import pytest
from rag.retriever import retriever
from rag.ingestion import build_and_save_vectorstore


@pytest.fixture(scope="module", autouse=True)
def setup_rag():
    """Ensure vectorstore is ingested and loaded."""
    build_and_save_vectorstore()
    retriever.load_vectorstore()


def test_rag_retrieval_query():
    symptoms = ["fever", "cough"]
    candidates = ["Pneumonia", "Influenza"]
    results = retriever.retrieve(symptoms=symptoms, candidate_diseases=candidates, top_k=3)

    assert isinstance(results, list)
    assert len(results) > 0
    first = results[0]
    assert "content" in first
    assert "source" in first
    assert "score" in first


def test_rag_retrieval_empty_inputs():
    results = retriever.retrieve(symptoms=[], candidate_diseases=[], query="")
    assert isinstance(results, list)
