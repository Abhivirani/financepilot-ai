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
    explanation: str
