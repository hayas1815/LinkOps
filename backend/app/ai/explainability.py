"""
Explainability engine for AI Copilot (S5-M3).

Provides confidence level classification and extracts supporting evidence
(excerpts) from retrieved document chunks based on word overlap with generated answers.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any


class ConfidenceLevel(StrEnum):
    """
    Standard confidence categories based on vector similarity.
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def get_confidence_level(score: float) -> ConfidenceLevel:
    """
    Map numerical confidence score to a categorical level.

    Args:
        score: The vector similarity score (0.0 to 1.0).

    Returns:
        ConfidenceLevel enum value.
    """
    if score >= 0.85:
        return ConfidenceLevel.HIGH
    elif score >= 0.65:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def extract_supporting_excerpts(
    answer: str,
    chunks: list[Any],
    max_excerpts: int = 3,
) -> list[str]:
    """
    Identify and extract sentences from retrieved chunks that directly
    support the generated answer.

    Uses a word overlap heuristic (intersection of unique words) to rank
    the relevance of candidate sentences.

    Args:
        answer: The generated answer text.
        chunks: A list of SearchResultItem-like objects (must have `text` field).
        max_excerpts: The maximum number of supporting excerpts to return.

    Returns:
        A list of string sentences representing supporting evidence.
    """
    if not answer or not chunks:
        return []

    # Clean and tokenize answer words for overlap comparison
    answer_words = set(re.findall(r"\w+", answer.lower()))
    if not answer_words:
        return []

    candidate_sentences: list[tuple[str, float]] = []

    for chunk in chunks:
        # Split chunk into sentences (handling basic punctuation boundaries)
        sentences = re.split(r"(?<=[.!?])\s+", chunk.text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:  # skip extremely short sentences/fragments
                continue

            # Tokenize sentence words
            sentence_words = set(re.findall(r"\w+", sentence.lower()))
            if not sentence_words:
                continue

            # Calculate word overlap count
            overlap = len(answer_words & sentence_words)
            if overlap == 0:
                continue

            # Calculate Jaccard-like score to normalize by sentence length
            score = overlap / len(answer_words | sentence_words)
            candidate_sentences.append((sentence, score))

    # Sort candidates by score descending
    candidate_sentences.sort(key=lambda x: x[1], reverse=True)

    # De-duplicate sentences to maintain varied output
    seen = set()
    unique_excerpts = []
    for sentence, _ in candidate_sentences:
        if sentence not in seen:
            seen.add(sentence)
            unique_excerpts.append(sentence)
            if len(unique_excerpts) >= max_excerpts:
                break

    return unique_excerpts
