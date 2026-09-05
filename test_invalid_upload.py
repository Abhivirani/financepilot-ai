import requests
import json

url = "http://127.0.0.1:8000/api/v1/upload"

valid_bank = """Bank_Txn_ID,Date,Amount,Description,Reference_ID
TXN1001,2026-03-01,1500.00,Payment from Client A,REF9001
"""

invalid_gateway = """Random_Header_1,Random_Header_2
Val1,Val2
"""

files = [
    ("files", ("Bank.csv", valid_bank, "text/csv")),
    ("files", ("Gateway.csv", invalid_gateway, "text/csv")),
]

print("Posting 1 valid and 1 invalid CSV file...")
resp = requests.post(url, files=files)
print("Status Code:", resp.status_code)
try:
    data = resp.json()
    msg = data.get("error", {}).get("message", "")
    print("Response Error Message:\n", msg.encode('ascii', errors='replace').decode('ascii'))
except Exception as e:
    print("Response text:", resp.text.encode('ascii', errors='replace').decode('ascii'))
