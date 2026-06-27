"""
API Router for the Document module.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])
