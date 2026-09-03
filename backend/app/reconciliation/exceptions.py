from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import uuid

@dataclass
class ExceptionRecord:
    transaction_id: str
    rule_name: str
    severity: str
    title: str
    description: str
    affected_datasets: List[str]
    recommended_action: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    exception_id: str = field(default_factory=lambda: f"EXC_{uuid.uuid4().hex[:8].upper()}")

@dataclass
class MatchedRecord:
    transaction_id: str
    bank_records: List[Dict[str, Any]] = field(default_factory=list)
    gateway_records: List[Dict[str, Any]] = field(default_factory=list)
    settlement_records: List[Dict[str, Any]] = field(default_factory=list)
    invoice_records: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_orphan(self) -> bool:
        """Returns True if the transaction only exists in ONE dataset."""
        presence = sum([
            len(self.bank_records) > 0,
            len(self.gateway_records) > 0,
            len(self.settlement_records) > 0,
            len(self.invoice_records) > 0
        ])
        return presence == 1
    
    @property
    def is_empty(self) -> bool:
        return sum([
            len(self.bank_records),
            len(self.gateway_records),
            len(self.settlement_records),
            len(self.invoice_records)
        ]) == 0

@dataclass
class ReconciliationResult:
    total_transactions: int
    matched_records: List[MatchedRecord]
    exceptions: List[ExceptionRecord]
    metrics: Dict[str, Any]
    summary: Dict[str, Any]
