from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinancePilot AI API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for FinancePilot AI Reconciliation Engine"
    
    # Upload limits
    MAX_BATCH_SIZE: int = 500
    MAX_RETAINED_BATCHES: int = 10
    MAX_RETAINED_RUNS: int = 10
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5MB
    
    # Paths
    UPLOAD_DIR: str = "backend/uploads"
    REPORT_DIR: str = "backend/generated_reports"
    
    # Business logic
    MATCH_AMOUNT_TOLERANCE: float = 0.01
    
    # AI settings
    ANTHROPIC_API_KEY: str = ""
    AI_PROVIDER: str = "anthropic"
    AI_MODEL: str = "claude-sonnet-4-20250514"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2048
    AI_TIMEOUT: int = 30
    AI_CACHE_TTL: int = 3600  # seconds
    
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
