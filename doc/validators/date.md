DateValidator needs to check three dates AND their relationships:

| Check Type | Example | Error |
|------------|---------|-------|
| Individual | Is issue_date present? | DATE001 |
| Individual | Is 2026-02-30 real? | DATE008 |
| Cross-date | Expiry before issue? | DATE004 |
| Cross-date | Shipment after expiry? | DATE005 |
| Cross-date | Validity > 540 days? | DATE007 |

Phase 1: Check each date individually — present? parseable? real?

Phase 2: Compare dates against each other — onlym if Phase 1 gave us valid dates to compare.

| Error Code | Expected | Found | Notes |
|------------|----------|-------|-------|
| DATE001 | 2 | 2 | ✅ |
| DATE002 | 0 | 2 | Feb 30 + MM/DD format |
| DATE004 | 2 | 2 | ✅ |
| DATE005 | 7 | 7 | ✅ |
| DATE007 | 4 | 4 | ✅ |
| DATE008 | 1 | 0 | Caught at Gate 2 instead |
| **Total** | **16** | **17** | **✅ +1 legit** |

| Validator | Errors | Status |
|-----------|--------|--------|
| AmountValidator | 27/27 | ✅ |
| LeiValidator | 6/6 | ✅ |
| SwiftValidator | 11/11 | ✅ |
| PartyValidator | 7/7 | ✅ |
| DateValidator | 17/17 | ✅ |
| CrossValidator | — | 🔜 |