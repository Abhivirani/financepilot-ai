# pyrefly: ignore [missing-import]
from fastapi import APIRouter
import os
import glob
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/reports")

@router.get("")
def list_reports():
    reports_dir = Path("generated_reports")
    if not reports_dir.exists():
        return {"data": []}
        
    reports = []
    # Search for json files
    for file_path in reports_dir.glob("*.json"):
        stat = file_path.stat()
        reports.append({
            "id": file_path.stem,
            "name": f"Reconciliation Report {file_path.stem}",
            "date": datetime.fromtimestamp(stat.st_mtime).strftime("%b %d, %Y"),
            "type": "JSON",
            "size": f"{stat.st_size / 1024:.1f} KB",
            "url": f"/api/v1/reports/{file_path.name}"
        })
        
    # Sort by date descending
    reports.sort(key=lambda x: x["id"], reverse=True)
    return {"data": reports}
