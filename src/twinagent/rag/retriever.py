"""RAG retriever interface for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from twinagent.rag.chunking import chunk_documents
from twinagent.rag.document_loader import load_markdown_documents
from twinagent.rag.vector_store import LocalTfidfVectorStore


@dataclass(frozen=True)
class RetrievalResult:
    """A retrieved source chunk with citation-friendly metadata."""

    source: str
    chunk_id: str
    title: str
    heading: str
    score: float
    text: str

    @property
    def citation(self) -> str:
        """Return a compact citation string for the chunk."""
        return f"{self.source}::{self.heading}"


class RagRetriever:
    """Local knowledge-base retriever for engineering documents."""

    def __init__(
        self,
        knowledge_base_dir: str | Path,
        chunk_size_chars: int = 900,
        chunk_overlap_chars: int = 120,
        file_extension: str = ".md",
    ) -> None:
        documents = load_markdown_documents(knowledge_base_dir, extension=file_extension)
        self.chunks = chunk_documents(
            documents,
            chunk_size_chars=chunk_size_chars,
            chunk_overlap_chars=chunk_overlap_chars,
        )
        self.vector_store = LocalTfidfVectorStore(self.chunks)

    @classmethod
    def from_config_file(cls, config_path: str | Path, project_root: str | Path | None = None) -> "RagRetriever":
        """Create a retriever from a YAML config file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"RAG config not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError(f"RAG config must be a YAML mapping: {path}")

        root = Path(project_root) if project_root is not None else path.parents[1]
        knowledge_config = config.get("knowledge_base", {})
        retrieval_config = config.get("retrieval", {})

        knowledge_dir = root / str(knowledge_config.get("directory", "knowledge_base"))

        return cls(
            knowledge_base_dir=knowledge_dir,
            chunk_size_chars=int(retrieval_config.get("chunk_size_chars", 900)),
            chunk_overlap_chars=int(retrieval_config.get("chunk_overlap_chars", 120)),
            file_extension=str(knowledge_config.get("file_extension", ".md")),
        )

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievalResult]:
        """Retrieve relevant knowledge-base chunks for a query."""
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        effective_top_k = int(top_k) if top_k is not None else 4
        scored_chunks = self.vector_store.search(query, top_k=effective_top_k)

        return [
            RetrievalResult(
                source=item.chunk.source,
                chunk_id=item.chunk.chunk_id,
                title=item.chunk.title,
                heading=item.chunk.heading,
                score=item.score,
                text=item.chunk.text,
            )
            for item in scored_chunks
        ]

    def retrieve_with_context(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        """Retrieve chunks and return a serializable context object."""
        results = self.retrieve(query=query, top_k=top_k)

        return {
            "query": query,
            "results": [
                {
                    "source": result.source,
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "heading": result.heading,
                    "score": result.score,
                    "citation": result.citation,
                    "text": result.text,
                }
                for result in results
            ],
        }
