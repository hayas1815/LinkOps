"""
Document module foundation for LinkOps.
Exposes enums, models, schemas, repositories, services, routers, and exceptions.
"""

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.exceptions import DocumentException, DocumentNotFoundException
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.router import router
from app.modules.documents.service import DocumentService

# Import DocumentChunk so SQLAlchemy can resolve the Document.chunks
# relationship string reference ('DocumentChunk') at mapper configuration time.
import app.modules.document_chunks.models  # noqa: F401, E402

__all__ = [
    "DocumentStatus",
    "DocumentType",
    "Document",
    "DocumentRepository",
    "DocumentService",
    "router",
    "DocumentException",
    "DocumentNotFoundException",
]
