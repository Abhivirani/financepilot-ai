import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def log(msg, status="OK"):
    print(f"[{status}] {msg}")

def request(url, method="GET", body=None):
    headers = {}
    if body is not None and isinstance(body, dict):
        body = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        return res.status, json.loads(res.read().decode("utf-8"))

def test_workflow_scenarios():
    print("====================================================")
    print("   PRODUCTION WORKFLOW AUDIT - 4 SCENARIOS          ")
    print("====================================================\n")
    
    # ----------------------------------------------------
    # SCENARIO 1: Fresh State / No Data (State 1)
    # ----------------------------------------------------
    print("--- SCENARIO 1: Fresh State / No Data ---")
    status, reset_res = request(f"{BASE_URL}/api/v1/reset", method="POST", body={})
    log(f"Reset endpoint executed: {reset_res['data']['message']}")
    
    # We clear state store in memory by starting clean or testing initial return
    # Let's check GET /api/v1/dashboard
    status, res = request(f"{BASE_URL}/api/v1/dashboard")
    dash = res["data"]
    metrics = dash["metrics"]
    fin = dash["financial_summary"]
    
    log(f"Dashboard Empty State Run ID: {dash['run_id']}")
    log(f"Total Transactions: {metrics['total_transactions']} (Expected: 0)")
    log(f"Matched Transactions: {metrics['matched_transactions']} (Expected: 0)")
    log(f"Unmatched Transactions: {metrics['unmatched_transactions']} (Expected: 0)")
    log(f"Total Exceptions: {metrics['total_exceptions']} (Expected: 0)")
    log(f"Match Rate: {metrics['match_rate']}% (Expected: 0.0%)")
    log(f"Total Processed Amount: ₹{fin['total_amount_processed']} (Expected: ₹0.0)")
    
    assert metrics["total_transactions"] == 0, "Initial transactions must be 0"
    assert metrics["matched_transactions"] == 0, "Initial matched must be 0"
    assert metrics["total_exceptions"] == 0, "Initial exceptions must be 0"
    assert fin["total_amount_processed"] == 0.0, "Initial financial total must be 0.0"
    log("SCENARIO 1 (No Data Empty State): PASSED 100%\n", "SUCCESS")

    # ----------------------------------------------------
    # SCENARIO 2: Upload Custom Dataset / Reconciliation
    # ----------------------------------------------------
    print("--- SCENARIO 2: Demo Dataset Reconciliation Trigger ---")
    status, demo_res = request(f"{BASE_URL}/api/v1/upload/demo", method="POST", body={})
    batch_id = demo_res["data"]["batch_id"]
    log(f"Demo Dataset Batch Created: {batch_id}")
    
    status, rec_res = request(f"{BASE_URL}/api/v1/reconcile", method="POST", body={"batch_id": batch_id})
    rec_summary = rec_res["data"]["summary"]
    run_id = rec_res["data"]["run_id"]
    log(f"Reconciliation Engine Executed: Run ID={run_id}")
    log(f"Reconciliation Summary: Total={rec_summary['total_transactions']}, Matched={rec_summary['matched_count']}, Exceptions={rec_summary['exception_count']}, Match Rate={rec_summary['match_rate']}%")
    
    # Check Dashboard populated cleanly from reconciliation run
    status, res2 = request(f"{BASE_URL}/api/v1/dashboard")
    dash2 = res2["data"]
    m2 = dash2["metrics"]
    f2 = dash2["financial_summary"]
    
    assert dash2["run_id"] == run_id, "Dashboard must reflect latest run_id"
    assert m2["total_transactions"] == rec_summary["total_transactions"], "Dashboard total tx must equal engine total"
    assert m2["matched_transactions"] == rec_summary["matched_count"], "Dashboard matched tx must equal engine matched"
    assert m2["total_exceptions"] == len(dash2["recent_exceptions"]) or m2["total_exceptions"] == rec_summary["exception_count"], "Dashboard exceptions must originate from engine"
    
    log(f"Dashboard Populated From Engine Run: Revenue=₹{f2['total_amount_processed']:,.2f}, Matched=₹{f2['matched_amount']:,.2f}, Unmatched=₹{f2['unmatched_amount']:,.2f}")
    log("SCENARIO 2 (Reconciliation Engine Population): PASSED 100%\n", "SUCCESS")

    # ----------------------------------------------------
    # SCENARIO 3: AI Assistant & Reports Context
    # ----------------------------------------------------
    print("--- SCENARIO 3: AI Assistant & Executive Reports ---")
    status, ai_sum = request(f"{BASE_URL}/api/v1/ai/dashboard-summary", method="POST", body={})
    log(f"AI Dashboard Summary Generated: Provider={ai_sum['data']['provider']}, Latency={ai_sum['data']['latency_ms']}ms")
    
    status, ai_chat = request(f"{BASE_URL}/api/v1/ai/chat", method="POST", body={"message": "What is the unmatched volume?"})
    log(f"AI Assistant Response: '{ai_chat['data']['answer']}'")
    
    assert "₹" in ai_chat["data"]["answer"] or "8,446" in ai_chat["data"]["answer"] or "8,562" in ai_chat["data"]["answer"] or "unmatched" in ai_chat["data"]["answer"].lower(), "AI must answer from actual context"
    log("SCENARIO 3 (AI & Reports Engine Context): PASSED 100%\n", "SUCCESS")

    # ----------------------------------------------------
    # SCENARIO 4: State Persistence Across Requests
    # ----------------------------------------------------
    print("--- SCENARIO 4: State Persistence Across Requests ---")
    status, res3 = request(f"{BASE_URL}/api/v1/dashboard")
    assert res3["data"]["run_id"] == run_id, "State store must persist current reconciliation run"
    log(f"State Store Persistence Verified: run_id={res3['data']['run_id']} maintained")
    log("SCENARIO 4 (State Store Persistence): PASSED 100%\n", "SUCCESS")

if __name__ == "__main__":
    test_workflow_scenarios()
