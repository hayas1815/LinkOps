"""
Text chunking service for document processing pipeline (S4-M4).

Splits extracted document text into semantically meaningful chunks
for downstream embedding generation.

Design decisions:
- Preserve paragraph boundaries to avoid splitting mid-sentence.
- Target chunk size: 500-800 tokens (approximated as ~4 chars/token).
- 20% overlap between consecutive chunks to preserve context.
- Stable, deterministic ordering for reproducible embeddings.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Sequence


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token approximation constants
# ---------------------------------------------------------------------------
# Rough character-to-token ratio for English text.  This avoids a hard
# dependency on a tokeniser at chunking time; exact token counts are less
# critical than keeping chunks roughly within the target window.
_CHARS_PER_TOKEN: float = 4.0

# Target chunk size in tokens
_TARGET_MIN_TOKENS: int = 500
_TARGET_MAX_TOKENS: int = 800

# Overlap fraction (20%)
_OVERLAP_FRACTION: float = 0.20

# Character equivalents
_TARGET_MIN_CHARS: int = int(_TARGET_MIN_TOKENS * _CHARS_PER_TOKEN)   # 2000
_TARGET_MAX_CHARS: int = int(_TARGET_MAX_TOKENS * _CHARS_PER_TOKEN)   # 3200
_OVERLAP_CHARS: int = int(_TARGET_MAX_CHARS * _OVERLAP_FRACTION)       # 640


@dataclass
class TextChunk:
    """A single text chunk ready for embedding."""

    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_estimate: int = field(init=False)

    def __post_init__(self) -> None:
        self.token_estimate = int(len(self.text) / _CHARS_PER_TOKEN)


class TextChunkingService:
    """
    Splits a document's extracted text into overlapping chunks.

    Usage::

        service = TextChunkingService()
        chunks = service.chunk(extracted_text)

    The algorithm:

    1. Split the full text into paragraphs (double newline boundaries).
    2. Accumulate paragraphs into a buffer until it reaches the max char
       target or runs out of paragraphs.
    3. Slide forward by (chunk_size - overlap) characters, re-anchoring on
       the nearest paragraph boundary to avoid mid-paragraph splits.
    4. Yield each chunk as a :class:`TextChunk`.
    """

    def chunk(self, text: str) -> list[TextChunk]:
        """
        Chunk *text* into overlapping segments.

        Args:
            text: The full extracted document text.

        Returns:
            Ordered list of :class:`TextChunk` objects.

        Raises:
            ValueError: If *text* is empty or None.
        """
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty or whitespace-only text.")

        paragraphs = self._split_paragraphs(text)
        chunks: list[TextChunk] = []
        chunk_index = 0

        # Build chunks by accumulating paragraphs
        start_para_idx = 0
        while start_para_idx < len(paragraphs):
            buffer_paras, end_para_idx = self._collect_paragraphs(
                paragraphs, start_para_idx
            )
            if not buffer_paras:
                break

            chunk_text = "\n\n".join(buffer_paras)
            char_start = self._char_offset(paragraphs, start_para_idx)
            char_end = char_start + len(chunk_text)

            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    text=chunk_text,
                    char_start=char_start,
                    char_end=char_end,
                )
            )
            chunk_index += 1

            # Advance start by finding the paragraph that begins after the
            # overlap window.  We slide forward by (max_chars - overlap).
            advance_chars = _TARGET_MAX_CHARS - _OVERLAP_CHARS
            advanced_start = self._find_para_after_offset(
                paragraphs, start_para_idx, char_start + advance_chars
            )
            if advanced_start <= start_para_idx:
                # Safety: always advance at least one paragraph to prevent loops
                advanced_start = start_para_idx + len(buffer_paras)
            start_para_idx = advanced_start

        logger.info(
            "Chunked text (%d chars) into %d chunks (target %d-%d tokens each).",
            len(text),
            len(chunks),
            _TARGET_MIN_TOKENS,
            _TARGET_MAX_TOKENS,
        )
        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        """Split *text* on paragraph boundaries (2+ newlines)."""
        raw = re.split(r"\n{2,}", text)
        return [p.strip() for p in raw if p.strip()]

    @staticmethod
    def _collect_paragraphs(
        paragraphs: list[str], start: int
    ) -> tuple[list[str], int]:
        """
        Accumulate paragraphs from *start* until the buffer exceeds
        *_TARGET_MAX_CHARS* or all paragraphs are consumed.

        Returns:
            A tuple of (collected_paragraphs, next_start_index).
        """
        buffer: list[str] = []
        total_chars = 0
        idx = start

        while idx < len(paragraphs):
            para = paragraphs[idx]
            para_chars = len(para) + 2  # +2 for the "\n\n" join separator

            if buffer and total_chars + para_chars > _TARGET_MAX_CHARS:
                break

            buffer.append(para)
            total_chars += para_chars
            idx += 1

            # Stop if we have at least the minimum and next para would exceed max
            if total_chars >= _TARGET_MIN_CHARS:
                break

        return buffer, idx

    @staticmethod
    def _char_offset(paragraphs: list[str], up_to_idx: int) -> int:
        """Return the character offset of *paragraphs[up_to_idx]* in the
        reconstructed full text (joined with double newlines)."""
        offset = 0
        for i in range(up_to_idx):
            offset += len(paragraphs[i]) + 2  # +2 for "\n\n"
        return offset

    @staticmethod
    def _find_para_after_offset(
        paragraphs: list[str], start: int, target_offset: int
    ) -> int:
        """
        Find the index of the first paragraph whose character offset in the
        reconstructed text is >= *target_offset*.
        """
        running = 0
        for i, para in enumerate(paragraphs):
            if i < start:
                running += len(para) + 2
                continue
            if running >= target_offset:
                return i
            running += len(para) + 2
        return len(paragraphs)
