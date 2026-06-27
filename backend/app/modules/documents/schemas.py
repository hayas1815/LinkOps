"""
Pydantic schemas for the Document module.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.modules.documents.enums import DocumentStatus, DocumentType


class DocumentBase(BaseModel):
    """
    Base schema for Document properties.
    """

    filename: str = Field(..., description="The name of the stored file")
    original_filename: str = Field(..., description="The original uploaded filename")
    document_type: DocumentType = Field(
        ..., description="The type or classification of the document"
    )
    mime_type: str | None = Field(
        default=None, description="The MIME type of the file"
    )
    file_size: int | None = Field(
        default=None, description="The size of the file in bytes"
    )


class DocumentCreate(DocumentBase):
    """
    Schema for creating a new Document record.
    """

    pass


class DocumentUpdate(BaseModel):
    """
    Schema for updating an existing Document record. All fields are optional.
    """

    filename: str | None = Field(
        default=None, description="The name of the stored file"
    )
    original_filename: str | None = Field(
        default=None, description="The original uploaded filename"
    )
    document_type: DocumentType | None = Field(
        default=None, description="The type or classification of the document"
    )
    mime_type: str | None = Field(
        default=None, description="The MIME type of the file"
    )
    file_size: int | None = Field(
        default=None, description="The size of the file in bytes"
    )


class DocumentResponse(DocumentBase):
    """
    Schema for a Document response payload, including metadata and state.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique UUID identifier for the document")
    status: DocumentStatus = Field(
        ..., description="The current processing status of the document"
    )
    storage_path: str | None = Field(
        default=None, description="The internal storage path of the document file"
    )
    checksum: str | None = Field(
        default=None, description="The checksum of the document file"
    )
    version: int = Field(..., description="The version of the document record")
    processing_started_at: datetime | None = Field(
        default=None, description="The timestamp when document processing started"
    )
    processing_completed_at: datetime | None = Field(
        default=None, description="The timestamp when document processing completed"
    )
    failure_reason: str | None = Field(
        default=None, description="The reason for processing failure, if applicable"
    )
    extracted_text: str | None = Field(
        default=None, description="The extracted text content of the document"
    )
    page_count: int | None = Field(
        default=None, description="The number of pages in the document"
    )
    extraction_method: str | None = Field(
        default=None, description="The method/tool used to extract text"
    )
    extraction_language: str | None = Field(
        default=None, description="The detected language of the extracted text"
    )
    extraction_confidence: float | None = Field(
        default=None, description="The confidence score of the text extraction"
    )
    extracted_at: datetime | None = Field(
        default=None, description="The timestamp when the text was extracted"
    )
    created_at: datetime = Field(
        ..., description="The timestamp when the document record was created"
    )
    updated_at: datetime = Field(
        ..., description="The timestamp when the document record was last updated"
    )



class DocumentListResponse(BaseModel):
    """
    Paginated schema for listing Document responses.
    """

    items: list[DocumentResponse] = Field(
        ..., description="List of document records in the current page"
    )
    total: int = Field(
        ..., description="Total count of document records matching query"
    )
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
