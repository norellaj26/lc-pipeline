

                                          AMOUNT VALIDATION

| Key | Purpose | Example |
|-----|---------|---------|
| `min_value` | Smallest valid amount | `Decimal('0.01')` |
| `max_value` | Largest valid amount | `Decimal('999999999.99')` |
| `allow_zero` | Is $0.00 valid? | `False` (LC must have value!) |
| `allow_negative` | Is -$100 valid? | `False` (never!) |
| `errors` | Error codes + messages | `'AMT001': {...}` |

                                            LEI VALIDATION

| Code | When It Triggers | Severity |
|------|------------------|----------|
| `LEI001` | Field is empty `""` | HIGH |
| `LEI002` | Wrong length: `"ABC123"` (not 20 chars) | HIGH |
| `LEI003` | Wrong pattern: `"HWUPKR0MPOU8FGXBT3##"` (invalid chars) | HIGH |
| `LEI004` | Valid format BUT not in GLEIF API | HIGH |
| `LEI005` | Found in GLEIF but status is LAPSED | MEDIUM |
| `LEI006` | API timeout/error (not LEI's fault) | LOW |
```
Why 8 or 11 characters?
```
| Length | Format | Example |
|--------|--------|---------|
| 8 | `BANKCCLL` | `HSBCHKHH` (HSBC Hong Kong, head office) |
| 11 | `BANKCCLLXXX` | `HSBCHKHHXXX` (same, with branch code) |

```   
    
HSBCHKHH
││││││││
││││││└└── LL = Location code (HH = head office)
││││└└──── CC = Country code (HK = Hong Kong)
└└└└────── BANK = Bank code (HSBC)


# Bank says country is "US" but SWIFT code says "HK"
issuing_bank_country = "US"
issuing_bank_swift = "HSBCHKHH"  # ← HK in position 5-6!
# Mismatch! → BIC004
```


| Position | Characters | Name | Example |
|----------|------------|------|---------|
| 1-4 | `HSBC` | Bank code | HSBC |
| 5-6 | `HK` | Country code (ISO) | Hong Kong |
| 7-8 | `HH` | Location code | Head office |
| 9-11 | `XXX` | Branch code (optional) | Main branch |


| SWIFT Code | Bank | Country | Location | Branch |
|------------|------|---------|----------|--------|
| `HSBCHKHH` | HSBC | HK | HH (head) | - |
| `HSBCHKHHXXX` | HSBC | HK | HH | XXX |
| `DEUTDEFF` | Deutsche Bank | DE | FF (Frankfurt) | - |

```

                              DATE VALIDATION
```
| Setting | Value | Why |
|---------|-------|-----|
| `min_date` | 2020-01-01 | Don't accept ancient data |
| `max_date` | 2030-12-31 | Don't accept far future |
| `max_validity_days` | 540 | LC can't be valid for 18+ months |
| `max_future_issue_days` | 30 | Issue date shouldn't be far in future |

```

Critical errors (DATE004, DATE005)
```
| Error | Example | Problem |
|-------|---------|---------|
| DATE004 | Issue: 2025-06-01, Expiry: 2025-03-01 | LC expired before it started! |
| DATE005 | Expiry: 2025-06-01, Shipment: 2025-07-15 | Ship after LC dead! |

``` 
 Why `_today` with underscore?
```
| Name | Meaning |
|------|---------|
| `_today` | Private helper, not for export |
| `today`  | Could conflict with other imports |
```

 What it calculates (today = Dec 11, 2025)
```

| Setting | Calculation | Result |
|---------|-------------|--------|
| `min_date` | 2025-12-11 - 540 days | `'2024-06-20'` |
| `max_date` | 2025-12-11 + 60 days | `'2026-02-09'` |
```
                                      PARTY VALIDATION
```

| Setting | Value | Why |
|---------|-------|-----|
| `min_name_length` | 2 | Single letter names suspicious |
| `max_name_length` | 140 | SWIFT MT700 field limit |
| `require_address` | True | Must know where party is |
| `require_lei` | True | We validate with GLEIF! |
```
  When each error triggers: 

```


| Code | Example | Severity |
|------|---------|----------|
| `PTY001` | name = `""` or `None` | CRITICAL |
| `PTY002` | name = `"A"` | HIGH |
| `PTY003` | name = 200 characters | MEDIUM |
| `PTY004` | address = `""` | HIGH |
| `PTY005` | country = `"XX"` (not in VALID_COUNTRY_CODES) | HIGH |
| `PTY006` | lei = `""` when require_lei is True | HIGH |
| `PTY007` | name = `"Apple Inc. @#$%"` | MEDIUM |
```

                                   LETTER OF CREDIT VALIDATION:

```
| Setting | Value | Why |
|---------|-------|-----|
| `lc_number_min_length` | 5 | Too short = suspicious |
| `lc_number_max_length` | 35 | SWIFT field limit |
| `require_confirming_bank` | False | Not all LCs are confirmed |

```
 Connection to constants.py
```
| Error Code | Validates Against |
|------------|-------------------|
| `LC004` | `LC_FORMS` (IRREVOCABLE, STANDBY, etc.) |
| `LC005` | `AVAILABLE_WITH_OPTIONS` (BY PAYMENT, etc.) |
| `LC008` | `CONFIRMATION_STATUSES` (CONFIRMED, UNCONFIRMED) |


                                     🚢 SHIPMENT VALIDATION
```
Connection to constants.py:
```
| Error Code | Validates Against |
|------------|-------------------|
| `SHIP001` | `INCOTERMS_ALL` (FOB, CIF, DDP, etc.) |
| `SHIP004` | `PATTERNS['port_code']` (regex) |
| `SHIP005` | `INCOTERMS_SEA_ONLY` (FOB, CIF, CFR, FAS) |
```
SHIP005 logic
```
| Incoterm | Port Required? | Why |
|----------|----------------|-----|
| `FOB` | YES | "Free On Board" = needs ship! |
| `CIF` | YES | "Cost Insurance Freight" = sea only |
| `DDP` | NO | "Delivered Duty Paid" = any transport |


                            🔗 CROSS-VALIDATION (Between fields/documents)

**What is cross-validation?**

Single field validation:
```
amount = -500 → AMT002 (negative)
```

Cross-validation (between fields):
```
applicant_name = "Apple Inc."
beneficiary_name = "Apple Inc."
→ XVAL001 (same party on both sides!)
```

**Examples:**


| Code | Field 1 | Field 2 | Problem |
|------|---------|---------|---------|
| `XVAL001` | applicant = "Apple" | beneficiary = "Apple" | Can't pay yourself! |
| `XVAL002` | applicant_country = "US" | issuing_bank_country = "JP" | Bank not in applicant's country |
| `XVAL003` | currency = "COP" | issuing_bank_country = "JP" | Japanese bank, Colombian pesos? |
| `XVAL004` | shipment = "2025-08-01" | expiry = "2025-06-01" | Ship after LC expired! |







