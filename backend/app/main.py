from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler
)
from backend.app.api.v1.router import api_router
from backend.app.core.middleware import LoggingMiddleware
import time

tags_metadata = [
    {
        "name": "Health",
        "description": "Service liveness/readiness.",
    }
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_tags=tags_metadata
)

# Application state
app.state.start_time = time.time()

# Middlewares
app.add_middleware(LoggingMiddleware)

# Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Routers
app.include_router(api_router, prefix="/api/v1")
