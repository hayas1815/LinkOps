"""
Unit tests for Document API router using FastAPI TestClient and dependency overrides.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.exceptions import DocumentNotFoundException
from app.modules.documents.models import Document
from app.modules.documents.router import get_document_service, router
from app.modules.documents.service import DocumentService

# Create test app and register router
app = FastAPI()
app.include_router(router)


@pytest.fixture
def test_client() -> TestClient:
    """
    Fixture returning a TestClient for the registered router app.
    """
    return TestClient(app)


def test_create_document(test_client: TestClient) -> None:
    """
    Test POST /api/v1/documents/ creates document successfully.
    """
    mock_service = MagicMock(spec=DocumentService)
    mock_doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        original_filename="orig.pdf",
        document_type=DocumentType.MANUAL,
        status=DocumentStatus.UPLOADED,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.create_document = AsyncMock(return_value=mock_doc)

    # Override service dependency
    app.dependency_overrides[get_document_service] = lambda: mock_service

    payload = {
        "filename": "test.pdf",
        "original_filename": "orig.pdf",
        "document_type": "MANUAL",
        "mime_type": "application/pdf",
        "file_size": 1234,
    }

    response = test_client.post("/api/v1/documents/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "UPLOADED"

    app.dependency_overrides.clear()


def test_list_documents(test_client: TestClient) -> None:
    """
    Test GET /api/v1/documents/ retrieves paginated list.
    """
    mock_service = MagicMock(spec=DocumentService)
    mock_doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        original_filename="orig.pdf",
        document_type=DocumentType.MANUAL,
        status=DocumentStatus.UPLOADED,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.list_documents = AsyncMock(return_value=[mock_doc])

    app.dependency_overrides[get_document_service] = lambda: mock_service

    response = test_client.get("/api/v1/documents/?skip=0&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["filename"] == "test.pdf"

    app.dependency_overrides.clear()


def test_get_document_success(test_client: TestClient) -> None:
    """
    Test GET /api/v1/documents/{id} returns document details.
    """
    mock_service = MagicMock(spec=DocumentService)
    doc_id = uuid.uuid4()
    mock_doc = Document(
        id=doc_id,
        filename="test.pdf",
        original_filename="orig.pdf",
        document_type=DocumentType.MANUAL,
        status=DocumentStatus.UPLOADED,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.get_document = AsyncMock(return_value=mock_doc)

    app.dependency_overrides[get_document_service] = lambda: mock_service

    response = test_client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["filename"] == "test.pdf"

    app.dependency_overrides.clear()


def test_get_document_not_found(test_client: TestClient) -> None:
    """
    Test GET /api/v1/documents/{id} returns 404 when document does not exist.
    """
    mock_service = MagicMock(spec=DocumentService)
    doc_id = uuid.uuid4()
    mock_service.get_document = AsyncMock(
        side_effect=DocumentNotFoundException(doc_id)
    )

    app.dependency_overrides[get_document_service] = lambda: mock_service

    response = test_client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

    app.dependency_overrides.clear()


def test_update_document_success(test_client: TestClient) -> None:
    """
    Test PATCH /api/v1/documents/{id} updates document.
    """
    mock_service = MagicMock(spec=DocumentService)
    doc_id = uuid.uuid4()
    mock_doc = Document(
        id=doc_id,
        filename="new.pdf",
        original_filename="orig.pdf",
        document_type=DocumentType.MANUAL,
        status=DocumentStatus.UPLOADED,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.update_document = AsyncMock(return_value=mock_doc)

    app.dependency_overrides[get_document_service] = lambda: mock_service

    response = test_client.patch(
        f"/api/v1/documents/{doc_id}", json={"filename": "new.pdf"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["filename"] == "new.pdf"

    app.dependency_overrides.clear()


def test_delete_document_success(test_client: TestClient) -> None:
    """
    Test DELETE /api/v1/documents/{id} soft-deletes document.
    """
    mock_service = MagicMock(spec=DocumentService)
    doc_id = uuid.uuid4()
    mock_service.delete_document = AsyncMock()

    app.dependency_overrides[get_document_service] = lambda: mock_service

    response = test_client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    app.dependency_overrides.clear()
