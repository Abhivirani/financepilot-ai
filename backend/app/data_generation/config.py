import yaml
from dataclasses import dataclass, field
from typing import Dict
from pathlib import Path

@dataclass
class AnomalyConfig:
    amount_mismatch_pct: float = 0.0
    duplicate_pct: float = 0.0
    missing_settlement_pct: float = 0.0
    missing_invoice_pct: float = 0.0
    late_settlement_pct: float = 0.0
    refund_pct: float = 0.0
    fee_mismatch_pct: float = 0.0
    orphan_record_pct: float = 0.0

@dataclass
class GeneratorConfig:
    transactions: int = 500
    anomalies: AnomalyConfig = field(default_factory=AnomalyConfig)

def load_config(config_path: str = "config.yaml") -> GeneratorConfig:
    """Loads configuration from a YAML file."""
    base_path = Path(__file__).parent
    full_path = base_path / config_path
    
    if not full_path.exists():
        return GeneratorConfig()

    with open(full_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    transactions = data.get("transactions", 500)
    anomalies_data = data.get("anomalies", {})
    
    anomalies = AnomalyConfig(
        amount_mismatch_pct=anomalies_data.get("amount_mismatch_pct", 0.0),
        duplicate_pct=anomalies_data.get("duplicate_pct", 0.0),
        missing_settlement_pct=anomalies_data.get("missing_settlement_pct", 0.0),
        missing_invoice_pct=anomalies_data.get("missing_invoice_pct", 0.0),
        late_settlement_pct=anomalies_data.get("late_settlement_pct", 0.0),
        refund_pct=anomalies_data.get("refund_pct", 0.0),
        fee_mismatch_pct=anomalies_data.get("fee_mismatch_pct", 0.0),
        orphan_record_pct=anomalies_data.get("orphan_record_pct", 0.0),
    )
    
    return GeneratorConfig(transactions=transactions, anomalies=anomalies)
