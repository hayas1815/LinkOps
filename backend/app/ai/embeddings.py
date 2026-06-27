"""
Embedding generation service for document processing pipeline (S4-M4).

Converts text chunks into dense semantic vector embeddings using the
sentence-transformers library with the all-MiniLM-L6-v2 model.

Design decisions:
- Lazy model loading: the model is loaded once on first use (singleton).
- Output: 384-dimensional float32 vectors (all-MiniLM-L6-v2 native dim).
- Normalisation: L2-normalised for cosine similarity via pgvector.
- Batch encoding for efficiency when processing multiple chunks.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from app.ai.chunking import TextChunk


logger = logging.getLogger(__name__)

# Model identifier — pinned to a lightweight, well-tested model.
_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

# Expected embedding dimensionality for all-MiniLM-L6-v2
EMBEDDING_DIM: int = 384


class EmbeddingService:
    """
    Generates sentence embeddings for :class:`~app.ai.chunking.TextChunk` objects.

    The underlying SentenceTransformer model is loaded lazily on first call
    and cached for the lifetime of the service instance (typically the Celery
    worker process).

    Usage::

        service = EmbeddingService()
        embeddings = service.embed_chunks(chunks)
        # embeddings[i] is a list[float] of length 384

    Thread safety:
        SentenceTransformer's ``encode()`` is not guaranteed thread-safe.
        In Celery's default prefork model each worker process has its own
        instance, so no locking is required.
    """

    def __init__(self, model_name: str = _MODEL_NAME) -> None:
        self._model_name = model_name
        self._model = None  # lazy-loaded

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_chunks(self, chunks: list["TextChunk"]) -> list[list[float]]:
        """
        Generate one embedding vector per chunk.

        Args:
            chunks: Ordered list of :class:`~app.ai.chunking.TextChunk` objects.

        Returns:
            Parallel list of embedding vectors (each a ``list[float]`` of
            length :data:`EMBEDDING_DIM`).

        Raises:
            RuntimeError: If the model cannot be loaded.
            ValueError: If *chunks* is empty.
        """
        if not chunks:
            raise ValueError("Cannot embed an empty chunk list.")

        model = self._get_model()
        texts = [chunk.text for chunk in chunks]

        logger.info(
            "Generating embeddings for %d chunks using model %s.",
            len(texts),
            self._model_name,
        )

        # encode() returns a numpy ndarray of shape (n_chunks, EMBEDDING_DIM)
        # normalize_embeddings=True applies L2 normalisation in-place.
        raw: np.ndarray = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        # Convert to plain Python lists for JSON-serialisability and
        # pgvector compatibility.
        embeddings: list[list[float]] = raw.tolist()

        logger.info(
            "Embedding generation complete. Shape: (%d, %d).",
            len(embeddings),
            len(embeddings[0]) if embeddings else 0,
        )
        return embeddings

    def embed_query(self, query: str) -> list[float]:
        """
        Generate a single embedding for a query string.

        Useful for similarity search at query time (not used in the
        processing pipeline but provided for downstream consumers).

        Args:
            query: Raw query text.

        Returns:
            Embedding vector as ``list[float]`` of length :data:`EMBEDDING_DIM`.
        """
        if not query or not query.strip():
            raise ValueError("Cannot embed empty query.")

        model = self._get_model()
        raw: np.ndarray = model.encode(
            [query],
            batch_size=1,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return raw[0].tolist()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_model(self):
        """
        Lazily load and cache the SentenceTransformer model.

        Returns:
            A loaded ``SentenceTransformer`` instance.

        Raises:
            RuntimeError: If the model fails to load.
        """
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # noqa: PLC0415

                logger.info("Loading SentenceTransformer model: %s", self._model_name)
                self._model = SentenceTransformer(self._model_name)
                logger.info("Model %s loaded successfully.", self._model_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load embedding model '{self._model_name}': {exc}"
                ) from exc
        return self._model
