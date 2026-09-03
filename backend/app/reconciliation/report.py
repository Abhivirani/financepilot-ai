import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import asdict
from backend.app.reconciliation.exceptions import ReconciliationResult

class ReportExporter(ABC):
    @abstractmethod
    def export(self, result: ReconciliationResult, filepath: Path) -> None:
        pass

class JsonReportExporter(ReportExporter):
    def export(self, result: ReconciliationResult, filepath: Path) -> None:
        os.makedirs(filepath.parent, exist_ok=True)
        
        # Convert exceptions to dict
        exceptions = [asdict(exc) for exc in result.exceptions]
        
        report_data = {
            "summary": result.summary,
            "metrics": result.metrics,
            "exceptions": exceptions
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

class ReportGenerator:
    def __init__(self, exporter: ReportExporter):
        self.exporter = exporter
        
    def generate(self, result: ReconciliationResult, filepath: str) -> None:
        path = Path(filepath)
        self.exporter.export(result, path)
