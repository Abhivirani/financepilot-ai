import pandas as pd
from typing import List
from backend.app.reconciliation.rules.base_rule import BaseRule
from backend.app.reconciliation.exceptions import ExceptionRecord, MatchedRecord
from backend.app.reconciliation.constants import Severity, RULE_LATE_SETTLEMENT, DatasetName

class LateSettlementRule(BaseRule):
    def __init__(self, allowed_days: int = 1):
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
                try:
                    gw_dt = pd.to_datetime(gw_date)
                    st_dt = pd.to_datetime(st_date)
                    diff = (st_dt - gw_dt).days
                    if diff > self.allowed_days:
                        exceptions.append(
                            self._create_exception(
                                record=record,
                                severity=Severity.LOW,
                                title="Late Settlement",
                                description=f"Settlement delayed by {diff} days.",
                                affected_datasets=[DatasetName.GATEWAY.value, DatasetName.SETTLEMENT.value],
                                recommended_action="Manual Review",
                                metadata={"delay_days": diff, "allowed_days": self.allowed_days}
                            )
                        )
                except Exception:
                    pass

        return exceptions
