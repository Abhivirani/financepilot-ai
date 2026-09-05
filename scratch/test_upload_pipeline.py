import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def create_multipart_body(files_dict):
    boundary = uuid.uuid4().hex
    body = bytearray()
    
    for field_name, (filename, content, content_type) in files_dict.items():
        body.extend(f"--{boundary}\r\n".encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
        if isinstance(content, str):
            body.extend(content.encode('utf-8'))
        else:
            body.extend(content)
        body.extend(b'\r\n')
        
    body.extend(f"--{boundary}--\r\n".encode('utf-8'))
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    return bytes(body), headers

def run_upload_tests():
    print("====================================================")
    print("   END-TO-END UPLOAD PIPELINE VERIFICATION AUDIT    ")
    print("====================================================\n")
    
    # Sample 1: Real CSV content with TitleCase headers and UTF-8 BOM
    bank_csv = "\ufeffBank_Txn_ID,Transaction_ID,Date,Amount,Type\nBNK101,TXN1001,2026-09-01,5000.00,CREDIT\nBNK102,TXN1002,2026-09-01,3500.00,CREDIT\n"
    gateway_csv = "Gateway_Txn_ID,Transaction_ID,Date,Gross_Amount,Fee,Status\nGW101,TXN1001,2026-09-01,5000.00,100.00,SUCCESS\nGW102,TXN1002,2026-09-01,3500.00,70.00,SUCCESS\n"
    settlement_csv = "Settlement_ID,Transaction_ID,Gateway_Txn_ID,Settlement_Date,Gross_Amount,Net_Amount,Fee_Deducted\nSET101,TXN1001,GW101,2026-09-02,5000.00,4900.00,100.00\nSET102,TXN1002,GW102,2026-09-02,3500.00,3430.00,70.00\n"
    invoice_csv = "Invoice_ID,Transaction_ID,Date,Total_Amount,Status\nINV101,TXN1001,2026-09-01,5000.00,PAID\nINV102,TXN1002,2026-09-01,3500.00,PAID\n"
    
    files = {
        "bank_statement": ("Bank.csv", bank_csv, "text/csv"),
        "payment_gateway": ("Gateway.csv", gateway_csv, "text/csv"),
        "settlement_report": ("Settlement.csv", settlement_csv, "text/csv"),
        "invoice": ("Invoice.csv", invoice_csv, "text/csv")
    }
    
    body, headers = create_multipart_body(files)
    req = urllib.request.Request(f"{BASE_URL}/api/v1/upload", data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("[PASSED] Upload API Success:", res.status)
            print("Batch ID:", data['data']['batch_id'])
            print("Total Transactions:", data['data']['total_transactions'])
            print("Status:", data['data']['status'])
            print("File Summaries:")
            for f in data['data']['files']:
                print(f"  - {f['source_type']}: {f['filename']} ({f['row_count']} rows, Valid: {f['is_valid']})")
                
            # Now trigger reconciliation with batch_id
            batch_id = data['data']['batch_id']
            rec_req = urllib.request.Request(f"{BASE_URL}/api/v1/reconcile", data=json.dumps({"batch_id": batch_id}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method="POST")
            with urllib.request.urlopen(rec_req) as rec_res:
                rec_data = json.loads(rec_res.read().decode('utf-8'))
                print("\n[PASSED] Reconciliation Success:", rec_res.status)
                print("Run ID:", rec_data['data']['run_id'])
                print("Reconciliation Summary:", rec_data['data']['summary'])
                
    except urllib.error.HTTPError as e:
        print("[FAILED] HTTP Error Code:", e.code)
        print("Response Body:\n", e.read().decode('utf-8'))
        raise e

if __name__ == "__main__":
    run_upload_tests()
