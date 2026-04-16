"""
ContentGenerator — Interfaces with EuriAI to produce human-readable
text outputs and documentation.

Includes retry logic with exponential backoff and response caching.
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.exceptions import APIAuthenticationError, APIRateLimitError, GenerationError
from app.core.logging import get_logger

logger = get_logger("ContentGenerator")


class ContentGenerator:
    """
    AI content generation engine.

    Uses EuriAI (gpt-4.1-nano) as the LLM backend.
    Includes caching to minimize API usage and costs.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._client = None

    def _init_client(self):
        """Lazily initialize the EuriAI client."""
        if self._client is None:
            if not settings.euri_api_key:
                raise APIAuthenticationError(
                    "EURI_API_KEY is not set. Add it to your .env file."
                )
            try:
                from euriai import EuriaiClient

                self._client = EuriaiClient(
                    api_key=settings.euri_api_key,
                    model=settings.euri_model,
                )
                logger.info(
                    f"EuriAI client initialized (model={settings.euri_model})"
                )
            except ImportError:
                raise GenerationError(
                    "euriai package not installed. Run: pip install euriai"
                )

    def _cache_key(self, prompt: str) -> str:
        """Generate a cache key from the prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()

    async def generate_text(
        self,
        prompt: str,
        use_cache: bool = True,
    ) -> str:
        """
        Generate text using the EuriAI backend.

        Args:
            prompt: The input prompt.
            use_cache: Whether to use cached responses.

        Returns:
            Generated text string.
        """
        # Check cache
        cache_key = self._cache_key(prompt)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached response")
            return self._cache[cache_key]

        # Generate via EuriAI
        result = await self._generate_euri(prompt)

        # Cache result
        self._cache[cache_key] = result
        return result

    async def _generate_euri(self, prompt: str) -> str:
        """Generate text using EuriAI with retry logic."""
        self._init_client()

        for attempt in range(settings.euri_retry_attempts):
            try:
                # EuriAI client is synchronous — run in thread pool
                response = await asyncio.to_thread(
                    self._client.generate_completion,
                    prompt=prompt,
                    temperature=settings.euri_temperature,
                    max_tokens=settings.euri_max_tokens,
                )
                return response["choices"][0]["message"]["content"]

            except Exception as e:
                error_str = str(e).lower()
                if "rate_limit" in error_str or "429" in error_str:
                    wait = settings.euri_retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Rate limited — retrying in {wait}s (attempt {attempt + 1})"
                    )
                    await asyncio.sleep(wait)
                    if attempt == settings.euri_retry_attempts - 1:
                        raise APIRateLimitError(
                            f"Rate limit exceeded after {attempt + 1} retries"
                        )
                elif "auth" in error_str or "401" in error_str:
                    raise APIAuthenticationError(f"Authentication failed: {e}")
                else:
                    raise GenerationError(f"EuriAI API error: {e}")

        raise GenerationError("Max retries exceeded")

    async def summarize(self, data: Dict[str, Any], context: str = "") -> str:
        """
        Generate a summary of structured data.

        Args:
            data: The data to summarize.
            context: Additional context for the summary.

        Returns:
            A human-readable summary string.
        """
        prompt = f"""You are a professional banking operations assistant.
Summarize the following data concisely and professionally:

Context: {context}

Data:
{json.dumps(data, indent=2, default=str)}

Provide a clear, concise summary in 2-3 paragraphs."""

        return await self.generate_text(prompt)

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Cache cleared")
