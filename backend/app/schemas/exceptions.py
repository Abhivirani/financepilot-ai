from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

from backend.app.schemas.common import RuleType, Severity, TransactionSource, SortOrder, PaginationMeta

class SortField(str, Enum):
    CREATED_AT = "CREATED_AT"
    AMOUNT = "AMOUNT"
    SEVERITY = "SEVERITY"
    RULE_TYPE = "RULE_TYPE"

class ExceptionFilterParams(BaseModel):
    run_id: Optional[str] = None
    page: int = 1
    page_size: int = 20
    severity: Optional[List[Severity]] = None
    rule_type: Optional[List[RuleType]] = None
    search: Optional[str] = None
    sort_by: SortField = SortField.CREATED_AT
    sort_order: SortOrder = SortOrder.desc

class ExceptionSummary(BaseModel):
    exception_id: str
    transaction_id: str
    source: TransactionSource
    rule_type: RuleType
    severity: Severity
    amount: float
    currency: str
    description: str
    created_at: datetime

class PaginatedExceptionsData(BaseModel):
    items: List[ExceptionSummary]
    pagination: PaginationMeta
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "exception_id": "exc-123",
                        "transaction_id": "txn-456",
                        "source": "Bank",
                        "rule_type": "AMOUNT_MISMATCH",
                        "severity": "HIGH",
                        "amount": 150.0,
                        "currency": "USD",
                        "description": "Amount mismatch between bank and gateway",
                        "created_at": "2026-09-03T09:00:00Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 1,
                    "total_pages": 1
                }
            }
        }
    )

class TransactionDetail(BaseModel):
    transaction_id: str
    source: TransactionSource
    amount: float
    currency: str
    timestamp: datetime
    raw_fields: Dict[str, Any]

class ExceptionDetailData(BaseModel):
    exception_id: str
    transaction: TransactionDetail
    related_transactions: List[TransactionDetail] = []
    rule_type: RuleType
    severity: Severity
    description: str
    ai_explanation: Optional[str] = None
    explanation_generated_at: Optional[datetime] = None
    suggested_action: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "exception_id": "exc-123",
                "transaction": {
                    "transaction_id": "txn-456",
                    "source": "Bank",
                    "amount": 150.0,
                    "currency": "USD",
                    "timestamp": "2026-09-03T09:00:00Z",
                    "raw_fields": {}
                },
                "related_transactions": [],
                "rule_type": "AMOUNT_MISMATCH",
                "severity": "HIGH",
                "description": "Amount mismatch between bank and gateway",
                "ai_explanation": "The discrepancy appears to be due to an unrecorded currency conversion fee.",
                "explanation_generated_at": "2026-09-03T09:05:00Z",
                "suggested_action": "Verify gateway configuration."
            }
        }
    )
