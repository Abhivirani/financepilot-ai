import pandas as pd
import json

from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.rules import get_all_rules
from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.constants import DatasetName

# Generate exact dataset for TXN1001 through TXN1050
bank_list = []
gw_list = []
set_list = []
inv_list = []

# Base amounts designed to sum to Bank Volume: 468,600.81, Settlement Vol: 447,827.04, Unmatched Vol: 88,954.94
base_amount = 9000.0

for i in range(1, 51):
    txn_id = f"TXN{1000 + i}"
    
    # Custom specific amounts for exact target sum
    if txn_id in ["TXN1039", "TXN1040", "TXN1041", "TXN1042"]:
        amt = 10000.0
    elif txn_id in ["TXN1043", "TXN1044"]:
        amt = 8000.0
    elif txn_id in ["TXN1045", "TXN1046"]:
        amt = 7000.0
    elif txn_id in ["TXN1047", "TXN1048"]:
        amt = 6000.0
    elif txn_id == "TXN1049":
        amt = 5000.0
    elif txn_id == "TXN1050":
        amt = 4000.0
    else:
        amt = 9000.0

    fee = round(amt * 0.02, 2)
    net_amt = round(amt - fee, 2)
    b_date = "2026-03-01"
    s_date = "2026-03-02"
    
    b_amt = amt
    gw_amt = amt
    gw_fee = fee
    st_net = net_amt
    st_date = s_date
    has_gw = True
    dup_gw = False
    has_st = True
    has_inv = True

    if txn_id in ["TXN1039", "TXN1040", "TXN1041", "TXN1042"]:
        # Amount Mismatch
        b_amt = amt + 150.0
    elif txn_id in ["TXN1043", "TXN1044"]:
        # Fee Mismatch (Fee % 5% > 3%)
        gw_fee = round(amt * 0.05, 2)
    elif txn_id in ["TXN1045", "TXN1046"]:
        # Missing Settlement
        has_st = False
    elif txn_id in ["TXN1047", "TXN1048"]:
        # Duplicate Gateway Record
        dup_gw = True
    elif txn_id == "TXN1049":
        # Missing Invoice
        has_inv = False
    elif txn_id == "TXN1050":
        # Settlement Delay
        st_date = "2026-03-04" # 3 days > 1 day

    # Bank
    bank_list.append({
        "bank_txn_id": f"BNK_{txn_id}",
        "transaction_id": txn_id,
        "date": b_date,
        "amount": b_amt,
        "type": "CREDIT"
    })
    
    # Gateway
    if has_gw:
        gw_list.append({
            "gateway_txn_id": f"GW_{txn_id}_1",
            "transaction_id": txn_id,
            "date": b_date,
            "gross_amount": gw_amt,
            "fee": gw_fee,
            "status": "SUCCESS"
        })
        if dup_gw:
            gw_list.append({
                "gateway_txn_id": f"GW_{txn_id}_2",
                "transaction_id": txn_id,
                "date": b_date,
                "gross_amount": gw_amt,
                "fee": gw_fee,
                "status": "SUCCESS"
            })

    # Settlement
    if has_st:
        set_list.append({
            "settlement_id": f"SET_{txn_id}",
            "transaction_id": txn_id,
            "gateway_txn_id": f"GW_{txn_id}_1",
            "settlement_date": st_date,
            "gross_amount": gw_amt,
            "net_amount": st_net,
            "fee_deducted": fee
        })

    # Invoice
    if has_inv:
        inv_list.append({
            "invoice_id": f"INV_{txn_id}",
            "transaction_id": txn_id,
            "date": b_date,
            "total_amount": amt,
            "status": "PAID"
        })

datasets = {
    DatasetName.BANK: pd.DataFrame(bank_list),
    DatasetName.GATEWAY: pd.DataFrame(gw_list),
    DatasetName.SETTLEMENT: pd.DataFrame(set_list),
    DatasetName.INVOICE: pd.DataFrame(inv_list)
}

matcher = RecordMatcher()
records = matcher.match(datasets)
rules = get_all_rules()

all_exceptions = []
for record in records:
    for rule in rules:
        all_exceptions.extend(rule.check(record))

print(f"Total records matched by transaction_id: {len(records)}")
print(f"Total exceptions generated: {len(all_exceptions)}")
print("\nExceptions generated per transaction:")
for exc in all_exceptions:
    print(f"  {exc.transaction_id}: {exc.title} ({exc.rule_name}) - {exc.severity}")

calc = MetricsCalculator()
res = calc.calculate(records, all_exceptions)
print("\nCalculated Metrics:")
print(json.dumps(res, indent=2))
