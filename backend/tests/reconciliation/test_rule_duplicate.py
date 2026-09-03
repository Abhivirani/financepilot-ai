from backend.app.reconciliation.rules.duplicate import DuplicateTransactionRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_duplicate_rule_passes():
    rule = DuplicateTransactionRule()
    record = MatchedRecord(
        transaction_id="T1",
        gateway_records=[{"gateway_txn_id": "G1"}],
        bank_records=[{"bank_txn_id": "B1"}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 0

def test_duplicate_rule_fails():
    rule = DuplicateTransactionRule()
    record = MatchedRecord(
        transaction_id="T1",
        gateway_records=[{"gateway_txn_id": "G1"}, {"gateway_txn_id": "G2"}],
        bank_records=[{"bank_txn_id": "B1"}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 1
    assert exceptions[0].title == "Duplicate Gateway Transaction"
