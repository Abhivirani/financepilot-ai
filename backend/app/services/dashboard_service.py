from datetime import datetime, timezone
from typing import Optional

from backend.app.schemas.dashboard import (
    DashboardResponseData, DashboardMetrics, DashboardCharts, 
    ChartDataPoint, RuleDistributionItem, FinancialSummary, ExceptionPreview
)
from backend.app.schemas.common import RuleType, Severity
from backend.app.core.exceptions import APIException
from backend.app.services.state_store import StateStore

class DashboardService:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store

    async def get_dashboard(self, run_id: Optional[str] = None) -> DashboardResponseData:
        if not run_id:
            run_id = self.state_store.latest_run_id
            
        run_data = None
        if run_id:
            run_data = await self.state_store.get_run(run_id)
            
        if not run_data:
            if run_id:
                raise APIException(code="RUN_NOT_FOUND", http_status=404, message=f"Run '{run_id}' not found")
            # Return empty dashboard instead of 404 when no runs exist yet
            return DashboardResponseData(
                run_id="empty-run",
                generated_at=datetime.now(timezone.utc),
                metrics=DashboardMetrics(
                    match_rate=0.0,
                    total_transactions=0,
                    matched_transactions=0,
                    unmatched_transactions=0,
                    total_exceptions=0,
                    critical_exceptions=0,
                    processing_time_ms=0
                ),
                charts=DashboardCharts(
                    match_status_breakdown=[],
                    rule_distribution_chart=[],
                    source_volume=[],
                    daily_transaction_volume=[]
                ),
                rule_distribution=[],
                financial_summary=FinancialSummary(
                    total_amount_processed=0.0,
                    matched_amount=0.0,
                    unmatched_amount=0.0,
                    discrepancy_amount=0.0,
                    currency="INR"
                ),
                recent_exceptions=[]
            )
            
        summary = run_data["summary"]
        metrics = run_data["metrics"]
        exceptions = run_data["exceptions"]
        
        # Calculate critical exceptions
        critical_count = sum(1 for exc in exceptions if exc["severity"] == Severity.CRITICAL.value)
        
        # We need matched/unmatched transactions based on total minus matched, or from metrics.
        # metrics dict structure was defined in reconciliation engine:
        # metrics = { "total_transactions": 505, "clean_transactions": 405, "total_exceptions": 115, "match_rate_percentage": 80.2, ... }
        total_tx = metrics.get("total_transactions", 0)
        clean_tx = metrics.get("clean_transactions", 0)
        unmatched_tx = total_tx - clean_tx
        
        m_rate = summary["match_rate"]
        if m_rate <= 1.0 and m_rate > 0:
            m_rate = m_rate * 100.0
            
        dash_metrics = DashboardMetrics(
            match_rate=round(m_rate, 1),
            total_transactions=total_tx,
            matched_transactions=clean_tx,
            unmatched_transactions=unmatched_tx,
            total_exceptions=len(exceptions),
            critical_exceptions=critical_count,
            processing_time_ms=run_data["processing_time_ms"]
        )
        
        # Build Charts
        # Match Status Breakdown
        match_status_breakdown = [
            ChartDataPoint(label="MATCHED", value=clean_tx),
            ChartDataPoint(label="UNMATCHED", value=unmatched_tx)
        ]
        
        # Rule Distribution
        rule_counts = {}
        for exc in exceptions:
            rt = exc["rule_name"]
            rule_counts[rt] = rule_counts.get(rt, 0) + 1
            
        rule_distribution = []
        rule_distribution_chart = []
        
        total_exceptions = len(exceptions)
        for rt, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_exceptions * 100) if total_exceptions > 0 else 0.0
            
            # Map string name to Enum if possible, otherwise string is fine (Pydantic will coerce or we use string representation)
            # The engine rule names are like "AMOUNT_MISMATCH".
            try:
                rule_enum = RuleType(rt)
            except ValueError:
                # Fallback to closest or exact string if not in enum
                rule_enum = rt 
                
            rule_distribution.append(RuleDistributionItem(
                rule_type=rule_enum,
                count=count,
                percentage=pct
            ))
            rule_distribution_chart.append(ChartDataPoint(label=rt, value=count))
            
        # Source volume - mock or derive from metrics
        # For MVP we can just distribute total equally or look at batch
        batch_id = run_data["batch_id"]
        batch = await self.state_store.get_batch(batch_id)
        source_volume = []
        if batch:
            for f in batch["files"]:
                source_volume.append(ChartDataPoint(label=f["source_type"], value=f["row_count"]))
                
        # Daily volume - simple mock for now, hard to extract without full data
        daily_volume = [ChartDataPoint(label=datetime.now(timezone.utc).strftime("%Y-%m-%d"), value=total_tx)]
        
        charts = DashboardCharts(
            match_status_breakdown=match_status_breakdown,
            rule_distribution_chart=rule_distribution_chart,
            source_volume=source_volume,
            daily_transaction_volume=daily_volume
        )
        
        # Financial summary - extract from metrics financials
        fin = metrics.get("financials", {})
        bank_vol = fin.get("total_bank_volume", fin.get("total_gateway_volume", 0.0))
        settled_vol = fin.get("total_settled_volume", 0.0)
        unmatched_vol = fin.get("unmatched_volume", 0.0)
        
        financial_summary = FinancialSummary(
            total_amount_processed=round(bank_vol, 2),
            matched_amount=round(settled_vol, 2),
            unmatched_amount=round(unmatched_vol, 2),
            discrepancy_amount=round(abs(bank_vol - settled_vol), 2),
            currency="INR"
        )
        
        rule_rank_map = {
            "AMOUNT_MISMATCH": 1,
            "FEE_MISMATCH": 2,
            "DUPLICATE_TRANSACTION": 3,
            "DUPLICATE": 3,
            "MISSING_SETTLEMENT": 4,
            "MISSING_INVOICE": 5,
            "LATE_SETTLEMENT": 6,
            "SETTLEMENT_DELAY": 6,
            "ORPHAN": 7
        }
        sev_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        def sort_key(x):
            rr = rule_rank_map.get(x.get("rule_name"), 99)
            sr = sev_rank.get(x.get("severity"), 4)
            tid = str(x.get("transaction_id", ""))
            num = int(tid.replace("TXN", "")) if tid.replace("TXN", "").isdigit() else 0
            return (sr, rr, -num)

        sorted_exc = sorted(exceptions, key=sort_key)
        recent_exceptions = []
        for exc in sorted_exc[:12]:
            try:
                rule_enum = RuleType(exc["rule_name"])
            except ValueError:
                rule_enum = RuleType.MISSING_RECORD
                
            try:
                sev_enum = Severity(exc["severity"])
            except ValueError:
                sev_enum = Severity.LOW
                
            recent_exceptions.append(ExceptionPreview(
                exception_id=exc["exception_id"],
                rule_type=rule_enum,
                severity=sev_enum,
                transaction_id=exc["transaction_id"],
                amount=exc.get("amount", 0.0),
                gateway_amount=exc.get("gateway_amount", 0.0),
                difference=exc.get("difference", 0.0),
                description=exc.get("description", ""),
                suggested_action=exc.get("suggested_action", exc.get("recommended_action", "")),
                created_at=datetime.fromisoformat(exc.get("created_at", datetime.now(timezone.utc).isoformat()))
            ))
            
        return DashboardResponseData(
            run_id=run_id,
            generated_at=datetime.now(timezone.utc),
            metrics=dash_metrics,
            charts=charts,
            rule_distribution=rule_distribution,
            financial_summary=financial_summary,
            recent_exceptions=recent_exceptions
        )
