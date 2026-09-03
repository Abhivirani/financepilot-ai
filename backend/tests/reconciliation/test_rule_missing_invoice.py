from backend.app.reconciliation.rules.missing_invoice import MissingInvoiceRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_missing_invoice_fails():
    rule = MissingInvoiceRule()
    record = MatchedRecord(transaction_id="T1", gateway_records=[{}], invoice_records=[])
    exceptions = rule.check(record)
    assert len(exceptions) == 1
