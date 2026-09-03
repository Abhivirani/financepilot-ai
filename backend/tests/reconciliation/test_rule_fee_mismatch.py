from backend.app.reconciliation.rules.fee_mismatch import FeeMismatchRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_fee_mismatch_fails():
    rule = FeeMismatchRule()
    record = MatchedRecord(
        transaction_id="T1", 
        gateway_records=[{"fee": 2.0}], 
        settlement_records=[{"fee_deducted": 5.0}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 1
