"""Document chunking utilities for TwinAgent AI RAG retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import re

from twinagent.rag.document_loader import KnowledgeDocument


@dataclass(frozen=True)
class DocumentChunk:
    """A retrievable chunk with source metadata."""

    chunk_id: str
    source: str
    title: str
    heading: str
    text: str


def chunk_documents(
    documents: list[KnowledgeDocument],
    chunk_size_chars: int = 900,
    chunk_overlap_chars: int = 120,
) -> list[DocumentChunk]:
    """Split markdown documents into retrieval chunks."""
    if chunk_size_chars <= 100:
        raise ValueError("chunk_size_chars must be greater than 100.")
    if chunk_overlap_chars < 0:
        raise ValueError("chunk_overlap_chars must be non-negative.")
    if chunk_overlap_chars >= chunk_size_chars:
        raise ValueError("chunk_overlap_chars must be smaller than chunk_size_chars.")

    chunks: list[DocumentChunk] = []

    for document in documents:
        sections = _split_markdown_sections(document.text)
        chunk_number = 1

        for heading, section_text in sections:
            normalized = _normalize_whitespace(section_text)
            if not normalized:
                continue

            for piece in _split_text_with_overlap(
                normalized,
                chunk_size_chars=chunk_size_chars,
                chunk_overlap_chars=chunk_overlap_chars,
            ):
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document.source}#chunk-{chunk_number:03d}",
                        source=document.source,
                        title=document.title,
                        heading=heading,
                        text=piece,
                    )
                )
                chunk_number += 1

    if not chunks:
        raise ValueError("No chunks were produced from the provided documents.")

    return chunks


def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown text into sections using headings."""
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_heading = "Overview"
    current_lines: list[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if heading_match:
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = heading_match.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    return [(heading, "\n".join(section_lines).strip()) for heading, section_lines in sections]


def _split_text_with_overlap(
    text: str,
    chunk_size_chars: int,
    chunk_overlap_chars: int,
) -> list[str]:
    """Split long text into overlapping character chunks."""
    if len(text) <= chunk_size_chars:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size_chars, len(text))
        piece = text[start:end].strip()

        if piece:
            chunks.append(piece)

        if end == len(text):
            break

        start = max(end - chunk_overlap_chars, start + 1)

    return chunks


def _normalize_whitespace(text: str) -> str:
    """Normalize repeated whitespace while preserving readable markdown lines."""
    lines = [line.strip() for line in text.splitlines()]
    compact_lines = [line for line in lines if line]
    return "\n".join(compact_lines)
