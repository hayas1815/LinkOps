"""
Unit tests for DocumentService.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.documents.enums import DocumentType
from app.modules.documents.exceptions import DocumentNotFoundException
from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate
from app.modules.documents.service import DocumentService

import app.tasks.document_processing  # noqa: F401 — ensures patch path resolves


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




@pytest.mark.asyncio
@patch("app.tasks.document_processing.process_document")
@patch("app.modules.documents.service.MinioService")
async def test_service_ingest_document_success(
    mock_minio_class: MagicMock,   # innermost @patch (MinioService) → first arg
    mock_process_task: MagicMock,  # outermost @patch (process_document) → second arg
    mock_repository: MagicMock,    # pytest fixture
) -> None:
    """
    Test ingest_document successfully uploads a unique file, saves metadata
    with QUEUED status, and dispatches the Celery processing task.
    """
    mock_minio_instance = mock_minio_class.return_value
    mock_minio_instance.upload_file = AsyncMock()
    mock_process_task.apply_async = MagicMock()

    from app.modules.documents.enums import DocumentStatus

    created_doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status=DocumentStatus.QUEUED,
    )

    service = DocumentService(mock_repository)
    mock_repository.get_by_checksum = AsyncMock(return_value=None)
    mock_repository.create = AsyncMock(return_value=created_doc)

    result = await service.ingest_document(
        filename="test.pdf",
        content=b"some binary pdf file content",
        content_type="application/pdf",
        document_type=DocumentType.MANUAL,
    )

    assert result.filename == "test.pdf"
    assert result.status == DocumentStatus.QUEUED
    mock_minio_instance.upload_file.assert_called_once()
    mock_repository.create.assert_called_once()
    mock_process_task.apply_async.assert_called_once()


@pytest.mark.asyncio
async def test_service_ingest_document_duplicate(mock_repository: MagicMock) -> None:
    """
    Test ingest_document returns existing document metadata for duplicate files.
    """
    service = DocumentService(mock_repository)
    existing_doc = Document(id=uuid.uuid4(), filename="existing.pdf")
    mock_repository.get_by_checksum = AsyncMock(return_value=existing_doc)

    result = await service.ingest_document(
        filename="duplicate.pdf",
        content=b"duplicate content",
        content_type="application/pdf",
        document_type=DocumentType.MANUAL,
    )

    assert result == existing_doc
    mock_repository.get_by_checksum.assert_called_once()
    mock_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_service_ingest_document_empty_file(mock_repository: MagicMock) -> None:
    """
    Test ingest_document raises DocumentValidationException for empty files.
    """
    service = DocumentService(mock_repository)
    from app.modules.documents.exceptions import DocumentValidationException

    with pytest.raises(DocumentValidationException, match="Empty files"):
        await service.ingest_document(
            filename="empty.pdf",
            content=b"",
            content_type="application/pdf",
            document_type=DocumentType.MANUAL,
        )


@pytest.mark.asyncio
async def test_service_ingest_document_file_too_large(mock_repository: MagicMock) -> None:
    """
    Test ingest_document raises DocumentValidationException for files exceeding size limit.
    """
    service = DocumentService(mock_repository)
    from app.modules.documents.exceptions import DocumentValidationException
    from app.modules.documents.constants import MAX_UPLOAD_SIZE

    large_content = b"a" * (MAX_UPLOAD_SIZE + 1)

    with pytest.raises(DocumentValidationException, match="File size exceeds"):
        await service.ingest_document(
            filename="large.pdf",
            content=large_content,
            content_type="application/pdf",
            document_type=DocumentType.MANUAL,
        )


@pytest.mark.asyncio
async def test_service_ingest_document_invalid_extension(mock_repository: MagicMock) -> None:
    """
    Test ingest_document raises DocumentValidationException for unsupported file extensions.
    """
    service = DocumentService(mock_repository)
    from app.modules.documents.exceptions import DocumentValidationException

    with pytest.raises(DocumentValidationException, match="Unsupported file extension"):
        await service.ingest_document(
            filename="malicious.exe",
            content=b"malicious code",
            content_type="application/x-msdownload",
            document_type=DocumentType.MANUAL,
        )

