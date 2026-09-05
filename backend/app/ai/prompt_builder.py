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
        self._report_template = _load_template("executive_report.md")
        self._dashboard_template = _load_template("dashboard_summary.md")
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
            rule_name=ctx.rule_name,
            severity=ctx.severity,
            title=ctx.title,
            description=ctx.description,
            transaction_id=ctx.transaction_id,
            affected_datasets=json.dumps(ctx.affected_datasets),
            recommended_action=ctx.recommended_action,
            metadata=json.dumps(ctx.metadata, default=str),
            amount=ctx.amount,
            currency=ctx.currency,
            total_exceptions=ctx.total_exceptions,
            current_match_rate=ctx.current_match_rate,
        )
        return [
            {"role": "user", "content": user_content},
        ]

    def build_dashboard_summary_messages(self, ctx: DashboardSummaryContext) -> List[Dict[str, str]]:
        """Return the messages list for a dashboard summary request."""
        user_content = Template(self._dashboard_template).safe_substitute(
            total_transactions=ctx.total_transactions,
            matched_transactions=ctx.matched_transactions,
            unmatched_transactions=ctx.unmatched_transactions,
            match_rate=ctx.match_rate,
            total_exceptions=ctx.total_exceptions,
            critical_exceptions=ctx.critical_exceptions,
            financial_summary=json.dumps(ctx.financial_summary, indent=2),
            rule_distribution=json.dumps(ctx.rule_distribution, indent=2),
            source_volume=json.dumps(ctx.source_volume, indent=2),
        )
        return [
            {"role": "user", "content": user_content},
        ]

    def build_report_messages(
        self, ctx: ReportSummaryContext
    ) -> List[Dict[str, str]]:
        """Return the ``messages`` list for a report summary request."""
        user_content = Template(self._report_template).safe_substitute(
            total_transactions=ctx.total_transactions,
            matched_transactions=ctx.matched_transactions,
            unmatched_transactions=ctx.unmatched_transactions,
            match_rate=ctx.match_rate,
            total_exceptions=ctx.total_exceptions,
            critical_exceptions=ctx.critical_exceptions,
            financial_summary=json.dumps(ctx.financial_summary, indent=2),
            rule_distribution=json.dumps(ctx.rule_distribution, indent=2),
            source_volume=json.dumps(ctx.source_volume, indent=2),
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

    def get_system_prompt(self, ctx: Optional[ChatContext] = None) -> str:
        """Return the system prompt used for all chat completions."""
        if not ctx or not ctx.dashboard_context:
            return Template(self._chat_system).safe_substitute(
                dashboard_context="No reconciliation data is currently available. Inform the user: 'No reconciliation data is currently available. Upload a dataset or use the Demo Dataset to begin.'"
            )
            
        dash = ctx.dashboard_context
        dash_str = (
            f"- Match Rate: {dash.match_rate}%\n"
            f"- Total Exceptions: {dash.total_exceptions}\n"
            f"- Critical Exceptions: {dash.critical_exceptions}\n"
            f"- Financials: {json.dumps(dash.financial_summary)}\n"
            f"- Rule Distribution: {json.dumps(dash.rule_distribution)}\n"
            f"- Source Volume: {json.dumps(dash.source_volume)}"
        )
        return Template(self._chat_system).safe_substitute(dashboard_context=dash_str)
