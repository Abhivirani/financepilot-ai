from backend.app.reconciliation.rules.amount_mismatch import AmountMismatchRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_amount_mismatch_rule_passes():
    rule = AmountMismatchRule()
    record = MatchedRecord(
        transaction_id="T1",
        gateway_records=[{"gross_amount": 100.0}],
        invoice_records=[{"total_amount": 100.0}],
        settlement_records=[{"gross_amount": 100.0}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 0

def test_amount_mismatch_rule_fails():
    rule = AmountMismatchRule()
    record = MatchedRecord(
        transaction_id="T1",
        gateway_records=[{"gross_amount": 100.0}],
        invoice_records=[{"total_amount": 90.0}],
        settlement_records=[{"gross_amount": 80.0}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 2
    
    assert exceptions[0].title == "Gateway/Invoice Amount Mismatch"
    assert exceptions[1].title == "Gateway/Settlement Amount Mismatch"
