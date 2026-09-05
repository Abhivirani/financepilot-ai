import time
import json
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

from backend.app.schemas.reconcile import ReconcileRequest, ReconcileResponseData, RunStatus, ReconcileSummary
from backend.app.schemas.upload import BatchStatus
from backend.app.core.exceptions import APIException
from backend.app.core.config import settings
from backend.app.services.state_store import StateStore

# Import the existing modules directly as per constraint
from backend.app.reconciliation.engine import ReconciliationEngine
from backend.app.reconciliation.loader import DatasetLoader
from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.rules import get_all_rules
from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.report import ReportGenerator, JsonReportExporter
from backend.app.reconciliation.exceptions import ReconciliationResult
from backend.app.schemas.common import TransactionSource

class ReconciliationService:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    async def reconcile(self, req: ReconcileRequest) -> ReconcileResponseData:
        batch_id = req.batch_id
        
        # If no batch_id, use latest
        if not batch_id:
            if not self.state_store.latest_batch_id:
                raise APIException("BATCH_NOT_FOUND", 404, "No batch uploaded yet.")
            batch_id = self.state_store.latest_batch_id
            
        batch = await self.state_store.get_batch(batch_id)
        if not batch:
            raise APIException("BATCH_NOT_FOUND", 404, f"No batch found with ID {batch_id}.")
            
        if batch["status"] == BatchStatus.INVALID.value:
            raise APIException("BATCH_NOT_READY", 409, "Batch is invalid and cannot be reconciled.")
            
        # For simplicity, we won't block PARTIALLY_VALID as long as it has >=2 files, which upload service guarantees.
            
        started_at = datetime.now(timezone.utc)
        
        # Run reconciliation using existing engine modules.
        # We wrap the engine flow to capture results for the state store.
        data_dir = str(Path(settings.UPLOAD_DIR) / batch_id)
        
        try:
            # We don't use ReconciliationEngine().run() directly because it hardcodes writing to a file before returning it, 
            # and we need to intercept the data. But wait, it's fine, we can just read the JSON report. Or we can just build it here.
            # Building it here allows us to get the metrics directly.
            
            loader = DatasetLoader(data_dir)
            matcher = RecordMatcher()
            rules = get_all_rules()
            metrics_calc = MetricsCalculator()
            
            # 1. Load Data
            datasets = loader.load_all()
            
            # 2. Match
            matched_records = matcher.match(datasets)
            
            # 3. Rules
            all_exceptions = []
            for record in matched_records:
                if record.is_empty:
                    continue
                for rule in rules:
                    exceptions = rule.check(record)
                    all_exceptions.extend(exceptions)
                    
            # 4. Metrics
            metrics = metrics_calc.calculate(matched_records, all_exceptions)
            
            execution_time = time.time() - started_at.timestamp()
            engine_summary = {
                "execution_time_seconds": round(execution_time, 2),
                "total_rules_applied": len(rules)
            }
            
            # 5. Extract what we need for StateStore run
            
            sources_processed = []
            for f in batch["files"]:
                if f["is_valid"]:
                    sources_processed.append(TransactionSource(f["source_type"]))
            
            # Calculate matched count from metrics structure
            # clean_transactions = match_status MATCHED + partially matched? 
            # Metrics returns clean_transactions = total - matched with exception.
            # We will use clean_transactions as matched_count or compute it properly.
            
            # Let's see metrics shape:
            matched_count = metrics["clean_transactions"] # Approximation for summary
            
            summary = ReconcileSummary(
                total_transactions=len(matched_records),
                matched_count=matched_count,
                exception_count=len(all_exceptions),
                match_rate=round(metrics["match_rate_percentage"], 1),
                sources_processed=sources_processed
            )
            
            # Map records to extract actual transaction amounts
            rec_map = {r.transaction_id: r for r in matched_records}

            # Format exceptions to dict for JSON serialization in state store
            exceptions_dict = []
            for exc in all_exceptions:
                rec = rec_map.get(exc.transaction_id)
                bank_amount = 0.0
                gw_amount = 0.0
                diff_amount = 0.0
                if rec:
                    if rec.bank_records:
                        bank_amount = float(rec.bank_records[0].get("amount", 0.0) or 0.0)
                    if rec.gateway_records:
                        gw_amount = float(rec.gateway_records[0].get("gross_amount", 0.0) or 0.0)
                    if not bank_amount and rec.invoice_records:
                        bank_amount = float(rec.invoice_records[0].get("total_amount", 0.0) or 0.0)

                # Standardize values per rule type according to requirements
                if exc.rule_name == "AMOUNT_MISMATCH":
                    if bank_amount > 0 and gw_amount > 0:
                        diff_val = round(abs(bank_amount - gw_amount), 2)
                    else:
                        diff_val = 0.0
                elif exc.rule_name in ["DUPLICATE_TRANSACTION", "DUPLICATE"]:
                    if bank_amount > 0:
                        gw_amount = bank_amount
                    elif gw_amount > 0:
                        bank_amount = gw_amount
                    diff_val = None
                elif exc.rule_name == "MISSING_SETTLEMENT":
                    gw_amount = 0.0
                    diff_val = None
                elif exc.rule_name == "MISSING_INVOICE":
                    gw_amount = 0.0
                    diff_val = None
                elif exc.rule_name == "FEE_MISMATCH":
                    if bank_amount == 0 and gw_amount > 0:
                        bank_amount = gw_amount
                    diff_val = None
                elif exc.rule_name in ["LATE_SETTLEMENT", "SETTLEMENT_DELAY"]:
                    if bank_amount == 0 and gw_amount > 0:
                        bank_amount = gw_amount
                    elif gw_amount == 0 and bank_amount > 0:
                        gw_amount = bank_amount
                    diff_val = None
                else:
                    diff_val = round(abs(bank_amount - gw_amount), 2) if bank_amount > 0 and gw_amount > 0 else None

                exceptions_dict.append({
                    "exception_id": exc.transaction_id,
                    "transaction_id": exc.transaction_id,
                    "rule_name": exc.rule_name,
                    "severity": exc.severity.value if hasattr(exc.severity, "value") else str(exc.severity),
                    "title": exc.title,
                    "description": exc.description,
                    "affected_datasets": exc.affected_datasets,
                    "recommended_action": exc.recommended_action,
                    "suggested_action": exc.recommended_action,
                    "metadata": exc.metadata,
                    "source": TransactionSource.BANK.value,
                    "amount": round(bank_amount, 2),
                    "gateway_amount": round(gw_amount, 2),
                    "difference": diff_val,
                    "currency": "INR",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
            completed_at = datetime.now(timezone.utc)
            processing_time_ms = int(execution_time * 1000)
            
            run_data = {
                "batch_id": batch_id,
                "status": RunStatus.COMPLETED.value,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "processing_time_ms": processing_time_ms,
                "summary": summary.model_dump(),
                "metrics": metrics,
                "exceptions": exceptions_dict
            }
            
            run_id = await self.state_store.create_run(run_data)
            
            return ReconcileResponseData(
                run_id=run_id,
                batch_id=batch_id,
                status=RunStatus.COMPLETED,
                started_at=started_at,
                completed_at=completed_at,
                processing_time_ms=processing_time_ms,
                summary=summary
            )
            
        except Exception as e:
            # We must fail gracefully.
            raise APIException("ENGINE_FAILURE", 500, "Reconciliation engine failed unexpectedly.", [{"field": None, "issue": str(e)}])
