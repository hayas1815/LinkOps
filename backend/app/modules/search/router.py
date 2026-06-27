"""
API Router for the Search module.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.search.schemas import SearchRequest, SearchResultItem
from app.modules.search.repository import SearchRepository
from app.modules.search.service import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


async def get_search_service(
    session: AsyncSession = Depends(get_db),
) -> SearchService:
    """
    Dependency provider for SearchService.
    """
    repository = SearchRepository(session)
    return SearchService(repository)


@router.post(
    "",
    response_model=list[SearchResultItem],
    status_code=status.HTTP_200_OK,
    summary="Semantic Document Search",
    description=(
        "Perform a vector similarity search across all active (non-soft-deleted) "
        "document chunks in the database using a natural language query."
    ),
)
async def search_documents(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service),
) -> list[SearchResultItem]:
    """
    POST endpoint to search document chunks semantically.

    Args:
        request: SearchRequest containing query and top_k limit.
        service: Injected SearchService instance.

    Returns:
        List of ranked SearchResultItem objects.
    """
    try:
        results = await service.search(
            query=request.query,
            top_k=request.top_k,
        )
        return results
    except ValueError as val_err:
        logger.warning("Validation error in search query: %s", val_err)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error("Internal error during semantic search execution: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing the search request.",
        )
