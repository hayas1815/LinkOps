"""
Unit tests for Search module schemas (S5-M1).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.search.schemas import SearchRequest


class TestSearchRequestSchema:
    """
    Tests for validation rules in the SearchRequest schema.
    """

    def test_valid_search_request(self):
        req = SearchRequest(query="pump manual", top_k=5)
        assert req.query == "pump manual"
        assert req.top_k == 5

    def test_whitespace_only_query_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc:
            SearchRequest(query="   \n   ", top_k=5)
        assert "Query string cannot be empty or whitespace only" in str(exc.value)

    def test_empty_query_raises_validation_error(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="", top_k=5)

    def test_query_too_long_raises_validation_error(self):
        long_query = "x" * 2001
        with pytest.raises(ValidationError):
            SearchRequest(query=long_query, top_k=5)

    def test_top_k_below_min_raises_validation_error(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="pump", top_k=0)

    def test_top_k_above_max_raises_validation_error(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="pump", top_k=51)
