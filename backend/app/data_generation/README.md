# FinancePilot AI - Synthetic Dataset Generator

This module is responsible for generating realistic synthetic financial datasets (Bank, Gateway, Settlement, and Invoice) to test the reconciliation engine and AI capabilities of FinancePilot AI.

## Architecture

The generation process follows a structured pipeline:
1. **Base Generation (`generator.py`)**: Generates perfect "happy-path" transactions where every `transaction_id` exists perfectly across all datasets, dates are aligned, and amounts exactly match.
2. **Anomaly Injection (`anomaly_injector.py`)**: Applies configurable mutations to the datasets to simulate real-world financial inconsistencies (e.g., missing settlements, fee mismatches, refunds).
3. **Validation (`validator.py`)**: Verifies that the final datasets conform to the expected schemas, differentiating between "unexpected errors" (which indicate bugs in the generator) and "expected anomalies" (which are intentionally injected).
4. **Summary & Export (`summary.py`)**: Exports the CSV files to `datasets/generated/csv/` and generates a detailed JSON report.

## Configuration

Configuration is managed via `config.yaml`. 

```yaml
transactions: 500

anomalies:
  amount_mismatch: 3       # 3% of transactions will have amount mismatches
  duplicate: 2             # 2% will be duplicated
  missing_settlement: 5    # 5% will miss settlements
  missing_invoice: 2       # 2% will miss invoices
  late_settlement: 4       # 4% will have delayed settlements
  refund: 1                # 1% will be refunded
  fee_mismatch: 2          # 2% will have incorrect fees charged
  orphan: 1                # 1% of total transaction count will be generated as orphans
```

You can run the generator and override the transaction count and seed:
```bash
python backend/app/data_generation/generator.py --transactions 1000 --seed 42
```

## Adding New Anomaly Types

To add a new anomaly type, follow these steps:
1. **Configuration**: Add the new anomaly key and default percentage to `config.yaml` and update `AnomalyConfig` in `config.py`.
2. **Injector Logic**:
   - Add a private method like `_inject_new_anomaly(self, datasets, txn_id)` in `anomaly_injector.py`.
   - Update the `inject()` method in `anomaly_injector.py` to allocate a sample of transactions and call your new method.
   - Add a tracking counter in the `__init__` method of `AnomalyInjector`.
3. **Validator**: Update `validator.py` to recognize the new anomaly so it is categorized as an "Expected Anomaly" rather than an "Unexpected Error".
4. **Testing**: Add a unit test in `test_anomaly_injector.py` to verify the logic correctly mutates the data.
