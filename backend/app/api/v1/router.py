from fastapi import APIRouter
from backend.app.api.v1 import health, upload, reconcile, dashboard, exceptions, settings, ai

api_router = APIRouter()

api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(reconcile.router, tags=["Reconciliation"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(exceptions.router, tags=["Exceptions"])
api_router.include_router(settings.router, tags=["Settings"])
api_router.include_router(ai.router, tags=["AI"])
api_router.include_router(health.router, tags=["Health"])

