from pydantic import BaseModel, ConfigDict

class AIExplainRequest(BaseModel):
    exception_id: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "exception_id": "exc-123"
            }
        }
    )

class AIExplainResponseData(BaseModel):
    summary: str
    markdown: str
    confidence: int
    latency_ms: int

class AIDashboardSummaryResponseData(BaseModel):
    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    generated_at: str

class AIChatRequest(BaseModel):
    message: str

class AIChatResponseData(BaseModel):
    answer: str
    confidence: int
    latency_ms: int
    generated_at: str

class AIExecutiveReportResponseData(BaseModel):
    title: str
    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    generated_at: str
