import pandas as pd
import json
from pathlib import Path

# Create synthetic 50 records matching the user's description if not present
# TXN1001-TXN1038: Perfect matches
# TXN1039-TXN1042: Amount Mismatch
# TXN1043-TXN1044: Fee Mismatch
# TXN1045-TXN1046: Missing Settlement
# TXN1047-TXN1048: Duplicate Gateway
# TXN1049: Missing Invoice
# TXN1050: Settlement Delay

bank_list = []
gw_list = []
set_list = []
inv_list = []

for i in range(1, 51):
    txn_id = f"TXN{1000 + i}"
    amt = 1000.0 + i * 10.0
    fee = round(amt * 0.02, 2)
    net_amt = round(amt - fee, 2)
    b_date = "2026-03-01"
    s_date = "2026-03-02"
    
    # Defaults
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
        b_amt = amt + 50.0
    elif txn_id in ["TXN1043", "TXN1044"]:
        # Fee Mismatch: fee % is 5% (> 3%)
        gw_fee = round(amt * 0.05, 2)
    elif txn_id in ["TXN1045", "TXN1046"]:
        # Missing Settlement
        has_st = False
    elif txn_id in ["TXN1047", "TXN1048"]:
        # Duplicate Gateway
        dup_gw = True
    elif txn_id == "TXN1049":
        # Missing Invoice
        has_inv = False
    elif txn_id == "TXN1050":
        # Settlement Delay (2 days > 1 day)
        st_date = "2026-03-03"

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

df_bank = pd.DataFrame(bank_list)
df_gw = pd.DataFrame(gw_list)
df_st = pd.DataFrame(set_list)
df_inv = pd.DataFrame(inv_list)

print("Generated sample dataset:")
print(f"Bank rows: {len(df_bank)}, Gateway rows: {len(df_gw)}, Settlement rows: {len(df_st)}, Invoice rows: {len(df_inv)}")
