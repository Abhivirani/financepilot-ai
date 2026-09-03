from abc import ABC, abstractmethod
from typing import List
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import DatasetName

class BaseRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the rule (used for tracking and reporting)."""
        pass

    @abstractmethod
    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        """
        Evaluates the matched record against this rule.
        Returns a list of ExceptionRecord objects if anomalies are found,
        otherwise returns an empty list.
        """
        pass

    def _create_exception(
        self, 
        record: MatchedRecord, 
        severity: str, 
        title: str, 
        description: str,
        affected_datasets: List[str],
        recommended_action: str,
        metadata: dict = None
    ) -> ExceptionRecord:
        """Helper to create an exception record cleanly."""
        return ExceptionRecord(
            transaction_id=record.transaction_id,
            rule_name=self.name,
            severity=severity,
            title=title,
            description=description,
            affected_datasets=affected_datasets,
            recommended_action=recommended_action,
            metadata=metadata or {}
        )
