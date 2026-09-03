from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Optional

# Initialize faker
fake = Faker()

def set_seed(seed: int) -> None:
    """Set the random seed for reproducibility."""
    Faker.seed(seed)
    random.seed(seed)

def generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    return f"TXN_{fake.uuid4()[:8].upper()}"

def generate_gateway_txn_id() -> str:
    """Generate a unique gateway transaction ID."""
    return f"GW_{fake.uuid4()[:12].replace('-', '')}"

def generate_settlement_id() -> str:
    """Generate a unique settlement ID."""
    return f"SET_{fake.uuid4()[:10].replace('-', '')}"

def generate_invoice_id() -> str:
    """Generate a unique invoice ID."""
    return f"INV_{fake.uuid4()[:8].upper()}"

def generate_bank_txn_id() -> str:
    """Generate a unique bank transaction ID."""
    return f"BANK_{fake.uuid4()[:12].replace('-', '')}"

def generate_date(start_date: str = "-30d", end_date: str = "now") -> datetime:
    """Generate a random date within a range."""
    return fake.date_time_between(start_date=start_date, end_date=end_date)

def add_days(date: datetime, days: int) -> datetime:
    """Add days to a date."""
    return date + timedelta(days=days)

def format_date(date: datetime) -> str:
    """Format date as YYYY-MM-DD."""
    return date.strftime("%Y-%m-%d")

def format_datetime(date: datetime) -> str:
    """Format date as ISO 8601 string."""
    return date.isoformat() + "Z"

def generate_amount(min_amount: float = 10.0, max_amount: float = 5000.0) -> float:
    """Generate a random amount rounded to 2 decimal places."""
    return round(random.uniform(min_amount, max_amount), 2)

def generate_merchant_id() -> str:
    """Generate a merchant ID."""
    return f"merch_{fake.uuid4()[:6]}"

def generate_customer_id() -> str:
    """Generate a customer ID."""
    return f"cust_{fake.uuid4()[:8]}"

def generate_customer_name() -> str:
    """Generate a customer name."""
    return fake.name()

def generate_bank_name() -> str:
    """Generate a bank name."""
    banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra"]
    return random.choice(banks)
