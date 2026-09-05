import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

# Step 1: Upload Demo Dataset
print("1. Uploading Demo Dataset via /upload/demo...")
resp = requests.post(f"{base_url}/upload/demo")
if resp.status_code != 201:
    print("Response text:", resp.text)
upload_data = resp.json().get("data", {})
batch_id = upload_data["batch_id"]
print("Batch ID:", batch_id)

# Step 2: Trigger Reconciliation
print("\n2. Triggering Reconciliation for batch:", batch_id)
reconcile_resp = requests.post(f"{base_url}/reconcile", json={"batch_id": batch_id})
print("Reconcile status:", reconcile_resp.status_code)
reconcile_data = reconcile_resp.json()["data"]
run_id = reconcile_data["run_id"]
print("Run ID:", run_id)
print("Reconcile Summary:", json.dumps(reconcile_data["summary"], indent=2))

# Step 3: Fetch Dashboard API
print("\n3. Fetching Dashboard API via /dashboard...")
dash_resp = requests.get(f"{base_url}/dashboard")
print("Dashboard status:", dash_resp.status_code)
dash_data = dash_resp.json()["data"]

print("\n--- Dashboard Metrics ---")
print("Total Transactions:", dash_data["metrics"]["total_transactions"])
print("Matched Transactions:", dash_data["metrics"]["matched_transactions"])
print("Unmatched Transactions:", dash_data["metrics"]["unmatched_transactions"])
print("Total Exceptions:", dash_data["metrics"]["total_exceptions"])
print("Match Rate (%):", dash_data["metrics"]["match_rate"])

print("\n--- Dashboard Financial Summary ---")
print("Total Processed (Bank Vol):", dash_data["financial_summary"]["total_amount_processed"])
print("Matched Amount (Settlement Vol):", dash_data["financial_summary"]["matched_amount"])
print("Unmatched Amount:", dash_data["financial_summary"]["unmatched_amount"])

# Step 4: Fetch AI Summary API
print("\n4. Fetching AI Dashboard Summary via /ai/dashboard-summary...")
ai_resp = requests.post(f"{base_url}/ai/dashboard-summary")
print("AI Summary status:", ai_resp.status_code)
ai_data = ai_resp.json()["data"]
print("AI Provider:", ai_data.get("provider"))
print("AI Summary Content Snippet:\n", ai_data["markdown"][:300].encode('ascii', errors='replace').decode('ascii'))
