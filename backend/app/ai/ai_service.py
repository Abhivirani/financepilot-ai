"""
AI Service — orchestration layer for all AI operations.

This is the **only entry point** that the FastAPI endpoint layer calls.
It coordinates:
  1. ContextBuilder  → gathers domain data
  2. PromptBuilder   → renders the prompt template
  3. ClaudeClient    → calls the LLM
  4. Cache           → checks / stores cached responses

By keeping this as a thin orchestrator, each sub-component stays
independently testable.

NOTE: Until the Claude integration is activated, every public method
returns a deterministic placeholder response.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


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

    When Claude is connected, inject a real ContextBuilder, PromptBuilder,
    and ClaudeClient.  Until then, every method returns a placeholder.
    """

    # ------------------------------------------------------------------
    # Exception explanation
    # ------------------------------------------------------------------

    async def explain_exception(self, exception_id: str) -> ExplanationResult:
        """Generate a natural-language explanation for a reconciliation exception."""
        return ExplanationResult(
            explanation=(
                f"Exception {exception_id}: This is a placeholder explanation. "
                "Connect Claude to receive AI-powered analysis of this exception, "
                "including root cause identification and recommended resolution steps."
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
        return ChatResult(
            reply=(
                "I'm currently in placeholder mode. Once Claude is connected, "
                "I'll be able to answer questions about your reconciliation data, "
                "explain specific exceptions, and suggest resolution strategies."
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
        return ReportSummaryResult(
            summary=(
                f"Report for run {run_id}: This is a placeholder summary. "
                "Connect Claude to receive an AI-generated executive summary "
                "covering match rates, exception trends, and recommended actions."
            ),
            key_findings=[
                "Placeholder finding 1",
                "Placeholder finding 2",
            ],
            source="placeholder",
        )
