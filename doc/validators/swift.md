

| Problem | Error Code | Severity | Count |
|---------|-----------|----------|-------|
| Missing issuing SWIFT | BIC001 | HIGH | 4 |
| Wrong length (SHORT) | BIC002 | HIGH | 3 |
| Invalid format (12345678) | BIC003 | HIGH | 2 |

Gate 1 has two checks — pd.isna() for pandas NaN, then separate empty string check. We split them because a SWIFT field could be an actual empty string '' in some systems, not just NaN.

Gate 2 uses not in with a list — [8, 11] from your config. LEI had one length, SWIFT has two. Same concept, not in handles multiple values cleanly.

| Error Code | Expected | Count |
|------------|----------|-------|
| BIC001 (missing) | 6 | 4 issuing + 2 confirming |
| BIC002 (wrong length) | 3 | SHORT × 3 |
| BIC003 (bad format) | 2 | 12345678 × 2 |
| **Total** | **11** | ✅ |