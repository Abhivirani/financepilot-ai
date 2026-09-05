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
        
        if record.gateway_records:
            gw = record.gateway_records[0]
            try:
                gw_fee = float(gw.get("fee", 0.0) or 0.0)
                gw_gross = float(gw.get("gross_amount", 0.0) or 0.0)
            except (ValueError, TypeError):
                gw_fee = 0.0
                gw_gross = 0.0

            # Check fee percentage (must be between 1% and 3%)
            if gw_gross > 0:
                fee_pct = gw_fee / gw_gross
                if fee_pct > 0.03:
                    desc_text = f"Gateway fee {round(fee_pct * 100, 2)}% exceeds allowed range (1%-3%)"
                elif fee_pct < 0.01:
                    desc_text = f"Gateway fee {round(fee_pct * 100, 2)}% below allowed range (1%-3%)"
                else:
                    desc_text = ""

                if desc_text:
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.HIGH,
                            title="Fee Mismatch",
                            description=desc_text,
                            affected_datasets=[DatasetName.GATEWAY.value],
                            recommended_action="Escalate Payment Gateway",
                            metadata={"fee": gw_fee, "gross_amount": gw_gross, "fee_percentage": round(fee_pct * 100, 2)}
                        )
                    )

            if record.settlement_records:
                st = record.settlement_records[0]
                try:
                    st_fee = float(st.get("fee_deducted", 0.0) or 0.0)
                    st_net = float(st.get("net_amount", 0.0) or 0.0)
                except (ValueError, TypeError):
                    st_fee = 0.0
                    st_net = 0.0

                if (abs(gw_fee - st_fee) > 0.01 or abs(st_net - (gw_gross - gw_fee)) > 0.01) and not exceptions:
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.MEDIUM,
                            title="Fee Mismatch",
                            description=f"Gateway fee {gw_fee} does not match Settlement fee deducted {st_fee} or Net Settlement {st_net}.",
                            affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                            recommended_action="Review gateway pricing agreement and dispute incorrect fee deductions.",
                            metadata={"gateway_fee": gw_fee, "settlement_fee": st_fee, "settlement_net": st_net}
                        )
                    )

        return exceptions
