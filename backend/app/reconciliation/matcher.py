import pandas as pd
from typing import Dict, List
from collections import defaultdict
from backend.app.reconciliation.constants import DatasetName
from backend.app.reconciliation.exceptions import MatchedRecord

class RecordMatcher:
    def match(self, datasets: Dict[DatasetName, pd.DataFrame]) -> List[MatchedRecord]:
        """
        Groups all records from all datasets by transaction_id into MatchedRecord objects.
        """
        # Dictionary to hold matched records by transaction_id
        # Note: If a record has no transaction_id (or NaN), it shouldn't normally happen, 
        # but we dropna to be safe or treat it as a special case. 
        # For our synthetic data, transaction_id is always present.
        
        matched_dict: Dict[str, MatchedRecord] = {}
        
        def get_or_create(txn_id: str) -> MatchedRecord:
            if pd.isna(txn_id) or not str(txn_id).strip():
                # For genuinely missing transaction_ids, we could generate a dummy ID to treat as orphan
                txn_id = "MISSING_TXN_ID"
            
            txn_id = str(txn_id)
            if txn_id not in matched_dict:
                matched_dict[txn_id] = MatchedRecord(transaction_id=txn_id)
            return matched_dict[txn_id]

        # Process Bank
        if DatasetName.BANK in datasets:
            bank_records = datasets[DatasetName.BANK].to_dict('records')
            for record in bank_records:
                mr = get_or_create(record.get('transaction_id'))
                mr.bank_records.append(record)
                
        # Process Gateway
        if DatasetName.GATEWAY in datasets:
            gw_records = datasets[DatasetName.GATEWAY].to_dict('records')
            for record in gw_records:
                mr = get_or_create(record.get('transaction_id'))
                mr.gateway_records.append(record)

        # Process Settlement
        if DatasetName.SETTLEMENT in datasets:
            set_records = datasets[DatasetName.SETTLEMENT].to_dict('records')
            for record in set_records:
                mr = get_or_create(record.get('transaction_id'))
                mr.settlement_records.append(record)

        # Process Invoice
        if DatasetName.INVOICE in datasets:
            inv_records = datasets[DatasetName.INVOICE].to_dict('records')
            for record in inv_records:
                mr = get_or_create(record.get('transaction_id'))
                mr.invoice_records.append(record)
                
        return list(matched_dict.values())
