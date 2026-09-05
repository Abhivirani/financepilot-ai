from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_upload_missing_sources():
    response = client.post(
        "/api/v1/upload",
        files={}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MINIMUM_SOURCES_NOT_MET"

def test_upload_invalid_file_type():
    response = client.post(
        "/api/v1/upload",
        files={
            "bank_statement": ("bank.txt", b"hello", "text/plain"),
            "payment_gateway": ("gw.csv", b"a,b,c\n1,2,3", "text/csv")
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] in ["INVALID_FILE_TYPE", "MINIMUM_SOURCES_NOT_MET"]

def test_upload_valid_csvs():
    # Provide two valid CSVs matching the schema to trigger a successful upload
    bank_csv = b"bank_txn_id,transaction_id,date,amount,type\nB1,T1,2026-01-01,100,CREDIT"
    gw_csv = b"gateway_txn_id,transaction_id,date,gross_amount,fee,status\nG1,T1,2026-01-01,100,2.0,SUCCESS"
    
    response = client.post(
        "/api/v1/upload",
        files={
            "bank_statement": ("bank.csv", bank_csv, "text/csv"),
            "payment_gateway": ("gw.csv", gw_csv, "text/csv")
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "VALIDATED"
    assert data["data"]["total_transactions"] == 2
