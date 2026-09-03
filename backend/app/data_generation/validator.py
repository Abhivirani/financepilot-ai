from typing import List, Dict, Any, Tuple
from collections import defaultdict

def validate_datasets(datasets: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Validates the generated datasets for schema, positive amounts, unique IDs, 
    and categorizes anomalies (expected vs unexpected).
    """
    unexpected_errors = []
    expected_anomalies = defaultdict(int)
    
    bank = datasets.get("bank", [])
    gateway = datasets.get("gateway", [])
    settlement = datasets.get("settlement", [])
    invoice = datasets.get("invoice", [])
    
    # 1. Unexpected Errors (Schema & Integrity)
    for item in bank:
        if not all(k in item for k in ["bank_txn_id", "transaction_id", "date", "amount", "type"]):
            unexpected_errors.append(f"Bank record {item.get('bank_txn_id')} missing required fields")
        if item.get("amount", -1) < 0:
            unexpected_errors.append(f"Bank record {item.get('bank_txn_id')} has negative amount")

    for item in gateway:
        if not all(k in item for k in ["gateway_txn_id", "transaction_id", "date", "gross_amount", "fee", "status"]):
            unexpected_errors.append(f"Gateway record {item.get('gateway_txn_id')} missing required fields")
        if item.get("gross_amount", -1) < 0 or item.get("fee", -1) < 0:
            unexpected_errors.append(f"Gateway record {item.get('gateway_txn_id')} has negative amount/fee")

    for item in settlement:
        if not all(k in item for k in ["settlement_id", "transaction_id", "gateway_txn_id", "settlement_date", "gross_amount", "net_amount", "fee_deducted"]):
            unexpected_errors.append(f"Settlement record {item.get('settlement_id')} missing required fields")
        if item.get("gross_amount", -1) < 0 or item.get("net_amount", -1) < 0 or item.get("fee_deducted", -1) < 0:
            unexpected_errors.append(f"Settlement record {item.get('settlement_id')} has negative amount/fee")

    for item in invoice:
        if not all(k in item for k in ["invoice_id", "transaction_id", "date", "total_amount", "status"]):
            unexpected_errors.append(f"Invoice record {item.get('invoice_id')} missing required fields")
        if item.get("total_amount", -1) < 0:
            unexpected_errors.append(f"Invoice record {item.get('invoice_id')} has negative amount")
            
    def check_uniqueness(data: List[Dict[str, Any]], key: str, name: str) -> None:
        seen = set()
        for item in data:
            val = item.get(key)
            if val in seen:
                unexpected_errors.append(f"Duplicate {name} Primary Key found: {val}")
            seen.add(val)

    check_uniqueness(bank, "bank_txn_id", "Bank")
    check_uniqueness(gateway, "gateway_txn_id", "Gateway")
    check_uniqueness(settlement, "settlement_id", "Settlement")
    check_uniqueness(invoice, "invoice_id", "Invoice")
    
    # 2. Expected Anomalies (Business Logic)
    bank_txns = {item["transaction_id"]: item for item in bank}
    gw_txns = defaultdict(list)
    for item in gateway:
        gw_txns[item["transaction_id"]].append(item)
    set_txns = {item["transaction_id"]: item for item in settlement}
    inv_txns = {item["transaction_id"]: item for item in invoice}
    
    all_txns = set(bank_txns.keys()).union(gw_txns.keys()).union(set_txns.keys()).union(inv_txns.keys())
    
    for txn_id in all_txns:
        # Orphan Check
        presence = sum([txn_id in bank_txns, txn_id in gw_txns, txn_id in set_txns, txn_id in inv_txns])
        if presence == 1:
            expected_anomalies["OrphanRecord"] += 1
            continue # Don't run other checks on orphans
            
        # Duplicate Transaction Check
        if len(gw_txns.get(txn_id, [])) > 1:
            expected_anomalies["DuplicateTransaction"] += 1
            
        # Missing Settlement Check
        if txn_id in gw_txns and txn_id not in set_txns:
            expected_anomalies["MissingSettlement"] += 1
            
        # Missing Invoice Check
        if txn_id in gw_txns and txn_id not in inv_txns:
            expected_anomalies["MissingInvoice"] += 1
            
        gw_list = gw_txns.get(txn_id, [])
        if not gw_list:
            continue
            
        gw = gw_list[0]
        
        # Refund Check
        if gw.get("status") == "REFUNDED":
            expected_anomalies["Refund"] += 1
            
        # Matches require settlement and invoice
        if txn_id in set_txns and txn_id in inv_txns:
            st = set_txns[txn_id]
            inv = inv_txns[txn_id]
            
            # Amount Mismatch
            if gw.get("gross_amount") != inv.get("total_amount"):
                expected_anomalies["AmountMismatch"] += 1
                
            # Fee Mismatch
            if gw.get("fee") != st.get("fee_deducted"):
                expected_anomalies["FeeMismatch"] += 1
                
            # Late Settlement Check (naive > 2 days)
            from datetime import datetime
            try:
                gw_date = datetime.strptime(gw["date"], "%Y-%m-%d")
                st_date = datetime.strptime(st["settlement_date"], "%Y-%m-%d")
                if (st_date - gw_date).days > 2:
                    expected_anomalies["LateSettlement"] += 1
                elif (st_date - gw_date).days < 0:
                    unexpected_errors.append(f"Settlement {st['settlement_id']} date is before Gateway date")
            except Exception:
                unexpected_errors.append(f"Invalid date format for txn {txn_id}")

    return {
        "valid": len(unexpected_errors) == 0,
        "unexpected_errors": unexpected_errors,
        "expected_anomalies": dict(expected_anomalies)
    }
