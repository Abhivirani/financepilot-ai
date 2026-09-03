from fastapi.testclient import TestClient
from backend.app.main import app
import pytest

client = TestClient(app)

def test_dashboard_no_runs():
    # If the state store is clear
    response = client.get("/api/v1/dashboard")
    # Our previous test ran reconcile so we MIGHT have a run! But in a fresh state it should be 404.
    # To be safe, we'll request a random run ID
    response = client.get("/api/v1/dashboard?run_id=some-invalid-id")
    assert response.status_code == 404

def test_dashboard_success():
    # Similar to reconcile test, we do E2E
    bank_csv = b"bank_txn_id,transaction_id,date,amount,type\nB1,T1,2026-01-01,100,CREDIT"
    gw_csv = b"gateway_txn_id,transaction_id,date,gross_amount,fee,status\nG1,T1,2026-01-01,100,2.0,SUCCESS"
    
    client.post(
        "/api/v1/upload",
        files={
            "bank_statement": ("bank.csv", bank_csv, "text/csv"),
            "payment_gateway": ("gw.csv", gw_csv, "text/csv")
        }
    )
    
    # Rely on latest batch and run
    client.post("/api/v1/reconcile", json={})
    
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metrics" in data["data"]
    assert "charts" in data["data"]
