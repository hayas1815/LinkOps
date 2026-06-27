"""
API Router for the Document module.
"""

import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.documents.enums import DocumentType
from app.modules.documents.exceptions import (
    DocumentNotFoundException,
    DocumentValidationException,
)
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.modules.documents.service import DocumentService


router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


async def get_async_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to yield an asynchronous database session.

    Yields:
        AsyncSession: The database session.
    """
    yield session



async def get_document_service(
    session: AsyncSession = Depends(get_async_session),
) -> DocumentService:
    """
    Dependency to resolve the DocumentService instance.

    Args:
        session: Active database session injected via get_async_session.

    Returns:
        DocumentService: An initialized service layer instance.
    """
    repository = DocumentRepository(session)
    return DocumentService(repository)


@router.post(
    "/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile = File(..., description="The document file to upload"),
    document_type: DocumentType = Form(
        default=DocumentType.UNKNOWN,
        description="The type/classification of the document",
    ),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Upload an industrial document file.

    Validates file size, extension, and MIME type. Automatically computes
    SHA-256 integrity checksum, stores file in MinIO object store, and
    saves metadata in PostgreSQL. Handles duplicate detection gracefully.
    """
    try:
        contents = await file.read()
        document = await service.ingest_document(
            filename=file.filename or "unknown",
            content=contents,
            content_type=file.content_type,
            document_type=document_type,
        )
        return DocumentResponse.model_validate(document)
    except DocumentValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        ) from e


@router.post(
    "/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)

async def create_document(
    document_in: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Create a new Document record.

    Args:
        document_in: Properties of the document to create.
        service: The injected service layer coordinator.

    Returns:
        DocumentResponse: The created document data.
    """
    document = await service.create_document(document_in)
    return DocumentResponse.model_validate(document)


@router.get("/", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """
    Retrieve a paginated list of active documents.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        service: The injected service layer coordinator.

    Returns:
        DocumentListResponse: Paginated results list.
    """
    items = await service.list_documents(skip=skip, limit=limit)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(item) for item in items],
        total=len(items),
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get(
    "/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK
)
async def get_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Retrieve details of a single document by its UUID.

    Args:
        document_id: UUID of the target document.
        service: The injected service layer coordinator.

    Returns:
        DocumentResponse: Document details.

    Raises:
        HTTPException: 404 error if the document is not found.
    """
    try:
        document = await service.get_document(document_id)
        return DocumentResponse.model_validate(document)
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.patch(
    "/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK
)
async def update_document(
    document_id: uuid.UUID,
    document_in: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Partially update properties of an existing document.

    Args:
        document_id: UUID of the target document.
        document_in: Fields to update.
        service: The injected service layer coordinator.

    Returns:
        DocumentResponse: Updated document details.

    Raises:
        HTTPException: 404 error if the document is not found.
    """
    try:
        document = await service.update_document(document_id, document_in)
        return DocumentResponse.model_validate(document)
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> None:
    """
    Soft-delete a document by setting its deleted_at field.

    Args:
        document_id: UUID of the target document.
        service: The injected service layer coordinator.

    Raises:
        HTTPException: 404 error if the document is not found.
    """
    try:
        await service.delete_document(document_id)
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
