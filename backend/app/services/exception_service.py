from typing import List, Optional
from datetime import datetime, timezone
import math

from backend.app.schemas.exceptions import (
    ExceptionFilterParams, PaginatedExceptionsData, ExceptionSummary,
    ExceptionDetailData, TransactionDetail, SortField
)
from backend.app.schemas.common import RuleType, Severity, TransactionSource, PaginationMeta
from backend.app.core.exceptions import APIException
from backend.app.services.state_store import StateStore

class ExceptionService:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    async def get_exceptions(self, filters: ExceptionFilterParams) -> PaginatedExceptionsData:
        run_id = filters.run_id
        if not run_id:
            run_id = self.state_store.latest_run_id
            
        run_data = None
        if run_id:
            run_data = await self.state_store.get_run(run_id)
            
        if not run_data:
            return PaginatedExceptionsData(
                items=[],
                pagination=PaginationMeta(page=1, page_size=filters.page_size, total_items=0, total_pages=0)
            )
            
        exceptions = run_data.get("exceptions", [])
        
        # 1. Filter
        filtered = []
        for exc in exceptions:
            # Severity (OR)
            if filters.severity and exc.get("severity") not in [s.value for s in filters.severity]:
                continue
                
            # Rule Type (OR)
            if filters.rule_type and exc.get("rule_name") not in [r.value for r in filters.rule_type]:
                continue
                
            # Search
            if filters.search:
                s = filters.search.lower()
                tx_id = str(exc.get("transaction_id", "")).lower()
                desc = str(exc.get("description", "")).lower()
                if s not in tx_id and s not in desc:
                    continue
                    
            filtered.append(exc)
            
        # 2. Sort
        reverse = (filters.sort_order.value == "desc")
        
        def sort_key(exc):
            if filters.sort_by == SortField.CREATED_AT:
                return exc.get("created_at", "")
            elif filters.sort_by == SortField.AMOUNT:
                return exc.get("amount", 0.0)
            elif filters.sort_by == SortField.SEVERITY:
                # Map to integer ordinal LOW=0, MEDIUM=1, HIGH=2, CRITICAL=3
                sev = exc.get("severity", "LOW")
                mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
                return mapping.get(sev, 0)
            elif filters.sort_by == SortField.RULE_TYPE:
                return exc.get("rule_name", "")
            return exc.get("created_at", "")
            
        filtered.sort(key=sort_key, reverse=reverse)
        
        # 3. Paginate
        total_items = len(filtered)
        total_pages = math.ceil(total_items / filters.page_size) if total_items > 0 else 0
        
        start_idx = (filters.page - 1) * filters.page_size
        end_idx = start_idx + filters.page_size
        paginated = filtered[start_idx:end_idx]
        
        # Map to Output Schema
        items = []
        for exc in paginated:
            # Safely parse enums
            try:
                rule_enum = RuleType(exc.get("rule_name"))
            except ValueError:
                rule_enum = RuleType.MISSING_RECORD
                
            try:
                sev_enum = Severity(exc.get("severity"))
            except ValueError:
                sev_enum = Severity.LOW
                
            items.append(ExceptionSummary(
                exception_id=exc.get("exception_id"),
                transaction_id=exc.get("transaction_id"),
                source=TransactionSource.BANK, # Default for now
                rule_type=rule_enum,
                severity=sev_enum,
                amount=exc.get("amount", 0.0),
                currency=exc.get("currency", "USD"),
                description=exc.get("description", ""),
                created_at=datetime.fromisoformat(exc.get("created_at", datetime.now(timezone.utc).isoformat()))
            ))
            
        meta = PaginationMeta(
            page=filters.page,
            page_size=filters.page_size,
            total_items=total_items,
            total_pages=total_pages
        )
        
        return PaginatedExceptionsData(items=items, pagination=meta)

    async def get_exception_detail(self, exception_id: str, run_id: Optional[str] = None) -> ExceptionDetailData:
        if not run_id:
            run_id = self.state_store.latest_run_id
            
        if not run_id:
            raise APIException("RUN_NOT_FOUND", 404, "No run provided and no default available.")
            
        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            raise APIException("RUN_NOT_FOUND", 404, f"No run found with ID {run_id}.")
            
        exceptions = run_data.get("exceptions", [])
        exc = next((e for e in exceptions if e.get("exception_id") == exception_id), None)
        
        if not exc:
            raise APIException("EXCEPTION_NOT_FOUND", 404, f"Exception {exception_id} not found in run {run_id}.")
            
        # Simulate AI explanation generation for the first time
        if "ai_explanation" not in exc or not exc["ai_explanation"]:
            exc["ai_explanation"] = "This is a simulated AI explanation. The root cause is a discrepancy between systems."
            exc["explanation_generated_at"] = datetime.now(timezone.utc).isoformat()
            exc["suggested_action"] = "Review the raw logs and adjust the settlement configuration."
            
            # Save the updated run back to state_store
            # In memory dict is mutated directly, but we might want to re-save to disk
            import json
            from backend.app.core.config import settings
            from pathlib import Path
            report_path = Path(settings.REPORT_DIR) / f"{run_id}.json"
            if report_path.exists():
                with open(report_path, "w") as f:
                    json.dump(run_data, f, default=str)
        
        # Build TransactionDetail
        tx_detail = TransactionDetail(
            transaction_id=exc.get("transaction_id", ""),
            source=TransactionSource.BANK,
            amount=exc.get("amount", 0.0),
            currency=exc.get("currency", "USD"),
            timestamp=datetime.fromisoformat(exc.get("created_at", datetime.now(timezone.utc).isoformat())),
            raw_fields=exc.get("metadata", {})
        )
        
        try:
            rule_enum = RuleType(exc.get("rule_name"))
        except ValueError:
            rule_enum = RuleType.MISSING_RECORD
            
        try:
            sev_enum = Severity(exc.get("severity"))
        except ValueError:
            sev_enum = Severity.LOW

        return ExceptionDetailData(
            exception_id=exc.get("exception_id"),
            transaction=tx_detail,
            related_transactions=[],
            rule_type=rule_enum,
            severity=sev_enum,
            description=exc.get("description", ""),
            ai_explanation=exc.get("ai_explanation"),
            explanation_generated_at=datetime.fromisoformat(exc.get("explanation_generated_at")) if exc.get("explanation_generated_at") else None,
            suggested_action=exc.get("suggested_action")
        )

    async def export_exceptions(self, run_id: Optional[str] = None) -> str:
        import csv
        import io
        if not run_id:
            run_id = self.state_store.latest_run_id
        if not run_id:
            return "Exception ID,Transaction ID,Rule Type,Severity,Amount,Status\n"
            
        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            return "Exception ID,Transaction ID,Rule Type,Severity,Amount,Status\n"
            
        exceptions = run_data.get("exceptions", [])
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Exception ID", "Transaction ID", "Rule Type", "Severity", "Amount", "Status", "Description"])
        
        for exc in exceptions:
            writer.writerow([
                exc.get("exception_id", ""),
                exc.get("transaction_id", ""),
                exc.get("rule_name", ""),
                exc.get("severity", ""),
                exc.get("amount", ""),
                exc.get("status", "OPEN"),
                exc.get("description", "")
            ])
            
        return output.getvalue()

    async def auto_resolve(self, run_id: Optional[str] = None) -> int:
        import json
        from pathlib import Path
        from backend.app.core.config import settings

        if not run_id:
            run_id = self.state_store.latest_run_id
        if not run_id:
            return 0
            
        run_data = await self.state_store.get_run(run_id)
        if not run_data:
            return 0
            
        exceptions = run_data.get("exceptions", [])
        count = 0
        for exc in exceptions:
            # We'll mark LOW severity or specific ones as RESOLVED for this demo.
            if exc.get("status", "OPEN") != "RESOLVED" and exc.get("severity", "LOW") == "LOW":
                exc["status"] = "RESOLVED"
                count += 1
                
        # Save state
        report_path = Path(settings.REPORT_DIR) / f"{run_id}.json"
        if report_path.exists():
            with open(report_path, "w") as f:
                json.dump(run_data, f, default=str)
                
        return count
