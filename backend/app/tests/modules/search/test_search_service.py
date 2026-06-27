"""
Unit tests for SearchService.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.modules.search.service import SearchService
from app.modules.search.schemas import SearchResultItem
from app.modules.documents.enums import DocumentType
from app.modules.document_chunks.models import DocumentChunk
from app.modules.documents.models import Document


@pytest.mark.asyncio
async def test_search_service_success(mock_repository: MagicMock) -> None:
    """
    Test SearchService.search generates embedding, queries repository, and formats results.
    """
    # Create service with mocked EmbeddingService
    mock_embedder = MagicMock()
    mock_embedder.embed_query.return_value = [0.1] * 384
    service = SearchService(mock_repository, embedding_service=mock_embedder)

    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    mock_doc = Document(
        id=doc_id,
        original_filename="pump.pdf",
        document_type=DocumentType.MANUAL,
    )
    mock_chunk = DocumentChunk(
        id=chunk_id,
        text="matching chunk text",
        chunk_index=2,
    )
    mock_score = 0.92

    # Repository returns tuples of (DocumentChunk, Document, score)
    mock_repository.semantic_search = AsyncMock(
        return_value=[(mock_chunk, mock_doc, mock_score)]
    )

    results = await service.search(query="pump specifications", top_k=5)

    mock_embedder.embed_query.assert_called_once_with("pump specifications")
    mock_repository.semantic_search.assert_called_once_with(
        query_embedding=[0.1] * 384,
        limit=5,
        min_score=0.0,
    )

    assert len(results) == 1
    item = results[0]
    assert isinstance(item, SearchResultItem)
    assert item.document_id == doc_id
    assert item.chunk_id == chunk_id
    assert item.score == mock_score
    assert item.text == "matching chunk text"
    assert item.filename == "pump.pdf"
    assert item.document_type == DocumentType.MANUAL
    assert item.page == 2
