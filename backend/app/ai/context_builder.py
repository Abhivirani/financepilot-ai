"""
Context Builder — gathers all domain state required for a single AI request.

Responsibilities:
  1. Fetch the exception record, its matched/unmatched transactions, and any
     related reconciliation metadata from the state store.
  2. Format the domain data into a structured dict that the PromptBuilder can
     interpolate into a prompt template.
  3. Enforce a configurable token budget so the context never exceeds the model's
     context window.

This module is **data-layer only**: it never touches the LLM, the HTTP layer,
or the prompt templates themselves.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ExceptionContext:
    """Immutable snapshot of everything the LLM needs to reason about an exception."""

    exception_id: str
    rule_type: str
    severity: str
    transaction_id: str
    amount: float
    currency: str

    # Optional enrichment — filled when available
    bank_record: Optional[Dict[str, Any]] = None
    gateway_record: Optional[Dict[str, Any]] = None
    related_exceptions: Optional[List[Dict[str, Any]]] = None
    reconciliation_metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ChatContext:
    """Context for a free-form chat request (not scoped to a single exception)."""

    user_message: str
    conversation_history: List[Dict[str, str]]
    run_id: Optional[str] = None
    active_exception_ids: Optional[List[str]] = None


@dataclass(frozen=True)
class ReportSummaryContext:
    """Context for generating a natural-language summary of a reconciliation report."""

    run_id: str
    total_transactions: int
    matched_count: int
    exception_count: int
    financial_summary: Dict[str, Any]
    rule_distribution: List[Dict[str, Any]]


class ContextBuilder(ABC):
    """
    Abstract interface that concrete implementations must satisfy.

    A concrete builder will be injected with a StateStore reference so it can
    pull live data at request time.
    """

    @abstractmethod
    async def build_exception_context(self, exception_id: str) -> ExceptionContext:
        """Build the full context for an exception explanation request."""
        ...

    @abstractmethod
    async def build_chat_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        run_id: Optional[str] = None,
    ) -> ChatContext:
        """Build the full context for a conversational chat request."""
        ...

    @abstractmethod
    async def build_report_summary_context(self, run_id: str) -> ReportSummaryContext:
        """Build the full context for a report summarisation request."""
        ...
