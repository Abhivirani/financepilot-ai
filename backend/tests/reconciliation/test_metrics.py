from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.exceptions import MatchedRecord, ExceptionRecord

def test_metrics_calculator():
    records = [
        MatchedRecord(transaction_id="T1", gateway_records=[{"gross_amount": 100}], settlement_records=[{"net_amount": 90}]),
        MatchedRecord(transaction_id="T2", gateway_records=[{"gross_amount": 200}], settlement_records=[{"net_amount": 180}]),
    ]
    
    exceptions = [
        ExceptionRecord(transaction_id="T1", rule_name="AMOUNT_MISMATCH", severity="HIGH", title="Title", description="Desc", affected_datasets=[], recommended_action="")
    ]
    
    calc = MetricsCalculator()
    metrics = calc.calculate(records, exceptions)
    
    assert metrics["total_transactions"] == 2
    assert metrics["clean_transactions"] == 1
    assert metrics["total_exceptions"] == 1
    assert metrics["match_rate_percentage"] == 50.0
    assert metrics["financials"]["total_gateway_volume"] == 300.0
    assert metrics["financials"]["total_settled_volume"] == 270.0
