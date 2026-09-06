import uuid
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from backend.app.core.config import settings

class StateStore:
    def __init__(self):
        self.batches: Dict[str, Any] = {}
        self.runs: Dict[str, Any] = {}
        
        self.latest_batch_id: Optional[str] = None
        self.latest_run_id: Optional[str] = None
        
        self._lock = asyncio.Lock()
        
        # Ensure directories exist
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.REPORT_DIR).mkdir(parents=True, exist_ok=True)

    async def create_batch(self, summary: Dict[str, Any]) -> str:
        async with self._lock:
            batch_id = str(uuid.uuid4())
            summary["batch_id"] = batch_id
            
            self.batches[batch_id] = summary
            self.latest_batch_id = batch_id
            self.latest_run_id = None
            
            # Mirror to disk
            batch_dir = Path(settings.UPLOAD_DIR) / batch_id
            batch_dir.mkdir(parents=True, exist_ok=True)
            with open(batch_dir / "manifest.json", "w") as f:
                # Convert datetime to ISO for JSON
                json_safe_summary = {
                    k: (v.isoformat() if isinstance(v, datetime) else v)
                    for k, v in summary.items()
                }
                json.dump(json_safe_summary, f, default=str)
                
            self._evict_batches()
            return batch_id

    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self.batches.get(batch_id)

    async def create_run(self, run_data: Dict[str, Any]) -> str:
        async with self._lock:
            run_id = str(uuid.uuid4())
            run_data["run_id"] = run_id
            
            self.runs[run_id] = run_data
            self.latest_run_id = run_id
            
            # Mirror to disk
            report_path = Path(settings.REPORT_DIR) / f"{run_id}.json"
            with open(report_path, "w") as f:
                json.dump(run_data, f, default=str)
                
            self._evict_runs()
            return run_id

    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self.runs.get(run_id)

    async def reset(self):
        async with self._lock:
            self.batches.clear()
            self.runs.clear()
            self.latest_batch_id = None
            self.latest_run_id = None

    def _evict_batches(self):
        if len(self.batches) > settings.MAX_RETAINED_BATCHES:
            # Simple eviction: pop the first (oldest) item
            oldest_key = next(iter(self.batches))
            self.batches.pop(oldest_key)

    def _evict_runs(self):
        if len(self.runs) > settings.MAX_RETAINED_RUNS:
            oldest_key = next(iter(self.runs))
            self.runs.pop(oldest_key)

# Singleton instance
state_store = StateStore()
