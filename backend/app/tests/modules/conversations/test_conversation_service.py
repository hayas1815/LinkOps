"""
Unit tests for ConversationService.
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.modules.conversations.service import ConversationService
from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.schemas import (
    ConversationResponse,
    MessageResponse,
    ChatResponse,
)
from app.modules.copilot.schemas import CitationSource
from app.modules.documents.enums import DocumentType


@pytest.mark.asyncio
async def test_create_conversation() -> None:
    """Test ConversationService.create_conversation persists and returns schema."""
    mock_repo = MagicMock()
    mock_search = MagicMock()
    conv_id = uuid.uuid4()
    from datetime import datetime, timezone

    mock_conv = Conversation(id=conv_id, title="Test")
    mock_conv.created_at = datetime.now(timezone.utc)
    mock_conv.updated_at = datetime.now(timezone.utc)

    mock_repo.create_conversation = AsyncMock(return_value=mock_conv)

    service = ConversationService(mock_repo, mock_search)
    result = await service.create_conversation("Test")

    assert isinstance(result, ConversationResponse)
    assert result.id == conv_id
    assert result.title == "Test"
    mock_repo.create_conversation.assert_called_once_with("Test")


@pytest.mark.asyncio
async def test_get_conversation_not_found() -> None:
    """Test ConversationService.get_conversation returns None when not found."""
    mock_repo = MagicMock()
    mock_search = MagicMock()

    mock_repo.get_conversation = AsyncMock(return_value=None)

    service = ConversationService(mock_repo, mock_search)
    result = await service.get_conversation(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_chat_raises_on_missing_conversation() -> None:
    """Test chat raises ValueError when conversation does not exist."""
    mock_repo = MagicMock()
    mock_search = MagicMock()

    mock_repo.get_conversation = AsyncMock(return_value=None)

    service = ConversationService(mock_repo, mock_search)

    with pytest.raises(ValueError, match="not found"):
        await service.chat(conversation_id=uuid.uuid4(), message_content="hello")


@pytest.mark.asyncio
async def test_chat_success() -> None:
    """Test ConversationService.chat runs full pipeline and returns ChatResponse."""
    mock_repo = MagicMock()
    mock_search = MagicMock()
    mock_llm = MagicMock()

    conv_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    from datetime import datetime, timezone
    mock_conv = Conversation(id=conv_id, title="Ops")
    mock_conv.created_at = datetime.now(timezone.utc)
    mock_conv.updated_at = datetime.now(timezone.utc)

    mock_repo.get_conversation = AsyncMock(return_value=mock_conv)
    mock_repo.add_message = AsyncMock()
    mock_repo.get_messages = AsyncMock(return_value=[])

    # Stub the RAG pipeline answer
    from app.ai.rag import RAGPipeline
    rag_return = (
        "Valve should be open.",
        0.88,
        "HIGH",
        [{
            "filename": "guide.pdf",
            "document_id": doc_id,
            "chunk_id": chunk_id,
            "similarity_score": 0.88,
            "page_number": 1,
            "excerpt": "valve instruction...",
        }],
        ["valve instruction..."],
        {
            "retrieved_chunks": 1,
            "average_similarity": 0.88,
            "max_similarity": 0.88,
            "processing_time_ms": 12.4,
        },
    )

    with pytest.MonkeyPatch.context() as mp:
        async def fake_answer(question, top_k=5, history=None):
            return rag_return

        mp.setattr(RAGPipeline, "answer", fake_answer)

        service = ConversationService(mock_repo, mock_search, llm_provider=mock_llm)
        response = await service.chat(
            conversation_id=conv_id,
            message_content="How does the valve work?",
        )

    assert isinstance(response, ChatResponse)
    assert response.conversation_id == conv_id
    assert response.assistant_message == "Valve should be open."
    assert response.confidence_score == pytest.approx(0.88)
    assert response.confidence_level == "HIGH"
    assert len(response.sources) == 1
    assert response.sources[0].filename == "guide.pdf"
