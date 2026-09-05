import pandas as pd
import io
from typing import List, Dict, Set, Optional, Tuple
from fastapi import UploadFile
from datetime import datetime, timezone
import aiofiles
from pathlib import Path

from backend.app.schemas.upload import FileValidationSummary, BatchStatus, UploadResponseData
from backend.app.schemas.common import TransactionSource
from backend.app.core.exceptions import APIException
from backend.app.core.config import settings
from backend.app.services.state_store import StateStore

COLUMN_ALIASES: Dict[str, List[str]] = {
    "bank_txn_id": ["bank_txn_id", "bank_transaction_id", "bank_ref", "bank_reference", "bank_id", "utr", "id", "txn_id"],
    "transaction_id": ["transaction_id", "txn_id", "txnid", "order_id", "merchant_txn_id", "reference_id", "ref_id"],
    "gateway_txn_id": ["gateway_txn_id", "pg_txn_id", "gateway_transaction_id", "payment_id", "razorpay_payment_id", "pg_id"],
    "settlement_id": ["settlement_id", "settlement_txn_id", "set_id", "settlement_number", "payout_id"],
    "invoice_id": ["invoice_id", "inv_id", "invoice_number", "invoice_no", "bill_id"],
    "date": ["date", "txn_date", "created_at", "timestamp", "transaction_date", "time", "invoice_date"],
    "settlement_date": ["settlement_date", "settled_at", "payout_date", "settlement_time"],
    "amount": ["amount", "total", "value", "net_amount", "txn_amount"],
    "gross_amount": ["gross_amount", "gross", "total_amount", "amount", "invoice_amount"],
    "net_amount": ["net_amount", "net", "settlement_amount", "payout_amount", "amount"],
    "total_amount": ["total_amount", "amount", "gross_amount", "invoice_amount"],
    "fee": ["fee", "fees", "commission", "charge", "gateway_fee"],
    "fee_deducted": ["fee_deducted", "fee", "deduction", "total_fee"],
    "status": ["status", "state", "txn_status", "payment_status"],
    "type": ["type", "txn_type", "transaction_type", "credit_debit"]
}


