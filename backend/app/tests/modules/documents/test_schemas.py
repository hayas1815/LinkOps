"""
Unit tests for Document Pydantic schemas.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)


def test_document_create_success() -> None:
    """
    Test successful validation of DocumentCreate.
    """
    data = {
        "filename": "sop_001.pdf",
        "original_filename": "standard_operating_procedure.pdf",
        "document_type": DocumentType.SOP,
        "mime_type": "application/pdf",
        "file_size": 1024,
    }
    schema = DocumentCreate(**data)
    assert schema.filename == "sop_001.pdf"
    assert schema.original_filename == "standard_operating_procedure.pdf"
    assert schema.document_type == DocumentType.SOP
    assert schema.mime_type == "application/pdf"
    assert schema.file_size == 1024


def test_document_create_validation_error() -> None:
    """
    Test validation errors in DocumentCreate when missing fields.
    """
    with pytest.raises(ValidationError):
        # Missing filename and original_filename
        DocumentCreate(document_type=DocumentType.SOP)  # type: ignore


def test_document_update_success() -> None:
    """
    Test validation of DocumentUpdate with partial fields.
    """
    schema1 = DocumentUpdate(filename="updated.pdf")
    assert schema1.filename == "updated.pdf"
    assert schema1.original_filename is None

    schema2 = DocumentUpdate()
    assert schema2.filename is None
    assert schema2.document_type is None


def test_document_response_success() -> None:
    """
    Test validation of DocumentResponse.
    """
    data = {
        "id": uuid.uuid4(),
        "filename": "sop_001.pdf",
        "original_filename": "standard_operating_procedure.pdf",
        "document_type": DocumentType.SOP,
        "status": DocumentStatus.READY,
        "mime_type": "application/pdf",
        "file_size": 1024,
        "storage_path": "/var/storage/sop_001.pdf",
        "checksum": "d3b07384d113edec49eaa6238ad5ff00",
        "version": 1,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    schema = DocumentResponse(**data)
    assert schema.id == data["id"]
    assert schema.status == DocumentStatus.READY
    assert schema.storage_path == "/var/storage/sop_001.pdf"
    assert schema.checksum == "d3b07384d113edec49eaa6238ad5ff00"
