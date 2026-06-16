# test_validation_service.py
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from services.validation_service import ValidationService
from config import settings

# Load dataset
file_path = settings.INPUT_DIR / settings.INPUT_FILE
df = pd.read_csv(file_path)

# Run the full pipeline
service = ValidationService()
results = service.validate_all(df)

# Count totals
total_errors = sum(len(errs) for errs in results.values())
clean_txns = sum(1 for errs in results.values() if not errs)
flagged_txns = sum(1 for errs in results.values() if errs)

print("=== FULL PIPELINE RESULTS ===")
print(f"Transactions: {len(df)}")
print(f"Clean: {clean_txns}")
print(f"Flagged: {flagged_txns}")
print(f"Total errors: {total_errors}\n")

# Error summary by code
all_errors = []
for txn_id, errs in results.items():
    for err in errs:
        all_errors.append({'transaction_id': txn_id, **err.to_dict()})

error_df = pd.DataFrame(all_errors)
if len(error_df) > 0:
    print("=== BY ERROR CODE ===")
    print(error_df['error_code'].value_counts().to_string())
    print(f"\n=== BY SEVERITY ===")
    print(error_df['severity'].value_counts().to_string())

"""
| Metric | Value |
|--------|-------|
| Transactions scanned | 200 |
| Clean (no errors) | 124 (62%) |
| Flagged (has errors) | 76 (38%) |
| Total errors found | 92 |
| CRITICAL | 31 |
| HIGH | 33 |
| MEDIUM | 28 |
"""

"""
    | Component | Type | Pattern |
|-----------|------|---------|
| ValidationError | dataclass (frozen) | Immutable data model |
| BaseValidator | ABC | Template Method Pattern |
| AmountValidator | Concrete validator | Two-phase (format → value) |
| LeiValidator | Concrete validator | Gate pattern |
| SwiftValidator | Concrete validator | Gate pattern |
| DateValidator | Concrete validator | Individual → cross-date |
| PartyValidator | Concrete validator | Multi-field checks |
| CrossValidator | Concrete validator | Cross-field relationships |
| ValidationService | Orchestrator | Composition pattern |
"""