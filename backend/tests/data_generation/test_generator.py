import pytest
from backend.app.data_generation.generator import generate_base_data

def test_generate_base_data_length():
    datasets = generate_base_data(5)
    
    assert len(datasets["bank"]) == 5
    assert len(datasets["gateway"]) == 5
    assert len(datasets["settlement"]) == 5
    assert len(datasets["invoice"]) == 5

def test_generate_base_data_relationships():
    datasets = generate_base_data(2)
    
    # Check that transaction_ids are linked
    bank_txn_ids = {item["transaction_id"] for item in datasets["bank"]}
    gateway_txn_ids = {item["transaction_id"] for item in datasets["gateway"]}
    settlement_txn_ids = {item["transaction_id"] for item in datasets["settlement"]}
    invoice_txn_ids = {item["transaction_id"] for item in datasets["invoice"]}
    
    assert bank_txn_ids == gateway_txn_ids
    assert gateway_txn_ids == settlement_txn_ids
    assert settlement_txn_ids == invoice_txn_ids

def test_happy_path_amounts():
    datasets = generate_base_data(1)
    
    gateway = datasets["gateway"][0]
    settlement = datasets["settlement"][0]
    invoice = datasets["invoice"][0]
    bank = datasets["bank"][0]
    
    assert invoice["total_amount"] == gateway["gross_amount"]
    assert settlement["gross_amount"] == gateway["gross_amount"]
    assert settlement["fee_deducted"] == gateway["fee"]
    assert settlement["net_amount"] == gateway["gross_amount"] - gateway["fee"]
    assert bank["amount"] == settlement["net_amount"]
