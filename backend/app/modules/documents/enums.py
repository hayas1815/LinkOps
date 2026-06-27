"""
Enums for the Document module.
"""

from enum import StrEnum


class DocumentStatus(StrEnum):
    """
    Status of a document during its lifecycle in the platform.
    """

    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    PROCESSED = "PROCESSED"
    VALIDATING = "VALIDATING"
    STORED = "STORED"
    READY = "READY"
    FAILED = "FAILED"



class DocumentType(StrEnum):
    """
    Type or classification of a document.
    """

    UNKNOWN = "UNKNOWN"
    MANUAL = "MANUAL"
    SOP = "SOP"
    P_AND_ID = "P_AND_ID"
    DRAWING = "DRAWING"
    INSPECTION = "INSPECTION"
    REPORT = "REPORT"
    WORK_ORDER = "WORK_ORDER"
    OEM_MANUAL = "OEM_MANUAL"
