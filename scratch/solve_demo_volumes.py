import pandas as pd
import json
from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.rules import get_all_rules
from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.constants import DatasetName

target_bank = 468600.81
target_st = 447827.04
target_unmatched = 88954.94

# We have 38 matched transactions (1..38) and 12 unmatched (39..50)
# 12 unmatched:
# 1039..1042 (4 txns): Amount Mismatch (Bank amount = gw_gross + delta)
# 1043..1044 (2 txns): Fee Mismatch (fee = 5%)
# 1045..1046 (2 txns): Missing Settlement (no settlement)
# 1047..1048 (2 txns): Duplicate Gateway
# 1049 (1 txn): Missing Invoice
# 1050 (1 txn): Settlement Delay

# Let's assign base gross amounts for each transaction 1..50
base_amounts = [
    # 38 matched
    9400.00] * 38 + [
    # 12 unmatched
    7500.00] * 12

# Let's adjust scale so that sums match target_bank, target_st, target_unmatched
scale_clean = (target_bank - target_unmatched) / sum(base_amounts[:38])
scale_unmatched = target_unmatched / sum(base_amounts[38:])

final_amounts = [round(a * scale_clean, 2) for a in base_amounts[:38]] + [round(a * scale_unmatched, 2) for a in base_amounts[38:]]

# Fix rounding difference on last clean and last unmatched
diff_clean = round((target_bank - target_unmatched) - sum(final_amounts[:38]), 2)
final_amounts[37] = round(final_amounts[37] + diff_clean, 2)

diff_unmatched = round(target_unmatched - sum(final_amounts[38:]), 2)
final_amounts[49] = round(final_amounts[49] + diff_unmatched, 2)

bank_records = []
gateway_records = []
settlement_records = []
invoice_records = []

for i in range(1, 51):
    txn_id = f"TXN{1000 + i}"
    amt = final_amounts[i-1]
    fee = round(amt * 0.02, 2)
    net_amt = round(amt - fee, 2)
    b_date = "2026-03-01"
    s_date = "2026-03-02"

    b_amt = amt # For Bank statement, gross or net credited
    gw_amt = amt
    gw_fee = fee
    st_net = net_amt
    st_date = s_date
    has_gw = True
    dup_gw = False
    has_st = True
    has_inv = True

    if txn_id in ["TXN1039", "TXN1040", "TXN1041", "TXN1042"]:
        # Amount Mismatch: Bank amount is different from Gateway gross
        b_amt = round(amt * 1.05, 2)
    elif txn_id in ["TXN1043", "TXN1044"]:
        # Fee Mismatch: Gateway fee is 5% (> 3%)
        gw_fee = round(amt * 0.05, 2)
        st_net = round(amt - gw_fee, 2)
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
        st_date = "2026-03-04"

    # Bank
    bank_records.append({
        "bank_txn_id": f"BNK_{txn_id}",
        "transaction_id": txn_id,
        "date": b_date,
        "description": f"NEFT/RAZORPAY/{txn_id}",
        "amount": b_amt,
        "type": "CREDIT",
        "currency": "INR",
        "bank_name": "HDFC Bank",
        "reference_number": f"UTR-GW_{txn_id}"
    })

    # Gateway
    if has_gw:
        gateway_records.append({
            "gateway_txn_id": f"GW_{txn_id}_1",
            "transaction_id": txn_id,
            "date": b_date,
            "gross_amount": gw_amt,
            "fee": gw_fee,
            "status": "SUCCESS",
            "payment_method": "UPI",
            "merchant_id": "merch_1001",
            "customer_id": f"cust_{i}",
            "captured_at": f"{b_date}T10:00:00Z"
        })
        if dup_gw:
            gateway_records.append({
                "gateway_txn_id": f"GW_{txn_id}_2",
                "transaction_id": txn_id,
                "date": b_date,
                "gross_amount": gw_amt,
                "fee": gw_fee,
                "status": "SUCCESS",
                "payment_method": "UPI",
                "merchant_id": "merch_1001",
                "customer_id": f"cust_{i}",
                "captured_at": f"{b_date}T10:05:00Z"
            })

    # Settlement
    if has_st:
        settlement_records.append({
            "settlement_id": f"SET_{txn_id}",
            "transaction_id": txn_id,
            "gateway_txn_id": f"GW_{txn_id}_1",
            "settlement_date": st_date,
            "gross_amount": gw_amt,
            "net_amount": st_net,
            "fee_deducted": gw_fee,
            "settlement_status": "SETTLED"
        })

    # Invoice
    if has_inv:
        invoice_records.append({
            "invoice_id": f"INV_{txn_id}",
            "transaction_id": txn_id,
            "date": b_date,
            "customer_name": f"Customer {i}",
            "total_amount": amt,
            "status": "PAID",
            "gst_amount": round(amt * 0.18, 2),
            "discount": 0.0,
            "net_amount": amt
        })

datasets = {
    DatasetName.BANK: pd.DataFrame(bank_records),
    DatasetName.GATEWAY: pd.DataFrame(gateway_records),
    DatasetName.SETTLEMENT: pd.DataFrame(settlement_records),
    DatasetName.INVOICE: pd.DataFrame(invoice_records)
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

print("Generated Demo Reconciliation Results:")
print(json.dumps(res, indent=2))
