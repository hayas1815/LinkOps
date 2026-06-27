"""
Repository for Document domain operations.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document


class DocumentRepository:
    """
    Repository class handling database access for Document entities.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the DocumentRepository with an active AsyncSession.

        Args:
            session: SQLAlchemy 2.0 AsyncSession for database operations.
        """
        self.session = session

    async def create(self, document: Document) -> Document:
        """
        Persist a new Document entity in the database.

        Args:
            document: The Document model instance to create.

        Returns:
            The created Document model instance.
        """
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """
        Retrieve a Document entity by its unique identifier if it is not soft-deleted.

        Args:
            document_id: The UUID of the document to retrieve.

        Returns:
            The Document model instance if found and not deleted, else None.
        """
        stmt = select(Document).where(
            Document.id == document_id, Document.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """
        Retrieve a list of Document entities that are not soft-deleted, with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            A list of Document model instances.
        """
        stmt = (
            select(Document)
            .where(Document.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, document: Document) -> Document:
        """
        Persist updates on a tracked Document entity.

        Args:
            document: The modified Document model instance.

        Returns:
            The updated Document model instance.
        """
        self.session.add(document)
        await self.session.flush()
        return document

    async def soft_delete(self, document_id: uuid.UUID) -> bool:
        """
        Soft-delete a Document entity by setting its deleted_at timestamp.

        Args:
            document_id: The UUID of the document to soft-delete.

        Returns:
            True if the document was found and soft-deleted, else False.
        """
        document = await self.get_by_id(document_id)
        if not document:
            return False

        document.deleted_at = datetime.now(UTC)
        self.session.add(document)
        await self.session.flush()
        return True
