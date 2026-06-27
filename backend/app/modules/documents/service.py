"""
Service layer for Document domain business logic.
"""

from datetime import datetime, UTC
import hashlib
import logging
import mimetypes
import os
import uuid

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.exceptions import (
    DocumentNotFoundException,
    DocumentValidationException,
)
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate
from app.services.storage.minio_service import MinioService


logger = logging.getLogger(__name__)



class DocumentService:
    """
    Service class orchestrating business logic and repository coordination for Documents.

    Documents undergo the following lifecycle transitions:
        UPLOADED → QUEUED → PROCESSING → TEXT_EXTRACTED → PROCESSED
                                       ↘ FAILED
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

    async def ingest_document(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        document_type: DocumentType,
    ) -> Document:
        """
        Ingest a document: check for duplicate using checksum, upload to MinIO,
        and persist its metadata in PostgreSQL.

        Args:
            filename: The filename of the uploaded document.
            content: The file binary content.
            content_type: The validated MIME type of the file.
            document_type: The document classification.

        Returns:
            Document: The newly created or existing Document model instance.
        """
        # 1. Validate File Size
        file_size = len(content)
        if file_size == 0:
            raise DocumentValidationException("Empty files are not allowed.")
        from app.modules.documents.constants import MAX_UPLOAD_SIZE
        if file_size > MAX_UPLOAD_SIZE:
            raise DocumentValidationException(
                f"File size exceeds the limit of {MAX_UPLOAD_SIZE} bytes."
            )

        # 2. Validate Extension
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpeg", "jpg"}
        if ext not in ALLOWED_EXTENSIONS:
            raise DocumentValidationException(f"Unsupported file extension: .{ext}")

        # 3. Validate MIME Type
        ALLOWED_MIME_TYPES = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "image/png",
            "image/jpeg",
        }
        
        # If content_type is unknown or not allowed, guess from extension
        if not content_type or content_type not in ALLOWED_MIME_TYPES:
            guessed_type, _ = mimetypes.guess_type(filename)
            if not guessed_type or guessed_type not in ALLOWED_MIME_TYPES:
                raise DocumentValidationException(
                    f"Unsupported or unknown MIME type: {content_type}"
                )
            content_type = guessed_type

        # 4. Compute SHA-256 Checksum
        checksum = hashlib.sha256(content).hexdigest()

        # 5. Check for Duplicate Detection
        existing_doc = await self.repository.get_by_checksum(checksum)
        if existing_doc:
            logger.info(
                "Duplicate document detected (checksum: %s). Returning existing metadata.",
                checksum,
            )
            return existing_doc

        # 6. Determine MinIO Object Key Path
        # Layout: documents/{year}/{month}/{uuid}_{filename}
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")
        doc_uuid = uuid.uuid4()
        storage_path = f"{year}/{month}/{doc_uuid}_{filename}"


        # 4. Upload file to MinIO
        minio_service = MinioService()
        await minio_service.upload_file(
            bucket="documents",
            object_name=storage_path,
            data=content,
            content_type=content_type,
        )

        # 5. Save metadata in PostgreSQL with QUEUED status
        document = Document(
            id=doc_uuid,
            filename=filename,
            original_filename=filename,
            document_type=document_type,
            mime_type=content_type,
            file_size=len(content),
            checksum=checksum,
            storage_path=storage_path,
            status=DocumentStatus.QUEUED,
            version=1,
        )

        document = await self.repository.create(document)

        # 6. Dispatch Celery processing task
        from app.tasks.document_processing import process_document  # noqa: PLC0415

        process_document.apply_async(
            args=[str(document.id)],
            queue="documents",
        )
        logger.info(
            "Document %s enqueued for background processing.",
            document.id,
        )

        return document

