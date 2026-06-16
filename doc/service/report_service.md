| Question | What Answers It |
|----------|----------------|
| Which transactions are clean? | valid_transactions.csv |
| Which ones have problems? | flagged_issues.csv |
| What's the overall picture? | Summary stats |


    Remember those 5 validation columns from `constants.py`? This creates all of them:

| Column | Example |
|--------|---------|
| validation_status | FLAGGED |
| error_count | 3 |
| error_codes | AMT005; PTY001; DATE004 |
| error_messages | [CRITICAL] AMT005: amount... |
| severity | CRITICAL |


    Three files, same data split three ways:

| File | What | Who Reads It |
|------|------|-------------|
| validation_report.csv | Everything + error columns | Data team |
| valid_transactions.csv | Clean rows only | Processing team |
| flagged_issues.csv | Problem rows only | Compliance team |