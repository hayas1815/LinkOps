"""
Unit tests for Search API router using FastAPI TestClient and dependency overrides.
"""

from __future__ import annotations

import uuid
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.modules.search.router import get_search_service, router
from app.modules.search.schemas import SearchResultItem
from app.modules.documents.enums import DocumentType

# Create test app and register search router
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Fixture returning a TestClient for the registered router app.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_search_service() -> MagicMock:
    """
    Fixture returning a mocked SearchService.
    """
    return MagicMock()


class TestSearchRouter:
    """
    API tests for the /api/v1/search endpoint.
    """

    def test_search_documents_success(
        self, client: TestClient, mock_search_service: MagicMock
    ) -> None:
        """
        POST /api/v1/search returns 200 and ranked results on success.
        """
        # Override the dependency to return our mock service
        app.dependency_overrides[get_search_service] = lambda: mock_search_service

        doc_id = uuid.uuid4()
        chunk_id = uuid.uuid4()

        # Mock service return value
        mock_search_service.search = AsyncMock(
            return_value=[
                SearchResultItem(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    score=0.88,
                    text="found passage content",
                    filename="document.pdf",
                    document_type=DocumentType.MANUAL,
                    page=1,
                )
            ]
        )

        response = client.post(
            "/api/v1/search",
            json={"query": "how to start pump", "top_k": 3},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["document_id"] == str(doc_id)
        assert data[0]["chunk_id"] == str(chunk_id)
        assert data[0]["score"] == 0.88
        assert data[0]["text"] == "found passage content"
        assert data[0]["filename"] == "document.pdf"
        assert data[0]["document_type"] == DocumentType.MANUAL.value
        assert data[0]["page"] == 1

        mock_search_service.search.assert_called_once_with(
            query="how to start pump",
            top_k=3,
        )

        # Cleanup overrides
        app.dependency_overrides.clear()

    def test_search_documents_validation_error_on_whitespace(
        self, client: TestClient
    ) -> None:
        """
        POST /api/v1/search returns 422 for a query containing only whitespace.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "   ", "top_k": 3},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_documents_validation_error_on_missing_query(
        self, client: TestClient
    ) -> None:
        """
        POST /api/v1/search returns 422 when the query field is missing.
        """
        response = client.post(
            "/api/v1/search",
            json={"top_k": 3},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_documents_validation_error_on_invalid_top_k(
        self, client: TestClient
    ) -> None:
        """
        POST /api/v1/search returns 422 when top_k exceeds MAX_TOP_K.
        """
        response = client.post(
            "/api/v1/search",
            json={"query": "valves", "top_k": 100},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
