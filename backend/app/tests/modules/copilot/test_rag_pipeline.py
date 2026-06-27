"""
Unit tests for the RAGPipeline implementation.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.ai.rag import RAGPipeline
from app.modules.search.schemas import SearchResultItem
from app.modules.documents.enums import DocumentType


@pytest.mark.asyncio
async def test_rag_pipeline_answer_success():
    """
    Test RAGPipeline returns generated answer, average confidence score, and matched source citations.
    """
    mock_search = MagicMock()
    mock_llm = MagicMock()

    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    # Mock search service to return 2 chunks
    mock_search.search = AsyncMock(
        return_value=[
            SearchResultItem(
                document_id=doc_id,
                chunk_id=chunk_id,
                score=0.90,
                text="RAG compiled answer text matching chunk content 1.",
                filename="doc1.pdf",
                document_type=DocumentType.MANUAL,
                page=0,
            ),
            SearchResultItem(
                document_id=doc_id,
                chunk_id=chunk_id,
                score=0.80,
                text="Some other unrelated chunk content 2.",
                filename="doc1.pdf",
                document_type=DocumentType.MANUAL,
                page=1,
            ),
        ]
    )

    # Mock LLM generation
    mock_llm.generate = AsyncMock(return_value="RAG compiled answer text")

    pipeline = RAGPipeline(mock_search, mock_llm)
    (
        answer,
        confidence,
        confidence_level,
        sources,
        supporting_chunks,
        retrieval_stats,
    ) = await pipeline.answer("how to calibrate pump", top_k=2)

    # Assertions
    assert answer == "RAG compiled answer text"
    # Average score: (0.90 + 0.80) / 2 = 0.85
    assert confidence == pytest.approx(0.85)
    assert confidence_level == "HIGH"
    assert len(sources) == 2
    assert sources[0]["document_id"] == doc_id
    assert sources[0]["similarity_score"] == 0.90
    assert sources[1]["similarity_score"] == 0.80
    assert len(supporting_chunks) > 0
    assert retrieval_stats["retrieved_chunks"] == 2
    assert retrieval_stats["average_similarity"] == pytest.approx(0.85)
    assert retrieval_stats["max_similarity"] == 0.90
    assert "processing_time_ms" in retrieval_stats

    mock_search.search.assert_called_once_with(query="how to calibrate pump", top_k=2)
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_rag_pipeline_fallback_on_no_chunks():
    """
    Test RAGPipeline returns fallback answer and 0.0 confidence when no matches are found.
    """
    mock_search = MagicMock()
    mock_llm = MagicMock()

    # Search returns empty list
    mock_search.search = AsyncMock(return_value=[])

    pipeline = RAGPipeline(mock_search, mock_llm)
    (
        answer,
        confidence,
        confidence_level,
        sources,
        supporting_chunks,
        retrieval_stats,
    ) = await pipeline.answer("missing query topic")

    assert "cannot find the answer" in answer
    assert confidence == 0.0
    assert confidence_level == "LOW"
    assert len(sources) == 0
    assert len(supporting_chunks) == 0
    assert retrieval_stats["retrieved_chunks"] == 0

    mock_search.search.assert_called_once_with(query="missing query topic", top_k=5)
    mock_llm.generate.assert_not_called()
