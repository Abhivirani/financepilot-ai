import requests
import json

url = "http://127.0.0.1:8000/api/v1/upload"

bank_csv = """Bank_Txn_ID,Date,Amount,Description,Reference_ID
TXN1001,2026-03-01,1500.00,Payment from Client A,REF9001
TXN1002,2026-03-02,2300.50,Refund to Client B,REF9002
"""

gateway_csv = """Gateway_Txn_ID,Transaction_Date,Amount,Status,Order_ID
GW5001,2026-03-01,1500.00,SUCCESS,REF9001
GW5002,2026-03-02,2300.50,SUCCESS,REF9002
"""

settlement_csv = """Settlement_ID,Settlement_Date,Net_Amount,Fee,UTR_Number
SET8001,2026-03-01,1485.00,15.00,UTR112233
SET8002,2026-03-02,2277.50,23.00,UTR112234
"""

invoice_csv = """Invoice_Number,Invoice_Date,Customer_Name,Invoice_Amount,Status
INV-001,2026-03-01,Acme Corp,1500.00,PAID
INV-002,2026-03-02,Beta LLC,2300.50,PAID
"""

files = [
    ("files", ("Bank.csv", bank_csv, "text/csv")),
    ("files", ("Gateway.csv", gateway_csv, "text/csv")),
    ("files", ("Settlement.csv", settlement_csv, "text/csv")),
    ("files", ("Invoice.csv", invoice_csv, "text/csv")),
]

print("Posting 4 CSV files to /api/v1/upload/process...")
resp = requests.post(url, files=files)
print("Status Code:", resp.status_code)
try:
    data = resp.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print("Response text:", resp.text)
