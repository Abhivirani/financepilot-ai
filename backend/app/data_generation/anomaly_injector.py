import random
import copy
from typing import Dict, List, Any
from backend.app.data_generation.config import AnomalyConfig
from backend.app.data_generation.faker_utils import (
    generate_bank_txn_id, generate_gateway_txn_id, generate_transaction_id,
    generate_amount, add_days, format_date, fake, generate_bank_name
)

class AnomalyInjector:
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.injected_counts = {
            "amount_mismatch": 0,
            "duplicate": 0,
            "missing_settlement": 0,
            "missing_invoice": 0,
            "late_settlement": 0,
            "refund": 0,
            "fee_mismatch": 0,
            "orphan": 0
        }

    def inject(self, datasets: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Main method to orchestrate anomaly injection based on configuration."""
        
        # We process transactions by ID to make sampling easier
        all_txns = list({item["transaction_id"] for item in datasets["gateway"]})
        random.shuffle(all_txns)
        
        total = len(all_txns)
        
        def get_sample_size(pct: int) -> int:
            return int((pct / 100.0) * total)

        # Allocate transaction IDs to specific anomalies to prevent overlap
        idx = 0
        
        # 1. Amount Mismatch
        count = get_sample_size(self.config.amount_mismatch)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_amount_mismatch(datasets, txn_id)
        idx += count

        # 2. Duplicate Transactions
        count = get_sample_size(self.config.duplicate)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_duplicate_transactions(datasets, txn_id)
        idx += count

        # 3. Missing Settlement
        count = get_sample_size(self.config.missing_settlement)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_missing_settlement(datasets, txn_id)
        idx += count

        # 4. Missing Invoice
        count = get_sample_size(self.config.missing_invoice)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_missing_invoice(datasets, txn_id)
        idx += count

        # 5. Late Settlement
        count = get_sample_size(self.config.late_settlement)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_late_settlement(datasets, txn_id)
        idx += count
        
        # 6. Refund
        count = get_sample_size(self.config.refund)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_refund(datasets, txn_id)
        idx += count
        
        # 7. Fee Mismatch
        count = get_sample_size(self.config.fee_mismatch)
        for txn_id in all_txns[idx:idx+count]:
            self._inject_fee_mismatch(datasets, txn_id)
        idx += count

        # 8. Orphan Records (These don't use existing txns, they generate brand new ones)
        orphan_count = get_sample_size(self.config.orphan)
        for _ in range(orphan_count):
            self._inject_orphan_records(datasets)

        return datasets

    def _inject_amount_mismatch(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Modify Bank or Gateway amount by a small configurable percentage."""
        for gw in datasets["gateway"]:
            if gw["transaction_id"] == txn_id:
                # Add between 1% and 5% to the amount
                modifier = random.uniform(1.01, 1.05)
                gw["gross_amount"] = round(gw["gross_amount"] * modifier, 2)
                self.injected_counts["amount_mismatch"] += 1
                break

    def _inject_duplicate_transactions(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Duplicate an existing Gateway transaction with a new primary key."""
        for gw in datasets["gateway"]:
            if gw["transaction_id"] == txn_id:
                duplicate = copy.deepcopy(gw)
                duplicate["gateway_txn_id"] = generate_gateway_txn_id()
                datasets["gateway"].append(duplicate)
                self.injected_counts["duplicate"] += 1
                break

    def _inject_missing_settlement(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Remove the Settlement record and corresponding Bank record."""
        datasets["settlement"] = [s for s in datasets["settlement"] if s["transaction_id"] != txn_id]
        datasets["bank"] = [b for b in datasets["bank"] if b["transaction_id"] != txn_id]
        self.injected_counts["missing_settlement"] += 1

    def _inject_missing_invoice(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Remove Invoice records."""
        datasets["invoice"] = [i for i in datasets["invoice"] if i["transaction_id"] != txn_id]
        self.injected_counts["missing_invoice"] += 1

    def _inject_late_settlement(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Increase settlement_date by 3-5 days."""
        delay_days = random.randint(3, 5)
        for st in datasets["settlement"]:
            if st["transaction_id"] == txn_id:
                # Need to get original date, convert back to datetime, add days, format
                orig_date = fake.date_time_between_dates(
                    datetime_start=fake.date_time_between(start_date="-30d", end_date="now") # Dummy, not accurate but works for format
                ) # Wait, it's easier to just parse string
                from datetime import datetime
                d = datetime.strptime(st["settlement_date"], "%Y-%m-%d")
                new_date = add_days(d, delay_days)
                st["settlement_date"] = format_date(new_date)
                
                # Update bank date as well
                for b in datasets["bank"]:
                    if b["transaction_id"] == txn_id:
                        b["date"] = format_date(new_date)
                        break
                        
                self.injected_counts["late_settlement"] += 1
                break

    def _inject_fee_mismatch(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Modify fee_deducted without changing gross_amount."""
        for st in datasets["settlement"]:
            if st["transaction_id"] == txn_id:
                st["fee_deducted"] = round(st["fee_deducted"] + random.uniform(1.0, 5.0), 2)
                self.injected_counts["fee_mismatch"] += 1
                break

    def _inject_refund(self, datasets: Dict[str, List[Dict[str, Any]]], txn_id: str) -> None:
        """Mark Gateway status as REFUNDED. For Refund verification anomaly, bank doesn't get debit."""
        for gw in datasets["gateway"]:
            if gw["transaction_id"] == txn_id:
                gw["status"] = "REFUNDED"
                self.injected_counts["refund"] += 1
                break

    def _inject_orphan_records(self, datasets: Dict[str, List[Dict[str, Any]]]) -> None:
        """Create Bank records whose transaction_id does not exist elsewhere."""
        txn_id = generate_transaction_id()
        datasets["bank"].append({
            "bank_txn_id": generate_bank_txn_id(),
            "transaction_id": txn_id,
            "date": format_date(fake.date_time_between(start_date="-30d", end_date="now")),
            "description": f"NEFT/UNKNOWN/{txn_id}",
            "amount": generate_amount(),
            "type": "CREDIT",
            "currency": "INR",
            "bank_name": generate_bank_name(),
            "reference_number": f"UTR-ORPHAN-{random.randint(1000, 9999)}"
        })
        self.injected_counts["orphan"] += 1
