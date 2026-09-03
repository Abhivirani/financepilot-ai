from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.app.schemas.ai import AIExplainRequest
from backend.app.schemas.common import ErrorResponse, ErrorBody

router = APIRouter()

@router.post("/ai/explain", response_model=ErrorResponse)
async def explain_exception(req: AIExplainRequest):
    error_body = ErrorBody(
        code="NOT_IMPLEMENTED",
        message="Coming soon"
    )
    return JSONResponse(
        status_code=501,
        content=ErrorResponse(success=False, error=error_body).model_dump()
    )
