import pandas as pd
from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_LATE_SETTLEMENT, DatasetName

class LateSettlementRule(BaseRule):
    def __init__(self, allowed_days: int = 2):
        self.allowed_days = allowed_days

    @property
    def name(self) -> str:
        return RULE_LATE_SETTLEMENT

    def check(self, record: MatchedRecord) -> List[ExceptionRecord]:
        exceptions = []
        
        if record.gateway_records and record.settlement_records:
            gw = record.gateway_records[0]
            st = record.settlement_records[0]
            
            gw_date = gw.get("date")
            st_date = st.get("settlement_date")
            
            if pd.notna(gw_date) and pd.notna(st_date):
                diff = (st_date - gw_date).days
                if diff > self.allowed_days:
                    exceptions.append(
                        self._create_exception(
                            record=record,
                            severity=Severity.LOW,
                            title="Late Settlement",
                            description=f"Settlement took {diff} days, exceeding the SLA of {self.allowed_days} days.",
                            affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                            recommended_action="Monitor for systemic delays and negotiate SLA credits if recurring.",
                            metadata={"delay_days": diff, "allowed_days": self.allowed_days}
                        )
                    )

        return exceptions
