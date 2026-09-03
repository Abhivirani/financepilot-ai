from backend.app.reconciliation.rules.orphan import OrphanRecordRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_orphan_fails():
    rule = OrphanRecordRule()
    record = MatchedRecord(transaction_id="T1", bank_records=[{}])
    exceptions = rule.check(record)
    assert len(exceptions) == 1
