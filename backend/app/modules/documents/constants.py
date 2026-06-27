"""
Constants for the Document module.
"""

from app.modules.documents.enums import DocumentType

SUPPORTED_DOCUMENT_TYPES: set[DocumentType] = {
    DocumentType.MANUAL,
    DocumentType.SOP,
    DocumentType.P_AND_ID,
    DocumentType.DRAWING,
    DocumentType.INSPECTION,
    DocumentType.REPORT,
    DocumentType.WORK_ORDER,
    DocumentType.OEM_MANUAL,
}

MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
DEFAULT_NAMESPACE: str = "default-documents"
