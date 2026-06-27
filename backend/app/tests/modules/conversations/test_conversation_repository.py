"""
Unit tests for ConversationRepository using mocked AsyncSession.
"""
from __future__ import annotations
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.models import Conversation, Message


@pytest.mark.asyncio
async def test_create_conversation(mock_session: MagicMock) -> None:
    repo = ConversationRepository(mock_session)
    mock_session.flush = AsyncMock()

    conv = await repo.create_conversation("Test Conversation")

    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    assert isinstance(conv, Conversation)
    assert conv.title == "Test Conversation"


@pytest.mark.asyncio
async def test_create_conversation_default_title(mock_session: MagicMock) -> None:
    repo = ConversationRepository(mock_session)
    mock_session.flush = AsyncMock()

    conv = await repo.create_conversation()

    assert conv.title == "New Conversation"


@pytest.mark.asyncio
async def test_get_conversation_found(mock_session: MagicMock) -> None:
    repo = ConversationRepository(mock_session)
    conv_id = uuid.uuid4()
    mock_conv = Conversation(id=conv_id, title="Pump Q&A")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conv
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_conversation(conv_id)
    assert result == mock_conv


@pytest.mark.asyncio
async def test_get_conversation_not_found(mock_session: MagicMock) -> None:
    repo = ConversationRepository(mock_session)
    conv_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_conversation(conv_id)
    assert result is None


@pytest.mark.asyncio
async def test_add_message(mock_session: MagicMock) -> None:
    repo = ConversationRepository(mock_session)
    conv_id = uuid.uuid4()
    mock_session.flush = AsyncMock()

    # Mock get_conversation for the parent update step
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Conversation(id=conv_id, title="Test")
    mock_session.execute = AsyncMock(return_value=mock_result)

    msg = await repo.add_message(
        conversation_id=conv_id,
        role="user",
        content="How does the valve work?",
    )

    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    assert isinstance(msg, Message)
    assert msg.role == "user"
    assert msg.content == "How does the valve work?"
