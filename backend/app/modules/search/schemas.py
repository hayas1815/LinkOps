"""
Pydantic schemas for the Search module.
"""

from __future__ import annotations

import uuid
from pydantic import BaseModel, Field, field_validator

from app.modules.documents.enums import DocumentType
from app.ai.retrieval import MAX_TOP_K


class SearchRequest(BaseModel):
    """
    Schema representing a request for semantic document search.
    """

    query: str = Field(
        ...,
        description="The natural language query string to search for.",
        min_length=1,
        max_length=2000,
    )
    top_k: int = Field(
        default=5,
        description="The maximum number of relevant passages (chunks) to return.",
        ge=1,
        le=MAX_TOP_K,
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure the query is not just whitespace."""
        if not v.strip():
            raise ValueError("Query string cannot be empty or whitespace only.")
        return v.strip()


class SearchResultItem(BaseModel):
    """
    Schema representing a single ranked result from the semantic search.
    """

    document_id: uuid.UUID = Field(
        ..., description="The unique identifier of the matching document."
    )
    chunk_id: uuid.UUID = Field(
        ..., description="The unique identifier of the specific matching chunk."
    )
    score: float = Field(
        ...,
        description="The cosine similarity score (typically 0.0 to 1.0, higher is more similar).",
    )
    text: str = Field(
        ..., description="The textual content of the matching passage."
    )
    filename: str = Field(
        ..., description="The name of the parent document file."
    )
    document_type: DocumentType = Field(
        ..., description="The type or classification of the parent document."
    )
    page: int | None = Field(
        default=None,
        description="The estimated page number (represented by chunk_index).",
    )
