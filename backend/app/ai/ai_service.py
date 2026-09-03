"""
AI Service — orchestration layer for all AI operations.

This is the **only entry point** that the FastAPI endpoint layer calls.
It coordinates:
  1. ContextBuilder  → gathers domain data
  2. PromptBuilder   → renders the prompt template
  3. BaseLLMClient   → calls the LLM  (via ``generate()``)
  4. Cache           → checks / stores cached responses

**Key rule:** This module NEVER imports a concrete LLM client (GeminiClient,
ClaudeClient, etc.).  It depends exclusively on ``BaseLLMClient`` and
receives a concrete instance via dependency injection or the
``create_llm_client()`` factory.

Until a provider is configured, every public method returns a deterministic
placeholder response.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from backend.app.ai.llm_client import BaseLLMClient


@dataclass(frozen=True)
class ExplanationResult:
    """Returned by ``explain_exception``."""

    explanation: str
    confidence: str  # "high" | "medium" | "low"
    suggested_actions: List[str]
    source: str  # "llm" | "cache" | "placeholder"


@dataclass(frozen=True)
class ChatResult:
    """Returned by ``chat``."""

    reply: str
    suggested_questions: List[str]
    source: str


@dataclass(frozen=True)
class ReportSummaryResult:
    """Returned by ``summarize_report``."""

    summary: str
    key_findings: List[str]
    source: str


class AIService:
    """
    Facade consumed by ``backend.app.api.v1.ai``.

    Accepts an optional ``BaseLLMClient``.  When one is provided, the
    service will use ``client.generate()`` for all LLM calls.  When
    ``None`` (the default), every method returns a placeholder.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self._llm = llm_client

    @property
    def is_active(self) -> bool:
        """True when a real LLM client has been injected."""
        return self._llm is not None

    # ------------------------------------------------------------------
    # Exception explanation
    # ------------------------------------------------------------------

    async def explain_exception(self, exception_id: str) -> ExplanationResult:
        """Generate a natural-language explanation for a reconciliation exception."""
        # TODO: when self._llm is set, call:
        #   context  = await context_builder.build_exception_context(exception_id)
        #   messages = prompt_builder.build_exception_messages(context)
        #   response = await self._llm.generate(system=..., messages=messages)
        return ExplanationResult(
            explanation=(
                f"Exception {exception_id}: This is a placeholder explanation. "
                "Connect an LLM provider to receive AI-powered analysis of this "
                "exception, including root cause identification and recommended "
                "resolution steps."
            ),
            confidence="low",
            suggested_actions=[
                "Review the original transaction records",
                "Compare bank and gateway amounts",
                "Check for processing fee deductions",
            ],
            source="placeholder",
        )

    # ------------------------------------------------------------------
    # Conversational chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        run_id: Optional[str] = None,
    ) -> ChatResult:
        """Handle a free-form chat message from the AI Assistant page."""
        # TODO: when self._llm is set, call self._llm.generate()
        return ChatResult(
            reply=(
                "I'm currently in placeholder mode. Once an LLM provider is "
                "connected, I'll be able to answer questions about your "
                "reconciliation data, explain specific exceptions, and suggest "
                "resolution strategies."
            ),
            suggested_questions=[
                "What caused exception EX-1001?",
                "Summarise today's reconciliation results",
                "Which exceptions should I prioritise?",
            ],
            source="placeholder",
        )

    # ------------------------------------------------------------------
    # Report summarisation
    # ------------------------------------------------------------------

    async def summarize_report(self, run_id: str) -> ReportSummaryResult:
        """Generate a natural-language summary of a reconciliation report."""
        # TODO: when self._llm is set, call self._llm.generate()
        return ReportSummaryResult(
            summary=(
                f"Report for run {run_id}: This is a placeholder summary. "
                "Connect an LLM provider to receive an AI-generated executive "
                "summary covering match rates, exception trends, and "
                "recommended actions."
            ),
            key_findings=[
                "Placeholder finding 1",
                "Placeholder finding 2",
            ],
            source="placeholder",
        )
