import pandas as pd
from typing import List
from fastapi import UploadFile
from datetime import datetime

from backend.app.schemas.upload import FileValidationSummary, BatchStatus, UploadResponseData
from backend.app.schemas.common import TransactionSource
from backend.app.core.exceptions import APIException
from backend.app.core.config import settings
from backend.app.services.state_store import StateStore
import aiofiles
from pathlib import Path

class UploadService:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        
        self.required_columns = {
            TransactionSource.BANK: {"bank_txn_id", "transaction_id", "date", "amount", "type"},
            TransactionSource.PAYMENT_GATEWAY: {"gateway_txn_id", "transaction_id", "date", "gross_amount", "fee", "status"},
            TransactionSource.SETTLEMENT: {"settlement_id", "transaction_id", "gateway_txn_id", "settlement_date", "gross_amount", "net_amount", "fee_deducted"},
            TransactionSource.INVOICE: {"invoice_id", "transaction_id", "date", "total_amount", "status"}
        }

    async def process_uploads(self, 
                              bank_statement: UploadFile | None, 
                              payment_gateway: UploadFile | None, 
                              settlement_report: UploadFile | None, 
                              invoice: UploadFile | None) -> UploadResponseData:
                              
        files_to_process = [
            (TransactionSource.BANK, bank_statement),
            (TransactionSource.PAYMENT_GATEWAY, payment_gateway),
            (TransactionSource.SETTLEMENT, settlement_report),
            (TransactionSource.INVOICE, invoice)
        ]
        
        valid_files_count = 0
        file_summaries: List[FileValidationSummary] = []
        total_transactions = 0
        
        valid_contents = {}
        
        # Check minimum sources
        provided_files = [f for t, f in files_to_process if f is not None]
        if len(provided_files) < 2:
            raise APIException("MINIMUM_SOURCES_NOT_MET", 400, "At least two sources must be uploaded.")

        # Check for duplicates or oversized files (FastAPI normally handles size via Spooling, but we can do a naive check if we read).
        # We will parse with pandas.
        for source_type, file in files_to_process:
            if not file:
                continue
                
            if not file.filename.endswith(".csv"):
                raise APIException("INVALID_FILE_TYPE", 400, f"File {file.filename} is not a CSV.")
                
            # Read file
            content = await file.read()
            if len(content) == 0:
                raise APIException("EMPTY_FILE", 400, f"File {file.filename} is empty.")
            if len(content) > settings.MAX_FILE_SIZE_BYTES:
                raise APIException("FILE_TOO_LARGE", 413, f"File {file.filename} exceeds {settings.MAX_FILE_SIZE_BYTES} bytes.")
                
            # Parse with pandas
            import io
            try:
                # Try decoding as utf-8
                text = content.decode('utf-8')
                df = pd.read_csv(io.StringIO(text))
            except UnicodeDecodeError:
                raise APIException("UNSUPPORTED_ENCODING", 400, f"File {file.filename} must be UTF-8 encoded.")
            except Exception:
                raise APIException("INVALID_FILE_TYPE", 400, f"File {file.filename} could not be parsed as a valid CSV.")
                
            # Validate row limit
            if len(df) == 0:
                raise APIException("EMPTY_FILE", 400, f"File {file.filename} has no data rows.")
            if len(df) > settings.MAX_BATCH_SIZE:
                raise APIException("ROW_LIMIT_EXCEEDED", 400, f"File {file.filename} has {len(df)} rows, max is {settings.MAX_BATCH_SIZE}.")
                
            # Validate columns
            expected_cols = self.required_columns[source_type]
            actual_cols = set(df.columns)
            missing = expected_cols - actual_cols
            
            is_valid = True
            warnings = []
            
            if missing:
                is_valid = False
                # If this was a hard fail for the whole batch we would raise, but spec says:
                # "If at least two valid source files remain... the batch is marked PARTIALLY_VALID"
                # Wait, "missing required columns fail the file."
                # I will mark is_valid=False and add a warning.
                warnings.append(f"MISSING_REQUIRED_COLUMNS: {missing}")
            
            if is_valid:
                valid_files_count += 1
                total_transactions += len(df)
                valid_contents[source_type] = content
                
            file_summaries.append(FileValidationSummary(
                source_type=source_type,
                filename=file.filename,
                row_count=len(df),
                column_count=len(df.columns),
                is_valid=is_valid,
                warnings=warnings
            ))
            
        if valid_files_count < 2:
            raise APIException("MINIMUM_SOURCES_NOT_MET", 400, "Fewer than two valid sources successfully processed.")
            
        batch_status = BatchStatus.VALIDATED if valid_files_count == len(provided_files) else BatchStatus.PARTIALLY_VALID
        
        summary_dict = {
            "uploaded_at": datetime.utcnow(),
            "files": [s.model_dump() for s in file_summaries],
            "total_transactions": total_transactions,
            "status": batch_status.value
        }
        
        # We need to save files after creating the batch, since we need batch_id.
        # But we already have the content in memory, so we can save it easily.
        batch_id = await self.state_store.create_batch(summary_dict)
        
        batch_dir = Path(settings.UPLOAD_DIR) / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        for source_type, content in valid_contents.items():
            expected_filename = f"{source_type.value}.csv"
            async with aiofiles.open(batch_dir / expected_filename, 'wb') as out_file:
                await out_file.write(content)
                
        # Write empty CSVs for missing sources so DatasetLoader doesn't crash
        for source_type, required_cols in self.required_columns.items():
            if source_type not in valid_contents:
                expected_filename = f"{source_type.value}.csv"
                header = ",".join(list(required_cols)) + "\n"
                async with aiofiles.open(batch_dir / expected_filename, 'w') as out_file:
                    await out_file.write(header)
        
        return UploadResponseData(
            batch_id=batch_id,
            uploaded_at=summary_dict["uploaded_at"],
            files=file_summaries,
            total_transactions=total_transactions,
            status=batch_status
        )
