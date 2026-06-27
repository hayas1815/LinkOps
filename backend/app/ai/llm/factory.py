"""
LLM Factory to retrieve configured LLM providers.
"""

from __future__ import annotations

import logging
from app.ai.llm.base import BaseLLMProvider
from app.ai.llm.openai_provider import OpenAIProvider
from app.ai.llm.ollama_provider import OllamaProvider
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider used when no remote LLM service is configured.
    Useful for testing and local dry-runs.
    """

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """
        Return a mock generated answer that reflects elements of the prompt context.
        """
        logger.info("Executing MockLLMProvider generation.")

        # Simple heuristic to extract context chunks to verify retrieval worked
        context_indicator = ""
        if "Context:" in prompt:
            # Try to grab some chunk text lines
            lines = prompt.split("\n")
            for line in lines:
                if line.startswith("- ") or line.startswith("[") or "Source:" in line:
                    context_indicator = line[:80] + "..."
                    break

        if context_indicator:
            return (
                f"This is a simulated RAG answer. Verified matching context: {context_indicator}. "
                "All operational systems are stable."
            )

        return "This is a simulated RAG answer. No active document context was detected in the prompt."


class LLMFactory:
    """
    Factory to construct LLM providers dynamically based on settings.
    """

    @staticmethod
    def get_provider() -> BaseLLMProvider:
        """
        Construct and return the configured LLM provider.

        Returns:
            An instance of BaseLLMProvider.
        """
        settings = get_settings()
        provider_name = (settings.future_ai_provider or "none").strip().lower()

        logger.info("Instantiating LLM provider for: %s", provider_name)

        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "ollama":
            return OllamaProvider()
        elif provider_name in ("none", "mock", ""):
            return MockLLMProvider()
        else:
            logger.warning(
                "Unknown LLM provider '%s' requested. Falling back to MockLLMProvider.",
                provider_name,
            )
            return MockLLMProvider()
