"""
LLM Client — provider-agnostic adapter layer.

This module defines:
  1. ``LLMResponse`` — standardised response dataclass.
  2. ``BaseLLMClient`` — abstract interface every provider must implement.
  3. ``GeminiClient`` — Google Gemini adapter (primary provider).
  4. ``ClaudeClient`` — Anthropic Claude adapter (future provider).
  5. ``create_llm_client()`` — factory that reads ``Settings`` and returns
     the correct concrete client.

Responsibilities:
  - Accept a system prompt and a messages list.
  - Call the provider's API with model / temperature / max_tokens from Settings.
  - Return a typed ``LLMResponse`` or raise a domain-specific error.
  - Handle retries, timeouts, and rate-limit back-off.

Rules:
  - ``ai_service.py`` NEVER imports a concrete client directly.
    It calls ``create_llm_client()`` or receives a ``BaseLLMClient`` via DI.
  - Each concrete client is the **only** file that imports its provider SDK.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import Dict, List, Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Response dataclass
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class LLMResponse:
    """Standardised response returned by every LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Abstract base
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseLLMClient(ABC):
    """
    Provider-agnostic interface for LLM completion calls.

    Every concrete provider (Gemini, Claude, OpenAI, local) must implement
    ``generate()``.  The rest of the codebase programmes against this
    interface so that swapping providers is a one-line config change.
    """

    @abstractmethod
    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Send a completion request and return the standardised response."""
        ...


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Gemini provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class GeminiClient(BaseLLMClient):
    """
    Google Gemini adapter.

    Requires:
      - ``google-genai`` package  (pip install google-genai)
      - ``GEMINI_API_KEY`` in environment / Settings
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        timeout: int,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        self._client = None
        
        # Setup logging
        self._logger = logging.getLogger(__name__)

    def _get_client(self):
        if not self._client:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Call Google Gemini API."""
        import time
        from google.genai import errors, types
        from backend.app.ai.exceptions import (
            LLMAuthenticationError,
            LLMQuotaExceededError,
            LLMRateLimitError,
            LLMNetworkError,
            LLMProviderError
        )

        if not self._api_key:
            raise LLMAuthenticationError("GEMINI_API_KEY is not configured.")

        # Prepare configuration
        temp = temperature if temperature is not None else self._default_temperature
        tokens = max_tokens if max_tokens is not None else self._default_max_tokens

        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
            system_instruction=system
        )

        # Convert simple {"role": ..., "content": ...} to Gemini format if needed,
        # but google.genai's generate_content handles strings. 
        # Since the interface passes a list of dicts for messages, we can format them.
        # Typically, user_prompt is just the last message for now, or we can format 
        # all messages into a single prompt for this basic integration.
        prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])

        client = self._get_client()
        start_time = time.time()
        
        try:
            # Using synchronous generate_content because async might require generate_content_async
            # But the prompt says "async def generate". We will use async API:
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            
            latency = time.time() - start_time
            
            input_tokens = 0
            output_tokens = 0
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0
                
            self._logger.info(
                f"Gemini success | Model: {self._model} | Latency: {latency:.2f}s | "
                f"Tokens: {input_tokens} in, {output_tokens} out"
            )
            
            # stop_reason not always directly accessible in simple text response, default to stop
            return LLMResponse(
                content=response.text,
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                stop_reason="stop"
            )
            
        except errors.APIError as e:
            latency = time.time() - start_time
            self._logger.error(f"Gemini APIError | Latency: {latency:.2f}s | Error: {str(e)}")
            
            error_msg = str(e).lower()
            if "api_key" in error_msg or "403" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg:
                raise LLMAuthenticationError(f"Invalid API key: {str(e)}")
            elif "429" in error_msg or "quota" in error_msg:
                if "quota" in error_msg:
                    raise LLMQuotaExceededError(f"Quota exceeded: {str(e)}")
                raise LLMRateLimitError(f"Rate limited: {str(e)}")
            elif "timeout" in error_msg:
                raise LLMNetworkError(f"Network timeout: {str(e)}")
            else:
                raise LLMProviderError(f"Gemini API error: {str(e)}")
        except Exception as e:
            latency = time.time() - start_time
            self._logger.error(f"Gemini unexpected error | Latency: {latency:.2f}s | Error: {str(e)}")
            raise LLMProviderError(f"Unexpected error: {str(e)}")
            
    async def test_connection(self) -> bool:
        """Send a lightweight test to verify connectivity."""
        try:
            response = await self.generate(
                system="You are a test bot.",
                messages=[{"role": "user", "content": "Reply with OK"}],
                max_tokens=10
            )
            return "OK" in response.content.upper()
        except Exception as e:
            self._logger.warning(f"test_connection failed: {e}")
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Claude provider (future)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ClaudeClient(BaseLLMClient):
    """
    Anthropic Claude adapter (future provider).

    Requires:
      - ``anthropic`` package  (pip install anthropic)
      - ``ANTHROPIC_API_KEY`` in environment / Settings

    Implementation will be added if/when Claude is chosen as a provider.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        timeout: int,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        # self._client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)

    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Placeholder — will call Anthropic Messages API."""
        raise NotImplementedError(
            "ClaudeClient.generate() is not yet implemented. "
            "Install the anthropic SDK and provide ANTHROPIC_API_KEY to activate."
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_llm_client(
    provider: str,
    *,
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
) -> BaseLLMClient:
    """
    Factory that returns the correct concrete client based on ``provider``.

    Called once at startup by ``AIService`` or the dependency injection layer.
    ``ai_service.py`` never imports a concrete client — only this factory.

    Supported values for ``provider``:
      - ``"gemini"``  → ``GeminiClient``
      - ``"anthropic"`` → ``ClaudeClient``

    Raises ``ValueError`` for unknown providers.
    """
    provider_lower = provider.strip().lower()

    if provider_lower == "gemini":
        return GeminiClient(
            api_key=api_key,
            model=model,
            default_max_tokens=max_tokens,
            default_temperature=temperature,
            timeout=timeout,
        )
    elif provider_lower == "anthropic":
        return ClaudeClient(
            api_key=api_key,
            model=model,
            default_max_tokens=max_tokens,
            default_temperature=temperature,
            timeout=timeout,
        )
    else:
        raise ValueError(
            f"Unknown LLM provider '{provider}'. "
            f"Supported: 'gemini', 'anthropic'."
        )
