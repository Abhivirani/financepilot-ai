from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_MISSING_SETTLEMENT, DatasetName

class MissingSettlementRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_MISSING_SETTLEMENT

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        # If it exists in gateway, but not in settlement
        # We assume SUCCESS status requires settlement. Refunded might also require settlement but let's handle that in Refund rule or here.
        if record.gateway_records and not record.settlement_records:
            gw_status = record.gateway_records[0].get("status")
            
            # If it's failed, it shouldn't have a settlement. 
            if gw_status == "SUCCESS":
                exceptions.append(
                    self._create_exception(
                        record=record,
                        severity=Severity.HIGH,
                        title="Missing Settlement",
                        description=f"Transaction {record.transaction_id} is marked SUCCESS in Gateway but missing from Settlement.",
                        affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                        recommended_action="Follow up with payment gateway for missing settlement payout.",
                        metadata={"gateway_status": gw_status}
                    )
                )

        return exceptions
