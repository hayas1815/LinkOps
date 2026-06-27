"""
Repository for Conversations module operations.

Handles database access for conversation sessions and persistent message logs.
"""

from __future__ import annotations

import logging
import uuid
from typing import Sequence
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import Conversation, Message

logger = logging.getLogger(__name__)


class ConversationRepository:
    """
    Handles database operations for conversation sessions and messages.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize ConversationRepository with an AsyncSession.

        Args:
            session: SQLAlchemy 2.0 AsyncSession.
        """
        self.session = session

    async def create_conversation(self, title: str | None = None) -> Conversation:
        """
        Create and persist a new Conversation session.

        Args:
            title: The title of the conversation.

        Returns:
            The created Conversation object.
        """
        db_title = title or "New Conversation"
        conversation = Conversation(title=db_title)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_conversation(self, conversation_id: uuid.UUID) -> Conversation | None:
        """
        Retrieve a Conversation session by ID.

        Args:
            conversation_id: Unique UUID of the conversation.

        Returns:
            The Conversation object or None if not found.
        """
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversations(self) -> Sequence[Conversation]:
        """
        Retrieve all Conversation sessions, ordered by updated_at descending.

        Returns:
            A sequence of Conversation objects.
        """
        stmt = select(Conversation).order_by(Conversation.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: uuid.UUID) -> bool:
        """
        Delete a Conversation session (and cascading messages).

        Args:
            conversation_id: Unique UUID of the conversation.

        Returns:
            True if deleted, False if conversation was not found.
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        stmt = delete(Conversation).where(Conversation.id == conversation_id)
        await self.session.execute(stmt)
        return True

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ) -> Message:
        """
        Create and persist a new Message in a conversation.

        Args:
            conversation_id: Unique UUID of the parent conversation.
            role: The message sender (user, assistant, system).
            content: The text content of the message.

        Returns:
            The created Message object.
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(message)
        await self.session.flush()

        # Update parent conversation updated_at timestamp
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        conversation = result.scalar_one_or_none()
        if conversation:
            # SQLAlchemy will trigger updated_at auto-update or we can set it
            conversation.updated_at = func.now()

        return message

    async def get_messages(self, conversation_id: uuid.UUID) -> Sequence[Message]:
        """
        Retrieve all messages belonging to a conversation, ordered chronologically.

        Args:
            conversation_id: Unique UUID of the conversation.

        Returns:
            A sequence of Message objects.
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
