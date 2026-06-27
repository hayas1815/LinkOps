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

    async def get_by_checksum(self, checksum: str) -> Document | None:
        """
        Retrieve an active (not soft-deleted) Document entity by its checksum.

        Args:
            checksum: The SHA-256 checksum of the file.

        Returns:
            The Document model instance if found and not deleted, else None.
        """
        stmt = select(Document).where(
            Document.checksum == checksum, Document.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        document_id: uuid.UUID,
        status: "DocumentStatus",
        *,
        failure_reason: str | None = None,
        processing_started_at: "datetime | None" = None,
        processing_completed_at: "datetime | None" = None,
        extracted_text: str | None = None,
        page_count: int | None = None,
        extraction_method: str | None = None,
        extraction_language: str | None = None,
        extraction_confidence: float | None = None,
        extracted_at: "datetime | None" = None,
    ) -> Document | None:
        """
        Update only the status (and optional processing timestamps) of a Document.

        Args:
            document_id: The UUID of the document to update.
            status: The new DocumentStatus value.
            failure_reason: Optional failure description.
            processing_started_at: Optional timestamp for when processing began.
            processing_completed_at: Optional timestamp for when processing completed.
            extracted_text: Optional extracted text.
            page_count: Optional page count.
            extraction_method: Optional method used for extraction.
            extraction_language: Optional detected language.
            extraction_confidence: Optional extraction confidence score.
            extracted_at: Optional timestamp when extraction finished.

        Returns:
            The updated Document model instance, or None if not found.
        """
        from app.modules.documents.enums import DocumentStatus  # noqa: PLC0415

        document = await self.get_by_id(document_id)
        if document is None:
            return None

        document.status = status
        if failure_reason is not None:
            document.failure_reason = failure_reason
        if processing_started_at is not None:
            document.processing_started_at = processing_started_at
        if processing_completed_at is not None:
            document.processing_completed_at = processing_completed_at

        # Text extraction fields
        if extracted_text is not None:
            document.extracted_text = extracted_text
        if page_count is not None:
            document.page_count = page_count
        if extraction_method is not None:
            document.extraction_method = extraction_method
        if extraction_language is not None:
            document.extraction_language = extraction_language
        if extraction_confidence is not None:
            document.extraction_confidence = extraction_confidence
        if extracted_at is not None:
            document.extracted_at = extracted_at

        self.session.add(document)
        await self.session.flush()
        return document
