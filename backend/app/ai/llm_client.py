"""
LLM Client — provider-agnostic multi-provider adapter layer with automatic fallback.

This module defines:
  1. ``LLMResponse`` — standardised response dataclass.
  2. ``BaseLLMClient`` — abstract interface every provider must implement.
  3. ``GeminiClient`` — Google Gemini adapter.
  4. ``GroqClient`` — Groq API adapter.
  5. ``OpenRouterClient`` — OpenRouter API adapter.
  6. ``FallbackLLMClient`` — automatic fallback chain wrapper.
  7. ``create_llm_client()`` — factory that builds provider fallback chain.
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
    provider: str = ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Abstract base
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseLLMClient(ABC):
    """Provider-agnostic interface for LLM completion calls."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier name."""
        ...

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
    """Google Gemini adapter."""

    def __init__(
        self,
        api_key: str,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        timeout: int,
    ) -> None:
        self._api_key = api_key
        self._model = model or "gemini-2.5-flash"
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        self._client = None
        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "Gemini"

    @property
    def model_name(self) -> str:
        return self._model

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
        import time
        from google.genai import errors, types
        from backend.app.ai.exceptions import (
            LLMAuthenticationError,
            LLMQuotaExceededError,
            LLMRateLimitError,
            LLMNetworkError,
            LLMProviderError,
        )

        if not self._api_key or self._api_key.startswith("your_"):
            raise LLMAuthenticationError("Gemini API key missing or invalid.")

        temp = temperature if temperature is not None else self._default_temperature
        tokens = max_tokens if max_tokens is not None else self._default_max_tokens

        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
            system_instruction=system
        )

        prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])

        client = self._get_client()
        start_time = time.time()

        try:
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            input_tokens = 0
            output_tokens = 0
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            return LLMResponse(
                content=response.text,
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                stop_reason="stop",
                provider="Gemini"
            )

        except errors.APIError as e:
            error_msg = str(e).lower()
            if "api_key" in error_msg or "403" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg:
                raise LLMAuthenticationError(f"Invalid API key: {str(e)}")
            elif "429" in error_msg or "quota" in error_msg or "unavailable" in error_msg:
                if "quota" in error_msg:
                    raise LLMQuotaExceededError(f"Quota exceeded: {str(e)}")
                raise LLMRateLimitError(f"Rate limited or unavailable: {str(e)}")
            elif "timeout" in error_msg:
                raise LLMNetworkError(f"Network timeout: {str(e)}")
            else:
                raise LLMProviderError(f"Gemini API error: {str(e)}")
        except Exception as e:
            raise LLMProviderError(f"Unexpected Gemini error: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Groq provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class GroqClient(BaseLLMClient):
    """Groq API adapter via OpenAI-compatible REST API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        timeout: int,
    ) -> None:
        self._api_key = api_key
        self._model = model or "llama-3.3-70b-versatile"
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "Groq"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        import time
        import httpx
        from backend.app.ai.exceptions import (
            LLMAuthenticationError,
            LLMQuotaExceededError,
            LLMRateLimitError,
            LLMNetworkError,
            LLMProviderError,
        )

        if not self._api_key or self._api_key.startswith("your_"):
            raise LLMAuthenticationError("Groq API key missing or invalid.")

        temp = temperature if temperature is not None else self._default_temperature
        tokens = max_tokens if max_tokens is not None else self._default_max_tokens

        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        for msg in messages:
            role = msg.get("role", "user")
            if role not in ["system", "user", "assistant"]:
                role = "user"
            formatted_messages.append({"role": role, "content": msg.get("content", "")})

        payload = {
            "model": self._model,
            "messages": formatted_messages,
            "temperature": temp,
            "max_tokens": tokens,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=float(self._timeout)) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )

            if resp.status_code == 401 or resp.status_code == 403:
                raise LLMAuthenticationError(f"Groq auth error ({resp.status_code}): {resp.text}")
            elif resp.status_code == 429:
                if "quota" in resp.text.lower():
                    raise LLMQuotaExceededError(f"Groq quota exceeded: {resp.text}")
                raise LLMRateLimitError(f"Groq rate limit: {resp.text}")
            elif resp.status_code >= 400:
                raise LLMProviderError(f"Groq API error ({resp.status_code}): {resp.text}")

            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            stop_reason = choice.get("finish_reason", "stop")

            return LLMResponse(
                content=content,
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                stop_reason=stop_reason,
                provider="Groq"
            )
        except (LLMAuthenticationError, LLMQuotaExceededError, LLMRateLimitError, LLMProviderError):
            raise
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            raise LLMNetworkError(f"Groq network error: {str(e)}")
        except Exception as e:
            raise LLMProviderError(f"Groq unexpected error: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OpenRouter provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OpenRouterClient(BaseLLMClient):
    """OpenRouter API adapter via OpenAI-compatible REST API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        timeout: int,
    ) -> None:
        self._api_key = api_key
        self._model = model or "meta-llama/llama-3.3-70b-instruct"
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "OpenRouter"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        import time
        import httpx
        from backend.app.ai.exceptions import (
            LLMAuthenticationError,
            LLMQuotaExceededError,
            LLMRateLimitError,
            LLMNetworkError,
            LLMProviderError,
        )

        if not self._api_key or self._api_key.startswith("your_"):
            raise LLMAuthenticationError("OpenRouter API key missing or invalid.")

        temp = temperature if temperature is not None else self._default_temperature
        tokens = max_tokens if max_tokens is not None else self._default_max_tokens

        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        for msg in messages:
            role = msg.get("role", "user")
            if role not in ["system", "user", "assistant"]:
                role = "user"
            formatted_messages.append({"role": role, "content": msg.get("content", "")})

        payload = {
            "model": self._model,
            "messages": formatted_messages,
            "temperature": temp,
            "max_tokens": tokens,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://financepilot.ai",
            "X-Title": "FinancePilot AI",
            "Content-Type": "application/json",
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=float(self._timeout)) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )

            if resp.status_code == 401 or resp.status_code == 403:
                raise LLMAuthenticationError(f"OpenRouter auth error ({resp.status_code}): {resp.text}")
            elif resp.status_code == 429:
                if "quota" in resp.text.lower():
                    raise LLMQuotaExceededError(f"OpenRouter quota exceeded: {resp.text}")
                raise LLMRateLimitError(f"OpenRouter rate limit: {resp.text}")
            elif resp.status_code >= 400:
                raise LLMProviderError(f"OpenRouter API error ({resp.status_code}): {resp.text}")

            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            stop_reason = choice.get("finish_reason", "stop")

            return LLMResponse(
                content=content,
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                stop_reason=stop_reason,
                provider="OpenRouter"
            )
        except (LLMAuthenticationError, LLMQuotaExceededError, LLMRateLimitError, LLMProviderError):
            raise
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            raise LLMNetworkError(f"OpenRouter network error: {str(e)}")
        except Exception as e:
            raise LLMProviderError(f"OpenRouter unexpected error: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi-Provider Fallback Wrapper
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FallbackLLMClient(BaseLLMClient):
    """
    Multi-provider LLM client with automatic fallback.

    Iterates through a chain of primary and fallback providers.
    Returns the first successful LLMResponse.
    Logs structured information including latency, tokens, and fallback usage.
    """

    def __init__(self, clients: List[BaseLLMClient]) -> None:
        if not clients:
            raise ValueError("FallbackLLMClient requires at least one provider client.")
        self._clients = clients
        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return self._clients[0].name

    @property
    def model_name(self) -> str:
        return self._clients[0].model_name

    async def generate(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        import time
        from backend.app.ai.exceptions import LLMProviderError

        last_exception = None
        attempt = 0

        for i, client in enumerate(self._clients):
            attempt += 1
            start_time = time.time()
            fallback_used = "Yes" if i > 0 else "No"
            try:
                response = await client.generate(
                    system=system,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                latency_ms = int((time.time() - start_time) * 1000)

                log_msg = (
                    f"\n--- LLM Completion Success ---\n"
                    f"Provider: {client.name}\n"
                    f"Model: {client.model_name}\n"
                    f"Latency: {latency_ms}ms\n"
                    f"Prompt Tokens: {response.input_tokens}\n"
                    f"Completion Tokens: {response.output_tokens}\n"
                    f"Retry Count: {attempt - 1}\n"
                    f"Fallback Used: {fallback_used}\n"
                    f"-------------------------------"
                )
                print(log_msg)
                self._logger.info(log_msg)

                return response

            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                last_exception = e
                err_log = (
                    f"Provider {client.name} (Model: {client.model_name}) failed after {latency_ms}ms: {str(e)}. "
                )
                if i < len(self._clients) - 1:
                    err_log += f"Falling back to {self._clients[i+1].name}..."
                else:
                    err_log += "All providers in fallback chain failed."
                print(f"[LLM Fallback Warning] {err_log}")
                self._logger.warning(err_log)

        if last_exception:
            raise last_exception
        raise LLMProviderError("All LLM providers failed in fallback chain.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_llm_client(
    provider: str,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    timeout: Optional[int] = None,
) -> BaseLLMClient:
    """
    Factory that initializes concrete provider clients and wraps them in
    a FallbackLLMClient chain according to LLM_PROVIDER and fallback order.
    """
    from backend.app.core.config import settings

    prov = (provider or settings.LLM_PROVIDER).strip().lower()

    m_tokens = max_tokens if max_tokens is not None else settings.MAX_TOKENS
    temp = temperature if temperature is not None else settings.TEMPERATURE
    t_out = timeout if timeout is not None else settings.TIMEOUT

    groq_c = GroqClient(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        default_max_tokens=m_tokens,
        default_temperature=temp,
        timeout=t_out,
    )

    openrouter_c = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY,
        model=settings.OPENROUTER_MODEL,
        default_max_tokens=m_tokens,
        default_temperature=temp,
        timeout=t_out,
    )

    gemini_c = GeminiClient(
        api_key=settings.GEMINI_API_KEY or api_key or "",
        model=settings.GEMINI_MODEL if not model or model == settings.GEMINI_MODEL else model,
        default_max_tokens=m_tokens,
        default_temperature=temp,
        timeout=t_out,
    )

    if prov == "groq":
        chain = [groq_c, openrouter_c, gemini_c]
    elif prov == "openrouter":
        chain = [openrouter_c, gemini_c, groq_c]
    elif prov == "gemini":
        chain = [gemini_c, groq_c, openrouter_c]
    else:
        chain = [groq_c, openrouter_c, gemini_c]

    return FallbackLLMClient(chain)
