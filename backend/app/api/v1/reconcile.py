from fastapi import APIRouter, Depends
from backend.app.schemas.reconcile import ReconcileRequest, ReconcileResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.services.reconciliation_service import ReconciliationService
from backend.app.core.dependencies import get_state_store

router = APIRouter()

def get_reconciliation_service(state_store = Depends(get_state_store)) -> ReconciliationService:
    return ReconciliationService(state_store)

@router.post("/reconcile", response_model=SuccessResponse[ReconcileResponseData])
async def reconcile_batch(
    request: ReconcileRequest,
    reconciliation_service: ReconciliationService = Depends(get_reconciliation_service)
):
    result = await reconciliation_service.reconcile(request)
    return SuccessResponse(data=result)

@router.post("/reset", response_model=SuccessResponse[dict])
async def reset_state(state_store = Depends(get_state_store)):
    await state_store.reset()
    return SuccessResponse(data={"message": "Application state reset to empty state successfully"})
