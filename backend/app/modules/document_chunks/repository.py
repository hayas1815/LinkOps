"""
Repository for DocumentChunk domain operations.

Provides synchronous bulk-insert used by the Celery worker, as well as
async helpers for API-facing queries.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.document_chunks.models import DocumentChunk


class DocumentChunkRepository:
    """
    Handles database access for :class:`DocumentChunk` entities.

    Two modes of operation:
    - **Sync** (``Session``): used inside Celery tasks.
    - **Async** (``AsyncSession``): reserved for future API endpoints.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialise with a *synchronous* SQLAlchemy session.

        Args:
            session: A plain ``sqlalchemy.orm.Session`` (not async).
        """
        self.session = session

    def bulk_create(self, chunks: list[DocumentChunk]) -> None:
        """
        Persist a list of :class:`DocumentChunk` rows in a single flush.

        Assigns server-default UUIDs and timestamps automatically.

        Args:
            chunks: Ordered list of populated ``DocumentChunk`` instances.
        """
        self.session.add_all(chunks)
        self.session.flush()

    def get_by_document_id(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        """
        Retrieve all chunks for a given document, ordered by ``chunk_index``.

        Args:
            document_id: UUID of the parent document.

        Returns:
            Ordered list of :class:`DocumentChunk` instances.
        """
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def delete_by_document_id(self, document_id: uuid.UUID) -> int:
        """
        Delete all chunks for a document (used when re-processing).

        Args:
            document_id: UUID of the parent document.

        Returns:
            Number of rows deleted.
        """
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        rows = list(self.session.execute(stmt).scalars().all())
        for row in rows:
            self.session.delete(row)
        self.session.flush()
        return len(rows)
