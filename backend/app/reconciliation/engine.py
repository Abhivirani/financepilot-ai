import time
import argparse
from pathlib import Path

from backend.app.reconciliation.loader import DatasetLoader
from backend.app.reconciliation.matcher import RecordMatcher
from backend.app.reconciliation.rules import get_all_rules
from backend.app.reconciliation.metrics import MetricsCalculator
from backend.app.reconciliation.report import ReportGenerator, JsonReportExporter
from backend.app.reconciliation.exceptions import ReconciliationResult
from backend.app.reconciliation.constants import DEFAULT_CSV_DIR, DEFAULT_REPORT_DIR

class ReconciliationEngine:
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        self.loader = DatasetLoader(data_dir)
        self.matcher = RecordMatcher()
        self.rules = get_all_rules()
        self.metrics_calc = MetricsCalculator()
        self.report_gen = ReportGenerator(JsonReportExporter())

    def run(self) -> None:
        start_time = time.time()
        print(f"Starting Reconciliation Engine...")
        print(f"Loading datasets from {self.data_dir}...")
        
        # 1. Load Data
        datasets = self.loader.load_all()
        
        # 2. Match Records
        print("Matching records by transaction ID...")
        matched_records = self.matcher.match(datasets)
        print(f"Found {len(matched_records)} unique transactions across datasets.")
        
        # 3. Apply Rules
        print(f"Applying {len(self.rules)} deterministic rules...")
        all_exceptions = []
        for record in matched_records:
            if record.is_empty:
                continue
            
            for rule in self.rules:
                exceptions = rule.check(record)
                all_exceptions.extend(exceptions)
                
        print(f"Identified {len(all_exceptions)} total exceptions.")
        
        # 4. Calculate Metrics
        print("Calculating financial and operational metrics...")
        metrics = self.metrics_calc.calculate(matched_records, all_exceptions)
        
        execution_time = time.time() - start_time
        summary = {
            "execution_time_seconds": round(execution_time, 2),
            "total_rules_applied": len(self.rules)
        }
        
        # 5. Generate Report
        result = ReconciliationResult(
            total_transactions=len(matched_records),
            matched_records=matched_records, # Can omit from JSON serialization in report if too large, but keeping in dataclass
            exceptions=all_exceptions,
            metrics=metrics,
            summary=summary
        )
        
        report_path = str(Path(self.output_dir) / "reconciliation_report.json")
        print(f"Exporting report to {report_path}...")
        self.report_gen.generate(result, report_path)
        print("Reconciliation complete.")

def main() -> None:
    parser = argparse.ArgumentParser(description="FinancePilot AI - Reconciliation Engine")
    
    # Get base directory of the project
    base_dir = Path(__file__).parent.parent.parent.parent
    default_in = base_dir / DEFAULT_CSV_DIR
    default_out = base_dir / DEFAULT_REPORT_DIR
    
    parser.add_argument("--input-dir", type=str, default=str(default_in), help="Directory containing CSV datasets")
    parser.add_argument("--output-dir", type=str, default=str(default_out), help="Directory to save reports")
    
    args = parser.parse_args()
    
    engine = ReconciliationEngine(data_dir=args.input_dir, output_dir=args.output_dir)
    engine.run()

if __name__ == "__main__":
    main()
