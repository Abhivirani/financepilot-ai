from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_AMOUNT_MISMATCH, DatasetName

class AmountMismatchRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_AMOUNT_MISMATCH

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        # We need Gateway and at least Invoice or Settlement to compare amounts
        if not record.gateway_records:
            return exceptions
            
        gw = record.gateway_records[0]
        gw_amount = gw.get("gross_amount", 0.0)

        if record.invoice_records:
            inv = record.invoice_records[0]
            inv_amount = inv.get("total_amount", 0.0)
            if abs(gw_amount - inv_amount) > 0.01:
                exceptions.append(
                    self._create_exception(
                        record=record,
                        severity=Severity.HIGH,
                        title="Gateway/Invoice Amount Mismatch",
                        description=f"Gateway amount {gw_amount} does not match Invoice amount {inv_amount}.",
                        affected_datasets=[DatasetName.GATEWAY.value, DatasetName.INVOICE.value],
                        recommended_action="Verify product pricing or discount application.",
                        metadata={"gateway_amount": gw_amount, "invoice_amount": inv_amount}
                    )
                )
                
        if record.settlement_records:
            st = record.settlement_records[0]
            st_amount = st.get("gross_amount", 0.0)
            if abs(gw_amount - st_amount) > 0.01:
                exceptions.append(
                    self._create_exception(
                        record=record,
                        severity=Severity.HIGH,
                        title="Gateway/Settlement Amount Mismatch",
                        description=f"Gateway amount {gw_amount} does not match Settlement gross amount {st_amount}.",
                        affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                        recommended_action="Dispute captured amount with payment gateway.",
                        metadata={"gateway_amount": gw_amount, "settlement_gross": st_amount}
                    )
                )

        return exceptions
