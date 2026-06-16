## Notebook Overview

| Cell | Purpose | What We Do |
|------|---------|------------|
| 1 | Imports + config | Load pandas, pathlib, our config files |
| 2 | Load CSV | Read `lc_transactions_v3_shuffled.csv` into DataFrame |
| 3 | Basic shape | Check rows (200) and columns (44) |
| 4 | Column names & dtypes | See what pandas guessed for each column |
| 5 | Missing values | Find nulls, count them per column |
| 6 | Categorical columns | Explore currency, lc_form, incoterm, etc. |
| 7 | Amounts | Check min, max, formats, decimal patterns |
| 8 | Amount deep-dive | Validate formats, find malformed values |
| 9 | LEI codes | Check presence, length, format |

## Goals

| Goal | What We'll Discover | Why It Matters |
|------|---------------------|----------------|
| **1. Load & inspect** | Does the CSV load? All 44 columns? 200 rows? | Confirm data arrived correctly |
| **2. Data types** | What did pandas guess? Strings? Numbers? | Pandas often guesses WRONG (amounts as strings!) |
| **3. Missing values** | Which columns have nulls? How many? | Know what needs cleaning |
| **4. Value distributions** | What currencies? What LC forms? What incoterms? | Verify data matches our `constants.py` |
| **5. Spot problems** | Extra spaces? Unicode issues? Invalid formats? | Plan our cleaning strategy |

## Notebooks vs Python Files

| Type | Purpose | Example |
|------|---------|---------|
| Notebooks (`.ipynb`) | Playground — experiment, explore, test | `01_data_exploration.ipynb` |
| Python files (`.py`) | Production — clean, tested, reusable code | `pipeline/cleaners.py` |


## Cell 1: Imports + Config

| Import | Purpose |
|--------|---------|
| `pandas` | Load and manipulate our CSV data |
| `Path` | Handle file paths (cross-platform) |
| `sys.path.insert` | Tell Python where to find our `config/` |
| `constants` | Our currencies, incoterms, column names |
| `settings` | Our file paths (INPUT_DIR, etc.) |

## Cell 4: Column Names & Data Types

| Pandas Guess | Reality | Problem |
|--------------|---------|---------|
| `object` | Could be string, could be anything | Vague! |
| `float64` | Amount like `50000.00` | Should be Decimal! |
| `object` | Date like `2024-01-15` | Should be datetime! |


## Cell 6: Explore Categorical Columns

| What We're Doing | Why |
|------------------|-----|
| Check unique values in key columns | Spot typos, invalid codes, unexpected values |
| Compare against `constants.py` | Verify data matches our allowed lists |
| Spot cleaning issues | Find lowercase, extra spaces, invalid entries |

| Column | What We Expect | From |
|--------|----------------|------|
| `currency` | USD, EUR, GBP... | `constants.VALID_CURRENCIES` |
| `lc_form` | IRREVOCABLE, STANDBY... | `constants.LC_FORMS` |
| `incoterm` | FOB, CIF, EXW... | `constants.INCOTERMS_ALL` |
| `confirmation_status` | CONFIRMED, UNCONFIRMED | `constants.CONFIRMATION_STATUSES` |

## Cell 6b: More Categorical Columns

| Column | Valid Values | Invalid Found | Error Code |
|--------|--------------|---------------|------------|
| `lc_form` | STANDBY, IRREVOCABLE, IRREVOCABLE TRANSFERABLE | `INVALID_FORM` (1) | LC004 |
| `incoterm` | FOB, CIF, EXW, CPT, etc. | `XXX` (3) | SHIP001 |

LC FORM breakdown:

| Value | Count | Status |
|-------|-------|--------|
| STANDBY | 75 | ✅ Valid |
| IRREVOCABLE | 66 | ✅ Valid |
| IRREVOCABLE TRANSFERABLE | 58 | ✅ Valid |
| INVALID_FORM | 1 | ❌ ERROR |

INCOTERM breakdown:

| Value | Count | Status |
|-------|-------|--------|
| CPT, FCA, DAP, DDP, DPU, EXW, CIP | Various | ✅ Any transport mode |
| CFR, FAS, CIF, FOB | Various | ✅ Sea only |
| XXX | 3 | ❌ ERROR transactions |

## Cell 6 Summary

| Column | What We Found | Action Needed |
|--------|---------------|---------------|
| `currency` | Mixed case (USD vs usd) | Clean: `.upper()` |
| `lc_form` | 1 invalid (INVALID_FORM) | Validate: LC004 |
| `incoterm` | 3 invalid (XXX) | Validate: SHIP001 |
| `confirmation_status` | 1 invalid (MAYBE) | Validate: CONF001 |


