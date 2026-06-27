"""
API Router for the Copilot module.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.search.repository import SearchRepository
from app.modules.search.service import SearchService
from app.modules.copilot.schemas import CopilotQuestionRequest, CopilotAnswerResponse
from app.modules.copilot.service import CopilotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/copilot", tags=["Copilot"])


async def get_copilot_service(
    session: AsyncSession = Depends(get_db),
) -> CopilotService:
    """
    Dependency provider for CopilotService.
    """
    repository = SearchRepository(session)
    search_service = SearchService(repository)
    return CopilotService(search_service)


@router.post(
    "/ask",
    response_model=CopilotAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask AI Copilot",
    description=(
        "Submit a question to the AI Copilot. The Copilot will retrieve relevant "
        "document chunks using semantic vector search and generate an answer grounded "
        "in the retrieved context, complete with citation sources."
    ),
)
async def ask_copilot(
    request: CopilotQuestionRequest,
    service: CopilotService = Depends(get_copilot_service),
) -> CopilotAnswerResponse:
    """
    POST endpoint to submit a question to the Copilot.

    Args:
        request: CopilotQuestionRequest payload.
        service: Injected CopilotService instance.

    Returns:
        CopilotAnswerResponse containing the answer and citations.
    """
    try:
        response = await service.ask(
            question=request.question,
            top_k=request.top_k,
        )
        return response
    except ValueError as val_err:
        logger.warning("Validation error in Copilot query: %s", val_err)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error("Internal error during Copilot execution: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while compiling your answer.",
        )
