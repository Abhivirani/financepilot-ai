from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_MISSING_INVOICE, DatasetName

class MissingInvoiceRule(BaseRule):
    @property
    def name(self) -> str:
        return RULE_MISSING_INVOICE

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        # If it exists in gateway but not invoice
        if record.gateway_records and not record.invoice_records:
            exceptions.append(
                self._create_exception(
                    record=record,
                    severity=Severity.MEDIUM,
                    title="Missing Invoice",
                    description="Invoice record not found.",
                    affected_datasets=[DatasetName.GATEWAY.value, DatasetName.INVOICE.value],
                    recommended_action="Regenerate Invoice",
                )
            )

        return exceptions
