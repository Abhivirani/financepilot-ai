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


from backend.app.services.state_store import StateStore
from backend.app.core.exceptions import APIException
from backend.app.utils.currency import format_currency

@dataclass(frozen=True)
class ExceptionContext:
    """Immutable snapshot of everything the LLM needs to reason about an exception."""

    exception_id: str
    rule_name: str
    severity: str
    title: str
    description: str
    transaction_id: str
    affected_datasets: List[str]
    recommended_action: str
    metadata: Dict[str, Any]
    
    amount: float
    currency: str

    # Context enrichment
    total_exceptions: int
    current_match_rate: float


@dataclass(frozen=True)
class ChatContext:
    """Context for a free-form chat request (not scoped to a single exception)."""

    user_message: str
    conversation_history: List[Dict[str, str]]
    run_id: Optional[str] = None
    active_exception_ids: Optional[List[str]] = None
    dashboard_context: Optional[DashboardSummaryContext] = None


@dataclass(frozen=True)
class DashboardSummaryContext:
    """Context for generating a natural-language executive summary of the dashboard."""

    run_id: str
    total_transactions: int
    matched_transactions: int
    unmatched_transactions: int
    total_exceptions: int
    match_rate: float
    critical_exceptions: int
    financial_summary: Dict[str, Any]
    rule_distribution: List[Dict[str, Any]]
    source_volume: List[Dict[str, Any]]


@dataclass(frozen=True)
class ReportSummaryContext:
    """Context for generating a natural-language summary of a reconciliation report."""
    run_id: str
    total_transactions: int
    matched_transactions: int
    unmatched_transactions: int
    total_exceptions: int
    match_rate: float
    critical_exceptions: int
    financial_summary: Dict[str, Any]
    rule_distribution: List[Dict[str, Any]]
    source_volume: List[Dict[str, Any]]

class ContextBuilder(ABC):
    """
    Abstract interface that concrete implementations must satisfy.
    """

    @abstractmethod
    async def build_exception_context(self, exception_id: str) -> ExceptionContext:
        """Build the full context for an exception explanation request."""
        ...

    @abstractmethod
    async def build_dashboard_summary_context(self) -> DashboardSummaryContext:
        """Build the full context for a dashboard executive summary request."""
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
    async def build_report_summary_context(self, run_id: Optional[str] = None) -> ReportSummaryContext:
        """Build the full context for a report summarisation request."""
        ...

