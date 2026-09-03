from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_explain_exception_not_implemented():
    response = client.post(
        "/api/v1/ai/explain",
        json={"exception_id": "test"}
    )
    assert response.status_code == 501
    assert response.json()["error"]["message"] == "Coming soon"
