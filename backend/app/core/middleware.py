import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.core.context import request_id_ctx

logger = logging.getLogger("financepilot.api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Custom log adapter to inject request_id
class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        req_id = request_id_ctx.get()
        return msg, dict(kwargs, extra={'request_id': req_id})

api_logger = RequestIdAdapter(logger, {})

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Assign Request ID
        req_id = str(uuid.uuid4())
        token = request_id_ctx.set(req_id)
        
        start_time = time.time()
        
        # Log request start
        api_logger.info(f"Incoming Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log request completion
            process_time_ms = int((time.time() - start_time) * 1000)
            api_logger.info(f"Completed Request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time_ms}ms")
            
            # Inject request_id into response headers just in case
            response.headers["X-Request-ID"] = req_id
            return response
            
        except Exception as e:
            process_time_ms = int((time.time() - start_time) * 1000)
            api_logger.error(f"Failed Request: {request.method} {request.url.path} - Exception: {str(e)} - Duration: {process_time_ms}ms")
            raise
        finally:
            request_id_ctx.reset(token)
