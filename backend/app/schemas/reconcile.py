from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime

from backend.app.schemas.common import TransactionSource

class ReconcileRequest(BaseModel):
    batch_id: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "a315052a-f874-430f-83c1-bc9c3cb7e0b4"
            }
        }
    )

class RunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"

class ReconcileSummary(BaseModel):
    total_transactions: int
    matched_count: int
    exception_count: int
    match_rate: float
    sources_processed: List[TransactionSource]

class ReconcileResponseData(BaseModel):
    run_id: str
    batch_id: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime
    processing_time_ms: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "r-993d01ab-1a3b-4c2d-98e7",
                "batch_id": "a315052a-f874-430f-83c1-bc9c3cb7e0b4",
                "status": "COMPLETED",
                "started_at": "2026-09-03T09:00:00Z",
                "completed_at": "2026-09-03T09:00:02Z",
                "processing_time_ms": 2000
            }
        }
    )
    summary: ReconcileSummary
