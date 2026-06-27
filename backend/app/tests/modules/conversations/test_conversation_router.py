"""
Integration tests for the Conversations router using FastAPI TestClient.
"""
from __future__ import annotations

import uuid
from typing import Generator
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.modules.conversations.router import get_conversation_service, router
from app.modules.conversations.schemas import (
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from app.modules.copilot.schemas import CitationSource

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_service() -> MagicMock:
    return MagicMock()


class TestConversationRouter:

    def test_create_conversation(self, client: TestClient, mock_service: MagicMock) -> None:
        """POST /api/v1/conversations creates session and returns 201."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        conv_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        mock_service.create_conversation = AsyncMock(
            return_value=ConversationResponse(
                id=conv_id,
                title="New Conversation",
                created_at=now,
                updated_at=now,
            )
        )

        response = client.post("/api/v1/conversations", json={"title": "New Conversation"})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == str(conv_id)
        assert data["title"] == "New Conversation"
        app.dependency_overrides.clear()

    def test_get_conversation_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """GET /api/v1/conversations/{id} returns 404 when not found."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        mock_service.get_conversation = AsyncMock(return_value=None)

        response = client.get(f"/api/v1/conversations/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        app.dependency_overrides.clear()

    def test_get_conversation_success(self, client: TestClient, mock_service: MagicMock) -> None:
        """GET /api/v1/conversations/{id} returns conversation on success."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        conv_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        mock_service.get_conversation = AsyncMock(
            return_value=ConversationResponse(
                id=conv_id, title="Test Session", created_at=now, updated_at=now
            )
        )

        response = client.get(f"/api/v1/conversations/{conv_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(conv_id)
        assert data["title"] == "Test Session"
        app.dependency_overrides.clear()

    def test_list_messages_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """GET /api/v1/conversations/{id}/messages returns 404 when conversation missing."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        mock_service.get_messages = AsyncMock(
            side_effect=ValueError("Conversation not found.")
        )

        response = client.get(f"/api/v1/conversations/{uuid.uuid4()}/messages")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        app.dependency_overrides.clear()

    def test_delete_conversation_success(self, client: TestClient, mock_service: MagicMock) -> None:
        """DELETE /api/v1/conversations/{id} returns 204 on success."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        mock_service.delete_conversation = AsyncMock(return_value=True)

        response = client.delete(f"/api/v1/conversations/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        app.dependency_overrides.clear()

    def test_delete_conversation_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        """DELETE /api/v1/conversations/{id} returns 404 when not found."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        mock_service.delete_conversation = AsyncMock(return_value=False)

        response = client.delete(f"/api/v1/conversations/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        app.dependency_overrides.clear()

    def test_chat_success(self, client: TestClient, mock_service: MagicMock) -> None:
        """POST /api/v1/copilot/chat returns ChatResponse on success."""
        app.dependency_overrides[get_conversation_service] = lambda: mock_service
        conv_id = uuid.uuid4()
        doc_id = uuid.uuid4()
        chunk_id = uuid.uuid4()

        mock_service.chat = AsyncMock(
            return_value=ChatResponse(
                conversation_id=conv_id,
                assistant_message="The pump starts by activating motor relay.",
                sources=[
                    CitationSource(
                        filename="pump_manual.pdf",
                        document_id=doc_id,
                        chunk_id=chunk_id,
                        similarity_score=0.92,
                        page_number=3,
                        excerpt="Motor relay activation...",
                    )
                ],
                confidence_score=0.92,
                confidence_level="HIGH",
            )
        )

        response = client.post(
            "/api/v1/copilot/chat",
            json={"conversation_id": str(conv_id), "message": "How does the pump start?"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == str(conv_id)
        assert data["assistant_message"] == "The pump starts by activating motor relay."
        assert data["confidence_score"] == 0.92
        assert data["confidence_level"] == "HIGH"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["filename"] == "pump_manual.pdf"
        app.dependency_overrides.clear()

    def test_chat_validation_error_on_whitespace(self, client: TestClient) -> None:
        """POST /api/v1/copilot/chat returns 422 for whitespace-only message."""
        response = client.post(
            "/api/v1/copilot/chat",
            json={"conversation_id": str(uuid.uuid4()), "message": "   "},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
