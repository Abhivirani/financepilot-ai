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
        try:
            gw_amount = float(gw.get("gross_amount", 0.0) or 0.0)
        except (ValueError, TypeError):
            gw_amount = 0.0

        if record.bank_records:
            bk = record.bank_records[0]
            try:
                bk_amount = float(bk.get("amount", 0.0) or 0.0)
            except (ValueError, TypeError):
                bk_amount = 0.0

            try:
                gw_fee = float(gw.get("fee", 0.0) or 0.0)
            except (ValueError, TypeError):
                gw_fee = 0.0

            net_gw_amount = round(gw_amount - gw_fee, 2)

            # Bank amount should match either gross_amount or net_amount (gross - fee)
            diff_amt = round(abs(bk_amount - gw_amount), 2)
            if abs(bk_amount - gw_amount) > 0.01 and abs(bk_amount - net_gw_amount) > 0.01:
                exceptions.append(
                    self._create_exception(
                        record=record,
                        severity=Severity.HIGH,
                        title="Amount Mismatch",
                        description=f"Bank: ₹{bk_amount:,.2f}, Gateway: ₹{gw_amount:,.2f}, Difference: ₹{diff_amt:,.2f}",
                        affected_datasets=[DatasetName.BANK.value, DatasetName.GATEWAY.value],
                        recommended_action="Manual Review",
                        metadata={"bank_amount": bk_amount, "gateway_amount": gw_amount, "difference": diff_amt}
                    )
                )

        if record.invoice_records:
            inv = record.invoice_records[0]
            try:
                inv_amount = float(inv.get("total_amount", 0.0) or 0.0)
            except (ValueError, TypeError):
                inv_amount = 0.0

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
            try:
                st_amount = float(st.get("gross_amount", 0.0) or 0.0)
            except (ValueError, TypeError):
                st_amount = 0.0

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
