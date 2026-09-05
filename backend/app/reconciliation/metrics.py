from typing import List, Dict, Any
from backend.app.reconciliation.exceptions import MatchedRecord, ExceptionRecord
from backend.app.reconciliation.constants import RULE_DUPLICATE

class MetricsCalculator:
    def calculate(self, records: List[MatchedRecord], exceptions: List[ExceptionRecord]) -> Dict[str, Any]:
        """Calculates high-level KPIs based on the matching and rule evaluation results."""
        
        total_transactions = len(records)
        total_exceptions = len(exceptions)
        
        # Calculate Match Rate
        # A record is considered "fully matched" if it has no exceptions (or at least, no high severity exceptions).
        # We will count a transaction as "clean" if it has no exceptions.
        txn_with_exceptions = {exc.transaction_id for exc in exceptions}
        clean_transactions = total_transactions - len(txn_with_exceptions)
        
        match_rate = (clean_transactions / total_transactions * 100) if total_transactions > 0 else 0.0
        exception_rate = (len(txn_with_exceptions) / total_transactions * 100) if total_transactions > 0 else 0.0
        
        duplicate_count = sum(1 for exc in exceptions if exc.rule_name == RULE_DUPLICATE)
        
        # Calculate Financial Totals safely
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

        unmatched_records = [rec for rec in records if rec.transaction_id in txn_with_exceptions]
        unmatched_volume = sum(
            sum(float(bk.get("amount", 0.0) or 0.0) for bk in rec.bank_records)
            for rec in unmatched_records
        )
        
        return {
            "total_transactions": total_transactions,
            "clean_transactions": clean_transactions,
            "total_exceptions": total_exceptions,
            "match_rate_percentage": round(match_rate, 2),
            "exception_rate_percentage": round(exception_rate, 2),
            "duplicate_count": duplicate_count,
            "financials": {
                "total_bank_volume": round(total_bank_volume, 2),
                "total_gateway_volume": round(total_gateway_volume, 2),
                "total_settled_volume": round(total_settled_volume, 2),
                "unmatched_volume": round(unmatched_volume, 2)
            }
        }
