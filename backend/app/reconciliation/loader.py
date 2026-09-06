import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from backend.app.reconciliation.constants import DatasetName

class DatasetLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
        self.required_columns = {
            DatasetName.BANK: ["bank_txn_id", "transaction_id", "date", "amount", "type"],
            DatasetName.GATEWAY: ["gateway_txn_id", "transaction_id", "date", "gross_amount", "fee", "status"],
            DatasetName.SETTLEMENT: ["settlement_id", "transaction_id", "gateway_txn_id", "settlement_date", "gross_amount", "net_amount", "fee_deducted"],
            DatasetName.INVOICE: ["invoice_id", "transaction_id", "date", "total_amount", "status"]
        }

    def _validate_file_exists(self, filepath: Path) -> bool:
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset file not found: {filepath}")
        return True

    def _validate_columns(self, df: pd.DataFrame, dataset_name: DatasetName) -> None:
        required = set(self.required_columns[dataset_name])
        actual = set(df.columns)
        missing = required - actual
        if missing:
            raise ValueError(f"Missing required columns in {dataset_name.value}: {missing}")

    def _normalize_bank(self, df: pd.DataFrame) -> pd.DataFrame:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def _normalize_gateway(self, df: pd.DataFrame) -> pd.DataFrame:
        df["gross_amount"] = pd.to_numeric(df["gross_amount"], errors="coerce").fillna(0.0)
        df["fee"] = pd.to_numeric(df["fee"], errors="coerce").fillna(0.0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def _normalize_settlement(self, df: pd.DataFrame) -> pd.DataFrame:
        df["gross_amount"] = pd.to_numeric(df["gross_amount"], errors="coerce").fillna(0.0)
        df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0.0)
        df["fee_deducted"] = pd.to_numeric(df["fee_deducted"], errors="coerce").fillna(0.0)
        df["settlement_date"] = pd.to_datetime(df["settlement_date"], errors="coerce")
        return df

    def _normalize_invoice(self, df: pd.DataFrame) -> pd.DataFrame:
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0.0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def load_all(self) -> Dict[DatasetName, pd.DataFrame]:
        """Loads, validates, and normalizes all 4 required datasets."""
        datasets = {}
        
        # Mapping of DatasetName to file names and normalization functions
        mappings = {
            DatasetName.BANK: ("Bank.csv", self._normalize_bank),
            DatasetName.GATEWAY: ("Gateway.csv", self._normalize_gateway),
            DatasetName.SETTLEMENT: ("Settlement.csv", self._normalize_settlement),
            DatasetName.INVOICE: ("Invoice.csv", self._normalize_invoice),
        }
        
        for name, (filename, normalizer) in mappings.items():
            filepath = self.data_dir / filename
            self._validate_file_exists(filepath)
            
            df = pd.read_csv(filepath)
            if len(df) == 0:
                raise ValueError(f"{filename} contains no records.")
                
            self._validate_columns(df, name)
            df = normalizer(df)
            
            print(f"Dataset : {name.value}")
            print(f"Rows : {len(df)}")
            print(f"Columns :\n{list(df.columns)}")
            
            datasets[name] = df
            
        return datasets
