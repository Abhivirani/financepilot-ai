import os
from pathlib import Path
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

_base_dir = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinancePilot AI API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for FinancePilot AI Reconciliation Engine"
    
    # Upload limits
    MAX_BATCH_SIZE: int = 5000
    MAX_RETAINED_BATCHES: int = 10
    MAX_RETAINED_RUNS: int = 10
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5MB
    
    # Paths
    UPLOAD_DIR: str = "backend/uploads"
    REPORT_DIR: str = "backend/generated_reports"
    
    # Business logic
    MATCH_AMOUNT_TOLERANCE: float = 0.01
    
    # ── LLM / AI settings ──────────────────────────────────
    # Provider selection — "gemini" | "anthropic"
    LLM_PROVIDER: str = "gemini"
    
    # API keys (only the active provider's key needs to be set)
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""      # future / fallback
    
    # Model configuration
    GEMINI_MODEL: str = "gemini-3.5-flash"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1500
    TIMEOUT: int = 30           # seconds
    LLM_CACHE_TTL: int = 3600       # seconds
    
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=str(_base_dir / ".env"),
        env_file_encoding='utf-8',
        extra="ignore"
    )

settings = Settings()
