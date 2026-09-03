from backend.app.reconciliation.rules.refund import RefundVerificationRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_refund_fails():
    rule = RefundVerificationRule()
    record = MatchedRecord(
        transaction_id="T1", 
        gateway_records=[{"status": "REFUNDED"}], 
        bank_records=[{"type": "CREDIT"}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 1
