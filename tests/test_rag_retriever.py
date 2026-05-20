"""Tests for TwinAgent AI local RAG retriever."""

from __future__ import annotations

from pathlib import Path

from twinagent.rag import RagRetriever, chunk_documents, load_markdown_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_knowledge_base_documents_load() -> None:
    documents = load_markdown_documents(PROJECT_ROOT / "knowledge_base")

    sources = {document.source for document in documents}

    assert "motor_manual.md" in sources
    assert "conveyor_maintenance_guide.md" in sources
    assert "bearing_failure_notes.md" in sources


def test_documents_are_chunked() -> None:
    documents = load_markdown_documents(PROJECT_ROOT / "knowledge_base")
    chunks = chunk_documents(documents, chunk_size_chars=900, chunk_overlap_chars=120)

    assert len(chunks) >= len(documents)
    assert all(chunk.source.endswith(".md") for chunk in chunks)
    assert all(chunk.text for chunk in chunks)


def test_retriever_finds_bearing_wear_guidance() -> None:
    retriever = RagRetriever.from_config_file(
        PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )

    results = retriever.retrieve(
        "vibration and temperature increased together, possible bearing wear",
        top_k=3,
    )

    assert results
    combined_sources = {result.source for result in results}
    combined_text = " ".join(result.text.lower() for result in results)

    assert "bearing_failure_notes.md" in combined_sources or "bearing" in combined_text


def test_retriever_finds_safety_guidance() -> None:
    retriever = RagRetriever.from_config_file(
        PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )

    results = retriever.retrieve("critical state high vibration should machine continue operating", top_k=3)

    assert results
    combined_text = " ".join(result.text.lower() for result in results)

    assert "critical" in combined_text or "stop" in combined_text or "reduce operation" in combined_text


def test_retriever_context_has_citations() -> None:
    retriever = RagRetriever.from_config_file(
        PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )

    context = retriever.retrieve_with_context("what should technician inspect for belt misalignment", top_k=2)

    assert context["query"]
    assert context["results"]
    assert all("citation" in result for result in context["results"])
    assert all("source" in result for result in context["results"])
