"""
Retrieval constants and helpers for the semantic search pipeline (S5-M1).

Centralises tuneable parameters so they can be adjusted without touching
the service or repository layers.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Default search parameters
# ---------------------------------------------------------------------------

#: Default number of results returned by semantic_search when top_k is not
#: explicitly specified.
DEFAULT_TOP_K: int = 5

#: Minimum cosine-similarity score required for a result to be included.
#: Set to 0.0 (no threshold) — callers may override per-request.
DEFAULT_MIN_SIMILARITY_SCORE: float = 0.0

#: Hard upper limit on top_k to prevent runaway queries.
MAX_TOP_K: int = 50
