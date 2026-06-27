"""
Unit tests for DocumentService.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.documents.enums import DocumentType
from app.modules.documents.exceptions import DocumentNotFoundException
from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate
from app.modules.documents.service import DocumentService


@pytest.mark.asyncio
async def test_service_create_document(mock_repository: MagicMock) -> None:
    """
    Test create_document creates and persists document.
    """
    service = DocumentService(mock_repository)
    schema = DocumentCreate(
        filename="test.pdf",
        original_filename="orig.pdf",
        document_type=DocumentType.MANUAL,
        mime_type="application/pdf",
        file_size=500,
    )

    mock_repository.create = AsyncMock(return_value=Document())

    result = await service.create_document(schema)

    mock_repository.create.assert_called_once()
    assert isinstance(result, Document)


@pytest.mark.asyncio
async def test_service_get_document_success(mock_repository: MagicMock) -> None:
    """
    Test get_document successfully returns document.
    """
    service = DocumentService(mock_repository)
    doc_id = uuid.uuid4()
    mock_doc = Document(id=doc_id, filename="test.pdf")

    mock_repository.get_by_id = AsyncMock(return_value=mock_doc)

    result = await service.get_document(doc_id)

    mock_repository.get_by_id.assert_called_once_with(doc_id)
    assert result == mock_doc


@pytest.mark.asyncio
async def test_service_get_document_not_found(mock_repository: MagicMock) -> None:
    """
    Test get_document raises DocumentNotFoundException when repository returns None.
    """
    service = DocumentService(mock_repository)
    doc_id = uuid.uuid4()

    mock_repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(DocumentNotFoundException):
        await service.get_document(doc_id)


@pytest.mark.asyncio
async def test_service_list_documents(mock_repository: MagicMock) -> None:
    """
    Test list_documents retrieves records.
    """
    service = DocumentService(mock_repository)
    mock_repository.list = AsyncMock(return_value=[Document()])

    result = await service.list_documents(skip=0, limit=10)

    mock_repository.list.assert_called_once_with(skip=0, limit=10)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_service_update_document_success(mock_repository: MagicMock) -> None:
    """
    Test update_document updates tracked attributes.
    """
    service = DocumentService(mock_repository)
    doc_id = uuid.uuid4()
    mock_doc = Document(id=doc_id, filename="old.pdf")

    mock_repository.get_by_id = AsyncMock(return_value=mock_doc)
    mock_repository.update = AsyncMock(return_value=mock_doc)

    update_schema = DocumentUpdate(filename="new.pdf")
    result = await service.update_document(doc_id, update_schema)

    assert result.filename == "new.pdf"
    mock_repository.update.assert_called_once_with(mock_doc)


@pytest.mark.asyncio
async def test_service_delete_document_success(mock_repository: MagicMock) -> None:
    """
    Test delete_document calls soft_delete.
    """
    service = DocumentService(mock_repository)
    doc_id = uuid.uuid4()

    mock_repository.soft_delete = AsyncMock(return_value=True)

    await service.delete_document(doc_id)

    mock_repository.soft_delete.assert_called_once_with(doc_id)


@pytest.mark.asyncio
async def test_service_delete_document_not_found(mock_repository: MagicMock) -> None:
    """
    Test delete_document raises DocumentNotFoundException.
    """
    service = DocumentService(mock_repository)
    doc_id = uuid.uuid4()

    mock_repository.soft_delete = AsyncMock(return_value=False)

    with pytest.raises(DocumentNotFoundException):
        await service.delete_document(doc_id)
