"""
Pydantic schemas for the DocumentChunk module.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentChunkResponse(BaseModel):
    """
    Read schema for a DocumentChunk — returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_estimate: int
    embedding: list[float] | None = Field(
        default=None,
        description="384-dimensional semantic embedding vector.",
    )
    created_at: datetime


class DocumentChunkCreate(BaseModel):
    """
    Write schema used internally when persisting chunks from the Celery task.
    Not exposed via the public API.
    """

    document_id: uuid.UUID
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_estimate: int
    embedding: list[float] | None = None
