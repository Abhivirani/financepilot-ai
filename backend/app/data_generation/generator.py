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

def generate_base_data(num_transactions: int) -> Dict[str, List[Dict[str, Any]]]:
    """Generate perfect, happy-path transactions."""
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
    
    # 1. Generate Base Data
    datasets = generate_base_data(num_transactions)
    
    # 2. Inject Anomalies
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
