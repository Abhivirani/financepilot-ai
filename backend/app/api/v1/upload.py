from fastapi import APIRouter, UploadFile, File, Depends
from typing import Optional

from backend.app.schemas.upload import UploadResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.services.upload_service import UploadService
from backend.app.core.dependencies import get_state_store

router = APIRouter()

def get_upload_service(state_store = Depends(get_state_store)) -> UploadService:
    return UploadService(state_store)

@router.post("/upload", response_model=SuccessResponse[UploadResponseData], status_code=201)
async def upload_files(
    bank_statement: Optional[UploadFile] = File(None),
    payment_gateway: Optional[UploadFile] = File(None),
    settlement_report: Optional[UploadFile] = File(None),
    invoice: Optional[UploadFile] = File(None),
    upload_service: UploadService = Depends(get_upload_service)
):
    result = await upload_service.process_uploads(
        bank_statement, 
        payment_gateway, 
        settlement_report, 
        invoice
    )
    return SuccessResponse(data=result)
