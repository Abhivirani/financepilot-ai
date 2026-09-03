from enum import Enum
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from backend.app.schemas.common import TransactionSource

class FileValidationSummary(BaseModel):
    source_type: TransactionSource
    filename: str
    row_count: int
    column_count: int
    is_valid: bool
    warnings: List[str] = []

class BatchStatus(str, Enum):
    VALIDATED = "VALIDATED"
    INVALID = "INVALID"
    PARTIALLY_VALID = "PARTIALLY_VALID"

class UploadResponseData(BaseModel):
    batch_id: str
    uploaded_at: datetime
    files: List[FileValidationSummary]
    total_transactions: int
    status: BatchStatus

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "a315052a-f874-430f-83c1-bc9c3cb7e0b4",
                "uploaded_at": "2026-09-03T09:00:00Z",
                "files": [
                    {
                        "source_type": "Bank",
                        "filename": "bank.csv",
                        "row_count": 500,
                        "column_count": 5,
                        "is_valid": True,
                        "warnings": []
                    }
                ],
                "total_transactions": 500,
                "status": "VALIDATED"
            }
        }
    )
