"""
Unit tests for the Explainability engine (S5-M3).
"""

from __future__ import annotations

import pytest
from app.ai.explainability import (
    ConfidenceLevel,
    get_confidence_level,
    extract_supporting_excerpts,
)


class TestExplainabilityEngine:
    """
    Tests for the explainability and confidence calculation helper functions.
    """

    def test_get_confidence_level_high(self):
        assert get_confidence_level(0.95) == ConfidenceLevel.HIGH
        assert get_confidence_level(0.85) == ConfidenceLevel.HIGH

    def test_get_confidence_level_medium(self):
        assert get_confidence_level(0.84) == ConfidenceLevel.MEDIUM
        assert get_confidence_level(0.65) == ConfidenceLevel.MEDIUM

    def test_get_confidence_level_low(self):
        assert get_confidence_level(0.64) == ConfidenceLevel.LOW
        assert get_confidence_level(0.30) == ConfidenceLevel.LOW

    def test_extract_supporting_excerpts_success(self):
        # Create a mock chunk class
        class MockChunk:
            def __init__(self, text: str):
                self.text = text

        chunks = [
            MockChunk("This is a guide for calibrating the centrifugal water pump. Ensure power is off."),
            MockChunk("Valves should be checked regularly. Piston settings are on page 5."),
        ]

        answer = "To calibrate the centrifugal water pump, first turn off the power supply."

        excerpts = extract_supporting_excerpts(answer, chunks)

        assert len(excerpts) > 0
        # The sentence containing "calibrating the centrifugal water pump" should be top match
        assert "calibrating the centrifugal water pump" in excerpts[0]
        # Should not include piston settings since it has low word overlap with answer
        assert not any("Piston settings" in e for e in excerpts)

    def test_extract_supporting_excerpts_no_overlap(self):
        class MockChunk:
            def __init__(self, text: str):
                self.text = text

        chunks = [MockChunk("Random details about safety goggles.")]
        answer = "Turn the valve key ninety degrees."

        excerpts = extract_supporting_excerpts(answer, chunks)
        assert len(excerpts) == 0
