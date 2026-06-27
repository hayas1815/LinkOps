"""
OpenAI LLM provider implementation using httpx.
"""

from __future__ import annotations

import logging
import httpx
from app.ai.llm.base import BaseLLMProvider
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    LLM provider for OpenAI Chat Completion API.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """
        Initialize the OpenAI LLM provider.

        Args:
            api_key: Optional OpenAI API key (falls back to app settings).
            model: Optional model name (falls back to app settings).
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.future_ai_model or "gpt-4o"

        if not self.api_key:
            logger.warning("OpenAI API key is missing. Requests to OpenAIProvider will fail.")

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """
        Asynchronously query the OpenAI Chat Completion API.
        """
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
        }

        url = "https://api.openai.com/v1/chat/completions"
        logger.info("Sending chat completion request to OpenAI using model %s", self.model)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                answer: str = data["choices"][0]["message"]["content"]
                return answer.strip()
            except httpx.HTTPStatusError as status_err:
                logger.error("OpenAI API returned status error: %s - %s", response.status_code, response.text)
                raise RuntimeError(f"OpenAI API request failed: {status_err}") from status_err
            except Exception as exc:
                logger.error("Failed to call OpenAI API: %s", exc)
                raise RuntimeError(f"Error querying OpenAI: {exc}") from exc
