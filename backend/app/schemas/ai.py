from pydantic import BaseModel, ConfigDict
from typing import List, Optional

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
    provider: Optional[str] = "Gemini"
    model: Optional[str] = ""
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0

class AIDashboardSummaryResponseData(BaseModel):
    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    generated_at: str
    provider: Optional[str] = "Gemini"
    model: Optional[str] = ""
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0

class AIChatRequest(BaseModel):
    message: str

class AIChatResponseData(BaseModel):
    answer: str
    confidence: int
    latency_ms: int
    generated_at: str
    provider: Optional[str] = "Gemini"
    model: Optional[str] = ""
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0

class AIExecutiveReportResponseData(BaseModel):
    title: str
    summary: str
    markdown: str
    confidence: int
    latency_ms: int
    generated_at: str
    provider: Optional[str] = "Gemini"
    model: Optional[str] = ""
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0

class AIProviderData(BaseModel):
    provider: str
    model: str
    fallback: List[str]
