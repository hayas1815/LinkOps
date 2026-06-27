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
