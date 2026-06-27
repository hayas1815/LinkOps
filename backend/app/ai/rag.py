"""
RAG (Retrieval-Augmented Generation) pipeline coordinator (S5-M2).
"""

from __future__ import annotations

import logging
from typing import Any

from app.ai.llm.base import BaseLLMProvider
from app.modules.search.service import SearchService

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are an industrial operational assistant. Answer the user's question "
    "as accurately and concisely as possible based only on the provided context. "
    "If the answer cannot be found in the context, state: 'I cannot find the answer "
    "in the provided documents.' Do not extrapolate or invent facts outside the context."
)


class RAGPipeline:
    """
    Coordinates semantic search retrieval and LLM generation (RAG).
    """

    def __init__(
        self,
        search_service: SearchService,
        llm_provider: BaseLLMProvider,
        system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
    ) -> None:
        """
        Initialize the RAG pipeline.

        Args:
            search_service: Injected SearchService for document retrieval.
            llm_provider: Injected LLM provider for text generation.
            system_instruction: The system prompt or instruction for the LLM.
        """
        self.search_service = search_service
        self.llm_provider = llm_provider
        self.system_instruction = system_instruction

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, float, str, list[dict[str, Any]], list[str], dict[str, Any]]:
        """
        Answer a question using the RAG pipeline.

        Args:
            question: The user's natural language query.
            top_k: The number of context chunks to retrieve.
            history: Optional conversation history.

        Returns:
            A tuple of (answer_text, confidence_score, confidence_level, sources, supporting_chunks, retrieval_statistics).
        """
        import time
        from app.ai.explainability import get_confidence_level, extract_supporting_excerpts

        logger.info("RAG Pipeline: Processing question: '%s' (top_k=%d)", question, top_k)

        # 1. Retrieve relevant context chunks (track time)
        start_time = time.perf_counter()
        chunks = await self.search_service.search(query=question, top_k=top_k)
        elapsed_time_ms = (time.perf_counter() - start_time) * 1000.0

        if not chunks:
            logger.info("RAG Pipeline: No relevant chunks found. Returning default fallback.")
            default_stats = {
                "retrieved_chunks": 0,
                "average_similarity": 0.0,
                "max_similarity": 0.0,
                "processing_time_ms": elapsed_time_ms,
            }
            return (
                "I cannot find the answer in the provided documents.",
                0.0,
                "LOW",
                [],
                [],
                default_stats,
            )

        # 2. Build prompt context & sources metadata
        context_str_parts = []
        sources: list[dict[str, Any]] = []

        for i, chunk in enumerate(chunks):
            context_str_parts.append(
                f"[Source {i+1}: {chunk.filename} (Chunk ID: {chunk.chunk_id})]\n{chunk.text}\n"
            )
            # Excerpt: a snippet of the chunk (first 200 chars as placeholder/excerpt)
            excerpt = chunk.text[:200]
            if len(chunk.text) > 200:
                excerpt += "..."

            sources.append({
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "chunk_id": chunk.chunk_id,
                "similarity_score": chunk.score,
                "page_number": chunk.page,  # chunk_index mapped to page
                "excerpt": excerpt,
            })

        context_block = "\n---\n".join(context_str_parts)

        # Format conversation history if available
        history_block = ""
        if history:
            history_lines = []
            for h in history:
                role_label = "User" if h["role"] == "user" else "Assistant"
                if h["role"] == "system":
                    continue
                history_lines.append(f"{role_label}: {h['content']}")
            history_block = "Conversation History:\n" + "\n".join(history_lines) + "\n\n"

        prompt = (
            "Context document chunks:\n"
            "=======================\n"
            f"{context_block}\n"
            "=======================\n\n"
            f"{history_block}"
            f"User Question: {question}\n\n"
            "Answer:"
        )

        # 3. Query LLM provider
        logger.info("RAG Pipeline: Sending prompt to LLM provider.")
        answer = await self.llm_provider.generate(
            prompt=prompt,
            system_instruction=self.system_instruction,
        )

        # 4. Calculate confidence, level, and stats
        scores = [s["similarity_score"] for s in sources]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        confidence_level = get_confidence_level(avg_score).value

        # Extract highlighted supporting excerpts
        supporting_excerpts = extract_supporting_excerpts(answer, chunks)

        retrieval_stats = {
            "retrieved_chunks": len(chunks),
            "average_similarity": avg_score,
            "max_similarity": max_score,
            "processing_time_ms": elapsed_time_ms,
        }

        logger.info(
            "RAG Pipeline: Generation complete. Confidence: %.4f (%s), Sources: %d",
            avg_score,
            confidence_level,
            len(sources),
        )
        return answer, avg_score, confidence_level, sources, supporting_excerpts, retrieval_stats
