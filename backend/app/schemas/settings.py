from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

class SettingsData(BaseModel):
    match_threshold: float
    enable_ai_explanations: bool
    ai_provider: str
    reconciliation_rules: Dict[str, bool]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_threshold": 0.01,
                "enable_ai_explanations": True,
                "ai_provider": "openai",
                "reconciliation_rules": {
                    "AMOUNT_MISMATCH": True,
                    "MISSING_SETTLEMENT": True,
                    "DUPLICATE_TRANSACTION": True,
                    "ORPHAN_TRANSACTION": True
                }
            }
        }
    )
