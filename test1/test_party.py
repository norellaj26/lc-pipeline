# test_party_validator.py
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from validators.party_validator import PartyValidator
from config import settings

# Load dataset
file_path = settings.INPUT_DIR / settings.INPUT_FILE
df = pd.read_csv(file_path)

# Run validator on both parties
validator = PartyValidator()
all_errors = []

parties = ['applicant', 'beneficiary']

for idx, row in df.iterrows():
    for party in parties:
        errors = validator.validate(
            field=party,
            value=row[f'{party}_name'],
            address=row[f'{party}_address'],
            country=row[f'{party}_country'],
            city=row[f'{party}_city'],
            postal_code=row[f'{party}_postal_code']
        )
        for err in errors:
            all_errors.append({
                'transaction_id': row['transaction_id'],
                **err.to_dict()
            })

# Results
print(f"=== PARTY VALIDATION RESULTS ===")
print(f"Transactions scanned: {len(df)}")
print(f"Parties checked: {len(df) * len(parties)}")
print(f"Total errors found: {len(all_errors)}\n")

error_df = pd.DataFrame(all_errors)
if len(error_df) > 0:
    print("=== BY ERROR CODE ===")
    print(error_df['error_code'].value_counts().to_string())
    print("\n=== ALL ERRORS ===")
    for _, row in error_df.iterrows():
        print(f"  {row['transaction_id']:12s} {row['field']:25s} {row['error_code']} [{row['severity']}] got: {row['value']}")