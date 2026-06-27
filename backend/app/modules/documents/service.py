"""
Service layer for Document domain business logic.
"""

import uuid

from app.modules.documents.enums import DocumentStatus
from app.modules.documents.exceptions import DocumentNotFoundException
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate


class DocumentService:
    """
    Service class orchestrating business logic and repository coordination for Documents.
    """

    def __init__(self, repository: DocumentRepository) -> None:
        """
        Initialize the DocumentService with a DocumentRepository.

        Args:
            repository: The repository instance for Document database operations.
        """
        self.repository = repository

    async def create_document(self, document_in: DocumentCreate) -> Document:
        """
        Create a new Document record with default UPLOADED status.

        Args:
            document_in: Pydantic schema containing properties to initialize the Document.

        Returns:
            The created Document model instance.
        """
        document = Document(
            filename=document_in.filename,
            original_filename=document_in.original_filename,
            document_type=document_in.document_type,
            mime_type=document_in.mime_type,
            file_size=document_in.file_size,
            status=DocumentStatus.UPLOADED,
        )
        return await self.repository.create(document)

    async def get_document(self, document_id: uuid.UUID) -> Document:
        """
        Retrieve a Document record by its unique UUID.

        Args:
            document_id: The UUID of the document to retrieve.

        Returns:
            The Document model instance.

        Raises:
            DocumentNotFoundException: If the document is not found or soft-deleted.
        """
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(
                f"Document with ID {document_id} not found."
            )
        return document

    async def list_documents(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """
        Retrieve a paginated list of active Document records.

        Args:
            skip: The number of documents to skip.
            limit: The maximum number of documents to return.

        Returns:
            A list of Document model instances.
        """
        return await self.repository.list(skip=skip, limit=limit)

    async def update_document(
        self, document_id: uuid.UUID, document_in: DocumentUpdate
    ) -> Document:
        """
        Apply partial updates to an existing Document record.

        Args:
            document_id: The UUID of the document to update.
            document_in: Pydantic schema containing fields to update.

        Returns:
            The updated Document model instance.

        Raises:
            DocumentNotFoundException: If the document is not found or soft-deleted.
        """
        document = await self.get_document(document_id)

        update_data = document_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(document, key, value)

        return await self.repository.update(document)

    async def delete_document(self, document_id: uuid.UUID) -> None:
        """
        Soft-delete a Document record.

        Args:
            document_id: The UUID of the document to delete.

        Raises:
            DocumentNotFoundException: If the document is not found or soft-deleted.
        """
        deleted = await self.repository.soft_delete(document_id)
        if not deleted:
            raise DocumentNotFoundException(
                f"Document with ID {document_id} not found."
            )
