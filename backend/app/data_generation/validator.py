from typing import List, Dict, Any, Tuple
from collections import defaultdict

def validate_datasets(datasets: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Validates the generated datasets for schema, positive amounts, unique IDs, 
    cross-dataset relationships, and date consistency.
    """
    errors = []
    
    bank = datasets.get("bank", [])
    gateway = datasets.get("gateway", [])
    settlement = datasets.get("settlement", [])
    invoice = datasets.get("invoice", [])
    
    # Check Required Fields
    for item in bank:
        if not all(k in item for k in ["bank_txn_id", "transaction_id", "date", "amount", "type"]):
            errors.append(f"Bank record {item.get('bank_txn_id')} missing required fields")
    for item in gateway:
        if not all(k in item for k in ["gateway_txn_id", "transaction_id", "date", "gross_amount", "fee", "status"]):
            errors.append(f"Gateway record {item.get('gateway_txn_id')} missing required fields")
    for item in settlement:
        if not all(k in item for k in ["settlement_id", "transaction_id", "gateway_txn_id", "settlement_date", "gross_amount", "net_amount", "fee_deducted"]):
            errors.append(f"Settlement record {item.get('settlement_id')} missing required fields")
    for item in invoice:
        if not all(k in item for k in ["invoice_id", "transaction_id", "date", "total_amount", "status"]):
            errors.append(f"Invoice record {item.get('invoice_id')} missing required fields")

    # Positive Amounts
    for item in bank:
        if item.get("amount", -1) < 0:
            errors.append(f"Bank record {item.get('bank_txn_id')} has negative amount")
    for item in gateway:
        if item.get("gross_amount", -1) < 0 or item.get("fee", -1) < 0:
            errors.append(f"Gateway record {item.get('gateway_txn_id')} has negative amount/fee")
    for item in settlement:
        if item.get("gross_amount", -1) < 0 or item.get("net_amount", -1) < 0 or item.get("fee_deducted", -1) < 0:
            errors.append(f"Settlement record {item.get('settlement_id')} has negative amount/fee")
    for item in invoice:
        if item.get("total_amount", -1) < 0:
            errors.append(f"Invoice record {item.get('invoice_id')} has negative amount")
            
    # Unique IDs
    def check_uniqueness(data: List[Dict[str, Any]], key: str, name: str) -> None:
        seen = set()
        for item in data:
            val = item.get(key)
            if val in seen:
                errors.append(f"Duplicate {name} ID found: {val}")
            seen.add(val)

    check_uniqueness(bank, "bank_txn_id", "Bank")
    check_uniqueness(gateway, "gateway_txn_id", "Gateway")
    check_uniqueness(settlement, "settlement_id", "Settlement")
    check_uniqueness(invoice, "invoice_id", "Invoice")
    
    # Cross-dataset relationships (Happy Path)
    # Every transaction_id should exist in all 4 datasets
    bank_txns = {item["transaction_id"] for item in bank}
    gw_txns = {item["transaction_id"] for item in gateway}
    set_txns = {item["transaction_id"] for item in settlement}
    inv_txns = {item["transaction_id"] for item in invoice}
    
    all_txns = bank_txns.union(gw_txns).union(set_txns).union(inv_txns)
    for txn_id in all_txns:
        if txn_id not in bank_txns:
            errors.append(f"Transaction ID {txn_id} missing in Bank")
        if txn_id not in gw_txns:
            errors.append(f"Transaction ID {txn_id} missing in Gateway")
        if txn_id not in set_txns:
            errors.append(f"Transaction ID {txn_id} missing in Settlement")
        if txn_id not in inv_txns:
            errors.append(f"Transaction ID {txn_id} missing in Invoice")
            
    # Date consistency (Settlement date >= Gateway date)
    gw_dates = {item["transaction_id"]: item["date"] for item in gateway}
    for item in settlement:
        txn_id = item["transaction_id"]
        if txn_id in gw_dates:
            if item["settlement_date"] < gw_dates[txn_id]:
                errors.append(f"Settlement {item['settlement_id']} date is before Gateway date")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors)
    }