class UploadService:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        
        self.required_columns = {
            TransactionSource.BANK: {"bank_txn_id", "transaction_id", "date", "amount", "type"},
            TransactionSource.PAYMENT_GATEWAY: {"gateway_txn_id", "transaction_id", "date", "gross_amount", "fee", "status"},
            TransactionSource.SETTLEMENT: {"settlement_id", "transaction_id", "gateway_txn_id", "settlement_date", "gross_amount", "net_amount", "fee_deducted"},
            TransactionSource.INVOICE: {"invoice_id", "transaction_id", "date", "total_amount", "status"}
        }

    def _normalize_and_alias_columns(self, df: pd.DataFrame, expected_cols: Set[str], source_type: Optional[TransactionSource] = None) -> pd.DataFrame:
        """Clean column headers, map aliases, and synthesize sensible default columns if missing."""
        cleaned_cols = {}
        for original_col in df.columns:
            # Strip BOM, whitespace, quotes, and convert to lower
            c_clean = str(original_col).replace('\ufeff', '').strip().strip('"').strip("'")
            c_lower = c_clean.lower()
            
            mapped_name = c_clean
            # Check if clean name matches expected columns directly (case-insensitive)
            for exp in expected_cols:
                if c_lower == exp.lower():
                    mapped_name = exp
                    break
            else:
                # Check alias mapping if direct match not found
                for exp in expected_cols:
                    aliases = COLUMN_ALIASES.get(exp, [])
                    if c_lower in [a.lower() for a in aliases]:
                        mapped_name = exp
                        break

            cleaned_cols[original_col] = mapped_name
            
        df = df.rename(columns=cleaned_cols)

        # Intelligently synthesize missing required columns where standard defaults apply
        if "type" in expected_cols and "type" not in df.columns:
            df["type"] = "CREDIT"
        if "fee" in expected_cols and "fee" not in df.columns:
            df["fee"] = 0.0
        if "fee_deducted" in expected_cols and "fee_deducted" not in df.columns:
            df["fee_deducted"] = 0.0
        if "status" in expected_cols and "status" not in df.columns:
            df["status"] = "SUCCESS"
        if "transaction_id" in expected_cols and "transaction_id" not in df.columns:
            for alt_id in ["bank_txn_id", "gateway_txn_id", "settlement_id", "invoice_id", "reference_id", "order_id"]:
                if alt_id in df.columns:
                    df["transaction_id"] = df[alt_id]
                    break
        if "gateway_txn_id" in expected_cols and "gateway_txn_id" not in df.columns:
            for alt_id in ["transaction_id", "settlement_id", "order_id", "bank_txn_id"]:
                if alt_id in df.columns:
                    df["gateway_txn_id"] = df[alt_id]
                    break
        if "gross_amount" in expected_cols and "gross_amount" not in df.columns:
            for alt_amt in ["net_amount", "amount", "total_amount"]:
                if alt_amt in df.columns:
                    df["gross_amount"] = df[alt_amt]
                    break
        if "net_amount" in expected_cols and "net_amount" not in df.columns:
            for alt_amt in ["gross_amount", "amount", "total_amount"]:
                if alt_amt in df.columns:
                    df["net_amount"] = df[alt_amt]
                    break
        if "total_amount" in expected_cols and "total_amount" not in df.columns:
            for alt_amt in ["amount", "gross_amount", "net_amount"]:
                if alt_amt in df.columns:
                    df["total_amount"] = df[alt_amt]
                    break

        return df

    async def process_uploads(
        self, 
        bank_statement: UploadFile | None, 
        payment_gateway: UploadFile | None, 
        settlement_report: UploadFile | None, 
        invoice: UploadFile | None
    ) -> UploadResponseData:
                              
        files_to_process = [
            (TransactionSource.BANK, bank_statement),
            (TransactionSource.PAYMENT_GATEWAY, payment_gateway),
            (TransactionSource.SETTLEMENT, settlement_report),
            (TransactionSource.INVOICE, invoice)
        ]
        
        provided_files = [f for t, f in files_to_process if f is not None]
        if len(provided_files) < 2:
            raise APIException("MINIMUM_SOURCES_NOT_MET", 400, "At least two sources must be uploaded.")

        valid_files_count = 0
        file_summaries: List[FileValidationSummary] = []
        total_transactions = 0
        valid_contents = {}
        validation_errors_per_file = []
        
        for source_type, file in files_to_process:
            if not file:
                continue
                
            fname = file.filename or "uploaded_file.csv"
            if not (fname.lower().endswith(".csv") or fname.lower().endswith(".xlsx") or fname.lower().endswith(".xls")):
                validation_errors_per_file.append(f"✗ {fname}: Unsupported format (must be .csv or .xlsx)")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=0,
                    column_count=0,
                    is_valid=False,
                    warnings=["UNSUPPORTED_FORMAT: File must be .csv or .xlsx"]
                ))
                continue
                
            content = await file.read()
            if len(content) == 0:
                validation_errors_per_file.append(f"✗ {fname}: File is empty (0 bytes)")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=0,
                    column_count=0,
                    is_valid=False,
                    warnings=["EMPTY_FILE: File contains 0 bytes"]
                ))
                continue

            if len(content) > settings.MAX_FILE_SIZE_BYTES:
                validation_errors_per_file.append(f"✗ {fname}: File exceeds maximum size of {settings.MAX_FILE_SIZE_BYTES} bytes")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=0,
                    column_count=0,
                    is_valid=False,
                    warnings=[f"FILE_TOO_LARGE: Exceeds {settings.MAX_FILE_SIZE_BYTES} bytes"]
                ))
                continue
                
            # Decode file with encodings fallback
            df = None
            decode_error = None
            if fname.lower().endswith(".xlsx") or fname.lower().endswith(".xls"):
                try:
                    df = pd.read_excel(io.BytesIO(content))
                except Exception as e:
                    decode_error = str(e)
            else:
                for enc in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'utf-16', 'utf-16le']:
                    try:
                        text = content.decode(enc)
                        df = pd.read_csv(io.StringIO(text))
                        break
                    except (UnicodeDecodeError, Exception) as e:
                        decode_error = str(e)
                        continue
            
            if df is None:
                validation_errors_per_file.append(f"✗ {fname}: Could not parse CSV data ({decode_error})")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=0,
                    column_count=0,
                    is_valid=False,
                    warnings=["PARSE_ERROR: Failed to read CSV structure"]
                ))
                continue

            if len(df) == 0:
                validation_errors_per_file.append(f"✗ {fname}: Has header but contains 0 data rows")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=0,
                    column_count=0,
                    is_valid=False,
                    warnings=["EMPTY_DATASET: 0 rows found"]
                ))
                continue

            if len(df) > settings.MAX_BATCH_SIZE:
                validation_errors_per_file.append(f"✗ {fname}: Has {len(df)} rows, exceeding limit of {settings.MAX_BATCH_SIZE}")
                file_summaries.append(FileValidationSummary(
                    source_type=source_type,
                    filename=fname,
                    row_count=len(df),
                    column_count=len(df.columns),
                    is_valid=False,
                    warnings=[f"ROW_LIMIT_EXCEEDED: {len(df)} > {settings.MAX_BATCH_SIZE}"]
                ))
                continue

            # Validate & normalize columns
            expected_cols = self.required_columns[source_type]
            df = self._normalize_and_alias_columns(df, expected_cols)
            actual_cols = set(df.columns)
            missing = expected_cols - actual_cols
            
            is_valid = True
            warnings = []
            
            if missing:
                is_valid = False
                sorted_missing = sorted(list(missing))
                actual_list = sorted(list(df.columns))
                err_detail = f"Missing required column(s): {sorted_missing}. (Found columns: {actual_list})"
                warnings.append(f"MISSING_REQUIRED_COLUMNS: {sorted_missing}")
                validation_errors_per_file.append(f"✗ {fname}: {err_detail}")
            else:
                validation_errors_per_file.append(f"✓ {fname}: Parsed successfully ({len(df)} rows)")
            
            if is_valid:
                valid_files_count += 1
                total_transactions += len(df)
                # Re-export clean UTF-8 CSV content
                out_buf = io.StringIO()
                df.to_csv(out_buf, index=False)
                valid_contents[source_type] = out_buf.getvalue().encode('utf-8')

            file_summaries.append(FileValidationSummary(
                source_type=source_type,
                filename=fname,
                row_count=len(df),
                column_count=len(df.columns),
                is_valid=is_valid,
                warnings=warnings
            ))
            
        if valid_files_count < 2:
            breakdown_str = "\n".join(validation_errors_per_file)
            err_message = f"Fewer than two valid sources successfully processed.\n\nFile Processing Breakdown:\n{breakdown_str}"
            raise APIException("MINIMUM_SOURCES_NOT_MET", 400, err_message)
            
        batch_status = BatchStatus.VALIDATED if valid_files_count == len(provided_files) else BatchStatus.PARTIALLY_VALID
        
        summary_dict = {
            "uploaded_at": datetime.now(timezone.utc),
            "files": [s.model_dump() for s in file_summaries],
            "total_transactions": total_transactions,
            "status": batch_status.value
        }
        
        batch_id = await self.state_store.create_batch(summary_dict)
        
        batch_dir = Path(settings.UPLOAD_DIR) / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        for source_type, content in valid_contents.items():
            expected_filename = f"{source_type.value}.csv"
            async with aiofiles.open(batch_dir / expected_filename, 'wb') as out_file:
                await out_file.write(content)
                
        # Write default headers for missing sources so engine won't crash
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
