from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_exceptions_list_success():
    # Similar to E2E
    bank_csv = b"bank_txn_id,transaction_id,date,amount,type\nB1,T1,2026-01-01,100,CREDIT"
    gw_csv = b"gateway_txn_id,transaction_id,date,gross_amount,fee,status\nG1,T1,2026-01-01,100,2.0,SUCCESS"
    
    client.post(
        "/api/v1/upload",
        files={
            "bank_statement": ("bank.csv", bank_csv, "text/csv"),
            "payment_gateway": ("gw.csv", gw_csv, "text/csv")
        }
    )
    
    client.post("/api/v1/reconcile", json={})
    
    # Check exceptions list
    response = client.get("/api/v1/exceptions?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "pagination" in data["data"]
    
    # If there are items, test detail view
    items = data["data"]["items"]
    if items:
        exc_id = items[0]["exception_id"]
        detail_resp = client.get(f"/api/v1/exceptions/{exc_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["success"] is True
        assert detail_data["data"]["exception_id"] == exc_id
        assert detail_data["data"]["ai_explanation"] is not None
