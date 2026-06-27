"""
Repository for Search module operations.

Handles vector similarity queries against the database using pgvector.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row

from app.modules.document_chunks.models import DocumentChunk
from app.modules.documents.models import Document

logger = logging.getLogger(__name__)


class SearchRepository:
    """
    Handles similarity search database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize SearchRepository with an AsyncSession.

        Args:
            session: SQLAlchemy 2.0 AsyncSession for database operations.
        """
        self.session = session

    async def semantic_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        min_score: float = 0.0,
    ) -> Sequence[Row[tuple[DocumentChunk, Document, float]]]:
        """
        Perform a cosine similarity search against document chunks.

        Returns a list of tuples containing (DocumentChunk, Document, similarity_score).
        Filters out soft-deleted documents.

        Args:
            query_embedding: 384-dimensional query embedding vector.
            limit: The maximum number of results to return.
            min_score: The minimum similarity score threshold (0.0 to 1.0).

        Returns:
            A sequence of SQLAlchemy Row objects matching the criteria.
        """
        # Calculate cosine distance using pgvector.
        # cosine_distance returns distance (0.0 = identical, 2.0 = opposite).
        distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
        score_expr = 1.0 - distance_expr

        stmt = (
            select(DocumentChunk, Document, score_expr.label("score"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.deleted_at.is_(None))
            .where(score_expr >= min_score)
            .order_by(distance_expr.asc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.all()
