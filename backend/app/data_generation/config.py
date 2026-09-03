import yaml
from dataclasses import dataclass, field
from typing import Dict
from pathlib import Path

@dataclass
class AnomalyConfig:
    amount_mismatch: int = 0
    duplicate: int = 0
    missing_settlement: int = 0
    missing_invoice: int = 0
    late_settlement: int = 0
    refund: int = 0
    fee_mismatch: int = 0
    orphan: int = 0

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
        amount_mismatch=anomalies_data.get("amount_mismatch", 0),
        duplicate=anomalies_data.get("duplicate", 0),
        missing_settlement=anomalies_data.get("missing_settlement", 0),
        missing_invoice=anomalies_data.get("missing_invoice", 0),
        late_settlement=anomalies_data.get("late_settlement", 0),
        refund=anomalies_data.get("refund", 0),
        fee_mismatch=anomalies_data.get("fee_mismatch", 0),
        orphan=anomalies_data.get("orphan", 0),
    )
    
    return GeneratorConfig(transactions=transactions, anomalies=anomalies)
