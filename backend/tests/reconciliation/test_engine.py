import pytest
import os
import json
from pathlib import Path
from backend.app.reconciliation.engine import ReconciliationEngine
from backend.app.data_generation.generator import generate_base_data, export_to_csv

def test_engine_end_to_end(tmp_path):
    # 1. Generate dummy data to a temp dir
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    datasets = generate_base_data(5)
    
    export_to_csv(datasets["bank"], csv_dir / "Bank.csv")
    export_to_csv(datasets["gateway"], csv_dir / "Gateway.csv")
    export_to_csv(datasets["settlement"], csv_dir / "Settlement.csv")
    export_to_csv(datasets["invoice"], csv_dir / "Invoice.csv")
    
    # 2. Setup engine with temp output dir
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    engine = ReconciliationEngine(data_dir=str(csv_dir), output_dir=str(report_dir))
    
    # 3. Run engine
    engine.run()
    
    # 4. Verify report
    report_path = report_dir / "reconciliation_report.json"
    assert report_path.exists()
    
    with open(report_path, "r") as f:
        data = json.load(f)
        
    assert data["metrics"]["total_transactions"] == 5
    assert data["metrics"]["clean_transactions"] == 5
    assert data["metrics"]["total_exceptions"] == 0
