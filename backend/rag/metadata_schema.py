"""
RAG Metadata Schema definitions.
Provides standardized metadata structure for medical evidence chunks.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str = ""
    source: str = "Medical Reference"
    organization: str = "Clinical Guidelines"
    author: str = ""
    publication_date: str = ""
    document_type: str = "clinical_guideline"
    chapter: str = ""
    section: str = ""
    topic: str = ""
    disease: str = ""
    symptom: str = ""
    patient_group: str = "general"
    age_group: str = "all"  # 'pediatric', 'adult', 'elderly', 'all'
    version: str = "1.0"
    url: str = ""


def build_chunk_metadata(
    content: str,
    raw_doc: Dict[str, Any],
    chunk_index: int = 0
) -> Dict[str, Any]:
    """Build enriched chunk metadata dict from raw document payload."""
    return {
        "chunk_id": f"{raw_doc.get('disease', 'doc')}_{chunk_index}",
        "content": content,
        "title": raw_doc.get("title", "Medical Guidance"),
        "source": raw_doc.get("source", "Clinical Reference"),
        "organization": raw_doc.get("organization", raw_doc.get("source", "Health Organization")),
        "author": raw_doc.get("author", "Clinical Expert Group"),
        "publication_date": raw_doc.get("publication_date", "2024"),
        "document_type": raw_doc.get("document_type", "reference"),
        "chapter": raw_doc.get("chapter", "General Medicine"),
        "section": raw_doc.get("section", "Clinical Overview"),
        "topic": raw_doc.get("topic", raw_doc.get("disease", "General")),
        "disease": raw_doc.get("disease", ""),
        "symptom": raw_doc.get("symptom", ""),
        "patient_group": raw_doc.get("patient_group", "general"),
        "age_group": raw_doc.get("age_group", "all"),
        "version": raw_doc.get("version", "1.0"),
        "url": raw_doc.get("url", ""),
    }
