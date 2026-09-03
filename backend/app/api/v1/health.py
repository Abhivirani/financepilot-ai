from fastapi import APIRouter, Request
from backend.app.schemas.common import SuccessResponse
from pydantic import BaseModel, ConfigDict

class HealthResponseData(BaseModel):
    status: str
    version: str
    engine: str
    generator: str
    uptime_seconds: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "engine": "available",
                "generator": "available",
                "uptime_seconds": 3600
            }
        }
    )

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[HealthResponseData])
def health_check(request: Request):
    import backend.app.reconciliation.engine as engine_module
    import backend.app.data_generation.generator as gen_module
    from backend.app.core.config import settings
    
    engine_status = "available" if engine_module else "unavailable"
    generator_status = "available" if gen_module else "unavailable"
    
    import time
    uptime = int(time.time() - request.app.state.start_time) if hasattr(request.app.state, "start_time") else 0
    
    data = HealthResponseData(
        status="healthy",
        version=settings.VERSION,
        engine=engine_status,
        generator=generator_status,
        uptime_seconds=uptime
    )
    return SuccessResponse(data=data)
