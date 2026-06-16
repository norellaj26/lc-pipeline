# test_cross_validator.py
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from validators.cross_validator import CrossValidator
from config import settings

# Load dataset
file_path = settings.INPUT_DIR / settings.INPUT_FILE
df = pd.read_csv(file_path)

# Run validator on every row
validator = CrossValidator()
all_errors = []

for idx, row in df.iterrows():
    errors = validator.validate(
        field='transaction',
        value=row['transaction_id'],
        applicant_name=row['applicant_name'],
        beneficiary_name=row['beneficiary_name'],
        issuing_bank_country=row['issuing_bank_country'],
        applicant_country=row['applicant_country']
    )
    for err in errors:
        all_errors.append({
            'transaction_id': row['transaction_id'],
            **err.to_dict()
        })

# Results
print(f"=== CROSS VALIDATION RESULTS ===")
print(f"Transactions scanned: {len(df)}")
print(f"Total errors found: {len(all_errors)}\n")

error_df = pd.DataFrame(all_errors)
if len(error_df) > 0:
    print("=== BY ERROR CODE ===")
    print(error_df['error_code'].value_counts().to_string())
    print("\n=== ALL ERRORS ===")
    for _, row in error_df.iterrows():
        print(f"  {row['transaction_id']:12s} {row['field']:25s} {row['error_code']} [{row['severity']}] got: {row['value']}")
else:
    print("No cross-validation errors found in current dataset.")