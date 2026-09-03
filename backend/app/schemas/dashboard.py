from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

from backend.app.schemas.common import RuleType, Severity

class DashboardMetrics(BaseModel):
    match_rate: float
    total_transactions: int
    matched_transactions: int
    unmatched_transactions: int
    total_exceptions: int
    critical_exceptions: int
    processing_time_ms: int

class ChartDataPoint(BaseModel):
    label: str
    value: float

class DashboardCharts(BaseModel):
    match_status_breakdown: List[ChartDataPoint]
    rule_distribution_chart: List[ChartDataPoint]
    source_volume: List[ChartDataPoint]
    daily_transaction_volume: List[ChartDataPoint]

class RuleDistributionItem(BaseModel):
    rule_type: RuleType
    count: int
    percentage: float

class FinancialSummary(BaseModel):
    total_amount_processed: float
    matched_amount: float
    unmatched_amount: float
    discrepancy_amount: float
    currency: str

class ExceptionPreview(BaseModel):
    exception_id: str
    rule_type: RuleType
    severity: Severity
    transaction_id: str
    amount: float
    created_at: datetime

class DashboardResponseData(BaseModel):
    run_id: str
    generated_at: datetime
    metrics: DashboardMetrics
    charts: DashboardCharts
    rule_distribution: List[RuleDistributionItem]
    financial_summary: FinancialSummary
    recent_exceptions: List[ExceptionPreview]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "r-993d01ab-1a3b-4c2d-98e7",
                "generated_at": "2026-09-03T09:00:00Z",
                "metrics": {
                    "match_rate": 95.5,
                    "total_transactions": 1000,
                    "matched_transactions": 955,
                    "unmatched_transactions": 45,
                    "total_exceptions": 40,
                    "critical_exceptions": 5,
                    "processing_time_ms": 1250
                },
                "charts": {
                    "match_status_breakdown": [{"label": "MATCHED", "value": 955}, {"label": "UNMATCHED", "value": 45}],
                    "rule_distribution_chart": [{"label": "AMOUNT_MISMATCH", "value": 20}],
                    "source_volume": [{"label": "BANK", "value": 500}, {"label": "GATEWAY", "value": 500}],
                    "daily_transaction_volume": [{"label": "2026-09-03", "value": 1000}]
                },
                "rule_distribution": [
                    {
                        "rule_type": "AMOUNT_MISMATCH",
                        "count": 20,
                        "percentage": 50.0
                    }
                ],
                "financial_summary": {
                    "total_amount_processed": 50000.0,
                    "matched_amount": 48000.0,
                    "unmatched_amount": 2000.0,
                    "discrepancy_amount": 0.0,
                    "currency": "USD"
                },
                "recent_exceptions": []
            }
        }
    )
