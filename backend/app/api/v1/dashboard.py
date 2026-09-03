from fastapi import APIRouter, Depends, Query
from typing import Optional

from backend.app.schemas.dashboard import DashboardResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.services.dashboard_service import DashboardService
from backend.app.core.dependencies import get_state_store

router = APIRouter()

def get_dashboard_service(state_store = Depends(get_state_store)) -> DashboardService:
    return DashboardService(state_store)

@router.get("/dashboard", response_model=SuccessResponse[DashboardResponseData])
async def get_dashboard(
    run_id: Optional[str] = Query(None, description="The ID of the run to fetch. Defaults to latest."),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    result = await dashboard_service.get_dashboard(run_id)
    return SuccessResponse(data=result)