class DefaultContextBuilder(ContextBuilder):
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    async def build_exception_context(self, exception_id: str) -> ExceptionContext:
        run_id = self.state_store.latest_run_id
        if not run_id:
            raise APIException("RUN_NOT_FOUND", 404, "No recent reconciliation run found.")

        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            raise APIException("RUN_NOT_FOUND", 404, f"Run {run_id} not found.")

        exceptions = run_data.get("exceptions", [])
        exc = next((e for e in exceptions if e.get("exception_id") == exception_id), None)
        if not exc:
            raise APIException("EXCEPTION_NOT_FOUND", 404, f"Exception {exception_id} not found.")

        summary = run_data.get("summary", {})
        total_tx = summary.get("total_transactions", 1)
        matched = summary.get("matched_records", 0)
        match_rate = (matched / total_tx) * 100 if total_tx > 0 else 0

        return ExceptionContext(
            exception_id=exc.get("exception_id", exception_id),
            rule_name=exc.get("rule_name", "UNKNOWN"),
            severity=exc.get("severity", "LOW"),
            title=exc.get("title", ""),
            description=exc.get("description", ""),
            transaction_id=exc.get("transaction_id", ""),
            affected_datasets=exc.get("affected_datasets", []),
            recommended_action=exc.get("recommended_action", ""),
            metadata=exc.get("metadata", {}),
            amount=exc.get("amount", 0.0),
            currency=exc.get("currency", "INR"),
            total_exceptions=len(exceptions),
            current_match_rate=round(match_rate, 2),
        )

    async def build_dashboard_summary_context(self) -> DashboardSummaryContext:
        run_id = self.state_store.latest_run_id
        if not run_id:
            raise APIException("RUN_NOT_FOUND", 404, "No recent reconciliation run found.")

        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            raise APIException("RUN_NOT_FOUND", 404, f"Run {run_id} not found.")

        summary = run_data.get("summary", {})
        metrics = run_data.get("metrics", {})
        exceptions = run_data.get("exceptions", [])
        
        # Calculate critical exceptions
        critical_count = sum(1 for exc in exceptions if exc.get("severity") == "CRITICAL")
        
        total_tx = metrics.get("total_transactions", 0)
        clean_tx = metrics.get("clean_transactions", 0)
        unmatched_tx = total_tx - clean_tx
        
        rule_counts = {}
        for exc in exceptions:
            rt = exc.get("rule_name", "UNKNOWN")
            rule_counts[rt] = rule_counts.get(rt, 0) + 1
            
        rule_distribution = []
        for rt, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
            rule_distribution.append({"rule_type": rt, "count": count})
            
        fin = metrics.get("financials", {})
        total_amt = fin.get("total_amount_processed", fin.get("total_bank_volume", 0.0))
        matched_amt = fin.get("matched_amount", fin.get("total_settled_volume", 0.0))
        unmatched_amt = fin.get("unmatched_amount", fin.get("unmatched_volume", 0.0))
        discrepancy_amt = fin.get("discrepancy_amount", round(abs(total_amt - matched_amt), 2))
        financial_summary = {
            "currency": "INR",
            "total_amount_processed": format_currency(total_amt),
            "matched_amount": format_currency(matched_amt),
            "unmatched_amount": format_currency(unmatched_amt),
            "discrepancy_amount": format_currency(discrepancy_amt),
            "total_amount_processed_raw": total_amt,
            "matched_amount_raw": matched_amt,
            "unmatched_amount_raw": unmatched_amt,
            "discrepancy_amount_raw": discrepancy_amt,
        }

        source_volume = []
        batch_id = run_data.get("batch_id")
        batch = await self.state_store.get_batch(batch_id) if batch_id else None
        if batch:
            for f in batch.get("files", []):
                source_volume.append({"source_type": f.get("source_type", "UNKNOWN"), "count": f.get("row_count", 0)})

        return DashboardSummaryContext(
            run_id=run_id,
            total_transactions=total_tx,
            matched_transactions=clean_tx,
            unmatched_transactions=unmatched_tx,
            total_exceptions=len(exceptions),
            match_rate=summary.get("match_rate", 0.0),
            critical_exceptions=critical_count,
            financial_summary=financial_summary,
            rule_distribution=rule_distribution,
            source_volume=source_volume
        )

    async def build_chat_context(self, user_message: str, conversation_history: List[Dict[str, str]], run_id: Optional[str] = None) -> ChatContext:
        dashboard_context = None
        try:
            dashboard_context = await self.build_dashboard_summary_context()
            if run_id is None:
                run_id = dashboard_context.run_id
        except APIException:
            pass
            
        return ChatContext(
            user_message=user_message,
            conversation_history=conversation_history,
            run_id=run_id,
            dashboard_context=dashboard_context
        )

    async def build_report_summary_context(self, run_id: Optional[str] = None) -> ReportSummaryContext:
        if not run_id:
            run_id = self.state_store.latest_run_id
            if not run_id:
                raise APIException("RUN_NOT_FOUND", 404, "No recent reconciliation run found.")
                
        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            raise APIException("RUN_NOT_FOUND", 404, f"Run {run_id} not found.")

        summary = run_data.get("summary", {})
        metrics = run_data.get("metrics", {})
        exceptions = run_data.get("exceptions", [])
        
        critical_count = sum(1 for exc in exceptions if exc.get("severity") == "CRITICAL")
        
        total_tx = metrics.get("total_transactions", 0)
        clean_tx = metrics.get("clean_transactions", 0)
        unmatched_tx = total_tx - clean_tx
        
        rule_counts = {}
        for exc in exceptions:
            rt = exc.get("rule_name", "UNKNOWN")
            rule_counts[rt] = rule_counts.get(rt, 0) + 1
            
        rule_distribution = []
        for rt, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
            rule_distribution.append({"rule_type": rt, "count": count})
            
        fin = metrics.get("financials", {})
        total_amt = fin.get("total_amount_processed", fin.get("total_bank_volume", 0.0))
        matched_amt = fin.get("matched_amount", fin.get("total_settled_volume", 0.0))
        unmatched_amt = fin.get("unmatched_amount", fin.get("unmatched_volume", 0.0))
        discrepancy_amt = fin.get("discrepancy_amount", round(abs(total_amt - matched_amt), 2))
        financial_summary = {
            "currency": "INR",
            "total_amount_processed": format_currency(total_amt),
            "matched_amount": format_currency(matched_amt),
            "unmatched_amount": format_currency(unmatched_amt),
            "discrepancy_amount": format_currency(discrepancy_amt),
            "total_amount_processed_raw": total_amt,
            "matched_amount_raw": matched_amt,
            "unmatched_amount_raw": unmatched_amt,
            "discrepancy_amount_raw": discrepancy_amt,
        }

        source_volume = []
        batch_id = run_data.get("batch_id")
        batch = await self.state_store.get_batch(batch_id) if batch_id else None
        if batch:
            for f in batch.get("files", []):
                source_volume.append({"source_type": f.get("source_type", "UNKNOWN"), "count": f.get("row_count", 0)})

        return ReportSummaryContext(
            run_id=run_id,
            total_transactions=total_tx,
            matched_transactions=clean_tx,
            unmatched_transactions=unmatched_tx,
            total_exceptions=len(exceptions),
            match_rate=summary.get("match_rate", 0.0),
            critical_exceptions=critical_count,
            financial_summary=financial_summary,
            rule_distribution=rule_distribution,
            source_volume=source_volume
        )
