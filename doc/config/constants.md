| Expression                         | Returns                | Example |
|------------------------------------|------------------------|---------|
| `CURRENCY_INFO`                    | Entire nested dict     | `{'USD': {...}, 'EUR': {...}}` |
| `CURRENCY_INFO.keys()`             | Just currency codes    | `['USD', 'EUR', 'GBP', ...]` |
| `CURRENCY_INFO['USD']`             | Inner dict for USD     | `{'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}` |
| `CURRENCY_INFO['USD']['decimals']` | Single value           | `2` |
| `VALID_CURRENCIES`                 | FrozenSet of all codes | `frozenset({'USD', 'EUR', ...})` |
| `'USD' in VALID_CURRENCIES`        | Check if valid         | `True` |





    MT700 Field Definitions


| Constant                 | Meaning                       | Real-World Use |
|--------------------------|-------------------------------|----------------|
| `LC_FORMS`               | Type of Letter of Credit      | `IRREVOCABLE` = cannot cancel without all parties agreeing |
| `AVAILABLE_WITH_OPTIONS` | How beneficiary gets paid     | `BY PAYMENT` = immediate, `BY ACCEPTANCE` = later date |
| `CONFIRMATION_STATUSES`  | Is another bank guaranteeing? | `CONFIRMED` = extra security for beneficiary |

    What are Incoterms?

Rules that define who pays for shipping, insurance, and who takes risk at each point.

| Incoterm   | Who Pays Shipping?  | Who Pays Insurance?   | Risk Transfers At |
|------------|---------------------|-----------------------|-------------------|
| `FOB`      | Buyer               | Buyer                 | Ship's rail (loading port) |
| `CIF`      | Seller              | Seller                | Ship's rail (loading port) |
| `DDP`      | Seller              | Seller                | Buyer's door |



  
     Why split into two sets?

| Set                  | Use Case |
|----------------------|----------|
| `INCOTERMS_ANY_MODE` | Truck, train, air, ship — any transport |
| `INCOTERMS_SEA_ONLY` | ONLY for sea/waterway transport |
| `INCOTERMS_ALL`      | Combined — for general validation |

    Set Operators:

| Operator   | Name         | Meaning        | Example |
|------------|--------------|----------------|---------|
| `          | `            | Union          | In A OR B | `{1,2} | {2,3}` → `{1,2,3}` |
| `&`        | Intersection | In A AND B     | `{1,2} & {2,3}` → `{2}` |
| `-`        | Difference   | In A but NOT B | `{1,2} - {2,3}` → `{1}` |




     Regex Patterns

| Key            | Pattern                    | Valid Example               | Invalid Example |
|----------------|----------------------------|-----------------------------|-----------------|
| `lei`          | 18 alphanumeric + 2 digits | `HWUPKR0MPOU8FGXBT394`      | `HWUPKR0MPOU8FGXBT3` (too short) |
| `swift_bic`    | 8 or 11 characters         | `HSBCHKHH` or `HSBCHKHHXXX` | `HSB` (too short) |
| `country_code` | 2 uppercase letters        | `US`, `GB`, `JP`            | `USA` (3 letters) |
| `port_code`    | 2 letters + 3 alphanumeric | `USLAX`, `KRPUS`            | `LA` (too short) |
| `date_iso`     | YYYY-MM-DD                 | `2025-12-11`                | `12/11/2025` (wrong format) |


| Group              | Count |
|--------------------|-------|
| `COLS_CORE`        | 4 |
| `COLS_DATES`       | 3 |
| `COLS_APPLICANT`   | 7 |
| `COLS_BENEFICIARY` | 7 |
| `COLS_BANKS`       | 8 |
| `COLS_AMOUNT`      | 3 |
| `COLS_SHIPMENT`    | 6 |
| `COLS_DOCUMENTS`   | 4 |
| `COLS_PAYMENT`     | 2 |
| **TOTAL**          | **44** ✅ |

    Validation columns explained

| Column              | Type | Example |
|---------------------|------|---------|
| `validation_status` | str | `'VALID'` or `'INVALID'` |
| `error_count`       | int | `0`, `1`, `3` |
| `error_codes`       | str | `'LEI001,DATE003'` |
| `error_messages`    | str | `'LEI is empty, Expiry before issue'` |
| `severity`          | str | `'CRITICAL'`, `'HIGH'`, `'MEDIUM'`, `'LOW'` |



One more pro tip on the alias pattern, since you appreciated it:

The 'flagged' / 'clean' alias trick has a name in software engineering:
"semantic indirection" or "intent-revealing names."

The principle: when the SAME value plays DIFFERENT ROLES, give each role
its own name even if the underlying value is identical.

Bad code:
   color=PIPELINE_PALETTE['high']   # Why is the flagged donut "high"?

Good code:
   color=PIPELINE_PALETTE['flagged'] # Crystal clear

Robert Martin (Clean Code author) calls this "naming for the reader, not
the writer." The reader of your code 6 months from now (probably you)
shouldn't have to remember WHY a flagged status is "high severity color."
The alias does the remembering.

Banks do this everywhere. The same hex code might be:
- 'flagged' in compliance dashboards
- 'high_risk' in market risk reports
- 'urgent' in operations alerts
- 'red' in executive summaries

Same color, four roles, four names. None of them confused with each other.













