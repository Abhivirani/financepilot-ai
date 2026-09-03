import json
import os
from pathlib import Path
from typing import Dict, Any, List

def generate_summary(
    datasets: Dict[str, List[Dict[str, Any]]], 
    validation_results: Dict[str, Any], 
    execution_time: float,
    reports_dir: Path
) -> None:
    """Generates console summary and exports generation_report.json"""
    
    counts = {
        "bank": len(datasets.get("bank", [])),
        "gateway": len(datasets.get("gateway", [])),
        "settlement": len(datasets.get("settlement", [])),
        "invoice": len(datasets.get("invoice", []))
    }
    
    report = {
        "record_counts": counts,
        "execution_time_seconds": round(execution_time, 2),
        "validation_status": "PASS" if validation_results.get("valid") else "FAIL",
        "expected_anomalies": validation_results.get("expected_anomalies", {}),
        "unexpected_errors": validation_results.get("unexpected_errors", [])
    }
    
    os.makedirs(reports_dir, exist_ok=True)
    report_path = reports_dir / "generation_report.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print("\n--- Generation Summary ---")
    print(f"Transactions Generated (approx): {max(counts.values())}")
    print(f"Bank Records:       {counts['bank']}")
    print(f"Gateway Records:    {counts['gateway']}")
    print(f"Settlement Records: {counts['settlement']}")
    print(f"Invoice Records:    {counts['invoice']}")
    
    print("\nExpected anomalies:")
    for k, v in report["expected_anomalies"].items():
        print(f"    {k}: {v}")
        
    print("\nUnexpected errors:")
    if not report["unexpected_errors"]:
        print("    None")
    else:
        for err in report["unexpected_errors"][:5]:
            print(f"    {err}")
        if len(report["unexpected_errors"]) > 5:
            print(f"    ... and {len(report['unexpected_errors']) - 5} more")

    print(f"\nExecution Time:     {round(execution_time, 2)} seconds")
    print(f"Validation Status:  {report['validation_status']}")
    print(f"Report saved to:    {report_path}")
    print("--------------------------\n")
