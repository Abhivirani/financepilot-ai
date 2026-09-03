from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_FEE_MISMATCH, DatasetName

class FeeMismatchRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_FEE_MISMATCH

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        if record.gateway_records and record.settlement_records:
            gw = record.gateway_records[0]
            st = record.settlement_records[0]
            
            gw_fee = gw.get("fee", 0.0)
            st_fee = st.get("fee_deducted", 0.0)
            
            if abs(gw_fee - st_fee) > 0.01:
                exceptions.append(
                    self._create_exception(
                        record=record,
                        severity=Severity.MEDIUM,
                        title="Fee Mismatch",
                        description=f"Gateway fee {gw_fee} does not match Settlement fee deducted {st_fee}.",
                        affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                        recommended_action="Review gateway pricing agreement and dispute incorrect fee deductions.",
                        metadata={"gateway_fee": gw_fee, "settlement_fee": st_fee}
                    )
                )

        return exceptions
