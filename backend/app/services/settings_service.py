import json
from pathlib import Path
from backend.app.schemas.settings import SettingsData
from backend.app.core.config import settings

class SettingsService:
    def __init__(self):
        self.settings_file = Path(settings.REPORT_DIR) / "settings.json"
        
    async def get_settings(self) -> SettingsData:
        if self.settings_file.exists():
            with open(self.settings_file, "r") as f:
                data = json.load(f)
                return SettingsData(**data)
                
        # Default
        return SettingsData(
            match_threshold=0.01,
            enable_ai_explanations=True,
            ai_provider="openai",
            reconciliation_rules={
                "AMOUNT_MISMATCH": True,
                "MISSING_SETTLEMENT": True,
                "DUPLICATE_TRANSACTION": True,
                "ORPHAN_TRANSACTION": True
            }
        )
        
    async def update_settings(self, new_settings: SettingsData) -> SettingsData:
        # In a real app we'd validate the AI provider against supported ones.
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, "w") as f:
            json.dump(new_settings.model_dump(), f, indent=2)
            
        return new_settings
