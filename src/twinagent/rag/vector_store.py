"""Lightweight local vector store for TwinAgent AI retrieval.

This module intentionally avoids external embedding downloads for the MVP. It
uses a deterministic TF-IDF style representation implemented with the Python
standard library. Later, this can be replaced by ChromaDB or FAISS without
changing the agent-facing retriever API.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re

from twinagent.rag.chunking import DocumentChunk


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_\-]*")


@dataclass(frozen=True)
class ScoredChunk:
    """A document chunk with a retrieval score."""

    chunk: DocumentChunk
    score: float


class LocalTfidfVectorStore:
    """In-memory TF-IDF retrieval over document chunks."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            raise ValueError("LocalTfidfVectorStore requires at least one chunk.")

        self.chunks = chunks
        self._chunk_tokens = [_tokenize(_chunk_search_text(chunk)) for chunk in chunks]
        self._document_frequency = self._compute_document_frequency(self._chunk_tokens)
        self._num_chunks = len(chunks)
        self._chunk_vectors = [self._build_vector(tokens) for tokens in self._chunk_tokens]

    def search(self, query: str, top_k: int = 4) -> list[ScoredChunk]:
        """Return the top matching chunks for a query."""
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        query_vector = self._build_vector(query_tokens)

        scored: list[ScoredChunk] = []
        for chunk, chunk_vector in zip(self.chunks, self._chunk_vectors, strict=True):
            score = _cosine_similarity(query_vector, chunk_vector)
            if score > 0:
                scored.append(ScoredChunk(chunk=chunk, score=round(score, 4)))

        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    @staticmethod
    def _compute_document_frequency(token_lists: list[list[str]]) -> dict[str, int]:
        """Compute token document frequency over chunks."""
        document_frequency: dict[str, int] = {}

        for tokens in token_lists:
            for token in set(tokens):
                document_frequency[token] = document_frequency.get(token, 0) + 1

        return document_frequency

    def _build_vector(self, tokens: list[str]) -> dict[str, float]:
        """Build a normalized TF-IDF vector."""
        token_counts = Counter(tokens)
        total_tokens = max(sum(token_counts.values()), 1)

        vector: dict[str, float] = {}
        for token, count in token_counts.items():
            term_frequency = count / total_tokens
            document_frequency = self._document_frequency.get(token, 0)
            inverse_document_frequency = math.log(
                (1 + self._num_chunks) / (1 + document_frequency)
            ) + 1.0
            vector[token] = term_frequency * inverse_document_frequency

        return vector


def _chunk_search_text(chunk: DocumentChunk) -> str:
    """Combine metadata and text into a searchable representation."""
    return f"{chunk.title}\n{chunk.heading}\n{chunk.source}\n{chunk.text}"


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms."""
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    """Compute cosine similarity between sparse vectors."""
    if not left or not right:
        return 0.0

    shared_tokens = set(left).intersection(right)
    dot_product = sum(left[token] * right[token] for token in shared_tokens)

    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return dot_product / (left_norm * right_norm)
