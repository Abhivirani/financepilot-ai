from fastapi import APIRouter, UploadFile, File, Depends
from typing import Optional, List, Tuple
import io
import csv

from backend.app.schemas.upload import UploadResponseData
from backend.app.schemas.common import SuccessResponse
from backend.app.schemas.reconcile import ReconcileRequest
from backend.app.services.upload_service import UploadService
from backend.app.services.reconciliation_service import ReconciliationService
from backend.app.core.dependencies import get_state_store

router = APIRouter()

def get_upload_service(state_store = Depends(get_state_store)) -> UploadService:
    return UploadService(state_store)

def get_reconciliation_service(state_store = Depends(get_state_store)) -> ReconciliationService:
    return ReconciliationService(state_store)

async def auto_assign_files(
    bank_statement: Optional[UploadFile],
    payment_gateway: Optional[UploadFile],
    settlement_report: Optional[UploadFile],
    invoice: Optional[UploadFile],
    files: Optional[List[UploadFile]]
) -> Tuple[Optional[UploadFile], Optional[UploadFile], Optional[UploadFile], Optional[UploadFile]]:
    """Intelligently map files sent under generic keys or unassigned field names to target source types."""
    assigned_files = {
        "bank": bank_statement,
        "gateway": payment_gateway,
        "settlement": settlement_report,
        "invoice": invoice
    }
    
    if not files:
        return bank_statement, payment_gateway, settlement_report, invoice
        
    for f in files:
        if not f or not f.filename:
            continue
            
        fname = f.filename.lower()
        if not assigned_files["bank"] and ("bank" in fname or "statement" in fname):
            assigned_files["bank"] = f
        elif not assigned_files["gateway"] and ("gateway" in fname or "pg" in fname or "razorpay" in fname or "paytm" in fname or "stripe" in fname):
            assigned_files["gateway"] = f
        elif not assigned_files["settlement"] and ("settlement" in fname or "payout" in fname):
            assigned_files["settlement"] = f
        elif not assigned_files["invoice"] and ("invoice" in fname or "bill" in fname or "sales" in fname):
            assigned_files["invoice"] = f
        else:
            # Inspect first line of file for header-based classification
            try:
                content = await f.read()
                await f.seek(0)
                text = content[:1024].decode('utf-8', errors='ignore').lower()
                if not assigned_files["bank"] and ("bank_txn_id" in text or "bank_ref" in text or "utr" in text):
                    assigned_files["bank"] = f
                elif not assigned_files["gateway"] and ("gateway_txn_id" in text or "pg_txn_id" in text or "payment_id" in text):
                    assigned_files["gateway"] = f
                elif not assigned_files["settlement"] and ("settlement_id" in text or "settlement_date" in text or "fee_deducted" in text):
                    assigned_files["settlement"] = f
                elif not assigned_files["invoice"] and ("invoice_id" in text or "total_amount" in text or "gst_amount" in text):
                    assigned_files["invoice"] = f
                else:
                    # Sequential fallback to first available unassigned slot
                    for slot in ["bank", "gateway", "settlement", "invoice"]:
                        if not assigned_files[slot]:
                            assigned_files[slot] = f
                            break
            except Exception:
                pass
                
    return assigned_files["bank"], assigned_files["gateway"], assigned_files["settlement"], assigned_files["invoice"]

@router.post("/upload", response_model=SuccessResponse[UploadResponseData], status_code=201)
async def upload_files(
    bank_statement: Optional[UploadFile] = File(None),
    payment_gateway: Optional[UploadFile] = File(None),
    settlement_report: Optional[UploadFile] = File(None),
    invoice: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    upload_service: UploadService = Depends(get_upload_service)
):
    b, g, s, i = await auto_assign_files(
        bank_statement, payment_gateway, settlement_report, invoice, files
    )
    result = await upload_service.process_uploads(b, g, s, i)
    return SuccessResponse(data=result)

@router.post("/upload/demo", response_model=SuccessResponse[UploadResponseData], status_code=201)
async def upload_demo_dataset(
    upload_service: UploadService = Depends(get_upload_service)
):
    from backend.app.data_generation.generator import generate_demo_50_dataset
    from backend.app.data_generation.anomaly_injector import AnomalyInjector
    from backend.app.data_generation.config import AnomalyConfig
    
    # Generate 50 transactions with exact deterministic anomalies and volume totals
    demo_data = generate_demo_50_dataset()
    
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
