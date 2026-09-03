import pytest
import copy
from backend.app.data_generation.generator import generate_base_data
from backend.app.data_generation.validator import validate_datasets

def test_validator_happy_path():
    datasets = generate_base_data(5)
    result = validate_datasets(datasets)
    assert result["valid"] is True
    assert result["error_count"] == 0

def test_validator_missing_field():
    datasets = generate_base_data(2)
    del datasets["bank"][0]["amount"]
    
    result = validate_datasets(datasets)
    assert result["valid"] is False
    assert any("missing required fields" in error for error in result["errors"])

def test_validator_negative_amount():
    datasets = generate_base_data(2)
    datasets["gateway"][0]["gross_amount"] = -50.0
    
    result = validate_datasets(datasets)
    assert result["valid"] is False
    assert any("negative amount" in error for error in result["errors"])

def test_validator_duplicate_id():
    datasets = generate_base_data(2)
    datasets["invoice"][1]["invoice_id"] = datasets["invoice"][0]["invoice_id"]
    
    result = validate_datasets(datasets)
    assert result["valid"] is False
    assert any("Duplicate Invoice ID found" in error for error in result["errors"])

def test_validator_missing_relationship():
    datasets = generate_base_data(2)
    # Remove one transaction from settlement
    datasets["settlement"].pop(0)
    
    result = validate_datasets(datasets)
    assert result["valid"] is False
    assert any("missing in Settlement" in error for error in result["errors"])

def test_validator_date_inconsistency():
    datasets = generate_base_data(1)
    # Make settlement date happen BEFORE gateway date
    datasets["settlement"][0]["settlement_date"] = "2000-01-01"
    datasets["gateway"][0]["date"] = "2026-01-01"
    
    result = validate_datasets(datasets)
    assert result["valid"] is False
    assert any("before Gateway date" in error for error in result["errors"])
