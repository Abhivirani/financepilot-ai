# FinancePilot AI - Backend Reconciliation Engine

This module contains the core deterministic reconciliation engine for FinancePilot AI. It identifies anomalies, missing records, mismatches, and orphan transactions across four financial datasets: Bank, Gateway, Settlement, and Invoice.

## Architecture

The engine is built around a dynamic, rule-based pipeline that separates data loading, grouping, evaluation, and reporting.

1. **Loader (`loader.py`)**: Loads CSV files from the `datasets/` directory, validates required columns, and normalizes standard data types using `pandas`.
2. **Matcher (`matcher.py`)**: Groups all dataset rows by their shared `transaction_id` into `MatchedRecord` dataclasses.
3. **Modular Rule Engine (`rules/`)**: Iterates through the matched records. Each rule is a subclass of `BaseRule` and evaluates a specific business constraint (e.g., `AmountMismatchRule`). Rules return `ExceptionRecord` objects upon detecting anomalies.
4. **Metrics (`metrics.py`)**: Calculates aggregate KPIs (e.g., Match Rate, Total Gateway Volume) based on the engine's output.
5. **Reporter (`report.py`)**: Structured as an Exporter pattern to easily allow future PDF/HTML exports, currently dumping the `ReconciliationResult` to `reconciliation_report.json`.

## Pipeline Execution

To run the reconciliation engine across the currently generated datasets:
```bash
python backend/app/reconciliation/engine.py
```

## Adding New Rules

To add a new deterministic rule:
1. Create a new python file in `backend/app/reconciliation/rules/` (e.g., `my_rule.py`).
2. Subclass `BaseRule` and implement the `check()` method.
3. Return a list of `ExceptionRecord`s using `self._create_exception()` if the rule is violated.
4. Add your rule to `get_all_rules()` in `backend/app/reconciliation/rules/__init__.py`.
5. Add a corresponding unit test in `backend/tests/reconciliation/`.
