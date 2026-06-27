"""
Service layer for the Search module.

Coordinates query embedding generation and similarity retrieval.
"""

from __future__ import annotations

import logging
from app.modules.search.repository import SearchRepository
from app.modules.search.schemas import SearchResultItem
from app.ai.embeddings import EmbeddingService
from app.ai.retrieval import DEFAULT_MIN_SIMILARITY_SCORE

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for executing semantic searches over document chunks.
    """

    def __init__(
        self,
        repository: SearchRepository,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        """
        Initialize the SearchService.

        Args:
            repository: SearchRepository instance.
            embedding_service: Optional EmbeddingService instance (lazily created if None).
        """
        self.repository = repository
        self.embedding_service = embedding_service or EmbeddingService()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = DEFAULT_MIN_SIMILARITY_SCORE,
    ) -> list[SearchResultItem]:
        """
        Perform a semantic search for a user query.

        1. Generates query embedding.
        2. Queries pgvector similarity via SearchRepository.
        3. Formats results into ranked SearchResultItem list.

        Args:
            query: The natural language query string.
            top_k: Number of ranked results to return.
            min_score: Minimum similarity score threshold.

        Returns:
            A list of SearchResultItem objects.
        """
        logger.info(
            "Executing semantic search for query: '%s' (top_k=%d, min_score=%.2f)",
            query,
            top_k,
            min_score,
        )

        # Generate embedding for the query.
        # This will load sentence-transformers/all-MiniLM-L6-v2 lazily if not loaded.
        query_embedding = self.embedding_service.embed_query(query)

        # Execute pgvector similarity search
        rows = await self.repository.semantic_search(
            query_embedding=query_embedding,
            limit=top_k,
            min_score=min_score,
        )

        results: list[SearchResultItem] = []
        for chunk, doc, score in rows:
            results.append(
                SearchResultItem(
                    document_id=doc.id,
                    chunk_id=chunk.id,
                    score=float(score),
                    text=chunk.text,
                    filename=doc.original_filename,
                    document_type=doc.document_type,
                    page=chunk.chunk_index,  # chunk_index as page proxy
                )
            )

        logger.info("Semantic search completed. Found %d results.", len(results))
        return results