## Cell 7: Explore Amounts

| What We Check | Why |
|---------------|-----|
| Data type | Should be string (we convert to Decimal later) |
| Format patterns | Commas? Dots? Spaces? |
| Range | Min and max values |
| Invalid entries | Empty? Negative? Zero? |

| Rule | Note |
|------|------|
| NEVER use float for money | Use `Decimal` — floats lose precision |
| Amount column is `str` | Pandas loaded it as string, not number |

First 10 rows — errors found:

| Row | Value | Problem | Error Code |
|-----|-------|---------|------------|
| 0 | `0` | Zero amount | AMT001 |
| 1 | `-50000` | Negative amount | AMT002 |
| 2 | `9999999999.99` | Exceeds maximum | AMT003 |
| 3 | `0.001` | Below minimum | AMT004 |
| 4 | `INVALID` | Not a number! | AMT005 |
| 5 | `12345.123` | 3 decimals (should be 2) | AMT006 |
| 6-9 | `17006024`, etc. | ✅ Look valid | — |

## Cell 8: Amount Format Patterns

| Pattern | Count | What it likely means |
|---------|-------|----------------------|
| With commas | 106 | Thousand separators (100 good + 6 malformed) |
| With decimals | 79 | Has `.XX` decimal places |
| Pure numeric | 77 | Raw numbers like `12345678` (no formatting) |
| Non-numeric | 1 | Garbage — probably that `INVALID` text |

## Cell 8b: Find the Non-Numeric Garbage

| Finding | Count | Validation Rule |
|---------|-------|-----------------|
| Non-numeric text | 1 | AMT005 |
| Malformed commas | 6 | AMT005 |
| Valid formats | 193 | ✅ Parse OK |

## .loc[] Basic Patterns

| Pattern | Syntax | What it does |
|---------|--------|--------------|
| All rows, one column | `df.loc[:, 'amount']` | Get entire column as Series |
| Filter rows, one column | `df.loc[mask, 'amount']` | Get filtered values from one column |
| Filter rows, multiple columns | `df.loc[mask, ['id', 'amount']]` | Get filtered rows with specific columns |
| All rows, multiple columns | `df.loc[:, ['id', 'amount']]` | Get specific columns for all rows |

## Indexing Method Comparison

| Method | Selection Type | When to use it |
|--------|----------------|----------------|
| `.loc[]` | Label-based (column names, index) | Most cases — select by row/column names |
| `.iloc[]` | Position-based (integer index) | When you need "row 5, column 3" by position |
| `[]` | Shorthand (columns or boolean) | Quick column access like `df['amount']` |

## Cell 8c: Better Writing Styles

| Style | Code Example | Recommendation |
|-------|--------------|----------------|
| Chained indexing | `df[mask]['amount']` | ❌ Avoid — can cause warnings |
| Single `.loc[]` | `df.loc[mask, 'amount']` | ✅ Good — explicit and safe |
| Two-step | `mask = ...` then `df.loc[mask, 'amount']` | ✅ Best — easy to read and debug |

## Why Use .loc[]?

| Reason | Explanation |
|--------|-------------|
| Explicit | Clear about selecting rows AND columns |
| No chaining | Single operation instead of `df[...][...]` |
| Safer | Avoids SettingWithCopyWarning |
| Consistent | Works for reading AND updating data |

## Cell 8d: Updated Amount Discovery Summary

| Finding | Count | Error Code | Status |
|---------|-------|------------|--------|
| Non-numeric (`INVALID`) | 1 | AMT005 | 🎯 Found |
| Malformed commas | 6 | AMT005 | 🎯 Found |
| Valid with commas | 100 | - | ✅ OK |
| Pure numeric (no commas) | 77 | - | ✅ OK |
| Other edge cases | ? | AMT001-006 | 🔍 Next |

## Cell 8e: Amount Problems Summary

| Problem Type | Count | Error Code | Severity |
|--------------|-------|------------|----------|
| Zero amounts | 3 | AMT001 | CRITICAL |
| Negative amounts | 11 | AMT002 | CRITICAL |
| Too many decimals | 3 | AMT006 | MEDIUM |
| Malformed commas | 6 | AMT005 | CRITICAL |
| Non-numeric (INVALID) | 1 | AMT005 | CRITICAL |
| **Total amount errors** | **24** | - | - |

## Cell 8f: Final Amount Exploration Summary

