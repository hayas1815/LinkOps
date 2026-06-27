"""
Ollama LLM provider implementation using httpx.
"""

from __future__ import annotations

import logging
import httpx
from app.ai.llm.base import BaseLLMProvider
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    LLM provider for local Ollama API.
    """

    def __init__(self, endpoint: str | None = None, model: str | None = None) -> None:
        """
        Initialize the Ollama LLM provider.

        Args:
            endpoint: Optional base endpoint URL (defaults to http://localhost:11434).
            model: Optional model name (defaults to app settings or llama3).
        """
        settings = get_settings()
        self.endpoint = endpoint or "http://localhost:11434"
        self.model = model or settings.future_ai_model or "llama3"

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        """
        Asynchronously query local Ollama generate endpoint.
        """
        url = f"{self.endpoint}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
            }
        }
        if system_instruction:
            payload["system"] = system_instruction

        headers = {"Content-Type": "application/json"}
        logger.info("Sending generate request to Ollama endpoint: %s (model=%s)", url, self.model)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                answer: str = data["response"]
                return answer.strip()
            except httpx.HTTPStatusError as status_err:
                logger.error("Ollama API returned status error: %s - %s", response.status_code, response.text)
                raise RuntimeError(f"Ollama request failed: {status_err}") from status_err
            except Exception as exc:
                logger.error("Failed to query Ollama API: %s", exc)
                raise RuntimeError(f"Error querying Ollama: {exc}") from exc
