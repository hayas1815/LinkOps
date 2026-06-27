"""
Unit tests for the Copilot router using FastAPI TestClient.
"""

from __future__ import annotations

import uuid
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.modules.copilot.router import get_copilot_service, router
from app.modules.copilot.schemas import CitationSource, CopilotAnswerResponse


# Create test app and register copilot router
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Fixture returning a TestClient for the registered copilot router app.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_copilot_service() -> MagicMock:
    """
    Fixture returning a mocked CopilotService.
    """
    return MagicMock()


class TestCopilotRouter:
    """
    API tests for the /api/v1/copilot/ask endpoint.
    """

    def test_ask_copilot_success(
        self, client: TestClient, mock_copilot_service: MagicMock
    ) -> None:
        """
        POST /api/v1/copilot/ask returns 200 and structured response on success.
        """
        # Override dependency
        app.dependency_overrides[get_copilot_service] = lambda: mock_copilot_service

        doc_id = uuid.uuid4()
        chunk_id = uuid.uuid4()

        # Mock service ask response
        from app.modules.copilot.schemas import RetrievalStatistics

        mock_copilot_service.ask = AsyncMock(
            return_value=CopilotAnswerResponse(
                answer="The pipeline is functioning properly.",
                confidence_score=0.91,
                confidence_level="HIGH",
                sources=[
                    CitationSource(
                        filename="op_guide.pdf",
                        document_id=doc_id,
                        chunk_id=chunk_id,
                        similarity_score=0.91,
                        page_number=1,
                        excerpt="pipeline starts...",
                    )
                ],
                supporting_chunks=["pipeline starts..."],
                retrieval_statistics=RetrievalStatistics(
                    retrieved_chunks=1,
                    average_similarity=0.91,
                    max_similarity=0.91,
                    processing_time_ms=5.4,
                ),
            )
        )

        response = client.post(
            "/api/v1/copilot/ask",
            json={"question": "what is the status?", "top_k": 3},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["answer"] == "The pipeline is functioning properly."
        assert data["confidence_score"] == 0.91
        assert data["confidence_level"] == "HIGH"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document_id"] == str(doc_id)
        assert data["sources"][0]["chunk_id"] == str(chunk_id)
        assert data["sources"][0]["filename"] == "op_guide.pdf"
        assert data["sources"][0]["similarity_score"] == 0.91
        assert data["sources"][0]["page_number"] == 1
        assert data["sources"][0]["excerpt"] == "pipeline starts..."
        assert len(data["supporting_chunks"]) == 1
        assert data["retrieval_statistics"]["retrieved_chunks"] == 1
        assert data["retrieval_statistics"]["average_similarity"] == 0.91
        assert data["retrieval_statistics"]["max_similarity"] == 0.91
        assert data["retrieval_statistics"]["processing_time_ms"] == 5.4

        mock_copilot_service.ask.assert_called_once_with(
            question="what is the status?",
            top_k=3,
        )

        # Cleanup overrides
        app.dependency_overrides.clear()

    def test_ask_copilot_validation_error_on_whitespace(
        self, client: TestClient
    ) -> None:
        """
        POST /api/v1/copilot/ask returns 422 for a question containing only whitespace.
        """
        response = client.post(
            "/api/v1/copilot/ask",
            json={"question": "   \n   ", "top_k": 3},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_ask_copilot_validation_error_on_invalid_top_k(
        self, client: TestClient
    ) -> None:
        """
        POST /api/v1/copilot/ask returns 422 when top_k is negative or too large.
        """
        # top_k too large (> 50)
        response = client.post(
            "/api/v1/copilot/ask",
            json={"question": "how does the pump start?", "top_k": 55},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # top_k negative
        response = client.post(
            "/api/v1/copilot/ask",
            json={"question": "how does the pump start?", "top_k": -1},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
