"""
Claude Client — thin adapter over the Anthropic SDK.

Responsibilities:
  1. Accept a system prompt and a messages list.
  2. Call the Anthropic Messages API with the model/temperature/max_tokens
     from ``Settings``.
  3. Return a typed response or raise a domain-specific error.
  4. Handle retries, timeouts, and rate-limit back-off.

This module is the **only** file that imports ``anthropic``.
All other modules interact with the LLM through this adapter.

NOTE: Implementation is deferred.  The class below defines the full public
interface but raises ``NotImplementedError`` in every method body.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LLMResponse:
    """Standardised response from any LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


class BaseLLMClient(ABC):
    """
    Provider-agnostic interface for LLM calls.

    Concrete implementations (Claude, OpenAI, local) must satisfy this
    contract so the rest of the codebase never couples to a single vendor.
    """

    @abstractmethod
    async def complete(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Send a completion request and return the response."""
        ...


class ClaudeClient(BaseLLMClient):
    """
    Anthropic Claude adapter.

    Requires:
      - ``anthropic`` package (pip install anthropic)
      - ``ANTHROPIC_API_KEY`` in environment / Settings

    Will be implemented when AI Copilot is activated.
    """

    def __init__(self, api_key: str, model: str, default_max_tokens: int, default_temperature: float, timeout: int) -> None:
        self._api_key = api_key
        self._model = model
        self._default_max_tokens = default_max_tokens
        self._default_temperature = default_temperature
        self._timeout = timeout
        # self._client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)

    async def complete(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Placeholder — will call Anthropic Messages API."""
        raise NotImplementedError(
            "ClaudeClient.complete() is not yet implemented. "
            "Install the anthropic SDK and provide ANTHROPIC_API_KEY to activate."
        )
