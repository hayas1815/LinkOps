"""
API Router for the Conversations module (S5-M4).
"""

from __future__ import annotations

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.search.repository import SearchRepository
from app.modules.search.service import SearchService
from app.modules.conversations.exceptions import ConversationNotFoundException
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.service import ConversationService
from app.modules.conversations.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Conversations"])


async def get_conversation_service(
    session: AsyncSession = Depends(get_db),
) -> ConversationService:
    """
    Dependency provider for ConversationService.
    """
    conv_repo = ConversationRepository(session)
    search_repo = SearchRepository(session)
    search_service = SearchService(search_repo)
    return ConversationService(conv_repo, search_service)


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/api/v1/copilot/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-turn Chat with AI Copilot",
    description=(
        "Continue an existing conversation with the AI Copilot. "
        "The Copilot maintains conversation history and uses it alongside "
        "semantic vector search to generate context-aware answers."
    ),
)
async def chat(
    request: ChatRequest,
    service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    try:
        return await service.chat(
            conversation_id=request.conversation_id,
            message_content=request.message,
        )
    except (ConversationNotFoundException, ValueError) as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error("Error during chat turn: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the chat request.",
        )


# ---------------------------------------------------------------------------
# Conversation CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/api/v1/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation",
    description="Start a new conversation session.",
)
async def create_conversation(
    request: ConversationCreate,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await service.create_conversation(request.title)


@router.get(
    "/api/v1/conversations/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Conversation",
    description="Retrieve a conversation session by its ID.",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    conv = await service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found.",
        )
    return conv


@router.get(
    "/api/v1/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="List Conversation Messages",
    description="Retrieve all messages in a conversation session.",
)
async def list_messages(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> list[MessageResponse]:
    try:
        return await service.get_messages(conversation_id)
    except (ConversationNotFoundException, ValueError) as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.delete(
    "/api/v1/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Conversation",
    description="Delete a conversation session and all its messages.",
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    deleted = await service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found.",
        )
