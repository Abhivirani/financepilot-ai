from fastapi.testclient import TestClient
from backend.app.main import app
import pytest
import json
from pathlib import Path
from backend.app.core.config import settings

client = TestClient(app)

def test_get_settings_default():
    # Delete file if exists to test default
    settings_file = Path(settings.REPORT_DIR) / "settings.json"
    if settings_file.exists():
        settings_file.unlink()
        
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["match_threshold"] == 0.01

def test_update_settings():
    payload = {
        "match_threshold": 0.05,
        "enable_ai_explanations": False,
        "ai_provider": "anthropic",
        "reconciliation_rules": {
            "AMOUNT_MISMATCH": False
        }
    }
    
    response = client.put("/api/v1/settings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["match_threshold"] == 0.05
    assert data["data"]["ai_provider"] == "anthropic"
    
    # Verify GET returns updated
    get_response = client.get("/api/v1/settings")
    assert get_response.json()["data"]["match_threshold"] == 0.05
