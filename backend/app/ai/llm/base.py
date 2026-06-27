"""
Abstract base class for LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract interface that all LLM providers (OpenAI, Ollama, Mocks) must implement.
    """

    @abstractmethod
    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """
        Asynchronously generate text completion for a given prompt.

        Args:
            prompt: The input user query or formatted prompt context.
            system_instruction: Optional system instruction/persona for the model.

        Returns:
            The generated text string from the model.
        """
        pass
