from backend.app.reconciliation.rules.missing_settlement import MissingSettlementRule
from backend.app.reconciliation.exceptions import MatchedRecord

def test_missing_settlement_fails():
    rule = MissingSettlementRule()
    record = MatchedRecord(transaction_id="T1", gateway_records=[{"status": "SUCCESS"}], settlement_records=[])
    exceptions = rule.check(record)
    assert len(exceptions) == 1
