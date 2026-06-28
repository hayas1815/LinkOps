"""
Service layer for the Conversations module.

Coordinates database persistence for chat history and executing multi-turn context-aware RAG.
"""

from __future__ import annotations

import logging
import uuid
from typing import Sequence

from app.ai.llm.base import BaseLLMProvider
from app.ai.llm.factory import LLMFactory
from app.ai.rag import RAGPipeline
from app.ai.context import build_conversation_context
from app.modules.conversations.exceptions import ConversationNotFoundException
from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.schemas import (
    ConversationResponse,
    MessageResponse,
    ChatResponse,
)
from app.modules.copilot.schemas import CitationSource
from app.modules.search.service import SearchService

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Coordinates conversation history operations and Q&A chat turn logic.
    """

    def __init__(
        self,
        repository: ConversationRepository,
        search_service: SearchService,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        """
        Initialize ConversationService.

        Args:
            repository: ConversationRepository.
            search_service: SearchService.
            llm_provider: Optional LLM provider instance.
        """
        self.repository = repository
        self.search_service = search_service
        self.llm_provider = llm_provider or LLMFactory.get_provider()

    async def create_conversation(self, title: str | None = None) -> ConversationResponse:
        """
        Create a new Conversation session.
        """
        conv = await self.repository.create_conversation(title)
        return ConversationResponse.model_validate(conv)

    async def get_conversation(self, conversation_id: uuid.UUID) -> ConversationResponse | None:
        """
        Retrieve a Conversation session.
        """
        conv = await self.repository.get_conversation(conversation_id)
        if not conv:
            return None
        return ConversationResponse.model_validate(conv)

    async def list_conversations(self) -> list[ConversationResponse]:
        """
        List all Conversation sessions.
        """
        convs = await self.repository.list_conversations()
        return [ConversationResponse.model_validate(c) for c in convs]

    async def delete_conversation(self, conversation_id: uuid.UUID) -> bool:
        """
        Delete a Conversation session.
        """
        return await self.repository.delete_conversation(conversation_id)

    async def get_messages(self, conversation_id: uuid.UUID) -> list[MessageResponse]:
        """
        List message history for a Conversation session.
        """
        conv = await self.repository.get_conversation(conversation_id)
        if not conv:
            raise ConversationNotFoundException(conversation_id)

        messages = await self.repository.get_messages(conversation_id)
        return [MessageResponse.model_validate(m) for m in messages]

    async def chat(
        self,
        conversation_id: uuid.UUID | None,
        message_content: str,
        top_k: int = 5,
    ) -> ChatResponse:
        """
        Execute a chat turn:
          1. Persist user message.
          2. Retrieve entire history, build trimmed context.
          3. Query context-aware RAG pipeline.
          4. Persist assistant response.
          5. Return chat results.
        """
        # Ensure conversation exists or auto-create one
        if conversation_id is None:
            conv = await self.repository.create_conversation()
            conversation_id = conv.id
        else:
            conv = await self.repository.get_conversation(conversation_id)
            if not conv:
                raise ConversationNotFoundException(conversation_id)

        # 1. Add user message
        await self.repository.add_message(
            conversation_id=conversation_id,
            role="user",
            content=message_content,
        )

        # 2. Retrieve history and format
        all_messages = await self.repository.get_messages(conversation_id)

        # Get settings for memory window configuration
        from app.core.config import get_settings
        settings = get_settings()

        # Trim conversation history (prior turns) to the configured memory window size.
        # We slice all_messages[:-1] to exclude the user message we just appended,
        # ensuring only prior turns are passed as the history parameter to RAG pipeline.
        trimmed_history = build_conversation_context(
            all_messages[:-1],
            max_messages=settings.copilot_memory_window,
        )

        # 3. Execute context-aware RAG
        pipeline = RAGPipeline(self.search_service, self.llm_provider)
        (
            answer,
            confidence_score,
            confidence_level,
            raw_sources,
            _,
            _,
        ) = await pipeline.answer(
            question=message_content,
            top_k=top_k,
            history=trimmed_history,
        )

        # 4. Save assistant response
        await self.repository.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

        # Map source citations
        sources = [
            CitationSource(
                filename=src["filename"],
                document_id=src["document_id"],
                chunk_id=src["chunk_id"],
                similarity_score=src["similarity_score"],
                page_number=src["page_number"],
                excerpt=src["excerpt"],
            )
            for src in raw_sources
        ]

        return ChatResponse(
            conversation_id=conversation_id,
            assistant_message=answer,
            sources=sources,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
        )
