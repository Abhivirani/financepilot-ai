from backend.app.reconciliation.rules.status_mismatch import StatusMismatchRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_status_mismatch_fails():
    rule = StatusMismatchRule()
    record = MatchedRecord(
        transaction_id="T1", 
        gateway_records=[{"status": "FAILED"}], 
        settlement_records=[{}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 1
