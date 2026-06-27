"""
Unit tests for the AI services layer (S4-M4):
  - TextChunkingService  (app.ai.chunking)
  - EmbeddingService     (app.ai.embeddings)
"""

from __future__ import annotations

import pytest

from app.ai.chunking import TextChunk, TextChunkingService, _CHARS_PER_TOKEN


# ---------------------------------------------------------------------------
# TextChunkingService
# ---------------------------------------------------------------------------


class TestTextChunkingService:
    """Tests for paragraph-aware text chunking with overlap."""

    def setup_method(self):
        self.service = TextChunkingService()

    def test_raises_on_empty_text(self):
        with pytest.raises(ValueError, match="empty"):
            self.service.chunk("")

    def test_raises_on_whitespace_only(self):
        with pytest.raises(ValueError, match="empty"):
            self.service.chunk("   \n\n   ")

    def test_single_paragraph_returns_one_chunk(self):
        text = "Hello world. " * 50  # short text, one paragraph
        chunks = self.service.chunk(text)
        assert len(chunks) >= 1
        assert chunks[0].chunk_index == 0

    def test_chunk_indices_are_sequential(self):
        """chunk_index values must form a 0-based contiguous sequence."""
        # Build multi-paragraph text big enough for multiple chunks
        para = ("word " * 200 + "\n\n")
        text = para * 20
        chunks = self.service.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_chunk_text_is_non_empty(self):
        para = ("word " * 200 + "\n\n")
        text = para * 10
        chunks = self.service.chunk(text)
        for chunk in chunks:
            assert chunk.text.strip()

    def test_token_estimate_is_positive(self):
        chunks = self.service.chunk("Hello world " * 500)
        for chunk in chunks:
            assert chunk.token_estimate > 0

    def test_token_estimate_equals_chars_divided_by_ratio(self):
        text = "Hello world " * 500
        chunks = self.service.chunk(text)
        for chunk in chunks:
            expected = int(len(chunk.text) / _CHARS_PER_TOKEN)
            assert chunk.token_estimate == expected

    def test_overlap_causes_later_chunks_to_repeat_content(self):
        """Consecutive chunks should share some content due to overlap."""
        # Build a multi-paragraph text large enough for at least 2 chunks
        para = ("overlap_test " * 300 + "\n\n")
        text = para * 15
        chunks = self.service.chunk(text)
        if len(chunks) < 2:
            pytest.skip("Text too short to produce multiple chunks")

        # The end of chunk[0] and the start of chunk[1] should share words
        end_words = set(chunks[0].text.split()[-50:])
        start_words = set(chunks[1].text.split()[:50])
        overlap = end_words & start_words
        assert len(overlap) > 0, "Expected some token overlap between consecutive chunks"

    def test_char_start_and_end_are_ordered(self):
        para = ("word " * 200 + "\n\n")
        text = para * 10
        chunks = self.service.chunk(text)
        for chunk in chunks:
            assert chunk.char_start <= chunk.char_end

    def test_returns_list_of_text_chunk_instances(self):
        text = "Hello world " * 500
        chunks = self.service.chunk(text)
        assert isinstance(chunks, list)
        for chunk in chunks:
            assert isinstance(chunk, TextChunk)


# ---------------------------------------------------------------------------
# TextChunk dataclass
# ---------------------------------------------------------------------------


class TestTextChunk:
    def test_token_estimate_auto_computed(self):
        chunk = TextChunk(chunk_index=0, text="Hello world!", char_start=0, char_end=12)
        assert chunk.token_estimate == int(len("Hello world!") / _CHARS_PER_TOKEN)

    def test_fields_accessible(self):
        chunk = TextChunk(chunk_index=3, text="abc", char_start=10, char_end=13)
        assert chunk.chunk_index == 3
        assert chunk.text == "abc"
        assert chunk.char_start == 10
        assert chunk.char_end == 13


# ---------------------------------------------------------------------------
# EmbeddingService (model loading is mocked to avoid downloading weights)
# ---------------------------------------------------------------------------


class TestEmbeddingService:
    """Unit tests for EmbeddingService using a mocked SentenceTransformer."""

    def _make_service_with_mock_model(self, mock_encode_fn):
        """Return an EmbeddingService whose internal model is pre-set to a mock."""
        from unittest.mock import MagicMock
        from app.ai.embeddings import EmbeddingService

        service = EmbeddingService()
        mock_model = MagicMock()
        mock_model.encode.side_effect = mock_encode_fn
        service._model = mock_model
        return service

    def test_embed_chunks_returns_correct_length(self):
        import numpy as np
        from app.ai.chunking import TextChunk

        chunks = [
            TextChunk(chunk_index=0, text="chunk one", char_start=0, char_end=9),
            TextChunk(chunk_index=1, text="chunk two", char_start=11, char_end=20),
        ]

        def fake_encode(texts, **kwargs):
            return np.zeros((len(texts), 384), dtype=np.float32)

        service = self._make_service_with_mock_model(fake_encode)
        result = service.embed_chunks(chunks)

        assert len(result) == 2

    def test_embed_chunks_returns_384_dim_vectors(self):
        import numpy as np
        from app.ai.chunking import TextChunk

        chunks = [TextChunk(chunk_index=0, text="test text", char_start=0, char_end=9)]

        def fake_encode(texts, **kwargs):
            return np.zeros((len(texts), 384), dtype=np.float32)

        service = self._make_service_with_mock_model(fake_encode)
        result = service.embed_chunks(chunks)

        assert len(result[0]) == 384

    def test_embed_chunks_returns_lists_of_floats(self):
        import numpy as np
        from app.ai.chunking import TextChunk

        chunks = [TextChunk(chunk_index=0, text="hello", char_start=0, char_end=5)]

        def fake_encode(texts, **kwargs):
            return np.ones((len(texts), 384), dtype=np.float32)

        service = self._make_service_with_mock_model(fake_encode)
        result = service.embed_chunks(chunks)

        assert isinstance(result[0], list)
        assert isinstance(result[0][0], float)

    def test_embed_chunks_raises_on_empty_list(self):
        from app.ai.embeddings import EmbeddingService

        service = EmbeddingService()
        with pytest.raises(ValueError, match="empty"):
            service.embed_chunks([])

    def test_embed_query_raises_on_empty_string(self):
        from app.ai.embeddings import EmbeddingService

        service = EmbeddingService()
        with pytest.raises(ValueError, match="empty"):
            service.embed_query("")

    def test_embed_query_returns_384_dim_vector(self):
        import numpy as np

        def fake_encode(texts, **kwargs):
            return np.ones((len(texts), 384), dtype=np.float32)

        service = self._make_service_with_mock_model(fake_encode)
        result = service.embed_query("What is the pump flow rate?")

        assert isinstance(result, list)
        assert len(result) == 384
