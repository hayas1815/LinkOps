"""
Service layer for the Copilot module.

Coordinates semantic search and LLM generation via the RAG pipeline.
"""

from __future__ import annotations

import logging
from app.ai.llm.base import BaseLLMProvider
from app.ai.llm.factory import LLMFactory
from app.ai.rag import RAGPipeline
from app.modules.search.service import SearchService
from app.modules.copilot.schemas import CitationSource, CopilotAnswerResponse

logger = logging.getLogger(__name__)


class CopilotService:
    """
    Service responsible for coordinating Copilot Q&A sessions.
    """

    def __init__(
        self,
        search_service: SearchService,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        """
        Initialize the CopilotService.

        Args:
            search_service: Injected SearchService.
            llm_provider: Optional LLM provider (falls back to LLMFactory).
        """
        self.search_service = search_service
        self.llm_provider = llm_provider or LLMFactory.get_provider()

    async def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> CopilotAnswerResponse:
        """
        Process a user question, retrieve context, call LLM, and return ranked citations.

        Args:
            question: User's question.
            top_k: Number of chunks to retrieve for grounding.

        Returns:
            A populated CopilotAnswerResponse schema.
        """
        logger.info("CopilotService: ask() request received.")

        # Coordinate RAG pipeline execution
        pipeline = RAGPipeline(self.search_service, self.llm_provider)
        (
            answer,
            confidence_score,
            confidence_level,
            raw_sources,
            supporting_chunks,
            retrieval_stats,
        ) = await pipeline.answer(
            question=question,
            top_k=top_k,
        )

        sources = [
            CitationSource(
                filename=src["filename"],
                document_id=src["document_id"],
                chunk_id=src["chunk_id"],
                similarity_score=src["similarity_score"],
                page_number=src["page_number"],
                excerpt=src["excerpt"],
            )
            for src in raw_sources
        ]

        from app.modules.copilot.schemas import RetrievalStatistics

        stats = RetrievalStatistics(
            retrieved_chunks=retrieval_stats["retrieved_chunks"],
            average_similarity=retrieval_stats["average_similarity"],
            max_similarity=retrieval_stats["max_similarity"],
            processing_time_ms=retrieval_stats["processing_time_ms"],
        )

        return CopilotAnswerResponse(
            answer=answer,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            sources=sources,
            supporting_chunks=supporting_chunks,
            retrieval_statistics=stats,
        )
