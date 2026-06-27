"""
Unit tests for SearchRepository using mocked AsyncSession.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.modules.search.repository import SearchRepository
from app.modules.document_chunks.models import DocumentChunk
from app.modules.documents.models import Document


@pytest.mark.asyncio
async def test_repository_semantic_search(mock_session: MagicMock) -> None:
    """
    Test SearchRepository.semantic_search creates the correct select query and executes it.
    """
    repo = SearchRepository(mock_session)
    query_embedding = [0.1] * 384

    # Mock execute result
    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    mock_doc = Document(id=doc_id, original_filename="pump.pdf")
    mock_chunk = DocumentChunk(id=chunk_id, text="pump body info", chunk_index=0)
    mock_score = 0.85

    mock_result = MagicMock()
    mock_result.all.return_value = [(mock_chunk, mock_doc, mock_score)]
    mock_session.execute = AsyncMock(return_value=mock_result)

    results = await repo.semantic_search(
        query_embedding=query_embedding,
        limit=3,
        min_score=0.5,
    )

    mock_session.execute.assert_called_once()
    assert len(results) == 1
    chunk, doc, score = results[0]
    assert chunk == mock_chunk
    assert doc == mock_doc
    assert score == mock_score
