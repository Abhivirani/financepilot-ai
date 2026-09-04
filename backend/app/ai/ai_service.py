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


import re
import time

@dataclass(frozen=True)
class ExplanationResult:
    """Returned by ``explain_exception``."""

    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    source: str


@dataclass(frozen=True)
class ChatResult:
    """Returned by ``chat``."""
    answer: str
    confidence: int
    latency_ms: int
    source: str


@dataclass(frozen=True)
class ReportSummaryResult:
    """Returned by ``generate_executive_report``."""
    title: str
    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    source: str


class AIService:
    def __init__(self, llm_client: Optional[BaseLLMClient] = None, context_builder=None, prompt_builder=None) -> None:
        self._llm = llm_client
        self._context_builder = context_builder
        self._prompt_builder = prompt_builder

    @property
    def is_active(self) -> bool:
        """True when a real LLM client has been injected."""
        return self._llm is not None

    # ------------------------------------------------------------------
    # Exception explanation
    # ------------------------------------------------------------------

    async def explain_exception(self, exception_id: str) -> ExplanationResult:
        """Generate a natural-language explanation for a reconciliation exception."""
        if not self._llm or not self._context_builder or not self._prompt_builder:
            return ExplanationResult(
                summary="AI explanation not available.",
                markdown=(
                    f"Exception {exception_id}: This is a placeholder explanation. "
                    "Connect an LLM provider to receive AI-powered analysis."
                ),
                confidence=0,
                latency_ms=0,
                source="placeholder",
            )
            
        start_time = time.time()
        context = await self._context_builder.build_exception_context(exception_id)
        messages = self._prompt_builder.build_exception_messages(context)
        
        response = await self._llm.generate(
            system="You are an expert financial reconciliation AI assistant.",
            messages=messages
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Parse confidence
        confidence = 0
        conf_match = re.search(r"Confidence:\s*(\d+)%", response.content, re.IGNORECASE)
        if conf_match:
            confidence = int(conf_match.group(1))
            
        # Extract summary
        summary = "No summary provided."
        summary_match = re.search(r"##\s*Summary\s*\n(.*?)(?=\n##|$)", response.content, re.IGNORECASE | re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
            
        # Clean up the output to remove the Confidence line at the end if desired, 
        # or just leave it since it's markdown. We will leave it.

        return ExplanationResult(
            summary=summary,
            markdown=response.content.strip(),
            confidence=confidence,
            latency_ms=latency_ms,
            source="llm"
        )

    # ------------------------------------------------------------------
    # Dashboard summary
    # ------------------------------------------------------------------

    async def generate_dashboard_summary(self) -> ExplanationResult:
        """Generate a natural-language executive summary of the dashboard."""
        if not self._llm or not self._context_builder or not self._prompt_builder:
            return ExplanationResult(
                summary="AI dashboard summary not available.",
                markdown=(
                    "This is a placeholder dashboard summary. "
                    "Connect an LLM provider to receive AI-powered analysis."
                ),
                confidence=0,
                latency_ms=0,
                source="placeholder",
            )
            
        start_time = time.time()
        context = await self._context_builder.build_dashboard_summary_context()
        messages = self._prompt_builder.build_dashboard_summary_messages(context)
        
        response = await self._llm.generate(
            system="You are an expert financial reconciliation AI assistant.",
            messages=messages
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Parse confidence
        confidence = 0
        conf_match = re.search(r"Confidence:\s*(\d+)%", response.content, re.IGNORECASE)
        if conf_match:
            confidence = int(conf_match.group(1))
            
        # Extract summary or just use the first paragraph
        summary = "No summary provided."
        summary_match = re.search(r"##\s*Executive Summary\s*\n(.*?)(?=\n##|$)", response.content, re.IGNORECASE | re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
            
        return ExplanationResult(
            summary=summary,
            markdown=response.content.strip(),
            confidence=confidence,
            latency_ms=latency_ms,
            source="llm"
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
        pass

        start_time = time.time()
        history = conversation_history or []
        
        # Build context (using same logic that gathers dashboard stats)
        context = await self._context_builder.build_chat_context(
            user_message=message,
            conversation_history=history,
            run_id=run_id
        )
        
        messages = self._prompt_builder.build_chat_messages(context)
        system_prompt = self._prompt_builder.get_system_prompt(context)

        response = await self._llm.generate(
            system=system_prompt,
            messages=messages
        )

        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract confidence
        confidence = 0
        conf_match = re.search(r"Confidence:\s*(\d+)%", response.content, re.IGNORECASE)
        if conf_match:
            confidence = int(conf_match.group(1))

        # We can clean up the response to remove the Confidence line if we want,
        # but leaving it is fine or we can strip it. Let's strip it from the end to be clean.
        answer = re.sub(r"\n+Confidence:\s*\d+%\s*$", "", response.content, flags=re.IGNORECASE).strip()

        return ChatResult(
            answer=answer,
            confidence=confidence,
            latency_ms=latency_ms,
            source="llm"
        )

    # ------------------------------------------------------------------
    # Report summarisation
    # ------------------------------------------------------------------

    async def generate_executive_report(self) -> ReportSummaryResult:
        """Generate a natural-language executive summary of the reconciliation report."""
        if not self._llm or not self._context_builder or not self._prompt_builder:
            return ReportSummaryResult(
                title="Executive Reconciliation Report (Placeholder)",
                summary="AI report generation not available.",
                markdown=(
                    "# Executive Reconciliation Report\n"
                    "Connect an LLM provider to receive an AI-generated executive "
                    "summary covering match rates, exception trends, and "
                    "recommended actions."
                ),
                confidence=0,
                latency_ms=0,
                source="placeholder",
            )

        start_time = time.time()
        context = await self._context_builder.build_report_summary_context()
        messages = self._prompt_builder.build_report_messages(context)
        
        response = await self._llm.generate(
            system="You are an expert financial reconciliation AI analyst.",
            messages=messages
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Parse confidence
        confidence = 0
        conf_match = re.search(r"Confidence:\s*(\d+)%", response.content, re.IGNORECASE)
        if conf_match:
            confidence = int(conf_match.group(1))
            
        # Extract summary (Executive Summary section)
        summary = "No summary provided."
        summary_match = re.search(r"#\s*Executive Summary\s*\n(.*?)(?=\n#|$)", response.content, re.IGNORECASE | re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
            
        return ReportSummaryResult(
            title="Executive Reconciliation Report",
            summary=summary,
            markdown=response.content.strip(),
            confidence=confidence,
            latency_ms=latency_ms,
            source="llm"
        )
