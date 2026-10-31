"""
BM25 Keyword Retriever.
Provides deterministic keyword search for specific medical terminology
(e.g., 'hematochezia', 'melena', 'dyspnea', 'tachycardia', 'ECG', 'troponin')
alongside dense semantic vector retrieval.
"""

from __future__ import annotations

import math
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def tokenize_text(text: str) -> List[str]:
    """Tokenize and normalize medical text for BM25 keyword matching."""
    text_clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in text_clean.split() if len(t) > 1]


class BM25Retriever:
    """Okapi BM25 keyword retriever implementation."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Dict[str, Any]] = []
        self.corpus_tokens: List[List[str]] = []
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.num_docs: int = 0
        self._is_indexed = False

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Build BM25 term frequency and IDF index across document chunks."""
        self.documents = documents
        self.num_docs = len(documents)
        if self.num_docs == 0:
            self._is_indexed = False
            return

        self.corpus_tokens = []
        self.doc_len = []
        self.doc_freqs = {}

        total_len = 0
        for doc in documents:
            text = doc.get("content", "") + " " + doc.get("title", "") + " " + doc.get("disease", "")
            tokens = tokenize_text(text)
            self.corpus_tokens.append(tokens)
            l = len(tokens)
            self.doc_len.append(l)
            total_len += l

            # Document frequency count
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avgdl = total_len / self.num_docs if self.num_docs > 0 else 1.0

        # Calculate IDF (smoothing: log( (N - n + 0.5) / (n + 0.5) + 1 ))
        self.idf = {}
        for term, freq in self.doc_freqs.items():
            idf_val = math.log((self.num_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            self.idf[term] = max(0.1, idf_val)

        self._is_indexed = True
        logger.info("BM25 Keyword Index built over %d document passages (%d unique terms).", self.num_docs, len(self.idf))

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top matching passages using BM25 keyword scoring."""
        if not self._is_indexed or self.num_docs == 0:
            return []

        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []

        scores = [0.0] * self.num_docs

        for q_term in query_tokens:
            if q_term not in self.idf:
                continue
            idf_score = self.idf[q_term]

            for idx, doc_tokens in enumerate(self.corpus_tokens):
                term_count = doc_tokens.count(q_term)
                if term_count == 0:
                    continue
                num = term_count * (self.k1 + 1.0)
                denom = term_count + self.k1 * (1.0 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
                scores[idx] += idf_score * (num / denom)

        # Rank documents
        scored_docs: List[tuple[float, int]] = [(scores[i], i) for i in range(self.num_docs) if scores[i] > 0.0]
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results: List[Dict[str, Any]] = []
        max_score = scored_docs[0][0] if scored_docs else 1.0

        for score, idx in scored_docs[:top_k]:
            doc_copy = self.documents[idx].copy()
            # Normalize BM25 score to 0..1 scale
            doc_copy["bm25_score"] = round(min(1.0, score / max_score), 4)
            results.append(doc_copy)

        return results


bm25_retriever = BM25Retriever()
