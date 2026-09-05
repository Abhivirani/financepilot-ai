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

@router.post("/upload/demo", response_model=SuccessResponse[UploadResponseData], status_code=201)
async def upload_demo_dataset(
    upload_service: UploadService = Depends(get_upload_service)
):
    import io
    import csv
    from backend.app.data_generation.generator import generate_base_data
    from backend.app.data_generation.anomaly_injector import AnomalyInjector
    from backend.app.data_generation.config import AnomalyConfig
    
    # Generate 50 transactions with anomalies
    raw_data = generate_base_data(50)
    config = AnomalyConfig(
        amount_mismatch=5,
        duplicate=2,
        missing_settlement=2,
        orphan=1,
        fee_mismatch=5
    )
    injector = AnomalyInjector(config)
    demo_data = injector.inject(raw_data)
    
    def create_upload_file(data: list[dict], filename: str) -> UploadFile:
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        file_bytes = output.getvalue().encode('utf-8')
        return UploadFile(file=io.BytesIO(file_bytes), filename=filename)
        
    bank = create_upload_file(demo_data["bank"], "demo_bank_statement.csv")
    gateway = create_upload_file(demo_data["gateway"], "demo_payment_gateway.csv")
    settlement = create_upload_file(demo_data["settlement"], "demo_settlement_report.csv")
    invoice = create_upload_file(demo_data["invoice"], "demo_invoice.csv")
    
    result = await upload_service.process_uploads(bank, gateway, settlement, invoice)
    return SuccessResponse(data=result)

