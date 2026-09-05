import json
from backend.app.data_generation.generator import generate_base_data
from backend.app.data_generation.anomaly_injector import AnomalyInjector
from backend.app.data_generation.config import AnomalyConfig
from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.rules import get_all_rules
from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.constants import DatasetName
import pandas as pd

raw_data = generate_base_data(50)
config = AnomalyConfig(
    amount_mismatch=5,
    duplicate=2,
    missing_settlement=2,
    orphan=1,
    fee_mismatch=5
)
injector = AnomalyInjector(config)
demo_data = injector.inject(raw_data)

datasets = {
    DatasetName.BANK: pd.DataFrame(demo_data["bank"]),
    DatasetName.GATEWAY: pd.DataFrame(demo_data["gateway"]),
    DatasetName.SETTLEMENT: pd.DataFrame(demo_data["settlement"]),
    DatasetName.INVOICE: pd.DataFrame(demo_data["invoice"])
}

matcher = RecordMatcher()
records = matcher.match(datasets)
rules = get_all_rules()

all_exceptions = []
for record in records:
    for rule in rules:
        all_exceptions.extend(rule.check(record))

calc = MetricsCalculator()
res = calc.calculate(records, all_exceptions)

print("Total Records:", len(records))
print("Total Exceptions:", len(all_exceptions))
print("Metrics:")
print(json.dumps(res, indent=2))
