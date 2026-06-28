"""
Unit tests for ConversationService.
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.modules.conversations.service import ConversationService
from app.modules.conversations.exceptions import ConversationNotFoundException
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

    with pytest.raises(ConversationNotFoundException, match="not found"):
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
        async def fake_answer(self, question, top_k=5, history=None):
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


@pytest.mark.asyncio
async def test_chat_auto_create_conversation() -> None:
    """Test chat creates a new conversation if conversation_id is None."""
    mock_repo = MagicMock()
    mock_search = MagicMock()
    mock_llm = MagicMock()

    conv_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    from datetime import datetime, timezone
    mock_conv = Conversation(id=conv_id, title="New Conversation")
    mock_conv.created_at = datetime.now(timezone.utc)
    mock_conv.updated_at = datetime.now(timezone.utc)

    mock_repo.create_conversation = AsyncMock(return_value=mock_conv)
    mock_repo.add_message = AsyncMock()
    mock_repo.get_messages = AsyncMock(return_value=[])

    from app.ai.rag import RAGPipeline
    rag_return = (
        "Created new conversation.",
        0.90,
        "HIGH",
        [{
            "filename": "guide.pdf",
            "document_id": doc_id,
            "chunk_id": chunk_id,
            "similarity_score": 0.90,
            "page_number": 1,
            "excerpt": "instruction...",
        }],
        ["instruction..."],
        {
            "retrieved_chunks": 1,
            "average_similarity": 0.90,
            "max_similarity": 0.90,
            "processing_time_ms": 5.0,
        },
    )

    with pytest.MonkeyPatch.context() as mp:
        async def fake_answer(self, question, top_k=5, history=None):
            return rag_return

        mp.setattr(RAGPipeline, "answer", fake_answer)

        service = ConversationService(mock_repo, mock_search, llm_provider=mock_llm)
        response = await service.chat(
            conversation_id=None,
            message_content="Hello world",
        )

    assert isinstance(response, ChatResponse)
    assert response.conversation_id == conv_id
    assert response.assistant_message == "Created new conversation."
    mock_repo.create_conversation.assert_called_once()


@pytest.mark.asyncio
async def test_chat_memory_window() -> None:
    """Test that the conversation history passed to RAG is trimmed to copilot_memory_window."""
    mock_repo = MagicMock()
    mock_search = MagicMock()
    mock_llm = MagicMock()

    conv_id = uuid.uuid4()

    from datetime import datetime, timezone
    mock_conv = Conversation(id=conv_id, title="Test Window")
    mock_conv.created_at = datetime.now(timezone.utc)
    mock_conv.updated_at = datetime.now(timezone.utc)

    mock_repo.get_conversation = AsyncMock(return_value=mock_conv)
    mock_repo.add_message = AsyncMock()

    # Generate a list of 25 messages (12 turns of user/assistant + 1 current user message)
    # The last message is the current user message.
    history_messages = []
    for i in range(25):
        role = "user" if i % 2 == 0 else "assistant"
        history_messages.append(
            Message(
                id=uuid.uuid4(),
                conversation_id=conv_id,
                role=role,
                content=f"msg {i}",
                created_at=datetime.now(timezone.utc),
            )
        )
    mock_repo.get_messages = AsyncMock(return_value=history_messages)

    from app.ai.rag import RAGPipeline
    from app.core.config import get_settings
    settings = get_settings()
    # We want to verify that settings.copilot_memory_window limits the history length.
    # We will temporarily override the window to 10 for testing
    original_window = settings.copilot_memory_window
    settings.copilot_memory_window = 10

    captured_history = None

    rag_return = (
        "Answer",
        0.95,
        "HIGH",
        [],
        [],
        {
            "retrieved_chunks": 0,
            "average_similarity": 0.0,
            "max_similarity": 0.0,
            "processing_time_ms": 1.0,
        },
    )

    try:
        with pytest.MonkeyPatch.context() as mp:
            async def fake_answer(self, question, top_k=5, history=None):
                nonlocal captured_history
                captured_history = history
                return rag_return

            mp.setattr(RAGPipeline, "answer", fake_answer)

            service = ConversationService(mock_repo, mock_search, llm_provider=mock_llm)
            await service.chat(
                conversation_id=conv_id,
                message_content="Current question",
            )
    finally:
        # Restore settings
        settings.copilot_memory_window = original_window

    assert captured_history is not None
    # Configured memory window is 10.
    assert len(captured_history) == 10
    # It must contain the latest 10 messages before the current question (i.e. messages index 14 to 23).
    # Since history_messages has 25 messages, history_messages[-1] is the current user message (index 24).
    # The history before current question is index 0 to 23.
    # The latest 10 of those are index 14 to 23.
    assert captured_history[0]["content"] == "msg 14"
    assert captured_history[-1]["content"] == "msg 23"

