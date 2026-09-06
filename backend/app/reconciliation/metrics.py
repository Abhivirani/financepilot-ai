from typing import List, Dict, Any
from backend.app.reconciliation.exceptions import MatchedRecord, ExceptionRecord
from backend.app.reconciliation.constants import RULE_DUPLICATE

class MetricsCalculator:
    def calculate(self, records: List[MatchedRecord], exceptions: List[ExceptionRecord]) -> Dict[str, Any]:
        """Calculates high-level KPIs based on the matching and rule evaluation results."""
        
        total_transactions = len(records)
        total_exceptions = len(exceptions)
        
        txn_with_exceptions = {exc.transaction_id for exc in exceptions}
        
        # A transaction is matched if it has no exceptions and is not an orphan record
        matched_records = [
            rec for rec in records 
            if rec.transaction_id not in txn_with_exceptions and not rec.is_orphan
        ]
        matched_transactions = len(matched_records)
        
        unmatched_records = [
            rec for rec in records 
            if rec.transaction_id in txn_with_exceptions or rec.is_orphan
        ]
        unmatched_transactions = len(unmatched_records)
        
        match_rate = (matched_transactions / total_transactions * 100) if total_transactions > 0 else 0.0
        exception_rate = (len(txn_with_exceptions) / total_transactions * 100) if total_transactions > 0 else 0.0
        
        duplicate_count = sum(1 for exc in exceptions if exc.rule_name == RULE_DUPLICATE)
        
        def get_rec_amount(rec: MatchedRecord) -> float:
            if rec.bank_records:
                return float(rec.bank_records[0].get("amount", 0.0) or 0.0)
            if rec.gateway_records:
                return float(rec.gateway_records[0].get("gross_amount", 0.0) or 0.0)
            if rec.settlement_records:
                return float(rec.settlement_records[0].get("gross_amount", 0.0) or 0.0)
            if rec.invoice_records:
                return float(rec.invoice_records[0].get("total_amount", 0.0) or 0.0)
            return 0.0

        total_amount_processed = sum(get_rec_amount(rec) for rec in records)
        matched_amount = sum(get_rec_amount(rec) for rec in matched_records)
        unmatched_amount = sum(get_rec_amount(rec) for rec in unmatched_records)
        
        discrepancy_amount = 0.0
        for exc in exceptions:
            if hasattr(exc, "metadata") and isinstance(exc.metadata, dict):
                diff = exc.metadata.get("difference")
                if diff is not None:
                    try:
                        discrepancy_amount += abs(float(diff))
                    except (ValueError, TypeError):
                        pass

        # Also compute volume metrics for backward compatibility
        total_bank_volume = sum(
            sum(float(bk.get("amount", 0.0) or 0.0) for bk in rec.bank_records)
            for rec in records
        )
        total_gateway_volume = sum(
            sum(float(gw.get("gross_amount", 0.0) or 0.0) for gw in rec.gateway_records) 
            for rec in records
        )
        total_settled_volume = sum(
            sum(float(st.get("net_amount", 0.0) or 0.0) for st in rec.settlement_records) 
            for rec in records
        )
        unmatched_volume = sum(get_rec_amount(rec) for rec in unmatched_records)
        
        return {
            "total_transactions": total_transactions,
            "clean_transactions": matched_transactions,
            "matched_transactions": matched_transactions,
            "unmatched_transactions": unmatched_transactions,
            "total_exceptions": total_exceptions,
            "match_rate_percentage": round(match_rate, 2),
            "exception_rate_percentage": round(exception_rate, 2),
            "duplicate_count": duplicate_count,
            "financials": {
                "total_amount_processed": round(total_amount_processed, 2),
                "matched_amount": round(matched_amount, 2),
                "unmatched_amount": round(unmatched_amount, 2),
                "discrepancy_amount": round(discrepancy_amount, 2),
                "total_bank_volume": round(total_bank_volume, 2),
                "total_gateway_volume": round(total_gateway_volume, 2),
                "total_settled_volume": round(total_settled_volume, 2),
                "unmatched_volume": round(unmatched_volume, 2)
            }
        }
