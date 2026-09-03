from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_STATUS_MISMATCH, DatasetName, TransactionStatus

class StatusMismatchRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_STATUS_MISMATCH

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        # Check if gateway failed but invoice says paid, or settlement exists
        if record.gateway_records:
            gw = record.gateway_records[0]
            if gw.get("status") == TransactionStatus.FAILED:
                if record.settlement_records:
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.HIGH,
                            title="Status Mismatch: Settlement for Failed Transaction",
                            description=f"Transaction {record.transaction_id} failed in Gateway but a Settlement record exists.",
                            affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                            recommended_action="Investigate why a failed transaction was settled. Contact gateway support."
                        )
                    )
                    
                if record.invoice_records and record.invoice_records[0].get("status") == "PAID":
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.MEDIUM,
                            title="Status Mismatch: Paid Invoice for Failed Transaction",
                            description=f"Transaction {record.transaction_id} failed in Gateway but Invoice is marked PAID.",
                            affected_datasets=[DatasetName.GATEWAY.value, DatasetName.INVOICE.value],
                            recommended_action="Verify if payment was retried or completed through another method."
                        )
                    )

        return exceptions
