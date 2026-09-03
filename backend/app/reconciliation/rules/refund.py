from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_REFUND, DatasetName, TransactionStatus

class RefundVerificationRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_REFUND

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        if record.gateway_records:
            gw = record.gateway_records[0]
            if gw.get("status") == TransactionStatus.REFUNDED:
                
                # Check if Bank has a corresponding debit or if Settlement shows refund
                # Note: In our synthetic dataset, refunds do not create Bank debits properly, 
                # which causes an exception.
                has_debit = False
                for bnk in record.bank_records:
                    if bnk.get("type") == "DEBIT":
                        has_debit = True
                        break
                        
                if not has_debit:
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.HIGH,
                            title="Refund Not Settled",
                            description=f"Transaction {record.transaction_id} is refunded in Gateway, but no bank debit was found.",
                            affected_datasets=[DatasetName.GATEWAY.value, DatasetName.BANK.value],
                            recommended_action="Verify if the refund is stuck in processing or requires manual bank transfer."
                        )
                    )

        return exceptions
