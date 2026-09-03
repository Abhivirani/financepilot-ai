from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_DUPLICATE, DatasetName

class DuplicateTransactionRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_DUPLICATE

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        if len(record.gateway_records) > 1:
            exceptions.append(
                self._create_exception(
                    record=record,
                    severity=Severity.HIGH,
                    title="Duplicate Gateway Transaction",
                    description=f"Multiple Gateway records found for transaction {record.transaction_id}.",
                    affected_datasets=[DatasetName.GATEWAY.value],
                    recommended_action="Check for accidental double charging or retry logic bugs.",
                    metadata={"count": len(record.gateway_records)}
                )
            )
            
        if len(record.bank_records) > 1:
            exceptions.append(
                self._create_exception(
                    record=record,
                    severity=Severity.HIGH,
                    title="Duplicate Bank Transaction",
                    description=f"Multiple Bank records found for transaction {record.transaction_id}.",
                    affected_datasets=[DatasetName.BANK.value],
                    recommended_action="Investigate bank statement duplicate entries.",
                    metadata={"count": len(record.bank_records)}
                )
            )

        return exceptions
