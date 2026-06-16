# test_full_pipeline.py
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from services.validation_service import ValidationService
from services.report_service import ReportService
from config import settings

# 1. Load
file_path = settings.INPUT_DIR / settings.INPUT_FILE
df = pd.read_csv(file_path)
print(f"Loaded: {len(df)} transactions\n")

# 2. Validate
service = ValidationService()
results = service.validate_all(df)

# 3. Report
reporter = ReportService(df, results)
reporter.save_reports()

# 4. Summary
total_errors = sum(len(errs) for errs in results.values())
clean = sum(1 for errs in results.values() if not errs)
flagged = sum(1 for errs in results.values() if errs)

print(f"\n=== PIPELINE COMPLETE ===")
print(f"Clean:   {clean}")
print(f"Flagged: {flagged}")
print(f"Errors:  {total_errors}")