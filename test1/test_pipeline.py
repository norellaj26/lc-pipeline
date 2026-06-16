#%%
from services.validation_service import ValidationService
from services.report_service import ReportService

validator = ValidationService()
results = validator.validate_all(result)  # 'result' = cleaned DataFrame

# Count errors
total_errors = sum(len(errs) for errs in results.values())
flagged = sum(1 for errs in results.values() if errs)
clean = sum(1 for errs in results.values() if not errs)

print(f"Total errors:  {total_errors} (was 92)")
print(f"Flagged:       {flagged} (was 76)")
print(f"Clean:         {clean} (was 124)")

# Show new LC errors specifically
lc_codes = ['LC001', 'LC002', 'LC003', 'LC004', 'LC005', 'LC007', 'LC008']
lc_errors = []
for txn, errs in results.items():
    for e in errs:
        if e.error_code in lc_codes:
            lc_errors.append(e)

print(f"\nNew LC errors:  {len(lc_errors)}")
for e in lc_errors:
    print(f"  {e}")