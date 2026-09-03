"""
Prompt Builder — renders Markdown prompt templates with structured context.

Responsibilities:
  1. Load prompt templates from ``app/ai/prompts/`` at startup.
  2. Accept a context dataclass and interpolate it into the template.
  3. Return a list of messages in the ``[{"role": ..., "content": ...}]``
     format expected by ``BaseLLMClient.generate()``.

Design decisions:
  - Templates live in Markdown files, **never** hardcoded strings.
  - The builder is stateless after init; safe for concurrent use.
  - Token estimation is deferred to the ``llm_client`` layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from string import Template
from typing import Any, Dict, List

from backend.app.ai.context_builder import (
    ChatContext,
    ExceptionContext,
    ReportSummaryContext,
)

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_template(name: str) -> str:
    """Read a prompt template from disk.  Raises FileNotFoundError early."""
    path = _PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


class PromptBuilder:
    """Builds model-ready message lists from context objects and templates."""

    def __init__(self) -> None:
        # Pre-load templates so missing files are caught at startup, not at
        # request time.
        self._exception_template = _load_template("exception_explanation.md")
        self._report_template = _load_template("report_summary.md")
        self._chat_system = _load_template("chat_system.md")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_exception_messages(
        self, ctx: ExceptionContext
    ) -> List[Dict[str, str]]:
        """Return the ``messages`` list for an exception explanation request."""
        user_content = Template(self._exception_template).safe_substitute(
            exception_id=ctx.exception_id,
            rule_type=ctx.rule_type,
            severity=ctx.severity,
            transaction_id=ctx.transaction_id,
            amount=ctx.amount,
            currency=ctx.currency,
            bank_record=json.dumps(ctx.bank_record, default=str) if ctx.bank_record else "N/A",
            gateway_record=json.dumps(ctx.gateway_record, default=str) if ctx.gateway_record else "N/A",
        )
        return [
            {"role": "user", "content": user_content},
        ]

    def build_report_messages(
        self, ctx: ReportSummaryContext
    ) -> List[Dict[str, str]]:
        """Return the ``messages`` list for a report summary request."""
        user_content = Template(self._report_template).safe_substitute(
            run_id=ctx.run_id,
            total_transactions=ctx.total_transactions,
            matched_count=ctx.matched_count,
            exception_count=ctx.exception_count,
            financial_summary=json.dumps(ctx.financial_summary, default=str),
            rule_distribution=json.dumps(ctx.rule_distribution, default=str),
        )
        return [
            {"role": "user", "content": user_content},
        ]

    def build_chat_messages(
        self, ctx: ChatContext
    ) -> List[Dict[str, str]]:
        """Return the ``messages`` list for a free-form chat request."""
        messages: List[Dict[str, str]] = []
        # Append prior conversation turns
        for turn in ctx.conversation_history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        # Append the latest user message
        messages.append({"role": "user", "content": ctx.user_message})
        return messages

    def get_system_prompt(self) -> str:
        """Return the system prompt used for all chat completions."""
        return self._chat_system
