import argparse
import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from backend.app.data_generation.config import load_config, GeneratorConfig
from backend.app.data_generation.faker_utils import (
    set_seed, generate_transaction_id, generate_gateway_txn_id, 
    generate_settlement_id, generate_invoice_id, generate_bank_txn_id,
    generate_date, add_days, format_date, format_datetime, generate_amount,
    generate_merchant_id, generate_customer_id, generate_customer_name, generate_bank_name
)
from backend.app.data_generation.validator import validate_datasets
from backend.app.data_generation.summary import generate_summary
from backend.app.data_generation.anomaly_injector import AnomalyInjector

def generate_demo_50_dataset() -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates a deterministic 50-transaction dataset with 38 matched and 12 unmatched records.
    Calibrated volume targets:
      Bank Volume: ₹4,68,600.81
      Settlement Volume: ₹4,47,827.04
      Unmatched Volume: ₹88,954.94
    """
    bank_records = []
    gateway_records = []
    settlement_records = []
    invoice_records = []

    target_bank_total = 468600.81
    target_settlement_total = 447827.04
    target_unmatched_total = 88954.94

    matched_bank_target = round(target_bank_total - target_unmatched_total, 2)
    avg_bank_matched = matched_bank_target / 38
    matched_bank_amounts = [round(avg_bank_matched, 2)] * 38
    diff_m = round(matched_bank_target - sum(matched_bank_amounts), 2)
    matched_bank_amounts[-1] = round(matched_bank_amounts[-1] + diff_m, 2)

    unmatched_bank_amounts = [
        11145.50, 1879.99, 4114.50, 7453.00, # TXN1039-1042 Amount Mismatch
        11941.45, 3415.04,                 # TXN1043-1044 Fee Mismatch
        1316.99, 9410.00,                  # TXN1045-1046 Missing Settlement
        5679.99, 15455.99,                 # TXN1047-1048 Duplicate Gateway
        1682.50,                           # TXN1049 Missing Invoice
        15459.99                           # TXN1050 Settlement Delay
    ]
    diff_u = round(target_unmatched_total - sum(unmatched_bank_amounts), 2)
    unmatched_bank_amounts[-1] = round(unmatched_bank_amounts[-1] + diff_u, 2)

    for i in range(1, 51):
        txn_id = f"TXN{1000 + i}"
        b_date = "2026-03-01"
        s_date = "2026-03-02"

        if i <= 38:
            b_amt = matched_bank_amounts[i-1]
            gw_amt = b_amt
            fee = round(b_amt * (7459.01 / 379645.87), 2)
            gw_fee = fee
            st_net = round(b_amt - fee, 2)
            has_gw = True
            dup_gw = False
            has_st = True
            has_inv = True
        else:
            b_amt = unmatched_bank_amounts[i-39]
            has_gw = True
            dup_gw = False
            has_st = True
            has_inv = True

            if txn_id in ["TXN1039", "TXN1040", "TXN1041", "TXN1042"]:
                gw_amt = round(b_amt * 0.70, 2)
                gw_fee = round(gw_amt * 0.02, 2)
                st_net = round(gw_amt - gw_fee, 2)
            elif txn_id == "TXN1043":
                gw_amt = b_amt
                gw_fee = round(gw_amt * 0.0759, 2)
                st_net = round(gw_amt - gw_fee, 2)
            elif txn_id == "TXN1044":
                gw_amt = b_amt
                gw_fee = round(gw_amt * 0.0059, 2)
                st_net = round(gw_amt - gw_fee, 2)
            elif txn_id in ["TXN1045", "TXN1046"]:
                gw_amt = b_amt
                gw_fee = round(b_amt * 0.02, 2)
                st_net = round(b_amt - gw_fee, 2)
                has_st = False
            elif txn_id in ["TXN1047", "TXN1048"]:
                gw_amt = b_amt
                gw_fee = round(b_amt * 0.02, 2)
                st_net = round(b_amt - gw_fee, 2)
                dup_gw = True
            elif txn_id == "TXN1049":
                gw_amt = b_amt
                gw_fee = round(b_amt * 0.02, 2)
                st_net = round(b_amt - gw_fee, 2)
                has_inv = False
            elif txn_id == "TXN1050":
                gw_amt = b_amt
                gw_fee = round(b_amt * 0.02, 2)
                st_net = round(b_amt - gw_fee, 2)
                s_date = "2026-03-04"

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

        if has_st:
            settlement_records.append({
                "settlement_id": f"SET_{txn_id}",
                "transaction_id": txn_id,
                "gateway_txn_id": f"GW_{txn_id}_1",
                "settlement_date": s_date,
                "gross_amount": gw_amt,
                "net_amount": st_net,
                "fee_deducted": gw_fee,
                "settlement_status": "SETTLED"
            })

        if has_inv:
            invoice_records.append({
                "invoice_id": f"INV_{txn_id}",
                "transaction_id": txn_id,
                "date": b_date,
                "customer_name": f"Customer {i}",
                "total_amount": gw_amt,
                "status": "PAID",
                "gst_amount": round(gw_amt * 0.18, 2),
                "discount": 0.0,
                "net_amount": gw_amt
            })

    gw_1039_1042 = {
        "TXN1039": 11074.38,
        "TXN1040": 1745.53,
        "TXN1041": 3967.79,
        "TXN1042": 7393.22
    }
    for tid, gw_amt in gw_1039_1042.items():
        gw_fee = round(gw_amt * 0.02, 2)
        net_amt = round(gw_amt - gw_fee, 2)
        for gw_rec in gateway_records:
            if gw_rec["transaction_id"] == tid:
                gw_rec["gross_amount"] = gw_amt
                gw_rec["fee"] = gw_fee
        for st_rec in settlement_records:
            if st_rec["transaction_id"] == tid:
                st_rec["gross_amount"] = gw_amt
                st_rec["net_amount"] = net_amt
                st_rec["fee_deducted"] = gw_fee
        for inv_rec in invoice_records:
            if inv_rec["transaction_id"] == tid:
                inv_rec["total_amount"] = gw_amt
                inv_rec["net_amount"] = gw_amt

    # Ensure total settlement volume equals exactly 447,827.04
    target_settlement_vol = 447827.04
    current_settlement_vol = round(sum(float(r["net_amount"]) for r in settlement_records), 2)
    st_diff = round(target_settlement_vol - current_settlement_vol, 2)
    if abs(st_diff) > 0:
        for r in settlement_records:
            if r["transaction_id"] == "TXN1038":
                r["net_amount"] = round(r["net_amount"] + st_diff, 2)
                r["fee_deducted"] = round(r["fee_deducted"] - st_diff, 2)
                for gw_rec in gateway_records:
                    if gw_rec["transaction_id"] == "TXN1038":
                        gw_rec["fee"] = round(gw_rec["fee"] - st_diff, 2)
                break

    return {
        "bank": bank_records,
        "gateway": gateway_records,
        "settlement": settlement_records,
        "invoice": invoice_records
    }

def generate_base_data(num_transactions: int) -> Dict[str, List[Dict[str, Any]]]:
    """Generate transactions. If num_transactions is 50, return deterministic demo 50 dataset."""
    if num_transactions == 50:
        return generate_demo_50_dataset()
    bank_data = []
    gateway_data = []
    settlement_data = []
    invoice_data = []

    merchant_id = generate_merchant_id()

    for _ in range(num_transactions):
        txn_id = generate_transaction_id()
        gw_txn_id = generate_gateway_txn_id()
        set_id = generate_settlement_id()
        inv_id = generate_invoice_id()
        bnk_txn_id = generate_bank_txn_id()

        txn_date = generate_date()
        settlement_date = add_days(txn_date, 1)

        amount = generate_amount()
        fee = round(amount * 0.02, 2)
        net_amount = round(amount - fee, 2)
        
        customer_id = generate_customer_id()
        payment_method = "UPI"
        currency = "INR"

        # Invoice
        invoice_data.append({
            "invoice_id": inv_id,
            "transaction_id": txn_id,
            "date": format_date(txn_date),
            "customer_name": generate_customer_name(),
            "total_amount": amount,
            "status": "PAID",
            "gst_amount": round(amount * 0.18, 2),
            "discount": 0.0,
            "net_amount": amount
        })

        # Gateway
        gateway_data.append({
            "gateway_txn_id": gw_txn_id,
            "transaction_id": txn_id,
            "date": format_date(txn_date),
            "gross_amount": amount,
            "fee": fee,
            "status": "SUCCESS",
            "payment_method": payment_method,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "captured_at": format_datetime(txn_date)
        })

        # Settlement
        settlement_data.append({
            "settlement_id": set_id,
            "transaction_id": txn_id,
            "gateway_txn_id": gw_txn_id,
            "settlement_date": format_date(settlement_date),
            "gross_amount": amount,
            "net_amount": net_amount,
            "fee_deducted": fee,
            "settlement_status": "SETTLED"
        })

        # Bank
        bank_data.append({
            "bank_txn_id": bnk_txn_id,
            "transaction_id": txn_id,
            "date": format_date(settlement_date),
            "description": f"NEFT/RAZORPAY/{txn_id}",
            "amount": net_amount,
            "type": "CREDIT",
            "currency": currency,
            "bank_name": generate_bank_name(),
            "reference_number": f"UTR-{gw_txn_id}"
        })

    return {
        "invoice": invoice_data,
        "gateway": gateway_data,
        "settlement": settlement_data,
        "bank": bank_data
    }

def export_to_csv(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Export a list of dictionaries to a CSV file."""
    if not data:
        return
    
    os.makedirs(filepath.parent, exist_ok=True)
    keys = data[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main() -> None:
    parser = argparse.ArgumentParser(description="FinancePilot AI - Synthetic Dataset Generator")
    parser.add_argument("--transactions", type=int, help="Number of transactions to generate")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override with CLI args if provided
    num_transactions = args.transactions if args.transactions is not None else config.transactions
    
    if args.seed is not None:
        set_seed(args.seed)

    print(f"Generating {num_transactions} base transactions...")
    start_time = time.time()
    
    # 1. Generate Data
    if num_transactions == 50:
        datasets = generate_demo_50_dataset()
    else:
        datasets = generate_base_data(num_transactions)
        print("Injecting anomalies...")
        injector = AnomalyInjector(config.anomalies)
        datasets = injector.inject(datasets)
    
    # 3. Validate Data
    print("Validating generated datasets...")
    validation_results = validate_datasets(datasets)
    
    if not validation_results.get("valid", False):
        print(f"CRITICAL: Unexpected validation errors occurred.")
        print(validation_results.get("unexpected_errors"))
        # We don't abort, we still generate the summary to see the damage.
        
    # 4. Export Data
    base_dir = Path(__file__).parent.parent.parent.parent
    csv_dir = base_dir / "datasets" / "generated" / "csv"
    
    export_to_csv(datasets["bank"], csv_dir / "Bank.csv")
    export_to_csv(datasets["gateway"], csv_dir / "Gateway.csv")
    export_to_csv(datasets["settlement"], csv_dir / "Settlement.csv")
    export_to_csv(datasets["invoice"], csv_dir / "Invoice.csv")
    
    execution_time = time.time() - start_time
    
    # 5. Generate Summary
    reports_dir = base_dir / "datasets" / "generated" / "reports"
    generate_summary(datasets, validation_results, execution_time, reports_dir)

if __name__ == "__main__":
    main()
