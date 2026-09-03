from backend.app.reconciliation.rules.late_settlement import LateSettlementRule
from backend.app.reconciliation.exceptions import MatchedRecord
import pandas as pd

def test_late_settlement_fails():
    rule = LateSettlementRule()
    record = MatchedRecord(
        transaction_id="T1", 
        gateway_records=[{"date": pd.to_datetime("2026-01-01")}], 
        settlement_records=[{"settlement_date": pd.to_datetime("2026-01-10")}]
    )
    exceptions = rule.check(record)
    assert len(exceptions) == 1
