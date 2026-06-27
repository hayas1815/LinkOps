"""
ORM model for the DocumentChunk entity.

Each row represents one text chunk extracted from a parent Document,
paired with its semantic embedding vector stored as a pgvector column.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# Embedding dimensionality for all-MiniLM-L6-v2
EMBEDDING_DIM: int = 384


class DocumentChunk(Base):
    """
    A single text chunk of a :class:`~app.modules.documents.models.Document`.

    Attributes:
        id: Primary key UUID.
        document_id: Foreign key to the parent document.
        chunk_index: 0-based position of this chunk within the document.
        text: The raw chunk text.
        char_start: Character offset of the chunk start within the full text.
        char_end: Character offset of the chunk end within the full text.
        token_estimate: Approximate token count (chars / 4).
        embedding: 384-dimensional float vector (pgvector).
        created_at: Server-side creation timestamp.
    """

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, nullable=False)

    # pgvector column — stores a 384-dim float32 vector
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship back to parent document (lazy="raise" to prevent N+1)
    document = relationship(
        "Document",
        back_populates="chunks",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk id={self.id} document_id={self.document_id} "
            f"chunk_index={self.chunk_index} tokens~{self.token_estimate}>"
        )
