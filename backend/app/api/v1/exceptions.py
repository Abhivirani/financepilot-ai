from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, List

from backend.app.schemas.exceptions import (
    PaginatedExceptionsData, ExceptionDetailData, ExceptionFilterParams, SortField
)
from backend.app.schemas.common import SuccessResponse, Severity, RuleType, SortOrder
from backend.app.services.exception_service import ExceptionService
from backend.app.core.dependencies import get_state_store

router = APIRouter()

def get_exception_service(state_store = Depends(get_state_store)) -> ExceptionService:
    return ExceptionService(state_store)

@router.get("/exceptions", response_model=SuccessResponse[PaginatedExceptionsData])
async def get_exceptions(
    run_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[List[Severity]] = Query(None),
    rule_type: Optional[List[RuleType]] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    sort_by: SortField = Query(SortField.CREATED_AT),
    sort_order: SortOrder = Query(SortOrder.desc),
    exception_service: ExceptionService = Depends(get_exception_service)
):
    filters = ExceptionFilterParams(
        run_id=run_id,
        page=page,
        page_size=page_size,
        severity=severity,
        rule_type=rule_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    result = await exception_service.get_exceptions(filters)
    return SuccessResponse(data=result)

from fastapi.responses import PlainTextResponse

@router.get("/exceptions/export/csv")
async def export_exceptions_csv(
    run_id: Optional[str] = Query(None),
    exception_service: ExceptionService = Depends(get_exception_service)
):
    csv_data = await exception_service.export_exceptions(run_id)
    return PlainTextResponse(content=csv_data, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename=exceptions_export.csv"
    })

@router.get("/exceptions/{id}", response_model=SuccessResponse[ExceptionDetailData])
async def get_exception_detail(
    id: str = Path(...),
    run_id: Optional[str] = Query(None),
    exception_service: ExceptionService = Depends(get_exception_service)
):
    result = await exception_service.get_exception_detail(id, run_id)
    return SuccessResponse(data=result)

@router.post("/exceptions/auto-resolve")
async def auto_resolve_exceptions(
    run_id: Optional[str] = Query(None),
    exception_service: ExceptionService = Depends(get_exception_service)
):
    count = await exception_service.auto_resolve(run_id)
    return SuccessResponse(data={"resolved_count": count})
