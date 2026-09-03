import pandas as pd
from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.constants import DatasetName

def test_record_matcher():
    datasets = {
        DatasetName.GATEWAY: pd.DataFrame([{"transaction_id": "T1", "amount": 100}]),
        DatasetName.BANK: pd.DataFrame([{"transaction_id": "T1", "amount": 100}, {"transaction_id": "T2", "amount": 200}])
    }
    
    matcher = RecordMatcher()
    matched = matcher.match(datasets)
    
    assert len(matched) == 2
    
    t1_record = next(m for m in matched if m.transaction_id == "T1")
    assert len(t1_record.gateway_records) == 1
    assert len(t1_record.bank_records) == 1
    assert not t1_record.is_orphan
    
    t2_record = next(m for m in matched if m.transaction_id == "T2")
    assert len(t2_record.gateway_records) == 0
    assert len(t2_record.bank_records) == 1
    assert t2_record.is_orphan
