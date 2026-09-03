import pytest
from backend.app.data_generation.generator import generate_base_data
from backend.app.data_generation.anomaly_injector import AnomalyInjector
from backend.app.data_generation.config import AnomalyConfig

def test_inject_amount_mismatch():
    datasets = generate_base_data(5)
    config = AnomalyConfig(amount_mismatch=20) # 1 transaction (20% of 5)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["amount_mismatch"] == 1
    
    # Verify there is exactly one amount mismatch between gateway and invoice
    mismatch_count = 0
    inv_map = {i["transaction_id"]: i for i in datasets["invoice"]}
    for gw in datasets["gateway"]:
        txn_id = gw["transaction_id"]
        if gw["gross_amount"] != inv_map[txn_id]["total_amount"]:
            mismatch_count += 1
    
    assert mismatch_count == 1

def test_inject_duplicate_transactions():
    datasets = generate_base_data(5)
    config = AnomalyConfig(duplicate=20) # 1 transaction
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["duplicate"] == 1
    assert len(datasets["gateway"]) == 6 # 5 original + 1 duplicate

def test_inject_missing_settlement():
    datasets = generate_base_data(5)
    config = AnomalyConfig(missing_settlement=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["missing_settlement"] == 1
    assert len(datasets["settlement"]) == 4
    assert len(datasets["bank"]) == 4

def test_inject_missing_invoice():
    datasets = generate_base_data(5)
    config = AnomalyConfig(missing_invoice=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["missing_invoice"] == 1
    assert len(datasets["invoice"]) == 4

def test_inject_late_settlement():
    datasets = generate_base_data(5)
    config = AnomalyConfig(late_settlement=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["late_settlement"] == 1

def test_inject_fee_mismatch():
    datasets = generate_base_data(5)
    config = AnomalyConfig(fee_mismatch=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["fee_mismatch"] == 1
    mismatch_count = 0
    gw_map = {g["transaction_id"]: g for g in datasets["gateway"]}
    for st in datasets["settlement"]:
        txn_id = st["transaction_id"]
        if st["fee_deducted"] != gw_map[txn_id]["fee"]:
            mismatch_count += 1
            
    assert mismatch_count == 1

def test_inject_refund():
    datasets = generate_base_data(5)
    config = AnomalyConfig(refund=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["refund"] == 1
    refunds = [g for g in datasets["gateway"] if g["status"] == "REFUNDED"]
    assert len(refunds) == 1

def test_inject_orphan_records():
    datasets = generate_base_data(5)
    config = AnomalyConfig(orphan=20)
    injector = AnomalyInjector(config)
    datasets = injector.inject(datasets)
    
    assert injector.injected_counts["orphan"] == 1
    assert len(datasets["bank"]) == 6 # 5 original + 1 orphan
    
    # Verify the orphan doesn't exist elsewhere
    all_gw_txns = {g["transaction_id"] for g in datasets["gateway"]}
    orphans = [b for b in datasets["bank"] if b["transaction_id"] not in all_gw_txns]
    assert len(orphans) == 1
