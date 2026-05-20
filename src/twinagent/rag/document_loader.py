"""Knowledge-base document loading for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeDocument:
    """A loaded markdown knowledge-base document."""

    source: str
    path: Path
    title: str
    text: str


def load_markdown_documents(directory: str | Path, extension: str = ".md") -> list[KnowledgeDocument]:
    """Load markdown documents from a knowledge-base directory."""
    knowledge_dir = Path(directory)
    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Knowledge-base directory not found: {knowledge_dir}")
    if not knowledge_dir.is_dir():
        raise NotADirectoryError(f"Knowledge-base path is not a directory: {knowledge_dir}")

    documents: list[KnowledgeDocument] = []

    for path in sorted(knowledge_dir.glob(f"*{extension}")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        title = _extract_title(text, fallback=path.stem.replace("_", " ").title())

        documents.append(
            KnowledgeDocument(
                source=path.name,
                path=path,
                title=title,
                text=text,
            )
        )

    if not documents:
        raise ValueError(f"No markdown documents found in: {knowledge_dir}")

    return documents


def _extract_title(text: str, fallback: str) -> str:
    """Extract the first markdown H1 title from a document."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback
