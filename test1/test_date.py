# test_date_validator.py
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from validators.date_validator import DateValidator
from config import settings

# Load dataset
file_path = settings.INPUT_DIR / settings.INPUT_FILE
df = pd.read_csv(file_path)

# Run validator on every row
validator = DateValidator()
all_errors = []

for idx, row in df.iterrows():
    errors = validator.validate(
        field='issue_date',
        value=row['issue_date'],
        expiry_date=row['expiry_date'],
        shipment_date=row['latest_shipment_date']
    )
    for err in errors:
        all_errors.append({
            'transaction_id': row['transaction_id'],
            **err.to_dict()
        })

# Results
print(f"=== DATE VALIDATION RESULTS ===")
print(f"Transactions scanned: {len(df)}")
print(f"Total errors found: {len(all_errors)}\n")

error_df = pd.DataFrame(all_errors)
if len(error_df) > 0:
    print("=== BY ERROR CODE ===")
    print(error_df['error_code'].value_counts().to_string())
    print("\n=== ALL ERRORS ===")
    for _, row in error_df.iterrows():
        print(f"  {row['transaction_id']:12s} {row['field']:25s} {row['error_code']} [{row['severity']}] got: {row['value']}")