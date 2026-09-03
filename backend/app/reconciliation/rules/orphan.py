from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_ORPHAN

class OrphanRecordRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_ORPHAN

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        if record.is_orphan:
            
            affected = []
            if record.bank_records: affected.append("Bank")
            if record.gateway_records: affected.append("Gateway")
            if record.settlement_records: affected.append("Settlement")
            if record.invoice_records: affected.append("Invoice")
            
            exceptions.append(
                self._create_exception(
                    record=record,
                    severity=Severity.HIGH,
                    title="Orphan Record",
                    description=f"Transaction {record.transaction_id} exists only in {', '.join(affected)}.",
                    affected_datasets=affected,
                    recommended_action="Manually reconcile against non-gateway accounting records.",
                )
            )

        return exceptions