| Problem Type | Count | Error Code | Severity | Example |
|--------------|-------|------------|----------|---------|
| Zero amounts | 3 | AMT001 | CRITICAL | `0` |
| Negative amounts | 11 | AMT002 | CRITICAL | `-50000`, `-1000` |
| Exceeds maximum | 2 | AMT003 | HIGH | `9999999999.99` |
| Too many decimals | 3 | AMT006 | MEDIUM | `0.001`, `12345.123` |
| Malformed commas | 6 | AMT005 | CRITICAL | `22,43,565`, `,123,456` |
| Non-numeric | 1 | AMT005 | CRITICAL | `INVALID` |
| **Total** | **26** | - | - | - |


## LEI CODES

### Cell 9: LEI Exploration — Basic Stats

| Column | Missing | Present |
|--------|---------|---------|
| `applicant_lei` | 1 | 199 |
| `beneficiary_lei` | 2 | 198 |

    Applicant LEI length distribution:

| Length | Count | Status |
|--------|-------|--------|
| 11 chars | 2 | ❌ Wrong length |
| 20 chars | 197 | ✅ Correct |

    Cell 9 Summary:

| Issue | Count | Error Code |
|-------|-------|------------|
| Missing applicant LEI | 1 | LEI001 |
| Missing beneficiary LEI | 2 | LEI001 |
| Wrong length (11 chars) | 2 | LEI002 |
| Correct length (20 chars) | 197 | ✅ Check format next |

    LEI length/missing problems:

| transaction_id | Field | Value | Problem | Error Code |
|----------------|-------|-------|---------|------------|
| LC-TRP0J4 | applicant_lei | `TOOSHORT123` | Only 11 chars | LEI002 |
| LC-Q85JSG | applicant_lei | `TOOSHORT123` | Only 11 chars | LEI002 |
| LC-L4ZKLO | applicant_lei | `NaN` | Missing | LEI001 |
| LC-6WKTAK | beneficiary_lei | `NaN` | Missing | LEI001 |
| LC-URTP0L | beneficiary_lei | `NaN` | Missing | LEI001 |

    Complete LEI exploration summary:

| Field | Problem | Count | Error Code | Severity |
|-------|---------|-------|------------|----------|
| applicant_lei | Missing | 1 | LEI001 | HIGH |
| applicant_lei | Wrong length (`TOOSHORT123`) | 2 | LEI002 | HIGH |
| applicant_lei | Invalid format (`INVALID!!LEI##CODE99`) | 1 | LEI003 | HIGH |
| beneficiary_lei | Missing | 2 | LEI001 | HIGH |
| beneficiary_lei | Wrong length | 0 | - | ✅ |
| beneficiary_lei | Invalid format | 0 | - | ✅ |
| **Total LEI errors** | - | **6** | - | - |

## Swift Codes
    Cell #10 SWIFT length issues:

| Column | Length | Count | Status |
|--------|--------|-------|--------|
| issuing_bank_swift | NaN (missing) | 4 | ❌ BIC001 |
| issuing_bank_swift | 5 chars | 3 | ❌ BIC002 |
| issuing_bank_swift | 8 chars | 193 | ✅ Check format |
| advising_bank_swift | 8 chars | 200 | ✅ Check format |
| confirming_bank_swift | 8 chars | 52 | ✅ Check format |

| transaction_id | Problem | Error Code |
|----------------|---------|------------|
| LC-DZR1YX | CONFIRMED but no confirming bank | LC007 |
| LC-A26YFP | CONFIRMED but no confirming bank | LC007 |

    Complete SWIFT/BIC summary:

| Issue | Count | Error Code | Severity |
|-------|-------|------------|----------|
| Missing issuing SWIFT | 4 | BIC001 | HIGH |
| Wrong length (SHORT) | 3 | BIC002 | HIGH |
| Invalid format (12345678) | 2 | BIC003 | HIGH |
| CONFIRMED + no confirming bank | 2 | LC007 | CRITICAL |
| Invalid status (MAYBE) | 1 | LC008 | HIGH |
| **Total SWIFT/confirmation errors** | **12** | - | - |

## DATES
    Updated date summary:

| Issue | Count | Error Code | Severity | Example |
|-------|-------|------------|----------|---------|
| Missing issue_date | 2 | DATE001 | HIGH | LC-30ME8F |
| Impossible date (Feb 30) | 1 | DATE008 | HIGH | LC-WM31YI |
| Expiry BEFORE issue | 2 | DATE004 | CRITICAL | -92 days validity |
| Shipment AFTER expiry | 7 | DATE005 | CRITICAL | LC-P0TVHH |
| Validity exceeds 540 days | 4 | DATE007 | MEDIUM | 882-2690 days |
| **Total date errors** | **16** | - | - | - |

