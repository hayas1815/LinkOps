"""
Unit tests for DocumentRepository using mocked AsyncSession.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository


@pytest.mark.asyncio
async def test_repository_create(mock_session: MagicMock) -> None:
    """
    Test DocumentRepository.create adds and flushes the entity.
    """
    repo = DocumentRepository(mock_session)
    document = Document(
        filename="test.pdf",
        original_filename="original.pdf",
        document_type=DocumentType.MANUAL,
        status=DocumentStatus.UPLOADED,
    )

    result = await repo.create(document)

    mock_session.add.assert_called_once_with(document)
    mock_session.flush.assert_called_once()
    assert result == document


@pytest.mark.asyncio
async def test_repository_get_by_id(mock_session: MagicMock) -> None:
    """
    Test DocumentRepository.get_by_id executes query and returns model.
    """
    repo = DocumentRepository(mock_session)
    doc_id = uuid.uuid4()
    mock_doc = Document(id=doc_id, filename="test.pdf")

    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_by_id(doc_id)

    mock_session.execute.assert_called_once()
    assert result == mock_doc


@pytest.mark.asyncio
async def test_repository_list(mock_session: MagicMock) -> None:
    """
    Test DocumentRepository.list returns list of documents.
    """
    repo = DocumentRepository(mock_session)
    mock_docs = [Document(filename="1.pdf"), Document(filename="2.pdf")]

    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_docs
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.list(skip=0, limit=10)

    mock_session.execute.assert_called_once()
    assert result == mock_docs


@pytest.mark.asyncio
async def test_repository_update(mock_session: MagicMock) -> None:
    """
    Test DocumentRepository.update calls add and flush.
    """
    repo = DocumentRepository(mock_session)
    document = Document(filename="test.pdf")

    result = await repo.update(document)

    mock_session.add.assert_called_once_with(document)
    mock_session.flush.assert_called_once()
    assert result == document


@pytest.mark.asyncio
async def test_repository_soft_delete(mock_session: MagicMock) -> None:
    """
    Test DocumentRepository.soft_delete sets deleted_at attribute.
    """
    repo = DocumentRepository(mock_session)
    doc_id = uuid.uuid4()
    document = Document(id=doc_id, filename="test.pdf", deleted_at=None)

    # Mock get_by_id behavior inside repository
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = document
    mock_session.execute = AsyncMock(return_value=mock_result)

    success = await repo.soft_delete(doc_id)

    assert success is True
    assert document.deleted_at is not None
    mock_session.add.assert_called_once_with(document)
    mock_session.flush.assert_called_once()
