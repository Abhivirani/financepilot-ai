from enum import Enum
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel, Field
from backend.app.core.context import request_id_ctx

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RuleType(str, Enum):
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    MISSING_RECORD = "MISSING_RECORD"
    UNMATCHED_TRANSACTION = "UNMATCHED_TRANSACTION"
    LATE_SETTLEMENT = "LATE_SETTLEMENT"
    FEE_MISMATCH = "FEE_MISMATCH"
    REFUND_VERIFICATION = "REFUND_VERIFICATION"
    ORPHAN_RECORD = "ORPHAN_RECORD"
    STATUS_MISMATCH = "STATUS_MISMATCH"
    MISSING_INVOICE = "MISSING_INVOICE"

class TransactionSource(str, Enum):
    BANK = "Bank"
    PAYMENT_GATEWAY = "Gateway"
    SETTLEMENT = "Settlement"
    INVOICE = "Invoice"

class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    PARTIALLY_MATCHED = "PARTIALLY_MATCHED"
    UNMATCHED = "UNMATCHED"
    EXCEPTION = "EXCEPTION"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class ErrorDetail(BaseModel):
    field: Optional[str]
    issue: str

class ErrorBody(BaseModel):
    code: str
    message: str
    details: List[ErrorDetail] = []

class ErrorResponse(BaseModel):
    success: bool = False
    request_id: str = Field(default_factory=lambda: request_id_ctx.get())
    error: ErrorBody

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    request_id: str = Field(default_factory=lambda: request_id_ctx.get())
    data: T

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