| Error Type | Transactions |
|------------|--------------|
| DATE001 | LC-30ME8F, LC-B2KNFT |
| DATE004 | LC-PUXQPH, LC-PXNF7C |
| DATE005 | LC-P0TVHH, LC-ODRO8B, LC-65KXVF, LC-CW790P, LC-PUXQPH, LC-38DALY, LC-PXNF7C |
| DATE007 | LC-0OXFQ8, LC-6DPBHS, LC-5IGQPK, LC-0TPAC5 |
| DATE008 | LC-WM31YI |

    Exploration progress:

| Column Group | Status | Errors Found |
|--------------|--------|--------------|
| Amounts | ✅ Done | 26 |
| LEI codes | ✅ Done | 6 |
| SWIFT/BIC | ✅ Done | 12 |
| Dates | ✅ Done | 16 |
| Party fields | 🔜 Next | ? |

## PARTY

| Rule | Constraint |
|------|------------|
| min_name_length | 2 chars |
| max_name_length | 140 chars |
| require_address | True |
| require_lei | True (already checked!) |


    In real trade finance:

| Field | Required? | Why |
|-------|-----------|-----|
| `applicant_name` | ✅ CRITICAL | KYC — who's the buyer? Can't process without |
| `beneficiary_name` | ✅ CRITICAL | KYC — who's the seller? Can't process without |
| `applicant_country` | ✅ CRITICAL | Sanctions screening (OFAC, EU lists) |
| `beneficiary_country` | ✅ CRITICAL | Sanctions screening |
| `applicant_address` | ⚠️ HIGH | Needed for docs, but not blocking |
| `beneficiary_address` | ⚠️ HIGH | Same |
| `applicant_city` | ⚠️ MEDIUM | Part of address |
| `beneficiary_city` | ⚠️ MEDIUM | Part of address |
| `postal_code` | 📋 LOW | Some countries don't even use them! |

    Party fields summary:
| Issue | Count | Error Code | Severity | Example |
|-------|-------|------------|----------|---------|
| Missing applicant_name | 1 | PTY001 | CRITICAL | LC-HHXFGC |
| Name too short (< 2) | 3 | PTY002 | HIGH | "A" |
| Missing applicant_address | 2 | PTY004 | HIGH | - |
| Invalid country code (XX) | 1 | PTY005 | HIGH | LC-XVG0FN |
| **Total party errors** | **7** | - | - | - |


    Full error summary across all columns:
| Column Group | Errors Found | Key Issues |
|--------------|--------------|------------|
| Amounts | 26 | Zero, negative, malformed commas, INVALID |
| LEI codes | 6 | Missing, too short, invalid format |
| SWIFT/BIC | 12 | Missing, SHORT, all digits, confirmation mismatch |
| Dates | 16 | Missing, Feb 30, expiry < issue, excessive validity |
| Party fields | 7 | Missing name, "A", invalid country XX |
| **TOTAL** | **67** | - |

    67 errors across 200 transactions — some transactions have multiple errors!

| Phase | Status |
|-------|--------|
| ✅ Load data | 200 rows, 44 columns |
| ✅ Explore structure | dtypes, missing values |
| ✅ Explore amounts | 26 validation issues found |
| ✅ Explore LEI codes | 6 validation issues found |
| ✅ Explore SWIFT/BIC | 12 validation issues found |
| ✅ Explore dates | 16 validation issues found |
| ✅ Explore party fields | 7 validation issues found |


**The purpose changes:**

| Dataset Size | Exploration Purpose |
|--------------|---------------------|
| 200 rows (learning) | Understand every error type, build intuition |
| 5k rows (small prod) | Validate assumptions, check distributions |
| 500k rows (production) | Monitor health, find anomalies, alert on trends |




## Real-world example:

You're at a bank. Every day, 10,000 LCs arrive. You don't explore each one. But you **monitor**:

| Metric | Normal | Alert! |
|--------|--------|--------|
| Invalid amount % | 0.5% | 5% ← Something broke upstream! |
| Missing LEI % | 0.1% | 10% ← New client not onboarded? |
| Country XX | 0 | 50 ← Data migration error? |


If suddenly 500 transactions have `XX` as country, you don't just reject them — you call the source team and say "¿Qué pasó? Your export is broken."



## For YOUR project:

| What you did | Why it matters |
|--------------|----------------|
| Found 6 comma errors | Now your regex handles them |
| Found Feb 30 | Now you use `errors='coerce'` |
| Found "A" as name | Now you enforce min length |
| Found XX country | Now you validate against ISO codes |