from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Dict, Any, Optional

from backend.app.schemas.common import ErrorResponse, ErrorBody, ErrorDetail

class APIException(Exception):
    def __init__(self, code: str, http_status: int, message: str, details: Optional[List[ErrorDetail]] = None):
        self.code = code
        self.http_status = http_status
        self.message = message
        self.details = details or []

class ValidationException(APIException):
    def __init__(self, details: List[ErrorDetail]):
        super().__init__("VALIDATION_ERROR", status.HTTP_422_UNPROCESSABLE_ENTITY, "Request validation failed.", details)

# --- Exception Handlers ---

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    error_body = ErrorBody(code=exc.code, message=exc.message, details=exc.details)
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(success=False, error=error_body).model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        issue = error["msg"]
        details.append(ErrorDetail(field=field, issue=issue))
        
    error_body = ErrorBody(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        details=details
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(success=False, error=error_body).model_dump()
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # In a real app we would log the full traceback here using core/logging.py
    error_body = ErrorBody(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(success=False, error=error_body).model_dump()
    )
