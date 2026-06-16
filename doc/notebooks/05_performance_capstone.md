# ================ Cell # 3-4 =======================================

| Problem                                   | Impact                           |
|-------------------------------------------|----------------------------------|
| String columns that should be categorical | 10-100x memory waste             |
| Wrong numeric type (int64 vs int8)        | 8x memory waste                  |
| Dates stored as strings                   | Can't do date math, slow filters |
| Missing values forcing float dtype        | Can't use integers at all        |

The memory_usage='deep' flag is critical — without it, pandas lies about string column

540 KB for 200 rows. For 2 million rows, that's ~5.4 GB. And look at what pandas chose:

| Column                      | Current dtype | Problem                                                       |
|-----------------------------|---------------|---------------------------------------------------------------|
| tolerance_percent           | int64         | 8 bytes per row when 1 byte would do (values 0-10)            |
| presentation_period_days    | int64         | Same — small range, wasted bytes                              |
| error_count                 | int64         | Same — max is 6                                               |
| lc_form, currency, severity | str           | Repeated values — should be category                          |
| issue_date, expiry_date     | str           | Dates stored as text — no date math possible                  |
| amount                      | str           | Dates stored as text because your pipeline has garbage values |

Part 2: Categorical — The Big Memory Win

When a string column has few distinct values repeated many times, it's a prime candidate for category.
Pandas stores the unique values once and uses tiny integer codes for each row.

Before (str):                     After (category):
| row | value | | row | code | | code | value |
|-----|-----------| |-----|------| |------|-------|
| 0 | FLAGGED | | 0 | 1 | | 0 | CLEAN |
| 1 | CLEAN | | 1 | 0 | | 1 | FLAGGED|
| 2 | FLAGGED | | 2 | 1 |

* Goal: Measure memory before and after converting a column to category dtype.

report['validation_status'] = report['validation_status'].astype('category')
Converts the column from str dtype to category. Instead of storing the full string (e.g. "VALID")
for every single row, pandas now stores:

- A lookup table of unique values: ["VALID", "FLAGGED", "WARNING"]
- An integer code per row pointing into that table: [0, 1, 0, 0, 2, ...]

This saves memory when a column has low cardinality — few unique values repeated many times.

| Test                              | Before   | After  | Saved |
|-----------------------------------|----------|--------|-------|
| Single column (validation_status) | 11,188 B | 442 B  | 96%   |
| Whole DataFrame (9 columns)       | 553 KB   | 455 KB | 17.8% |

That single column went from 11KB to 442 bytes — 25x smaller.
And across the whole DataFrame, converting just 9 columns saved ~100KB.
Imagine that on 2 million rows: ~1GB saved by changing 9 dtypes.

When to use category — the rule

| Condition                              | Use category?                |
|----------------------------------------|------------------------------|
| Few unique values, many rows           | YES (huge win)               |
| Many unique values relative to rows    | NO (overhead > savings)      |
| Values are stable (won't get new ones) | YES                          |
| Values change frequently               | NO (cat operations are slow) |
| You'll do groupby/sort on it           | YES (much faster)            |
| Free-form text (names, addresses)      | NO                           |

# ================ Cell # 5-6 =======================================

* Goal: Systematically find which columns are good candidates to convert to category dtype, instead of guessing.

Step 1 — Get all string columns

str_cols = report.select_dtypes(include='object').columns

select_dtypes(include='object') filters the DataFrame to only columns with the object dtype (string columns). .
columns gives you just their names.

The warning you see is pandas 2.x telling you that in the future,
you'll need to write include='str' instead of include='object'.
It still works, just a heads-up about a coming change.
                                                                                                                                                                     
---             
Step 2 — Calculate the uniqueness ratio for each column

unique_ratio = report[col].nunique() / len(report)

- nunique() = how many distinct values the column has
- len(report) = total number of rows (200)
- The ratio tells you: what fraction of rows have a unique value?

Examples from your output:

┌────────────────────┬─────────┬───────┬─────────────────────────────────────────┐                                                                                 
│ Column │ nunique │ ratio │ Meaning │
├────────────────────┼─────────┼───────┼─────────────────────────────────────────┤                                                                                 
│ documents_required │ 1 │ 0.005 │ Same value in almost every row │
├────────────────────┼─────────┼───────┼─────────────────────────────────────────┤
│ payment_terms │ 3 │ 0.015 │ Only 3 different values across 200 rows
│                                                                                 
├────────────────────┼─────────┼───────┼─────────────────────────────────────────┤
│ applicant_country │ 8 │ 0.040 │ 8 unique countries, 200 rows
│                                                                                 
└────────────────────┴─────────┴───────┴─────────────────────────────────────────┘
  
---                                                                                                                                                                
Step 3 — Build and sort a DataFrame of results

candidates = pd.DataFrame(ratios).sort_values('unique_ratio')
candidates.head(15)

Builds a table from the list of dicts, sorts by unique_ratio ascending (lowest = most repeated = best candidate), and
shows the top 15.
                  
---                                                                                                                                                                
The rule of thumb (from the markdown above the cell)

▎ If nunique() / len() < 0.5, it's a candidate.

A ratio of 0.5 means half the values are unique — still worth converting. A ratio near 0 means values are heavily
repeated — categorical will compress it          
dramatically, like you saw with validation_status (96% savings).

Everything in that top-15 list has a ratio ≤ 0.075, meaning they're all excellent candidates. Columns like
applicant_name or transaction_id would be near 1.0 —    
nearly every value is unique — so categorical would actually waste memory there.

| Column               | Unique | Verdict                                       |
|----------------------|--------|-----------------------------------------------|
| documents_required   | 1      | Only 1 value?! Same string in all 200 rows    |
| payment_terms        | 3      | Perfect category candidate                    |
| charges              | 3      | Perfect                                       |
| issuing_bank_country | 6      | Perfect                                       |
| beneficiary_country  | 7      | Perfect                                       |
| applicant_country    | 8      | Perfect                                       |
| issuing_bank_name    | 12     | Still good — 12 banks across 200 transactions |

50% saved by converting 22 columns. The DataFrame is now half its original size — and you didn't change a single value,
just told pandas to store them smarter.

| Stage                   | Memory | Cumulative savings |
|-------------------------|--------|--------------------|
| Original                | 553 KB | —                  |
| First 9 cat conversions | 455 KB | 18%                |
| All 22 cat conversions  | 226 KB | 59% from original  |

Goal: Take the candidate list from cell #5 and automatically convert ALL good candidates in one shot, then measure the
total impact.
                                                                                                                                                                     
---                                                                                                                                                                
Step 1 — Filter candidates by the threshold

good_candidates = candidates.query("unique_ratio < 0.1")['column'].tolist()

- candidates is the DataFrame built in cell #5 (column name + ratio + nunique)
- .query("unique_ratio < 0.1") keeps only columns where fewer than 10% of values are unique — meaning they're heavily
  repeated
- ['column'] grabs just the column name column
- .tolist() converts it from a pandas Series to a plain Python list of strings

Result: 22 column names that qualify.
                                                                                                                                                                     
---                                                                                                                                                                
Step 2 — Measure memory before

before = report.memory_usage(deep=True).sum()

memory_usage(deep=True) returns a Series — one byte count per column. .sum() adds them all up to get the total DataFrame
memory.
This is the baseline: 454,756     
bytes (already lower than cell #4's 553K because cell #4 had already converted 9 columns).
                                                                                                                                                                     
---                                                                                                                                                              
Step 3 — Convert all 22 columns

for col in good_candidates:
report[col] = report[col].astype('category')

Same pattern as before — loop through the list and convert each column in place.
   
---                                                                                                                                                                
Step 4 — Measure after and report

after = report.memory_usage(deep=True).sum()
print(f"Saved:  {(1 - after/before) * 100:.1f}%")

Result: 50.3% saved — the DataFrame went from ~455K to ~226K bytes.
                                                                                                                                                                     
---                                                                                                                                                                
The bigger picture — cumulative savings

Notice the before here is 454,756, not the original 553K.
That's because cell #4 already converted 9 columns. So the total journey is:

┌──────────────────────────────────┬───────────────┬─────────────────────┐                                                                                         
│ Stage │ Memory │ Savings vs original
│                                                                                         
├──────────────────────────────────┼───────────────┼─────────────────────┤                                                                                         
│ Original (cell #4 baseline)      │ 553,152 bytes │ —
│                                                                                       
├──────────────────────────────────┼───────────────┼─────────────────────┤
│ After cell #4 (9 columns)        │ 454,756 bytes │ 17.8%
│                                                                                         
├──────────────────────────────────┼───────────────┼─────────────────────┤                                                                                         
│ After cell #6 (22 columns total) │ 225,848 bytes │ 59.2%
│                                                                                         
└──────────────────────────────────┴───────────────┴─────────────────────┘

The key insight: cell #5 gave you a data-driven way to find candidates (ratio < 0.1),
instead of manually guessing which columns to convert like cell #4 did. Cell
#6 just automates acting on that finding.

## ================ Cell # 7 - 8 =======================================

| Dtype  | Range             | Bytes              |
|--------|-------------------|--------------------|
| int8   | -128 to 127       | 1                  |
| int16  | -32,768 to 32,767 | 2                  |
| int32  | -2.1B to 2.1B     | 4                  |
| int64  | huge              | 8                  |
| uint8  | 0 to 255          | 1 (only positives) |
| uint16 | 0 to 65,535       | 2 (only positives) |

* Goal: Inspect the integer columns to see if their actual value ranges justify using int64.

---                                                                                                                                                                
The problem it's addressing

By default, pandas reads all integer columns as int64. That dtype uses 8 bytes per value and
can store numbers up to 9,223,372,036,854,775,807 (9 quintillion).

But look at what's actually in these columns:

┌──────────────────────────┬─────┬─────┬────────────────────────────────┐                                                                                          
│ Column │ min │ max │ What it represents │
├──────────────────────────┼─────┼─────┼────────────────────────────────┤                                                                                          
│ tolerance_percent │ 0 │ 10 │ A percentage, never exceeds 10 │
├──────────────────────────┼─────┼─────┼────────────────────────────────┤
│ presentation_period_days │ 14 │ 21 │ A day count, tiny range
│                                                                                          
├──────────────────────────┼─────┼─────┼────────────────────────────────┤
│ error_count │ 0 │ 6 │ Number of validation errors
│                                                                                          
└──────────────────────────┴─────┴─────┴────────────────────────────────┘

All three columns are using 8 bytes per value to store numbers that could fit in 1 byte.
That's the overkill the comment refers to.

For your three columns, uint8 (or even int8) is plenty — values 0-21 fit comfortably in a single byte.
---                                                                                                                                                                
The code itself

int_cols = ['tolerance_percent', 'presentation_period_days', 'error_count']
for col in
int_cols:                                                                                                                                               
print(f"{col}: min={report[col].min()}, max={report[col].max()}, dtype={report[col].dtype}")

Just loops over the 3 integer columns (identified from cell #2's info() output —
those were the only 3 int64 columns) and prints their min, max, and current dtype.
No conversion yet — this cell is just reconnaissance before acting.
                                                                                                                                                                     
---             
What comes next (the payoff)

Once you know the ranges, you can downcast:

- Values 0–10 fit in int8 (1 byte, handles –128 to 127)
- Values 0–21 fit in int8 too
- Values 0–6 fit in int8 too

So all 3 columns could go from int64 (8 bytes each) → int8 (1 byte each) — an 87.5% reduction per column.
Cell #8 will likely do exactly that with                 
pd.to_numeric(..., downcast='integer') or .astype('int8').

ell #8 is numeric downcasting — shrinking integer columns from their default oversized type to the smallest type that
still fits the data.

before = report.memory_usage(deep=True).sum()

for col in
int_cols:                                                                                                                                               
report[col] = pd.to_numeric(report[col],
downcast='unsigned')                                                                                                  
print(f"{col} -> {report[col].dtype}")

What pd.to_numeric(..., downcast='unsigned') does:

It takes a column and asks: "What's the smallest unsigned integer type that can hold every value in this column?" Then
it converts it.

From cell #7 you saw the actual ranges:

- tolerance_percent: 0–10
- presentation_period_days: 14–21
- error_count: 0–6

All three had been stored as int64 (8 bytes per value). But those tiny ranges fit comfortably in uint8
(1 byte per value, holds 0–255). So pandas downcasts them
automatically.

The unsigned part means it picks from the unsigned family (uint8, uint16, uint32, uint64)
instead of signed (int8, int16, etc.). Unsigned types have no negative   
numbers, so they can hold slightly larger positive values in the same space. Since all your values are ≥ 0, unsigned is
the right choice.

The memory saving: each column goes from 8 bytes per row → 1 byte per row.
For 200 rows that's 1,600 bytes → 200 bytes per column, an 8x reduction per column.

* downcast='unsigned' tells pandas: "find the smallest unsigned int that fits."
  Use 'integer' instead if any values could be negative. Run it!
*

# ================ Cell # 9 - 11 =======================================

Part 4: Datetime conversion
Your date columns (issue_date, expiry_date, latest_shipment_date) are stored as strings. That means:

Can't compute expiry - issue to get days
Can't filter by > '2024-01-01' properly (string comparison, not date)
Slower than native datetime

errors='coerce' is your defensive friend — bad date strings become NaT
(Not a Time, the datetime version of NaN) instead of crashing.

Cell #8 is numeric downcasting — shrinking integer columns from their default oversized type to the smallest type that
still fits the data.

before = report.memory_usage(deep=True).sum()

for col in int_cols:
report[col] = pd.to_numeric(report[col], downcast='unsigned')
print(f"{col} -> {report[col].dtype}")

What pd.to_numeric(..., downcast='unsigned') does:

It takes a column and asks: "What's the smallest unsigned integer type that can hold every value in this column?" Then
it converts it.

From cell #7 you saw the actual ranges:

- tolerance_percent: 0–10
- presentation_period_days: 14–21
- error_count: 0–6

All three had been stored as int64 (8 bytes per value). But those tiny ranges fit comfortably in uint8 (1 byte per
value, holds 0–255). So pandas downcasts them
automatically.

The unsigned part means it picks from the unsigned family (uint8, uint16, uint32, uint64) instead of signed (int8,
int16, etc.). Unsigned types have no negative
numbers, so they can hold slightly larger positive values in the same space. Since all your values are ≥ 0, unsigned is
the right choice.

The memory saving: each column goes from 8 bytes per row → 1 byte per row. For 200 rows that's 1,600 bytes → 200 bytes
per column, an 8x reduction per column.

# cell 9

● Cell #9 is datetime conversion — changing date columns from plain strings into proper datetime objects that pandas
understands as time.

date_cols = ['issue_date', 'expiry_date', 'latest_shipment_date']
for col in date_cols:
report[col] = pd.to_datetime(report[col], errors='coerce')

Why bother converting?

Right now those columns are just text like "2024-03-15". Pandas has no idea that's a date — it can't sort them
chronologically, can't do expiry_date - issue_date
to get a duration, can't filter by month. Once converted to datetime64, all of that works naturally.

What errors='coerce' does:

It's your safety net for bad data. Without it, a single malformed value like "2024-99-99" would crash the whole
conversion. With errors='coerce', bad values
silently become NaT (Not a Time) — the datetime equivalent of NaN. The rest of the column converts successfully.

The output — datetime64[us]:

us means microsecond precision. That's just pandas choosing a storage format internally — nothing you need to configure.

Connecting to your project: your DateValidator already catches bad dates during validation, so by the time you reach
this stage most dates should be clean. But
errors='coerce' is still good practice defensively, since the report CSV could have NaN rows from transactions that were
missing dates entirely (you saw issue_date
had 198 non-null out of 200 back in cell #2).

❯ so without think , always we have to convert date ?

● Not always — it depends on what you need to do with the dates.

Convert to datetime when you need to:

- Calculate durations (expiry_date - issue_date)
- Sort chronologically
- Filter by year/month/day
- Check if a date is before/after another

Leave as strings when:

- You're just displaying or storing them (passing through to a report CSV)
- Your validator already handles them as strings (like your DateValidator does — it parses them manually with
  datetime.strptime)

In your pipeline specifically, DataCleaner and ValidationService work with strings just fine.
The datetime conversion in the notebook is only useful for analysis —
like "how many LCs expire this month?" or "what's the average validity period?".
If you're not doing that kind of analysis, there's no reason to convert.

* The .dt accessor is to datetimes what .str is to strings — it gives you date-specific operations.  
  report['validity_days'] = (report['expiry_date'] - report['issue_date']).dt.days at cell # 10

This line calculates how many days each LC is valid for and stores it in a new column.

Breaking it down left to right:

report['expiry_date'] -
report['issue_date']                                                                                                                       
Subtracts two datetime columns. Because they're datetime64 (converted in cell #9), pandas knows how to do this
— the result is a Timedelta column, like "45 days
00:00:00". You can't do this with plain strings.

.dt.days                                                                                                                                                           
.dt is the datetime accessor — it lets you extract parts of a Timedelta/datetime. .
days pulls out just the integer number of days, so "45 days 00:00:00" becomes

45.

report['validity_days'] = ...                                                                                                                                      
Creates a brand new column on the DataFrame with those integers.
                                                                                                                                                                     
---                                                                                                                                                                
So a row with issue_date = 2024-01-01 and expiry_date = 2024-03-15 would get validity_days = 74.

This is exactly the kind of calculation that would be impossible if those columns were still strings
— which ties back to your earlier question about when you
actually need to convert dates.

| Concept                    | What you learned                                    |
|----------------------------|-----------------------------------------------------|
| .info(memory_usage='deep') | Truth-telling about real memory use                 |
| Categorical dtype          | 25-100x memory win for repeated values              |
| When to use category       | nunique/len < 0.5 + stable values + groupby usage   |
| pd.to_numeric(downcast=)   | Shrink int64 → uint8 when range is small            |
| pd.to_datetime()           | Strings → real dates, enables .dt operations        |
| errors='coerce'            | Bad values become NaT instead of crashing           |
| .dt accessor               | Like .str but for dates (.dt.days, .dt.year, etc.)  |
| Real-world LC validity     | Not a tech rule — it's a business rule              |
| Engineering judgment       | Document improvements, don't always fix immediately |  

| Memory journey | Size   | Reduction |
|----------------|--------|-----------|
| Original       | 553 KB | —         |
| + Categories   | 226 KB | 59%       |
| + Downcasts    | 222 KB | 60%       |

## Day 62 — Missing Data Strategies.

# ================ Cell # 12 - =======================================

Missing data is the #1 source of silent bugs in data engineering.
Pandas uses NaN (Not a Number) for missing values,
and NaN has some very sneaky behaviors that can corrupt your analysis without any errors or warnings.

* report.isnull() first scans the entire DataFrame and returns a same-shaped table of True/False:

  transaction_id lc_number
  issue_date ...                                                                                                                         
  False False False ... ← row
  0                                                                                                              
  False True False ... ← row 1  (NaN
  here)                                                                                                    
  False False True ... ← row 2  (NaN
  here)                                                                                                    
  ...

  Then .sum() goes column by column and adds up all the Trues (since True = 1, False = 0):

  transaction_id
  0                                                                                                                                              
  lc_number 2
  issue_date
  2                                                                                                                                              
  ...
* my cloumn nane for missing column is unnamed ,, for exapme how can i give it a name 'missing

● When you call .sum() on a DataFrame it returns a Series, not a DataFrame — so there's no column name, just an index.

* To give it a name:

  missing = report.isnull().sum().rename('missing')

  Or if you want it as a proper DataFrame with a named column:

  missing = report.isnull().sum().rename_axis('column').reset_index(name='missing')

  The second one gives you a cleaner
  table:                                                                                                                          
  column
  missing                                                                                                                                          
  0 transaction_id 0
  1 lc_number 2
  2 issue_date
  2                                                                                                                                          
  ...

  The first one is simpler and usually enough for quick analysis.
  | Column | Missing | Why | Type of missingness |
  |------- -|---------|-----|-------------------|
  | additional_conditions | 175 | Most LCs don't have extra conditions | Legitimately absent |
  | confirming_bank_name/swift | 148 | Only 52 LCs are CONFIRMED | Structurally absent |
  | error_codes/messages | 72 | Clean transactions have no errors | By design |
  | port_of_loading | 23 | SHIP002 errors — missing ports | Data quality issue |
  | issue_date | 4 | DATE001 — date missing | Data quality issue |
  | issuing_bank_swift | 4 | BIC001 — SWIFT missing | Data quality issue |
  | lc_number | 2 | LC001 — LC number missing | Data quality issue |

This distinction matters because each type requires a different strategy:

| Type                | Example                            | Strategy                                  |
|---------------------|------------------------------------|-------------------------------------------|
| Legitimately absent | additional_conditions              | Leave as NaN — absence IS the information |
| Structurally absent | confirming_bank when UNCONFIRMED   | Leave as NaN — not applicable             |
| By design           | error_codes for clean transactions | Could fill with '' or leave as NaN        |
| Data quality issue  | missing port_of_loading            | Flag, investigate, possibly impute        |

* design

The core difference:

- NaN is a float in disguise — it sneaks into string columns and breaks string operations
- '' is just an empty string — it behaves predictably everywhere

So if a column is going to be used in string operations downstream, '' is safer.
But if you want to use .isnull() to detect missing values later, NaN is better —  
because '' == '' is always True and pandas won't count it as missing.

❯ so if we want the safe way, we should use '' ? maybe someone will use it in string op

● Not necessarily — it's a trade-off, not a clear winner:

''
breaks:                                                                                                                                                         
report.isnull().sum()  # won't count '' as missing — invisible gap in your
data                                                                                    
report['error_codes'].fillna('none')  # does nothing — '' is not NaN

NaN
breaks:                                                                                                                                                        
"Errors: " + row['error_codes']  # crashes on string ops
                                                                                                                                                                     
---                                                                                                                                                                
So the "safe" choice depends on what comes next:

- If the column is used for display/export/string ops → ''
- If the column needs missing value detection → NaN

  ---                                                                                                                                                                
The real safe way is to handle it explicitly before use:

# convert NaN to '' just before string ops

report['error_codes'].fillna('')

This way you keep NaN in storage (so .isnull() still works) and only convert to '' at the moment you need it. Best of
both worlds.

"type of missingness" is about why the value is missing, which matters a lot for how you handle it.
                                                                                                                                                                     
---                                                                                                                                                                
Legitimately absent — the field is optional and missing is the normal, expected state.

- additional_conditions — most LCs simply don't have extra conditions. A blank here means "none", not "someone forgot to
  fill it in."

  ---                                                                                                                                                                
Structurally absent — missing because of how the data is designed. Another field controls whether this one exists.

- confirming_bank_name/swift — only CONFIRMED LCs have a confirming bank. If confirmation_status = "UNCONFIRMED",
- these fields will always be empty. The structure
  of the data makes them absent.

  ---             
By design — missing because the pipeline intentionally leaves it blank.

- error_codes/messages — clean transactions have no errors, so these are blank on purpose.
- Your ReportService only writes them when there are actual errors.

  ---                                                                                                                                                                
Data quality issue — missing when it shouldn't be. These are real problems.

- port_of_loading, issue_date, issuing_bank_swift,
- lc_number — these are required fields that got flagged by your validators (SHIP002, DATE001, BIC001, LC001).    
  Missing here = bad data.

  ---             
Why it matters: the first three types you leave alone. Only the last type needs fixing
— and your pipeline already catches them as validation errors.

Leave as NaN — absence IS the
information                                                                                                                          
The NaN itself carries meaning. additional_conditions = NaN tells you "this LC has no special conditions." Filling it
with "" or "none" would actually lose that   
signal.
                                                                                                                                                                     
---             
Leave as NaN — not
applicable                                                                                                                                      
Same idea but stricter. confirming_bank = NaN when confirmation_status = UNCONFIRMED isn't just absent — it's logically
impossible to have a value there. NaN is
the correct and only valid state.
                                                                                                                                                                     
---
Could fill with '' or leave as
NaN                                                                                                                                 
This one is a judgment call. error_codes = NaN on a clean transaction is fine as-is, but if you're exporting to CSV or
feeding it downstream, an empty string ''
might be easier to work with than NaN. Either is defensible.
                                                                                                                                                                     
---
Flag, investigate, possibly
impute                                                                                                                                 
"Impute" means fill in a missing value with an estimate — like using the most common port, or inferring from other
fields. But for your pipeline, your validators
already flagged these (SHIP002 etc.), so the "flag" step is already done. Imputing LC data would be risky — you don't
want to guess a port of loading on a
financial document.
   
---                                                                                                                                                                
The big insight: not all NaNs are equal. Same symbol, four completely different meanings.

# ================ Cell # 13 - 20 =======================================

------- --------------------- ------------- -----  
import numpy as np

print(f"1 + NaN = {1 + np.nan}")       #
nan                                                                                                                       
print(f"NaN == NaN: {np.nan == np.nan}")  #
False                                                                                                                  
print(f"NaN > 5: {np.nan > 5}")           # False
------- ---------------- ---- ----------------- --
1 + NaN = nan — NaN is contagious

Any arithmetic involving NaN produces NaN. Think of it as "unknown"
— if you add 1 to an unknown value, the result is still unknown. This is called NaN
propagation.

Real danger in your
pipeline:                                                                                                                                      
total = report['error_count'].sum()  # fine
avg = report['validity_days'].mean() # fine — pandas skips NaN by
default                                                                                          
But in plain
Python:                                                                                                                                               
1 + float('nan')  # → nan, silently ruins your calculation
                                                                                                                                                                     
---                                                                                                                                                                
NaN == NaN: False — NaN is not equal to itself

This is the most surprising one. NaN means "unknown value" — and two unknown values aren't necessarily
the same unknown. So by definition, NaN != NaN.

Real danger:
if row['issue_date'] == np.nan:  # NEVER True, even when it IS
NaN                                                                                                 
...

# Correct way:

if pd.isna(row['issue_date']):   # ✓
...

This is exactly why your validators use the two-guard pattern — if not x + if pd.isna(x).
The == NaN check would silently fail every time.
                                                                                                                                                                     
---
NaN > 5: False — comparisons with NaN are always False

Any comparison with NaN returns False — greater than, less than, equal to — all False. NaN is incomparable.

Real danger:    
report.query("validity_days > 0")  # rows where validity_days is NaN are silently
excluded                                                                         
They don't error — they just quietly disappear from your results, which is harder to spot than a crash.
                                                                                                                                                                     
---                                                                                                                                                                
The big picture: NaN doesn't crash loudly — it silently corrupts results. That's what makes it dangerous.
The cell is showing you the three ways it does that so   
you know what to watch for.    
| Expression | Result | Why it's dangerous |
|-----------|--------|-------------------|
| 1 + NaN = NaN | NaN infects arithmetic | Any sum/mean/calc touching NaN becomes NaN |
| NaN == NaN → False | NaN is never equal to anything, even itself | You CAN'T filter with == NaN |
| NaN > 5 → False | All comparisons with NaN return False | Silent filter failures |

The principle: NaN handling must be explicit, never accidental.
Every time you write a filter, ask yourself: "what should happen to NaN rows?" Then write it.

| Intent                        | Filter pattern           |
|-------------------------------|--------------------------|
| "Below 80 OR unknown"         | (col < 80)               | col.isna() |
| "Definitely below 80"         | col.notna() & (col < 80) |
| "Treat unknown as 0"          | col.fillna(0) < 80       |
| "Treat unknown as worst case" | col.fillna(100) < 80     |

| Strategy              | When to use                           | Danger                                         |
|-----------------------|---------------------------------------|------------------------------------------------|
| Constant (UNKNOWN, 0) | Explicit "we don't know" marker       | Using 0 for amount changes sums/means!         |
| Mean/median           | Preserves statistical properties      | Creates fake data — bad for ML, audit, finance |
| ffill (forward)       | Time series where last value persists | Copies unrelated data across rows              |
| bfill (backward)      | Future known, past unknown            | Looks ahead — dangerous for real-time systems  |

Cell #17 shows 4 strategies for filling NaN values, each with a different use case. Let me walk through each one using
the demo data:

    currency  amount                                                                                                                                                 

0 USD
100.0                                                                                                                                                 
1 EUR NaN ← missing
amount                                                                                                                              
2 NaN 150.0 ← missing
currency                                                                                                                            
3 USD 200.0
4 EUR NaN ← missing
amount                                                                                                                              
5 NaN 250.0 ← missing currency
6 USD 180.0
                                                                                                                                                                     
---
Strategy 1 — Constant
fill:                                                                                                                                        
demo.fillna({'currency': 'UNKNOWN', 'amount': 0})
Replaces NaN with a fixed value you define — different value per column. currency NaN → 'UNKNOWN', amount NaN → 0.

Use when: you want a safe placeholder that's clearly "not real data." Good for display/export. Bad for math — 0 would
corrupt averages.
                                                                                                                                                                     
---                                                                                                                                                                
Strategy 2 — Mean
fill:                                                                                                                                            
demo_v2['amount'].fillna(demo_v2['amount']
.mean())                                                                                                                 
Calculates the mean of existing values ((100+150+200+250+180)/5 = 176) and uses that to fill. Notice currency is still
NaN — mean only works on numbers.

Use when: you're doing statistical analysis and need a neutral estimate. Bad for LC data — you'd never guess an amount
for a financial document.
                                                                                                                                                                     
---                                                                                                                                                                
Strategy 3 — Forward fill (
ffill):                                                                                                                                 
demo.ffill()    
Looks up to the previous valid value and copies it down. So row 1 (NaN amount) gets 100.0 from row 0, row 2 (NaN
currency) gets 'EUR' from row 1.

Use when: data is time-ordered and the previous value is still valid — like stock prices or sensor readings. Risky for
LC data — copying a previous transaction's  
currency makes no sense.
                                                                                                                                                                     
---                                                                                                                                                                
Strategy 4 — Backward fill (bfill):
demo.bfill()                                                                                                                                                       
Opposite — looks down to the next valid value and copies it up. Row 1 (NaN amount) gets 150.0 from row 2.

Use when: same as ffill but the next value is more relevant than the previous. Also risky for LC data for the same
reason.
                                                                                                                                                                     
---                                                                                                                                                                
For your LC pipeline — none of these are appropriate for most fields. Missing currency, amount, issue_date should stay
flagged as errors, not filled. The only case
where filling might make sense is something like additional_conditions → '' for display purposes.

Should I fill this NaN?
├── Is it legitimately absent? (additional_conditions) → NO, keep NaN
├── Is it structurally absent? (confirming bank when UNCONFIRMED) → NO, keep NaN  
├── Is it a data quality issue? (missing amount) → FLAG, don't fill
├── Is it for presentation only? (dashboard display) → Fill with "—" or "N/A"
├── Is it for ML modeling? → Impute carefully, add is_missing flag column
└── Is it time series? → ffill/bfill if business logic allows

Is it for presentation only? → Fill with "—" or "N/A"

This is purely cosmetic. When you're showing data in a dashboard or report to a human, NaN looks ugly and confusing.
Replacing it with "—" or "N/A" is honest — it
clearly signals "no value" without pretending the data exists.

Important: do this only at display time, not in your working DataFrame. Keep NaN in storage, convert to "—" just before
rendering.
                  
---                                                                                                                                                                
Is it for ML modeling? → Impute carefully, add is_missing flag column

ML algorithms can't handle NaN at all — most will crash. So you have to fill. But the trick is: also add a new column
that remembers the NaN was there.

report['port_missing'] = report['port_of_loading'].isna().astype(int)  # 1 = was missing
report['port_of_loading'] = report['port_of_loading'].fillna('UNKNOWN')

Why? Because the fact that a value was missing is itself useful information for the model. Without the flag column, you
lose that signal forever.
                  
---                                                                                                                                                                
Is it time series? → ffill/bfill if business logic allows

This is the only case where forward/backward fill is genuinely appropriate. Example: a temperature sensor that missed a
reading
— it's reasonable to assume the
temperature was close to the previous reading.

The key phrase is "if business logic allows" — meaning the previous/next value is actually a valid substitute in your
domain.
For LC data it almost never is, which
is why you noted it's risky.
                                                                                                                                                                     
---             
The big picture: the whole flowchart forces you to ask why before acting. Same NaN, completely different responses
depending on context.
That's professional data
thinking.

| Parameter               | Meaning                                        |
|-------------------------|------------------------------------------------|
| subset=['col1', 'col2'] | Only check these columns                       |
| how='any' (default)     | Drop if ANY value in row is null               |
| how='all'               | Drop only if ALL values in row are null        |
| thresh=N                | Keep rows/cols with at least N non-null values |
| axis=0 (default)        | Drop ROWS                                      |
| axis=1                  | Drop COLUMNS                                   |

| Strategy                 | Result   | Meaning                                                    |
|--------------------------|----------|------------------------------------------------------------|
| Drop if critical missing | 200 rows | Nothing missing in critical fields ✅                       |
| Drop if all null         | 200 rows | No entirely-empty rows exist                               |
| Keep columns ≥50% filled | 48 of 51 | 3 columns dropped (likely the ones with 175/148/148 nulls) | 

The most commonly used thresholds in practice are:

thresh=0.5 (50%) — the most common

- "If more than half the column is missing, it's not useful"
- This is the safe default most data engineers use

thresh=0.8 (80%) — stricter, more conservative

- "Keep the column unless it's really mostly empty"
- Used when data is naturally sparse and you want to be careful

thresh=0.2 (20%) — aggressive cleanup

- "Drop if more than 80% is missing"
- Used for ML where even small amounts of missing data cause problems

  ---                                                                                                                                                                
The rule of thumb:

- Analysis/reporting → 0.5 is fine
- ML modeling → 0.8 or higher (keep more data)
- Quick exploration → 0.5 as a starting point, then adjust  
  Cell #20 shows the 3 smarter ways to use .dropna() compared to the blind version in cell #19.

  ---                                                                                                                                                                
subset= — drop only if critical columns are
missing:                                                                                                               
report.dropna(
subset=['transaction_id', 'amount', 'currency'])                                                                                                     
Result: 200 rows — all kept! Because every row has these three fields. This is the version you'd actually use in your
pipeline
— only drop a transaction if the    
fields you absolutely can't work without are missing.
                                                                                                                                                                     
---
how='all' — drop only if the entire row is
empty:                                                                                                                  
report.dropna(
how='all')                                                                                                                                           
Result: 200 rows — all kept! No row is completely empty. This is a safety check more than anything
— catches ghost rows that somehow have no data at all.
                                                                                                                                                                     
---                                                                                                                                                                
thresh= + axis=1 — drop mostly empty COLUMNS:
report.dropna(thresh=len(report) * 0.5,
axis=1)                                                                                                                    
This one is different — axis=1 means it operates on columns, not rows.

thresh=len(report) * 0.5 = thresh=100 — keep a column only if it has at least 100 non-null values (50% of 200 rows).

Result: 48 columns (was 51). Three columns got dropped — most likely additional_conditions (175 NaN = only 12.5% filled)
and the two confirming bank columns (148  
NaN = only 26% filled).
                                                                                                                                                                     
---             
Why would you use thresh on columns?

In real data science work — imagine you receive a dataset with 200 columns and 80 of them are 90% empty.
Those columns are useless for analysis or ML.
dropna(thresh=..., axis=1) cleans them out automatically instead of manually listing them.

For your LC pipeline specifically — you wouldn't use it, because every column was deliberately designed and named.
But in exploratory data analysis on unknown     
datasets, it's very handy.

| Severity                   | Columns                                   | Interpretation                                               |
|----------------------------|-------------------------------------------|--------------------------------------------------------------|
| 🟢 Expected (70%+ missing) | additional_conditions, confirming_bank_*  | Normal — most LCs don't have these                           |
| 🟡 Design decision (36%)   | error_codes, error_messages               | Clean transactions have none — expected                      |
| 🟠 Investigate (11.5%)     | port_of_loading                           | Could be legit for air freight OR data issue                 |
| 🔴 Problem (1-2%)          | issue_date, issuing_bank_swift, lc_number | Should NEVER be missing — your validators already flag these |

And notice validity_days shows 4 missing — that's derived from issue_date and expiry_date, so if either parent is
missing,
the computed column is NaN too. NaN propagation at work.
Also interesting: validity_days is float64 even though days are integers. Why? Because pandas can't have NaN in integer
columns
— the moment you introduce a NaN, pandas upgrades to float. That's called the integer-NaN trap,
and it's why pandas created nullable integer types (Int64 with capital I) in recent versions.

| Concept                            | What you learned                                |
|------------------------------------|-------------------------------------------------|
| Types of missingness               | Legitimate, structural, by-design, data quality |
| NaN == NaN is False                | Never filter with == NaN, use .isna()/.notna()  |
| NaN > 5 is False                   | Silent filter failures — Bob disappeared        |
| NaN propagation                    | 1 + NaN = NaN, spreads through math             |
| .fillna(constant)                  | Explicit replacement, may distort statistics    |
| .fillna(mean/median)               | Preserves stats, invents data                   |
| .ffill() / .bfill()                | Time-series patterns, dangerous for finance     |
| Add is_missing flag before filling | Never destroy information silently              |
| .dropna() default drops 98%        | Always use subset= or how='all'                 |
| Integer-NaN trap                   | Pandas upgrades int → float when NaN appears    |
| Missing data report                | Quantify before deciding strategy               |

Key principle, banking edition:

In finance, a missing value is a data quality flag, not a number to invent. Never silently fill amounts, LEIs, dates, or
account numbers.
Always preserve the signal.

| Topic                       | Finance angle I'll weave in                                                              |
|-----------------------------|------------------------------------------------------------------------------------------|
| Performance & vectorization | Why it matters for real-time fraud detection, overnight batch jobs, regulatory reporting |
| Window functions & time     | Rolling exposure, VaR calculations, settlement windows                                   |
| Pivots & reshaping          | How these become regulatory reports (COREP, FINREP, Basel III submissions)               |
| Capstone                    | Building a production-style end-to-end audit pipeline                                    | 

## ++++++++++++++++++++++++++ Day 63 — Performance & Vectorization +++++++++++++++++++++++++++++++++

| Scenario                         | Volume               | Time constraint                             |
|----------------------------------|----------------------|---------------------------------------------|
| End-of-day trade reconciliation  | 500K-2M transactions | Must finish before market opens (4-6 hours) |
| Real-time fraud detection        | Thousands/second     | Must decide in <100ms per transaction       |
| Regulatory reporting (Basel III) | Entire portfolio     | Monthly deadline, massive aggregations      |
| AML screening                    | Every transaction    | Can't delay customer payments               |
| LC validation (your pipeline!)   | Batch of LCs         | Currently 16s for 200 — what about 200,000? |

# ================ Cell # 22 - 26 =======================================

# Method 1: Python for loop (the worst)

big_df.iloc[i] is the killer. Every single iteration it has to:

1. Go find row i in the DataFrame
2. Extract just that row as a Series
3. Then look up 'amount' inside that Series

You're doing that 100,000 times — 100,000 individual row lookups.
Pandas was not designed to be used one row at a time like this.
It's essentially fighting against the library instead of using it.

# Method 2: .apply() with lambda

Same goal, cleaner approach.

result2 = big_df['amount'].apply(lambda x: 'high' if x > 50000 else 'low')

Instead of looping manually with for i in range(...), you hand the whole column to .apply() and give it a function to
run on each value.

The lambda is just a mini one-line
function:                                                                                                                       
lambda x: 'high' if x > 50000 else 'low'

# same as writing:

def label(
x):                                                                                                                                                      
if x > 50000:
return '
high'                                                                                                                                              
else:                                                                                                                                                          
return 'low'

.apply() calls that function once per value in the column — so x is just the amount number each time (e.g. 73241.5,
12034.8, etc.).

Why it's faster than Method 1:

The for loop was doing big_df.iloc[i] — fetching an entire row as a Series each iteration.
Here you already isolated the column first (big_df['amount']), so       
.apply() is iterating over raw values, not rows. Less overhead per step.

But it's still not the fastest — .apply() is still a Python-level loop under the hood. It's just a tidier one.
The real speed jump comes in Method 3/4 where pandas
avoids the Python loop entirely.

# Method 3: np.where (vectorized)

result3 = np.where(big_df['amount'] > 50000, 'high', 'low')

np.where takes 3
arguments:                                                                                                                                        
np.where(condition, value_if_true, value_if_false)

So here:

- big_df['amount'] > 50000 — evaluates the entire column at once, producing an array of True/False for all 100,000 rows
  simultaneously
- 'high' — use this where True
- 'low' — use this where False

Why it's so much faster:

Methods 1 and 2 were Python loops — even if hidden inside .apply(), Python was still touching each value one at a time.

np.where runs in C under the hood. NumPy operates on the entire array in one shot, no Python loop at all.
This is what "vectorized" means — the operation is       
applied to the whole array at once at the C level, not row by row at the Python level.

A rough analogy: the for loop is like checking 100,000 boxes one by one yourself.
np.where is like hiring a machine that scans all 100,000 at once.

# - Method 4: Boolean indexing (vectorized)

result4 = pd.Series('low',
index=big_df.index)                                                                                                                     
Creates a Series of 100,000 rows, every value set to 'low' by default.
index=big_df.index just makes sure it has the same row labels (0 to 99,999) as the original DataFrame.

result4[big_df['amount'] > 50000] = '
high'                                                                                                                         
This is the vectorized part. Two things happen here:

1. big_df['amount'] > 50000 — evaluates the whole column at once, gives back a boolean array
   like [False, True, False, True, True, ...]
2. result4[...] — uses that boolean array as a mask to select only the True positions and overwrites them with 'high'

So instead of asking "what should this row be?", it asks "which rows need to change?" and updates them all at once.

The key difference from Method 3:

np.where builds the result from scratch in one call. Boolean indexing starts with a default ('low') and then patches the
exceptions ('high').

Both are vectorized and fast. Boolean indexing is more useful when you have more than 2 outcomes — you can apply
multiple masks in sequence instead of nesting     
conditions.

| Method           | Time    | vs fastest    | Speed    |
|------------------|---------|---------------|----------|
| For loop         | 1.579s  | 2,256x slower | 🐌🐌🐌🐌 |
| .apply()         | 0.012s  | 17x slower    | 🐌       |
| Boolean indexing | 0.002s  | 2.6x slower   | 🐇       |
| np.where         | 0.0007s | 1x (baseline) | 🚀       |

| Method           | What happens under the hood                                                        |
|------------------|------------------------------------------------------------------------------------|
| For loop         | Python interpreter processes each row individually. Each .iloc[] call is overhead. |
| .apply()         | Still a Python loop, but pandas handles the iteration — less overhead per row      |
| Boolean indexing | One C-level operation creates the mask, one assigns values                         |
| np.where()       | Pure C/Fortran — entire array processed in one pass, no Python involved            |

Think of it like trade finance document processing:

For loop = one clerk reads one document, stamps it, moves to the next
Apply = same clerk but with a faster desk
Vectorized = a machine that stamps the entire stack in one motion

# SLOW: apply for string building

slow = big_df.apply(lambda row: f"{row['currency']}_{row['amount']:.0f}", axis=1)

The key difference from Method 2 is axis=1.

- axis=0 (default) — apply the function to each column
- axis=1 — apply the function to each row

So here, row is an entire row as a Series — it has both currency and amount.
That's why you can do row['currency'] and row['amount'] inside the lambda.

The lambda builds a string like "USD_73241" for each
row:                                                                                                          
f"{row['currency']}_{row['amount']:.0f}"

# 'USD' + '_' + '73241' →  'USD_73241'

# :.0f means format the float with 0 decimal places

Why it's slow:

axis=1 is the most expensive form of .apply(). Instead of iterating over a simple column of numbers,
pandas has to pack each row into a full Series object (with   
index, dtype, etc.) and pass that to your function — 100,000 times. Much more overhead than column-wise .apply().


# - FAST: vectorized string operations 
fast = big_df['currency'] + '_' + big_df['amount'].astype(int).astype(str)                                                                                         

  This does the same thing — builds "USD_73241" — but operates on entire columns at once instead of row by row.                                                      
   
  Breaking it down left to right:                                                                                                                                    
                                                                                                                                                                   
  big_df['amount'].astype(int)   # 73241.8  →  73241  (drop decimals)                                                                                                
                  .astype(str)   # 73241    →  '73241' (make it a string)                                                                                            
                                                                                                                                                                     
  Then:                                                                                                                                                              
  big_df['currency'] + '_' + big_df['amount'].astype(int).astype(str)                                                                                                
  # 'USD' column + '_' + '73241' column  →  'USD_73241' column       
                                                                                                                                                                     
  The + operator on two Series concatenates them element-wise across the whole column at once — no Python loop, no row packing.                                      
                                                                                                                                                                     
  Why it's faster:                                                                                                                                                   
                                                                                                                                                                     
  The slow version created a full Series object for each of 100,000 rows. Here pandas just operates on 3 columns as arrays — currency, separator, amount — and       
  combines them in one vectorized pass.
                                                                                                                                                                     
  You'll likely see something like 10-50x faster than the axis=1 version in the timing output.    

"I need to transform data"
│
├── Single column, simple logic?
│   ├── Lookup/mapping → .map(dict)              🚀
│   ├── if/else → np.where()                     🚀
│   └── if/elif/else → np.select()               🚀
│
├── Multiple columns, simple logic?
│   ├── Math between columns → direct operations  🚀
│   │   df['total'] = df['price'] * df['qty']
│   ├── String building → Series + operator        🚀
│   │   df['a'] + '_' + df['b']
│   └── Conditional → np.where / np.select         🚀
│
├── Aggregation?
│   └── Always groupby, NEVER manual loops          🚀
│
└── Truly complex logic? (API calls, nested ifs, external lookups)
    └── .apply(axis=1) — LAST resort               🐌

The rule: if you're about to write .apply(), pause and ask "can I express this with np.where, np.select,
or column math?" 90% of the time, you can.


 This is the multi-condition version of the vectorization problem. np.where handles 2 outcomes (true/false), but here you have 4 — so you need np.select.
                                                                                                                                                                     
  The slow way — .apply(classify_risk):                                                                                                                              
                                                                                                                                                                     
  Calls classify_risk(n) once per row, Python-level, 100,000 times. Same story as before.                                                                            
                                                                                                                                                                   
  ---                                                                                                                                                                
  The fast way — np.select:

  conditions = [
      big_df['error_count'] == 0,    # array of True/False for all 100k rows
      big_df['error_count'] <= 2,    # array of True/False for all 100k rows                                                                                         
      big_df['error_count'] <= 4,    # array of True/False for all 100k rows
  ]                                                                                                                                                                  
  choices = ['no_risk', 'low_risk', 'medium_risk']
                                                                                                                                                                     
  r2 = np.select(conditions, choices, default='high_risk')                                                                                                           
   
  np.select pairs each condition with its choice in order — first match wins:                                                                                        
  - == 0 → 'no_risk'
  - <= 2 → 'low_risk'                                                                                                                                                
  - <= 4 → 'medium_risk'
  - nothing matched → default='high_risk'
                                                                                                                                                                     
  All three condition arrays are evaluated at once at the C level, then np.select picks the right label per row — no Python loop.
                                                                                                                                                                     
  The pattern to remember:                                                                                                                                           
  - 2 outcomes → np.where                                                                                                                                            
  - 3+ outcomes → np.select                                                                                                                                          
                           
  This is directly applicable to your LC pipeline — classify_risk based on error_count is exactly the kind of thing
  you'd want when generating the validation report.
  
Part 5: When .apply() IS the right choice
I've been beating up on .apply(), but there are legitimate cases where it's the only option:

| Scenario                 | Why apply is needed                  | Example |
|--------------------------|--------------------------------------|---------|
| API calls per row        | Can't vectorize HTTP requests        | Your GLEIF LEI validation |
| Complex nested logic     | Too many branches for np.select      | 10+ conditions with dependencies |
| External library per row | Library expects single values        | Address parsing, NLP |
| Debugging/prototyping    | Get it working first, optimize later | Exploratory analysis |


apply() is slow, but sometimes you have no choice. Here's when and why:

  ---                                                                                                                                                                
  API calls per row
  df['lei'].apply(lambda lei: call_gleif_api(lei))                                                                                                                   
  You literally cannot vectorize this — you need to send one HTTP request per LEI and wait for a response. There's no C-level trick that can batch that for you. This
   is exactly what you'll face when you add GLEIF validation to your LeiValidator.                                                                                   
                                                                                                                                                                     
  ---
  Complex nested logic                                                                                                                                               
  # np.select breaks down when conditions depend on each other                                                                                                     
  if amount > 50000 and currency == 'USD':                    
      if issuing_country == beneficiary_country:                                                                                                                     
          return 'flag_A'                                                                                                                                            
      else:                                                                                                                                                          
          return 'flag_B'                                                                                                                                            
  np.select works well for simple independent conditions. Once your branches start depending on each other or you have 10+ cases, the conditions list becomes      
  unreadable. A plain function with if/elif is clearer — take the readability win.                                                                                   
                                                                                                                                                                     
  ---
  External library per row                                                                                                                                           
  df['address'].apply(lambda addr: some_nlp_library.parse(addr))                                                                                                   
  Third-party libraries expect a single value, not a whole column. You can't pass 100,000 addresses to a function designed to handle one. .apply() is the bridge.
                                                                                                                                                                     
  ---                                                                                                                                                                
  Debugging/prototyping                                                                                                                                              
  .apply() with a named function is easy to test in isolation:                                                                                                       
  classify_risk(3)  # → 'medium_risk'  ✓                                                                                                                           
  Get the logic right first, then optimize to np.select if speed matters. Don't prematurely optimize code that might change.                                         
                                                                                                                                                                     
  ---                                                                                                                                                                
  The rule of thumb: default to vectorized. Reach for .apply() only when the operation genuinely can't be expressed as array math — like your upcoming GLEIF API     
  calls.                                                            

## The principle for banking/fintech:

| Layer                          | Approach            | Why |
|--------------------------------|---------------------|-----|
| Data cleaning & transformation | Vectorized always   | Runs on millions of rows nightly |
| Business rule validation       | .apply() is fine    | Complex logic, correctness > speed |
| Reporting & aggregation        | GroupBy + pivot     | Built-in optimization |
| Real-time scoring              | Vectorized critical | <100ms per decision |

In your pipeline: the DataCleaner (unicode, whitespace) should be vectorized 
(and it already is — .str.replace() on whole columns). 
The ValidationService uses a loop because correctness matters more than speed there.
The ReportService uses vectorized .apply() with lambdas because it's simple transforms.
You already made the right calls.

Day 63 Summary

| Concept                 | What you learned |
|-------------------------|-----------------|
| Speed hierarchy         | for loop < .apply() < boolean indexing < np.where |
| For loops on DataFrames | 2000x slower than vectorized — never do this |
| .apply()                | 10-20x slower than vectorized — last resort |
| np.where / np.select    | Pure C-level operations, fastest option |
| String concatenation    | Series + operator is vectorized, f-strings in apply are not |
| GroupBy vs manual loops | GroupBy hashes once, manual loop filters N times |
| When apply IS correct   | API calls, complex validation, prototyping |
| Banking context         | Batch jobs must finish overnight, real-time needs <100ms |

The golden rule:

Write it with .apply() first to get it correct. Then ask: "can I vectorize this?"
If yes, do it. If not, the correct .apply() is better than the broken vectorized attempt.

## ==================  Day 64 is Window Functions & Time ===============================================

| Use case                        | Window function       | Why banks care |
|---------------------------------|-----------------------|---------------|
| 30-day rolling average exposure | rolling(30).mean()    | Risk management — smooth out daily volatility |
| Cumulative transaction volume   | cumsum()              | AML monitoring — "has this customer moved $1M this month?" |
| Running error count             | cumsum()              | Quality tracking — "are we getting worse over time?" |
| Rank within group               | rank()                | Compliance — "top 10 riskiest counterparties" |
| Change from previous value      | diff() / pct_change() | Market surveillance — sudden spikes trigger alerts |


The key idea: window functions compute a value based on a window of surrounding rows, not just the current row. 
They return a result for EVERY row — same size as the input, like transform().

rolling(30).mean() — look at a 30-day sliding window and average it. Instead of a single day's value (noisy), you see the trend. Like a moving average on a stock  
  chart.                                                                                                                                                             
                                                                                                                                                                   
  cumsum() — running total. Each row = sum of everything up to that point. Row 1: $10k, Row 2: $10k+$25k=$35k, Row 3: $35k+$8k=$43k... Banks use this to catch money 
  laundering — if the cumulative total crosses $1M, flag it.                                                                                                         
   
  rank() — assigns a rank within a group. Who has the most errors? Who processed the most volume? Rank 1 = worst/best, depending on direction.                       
                  
  ---                                                                                                                                                                
  diff() / pct_change() — the last one:
                                                                                                                                                                     
  # diff() — absolute change from previous row
  amounts = [10000, 11000, 10500, 95000, 10200]                                                                                                                      
  diff   = [  NaN,  1000,  -500, 84500, -84800]                                                                                                                      
                                                                                                                                                                     
  # pct_change() — percentage change from previous row                                                                                                               
  pct    = [  NaN,  10%,  -4.5%, 804%,  -89%]                                                                                                                        
                                                                                                                                                                     
  diff() asks: how much did it change?                                                                                                                               
  pct_change() asks: by what percentage did it change?                                                                                                               
                                                                                                                                                                     
  Why banks care — sudden spikes:                                                                                                                                    
   
  A transaction of $95,000 might look normal in isolation. But if the previous 10 transactions were all ~$10,000, the pct_change() of +804% screams anomaly. That's  
  exactly the kind of signal fraud detection systems look for — not the absolute value, but the sudden jump relative to history.
                                                                                                                                                                     
  In your LC pipeline context: if a counterparty's transaction amounts suddenly spike 800% compared to their previous activity, that's a red flag worth flagging even
   if the amount itself isn't unusual in the broader dataset.

# ================ Cell # 27 -  =======================================     

In banking, this is how AML (Anti-Money Laundering) monitoring works:
"This customer has cumulatively transferred $847,000 this month — approaching the $1M 
threshold that triggers enhanced due diligence."

* rolling(window=5) 
In banking terms: this is exactly how a rolling risk metric works. 
A 30-day rolling average of transaction volumes smooths out daily noise and shows you the trend. 
A sudden spike in the rolling average triggers an alert.
____In real banking, the windows are much larger and tied to regulatory or business periods:

| Use case                       | Typical window    | Why that number |
|--------------------------------|-------------------|-----------------|
| AML transaction monitoring     | 30 days           | Regulatory threshold — "cumulative activity in 30 days" |
| Market risk (VaR)              | 250 trading days  | 1 year of trading days — Basel III requirement |
| Credit card fraud detection    | 24 hours / 7 days | Recent behavior vs normal pattern |
| Liquidity coverage ratio (LCR) | 30 days           | Basel III — "can you survive 30 days of stress?" |
| Moving average for FX rates    | 50 / 200 days     | Industry standard — 50-day vs 200-day crossover signals |
| LC processing quality          | 30 / 90 days      | Internal KPI — "are we getting better or worse?" |
| Customer risk scoring          | 90 days           | Quarterly review cycle |

# Real-world examples (if you had daily data):
daily_volume.rolling(window=30).sum()     # 30-day cumulative volume for AML
daily_returns.rolling(window=250).std()   # 1-year volatility for VaR
fx_rate.rolling(window=200).mean()        # 200-day moving average for trend

The window number always comes from a business or regulatory requirement, never from a programmer's guess.
Same principle as your pipeline — no magic numbers, everything config-driven. 
In production, you'd put these in settings.py:

AML_ROLLING_WINDOW_DAYS = 30
VAR_LOOKBACK_DAYS = 250
QUALITY_REVIEW_WINDOW = 90

cell # 29
| Row  | Values in window   | Calculation   | Result |
|------|--------------------|---------------|--------|
| 0    | [1]                | 1/1           | 1.00 |
| 1    | [1, 2]             | 3/2           | 1.50 |
| 2    | [1, 2, 5]          | 8/3           | 2.67 |
| 3    | [1, 2, 5, 1]       | 9/4           | 2.25 |
| 4    | [1, 2, 5, 1, 1]    | 10/5          | 2.00 ← full window starts here |

min_periods=1 means "start computing as soon as you have at least 1 value."
Without it, pandas waits for the full window. In banking, you'd choose based on context 
— if you're computing a 30-day average for a new customer account, min_periods=1 makes sense 
because you don't want to wait 30 days before showing any metric.



 * USE min_periods=1 — partial data is still useful
                                                                                                                                                                     
  New customer onboarding                                                                                                                                          
  # Credit score based on transaction history                                                                                                                        
  # Day 1: only 1 transaction — still show something rather than nothing                                                                                             
  customer['avg_daily_spend'].rolling(30, min_periods=1).mean()         
  The bank needs some number to display on the dashboard. An estimate from 3 days is better than a blank.                                                            
                                                                                                                                                                     
  Branch performance dashboard                                                                                                                                       
  # Branch opened last week — show what you have                                                                                                                     
  branch['daily_transactions'].rolling(7, min_periods=1).mean()                                                                                                      
  Management wants to see the new branch performing. Showing NaN for the first 6 days is useless.                                                                    
                                                                                                                                                                     
  Fraud alert warm-up                                                                                                                                                
  # New card issued today — start building a spend baseline immediately                                                                                              
  card['transaction_amount'].rolling(14, min_periods=1).mean()                                                                                                       
  You'd rather flag suspicious activity on day 2 using a 2-day baseline than wait 14 days with no protection.                                                        
                  
  ---                                                                                                                                                                
  USE strict window (no min_periods) — partial data is misleading
                                                                                                                                                                     
  AML 30-day threshold monitoring
  # "Has this account moved > $10,000 this month?"                                                                                                                   
  # A 3-day average extrapolated to 30 days would trigger false alerts
  account['daily_transfers'].rolling(30).mean()                                                                                                                      
  If you calculate with only 5 days of data, the average might look huge. You need the full 30 days before making a compliance decision.                             
                                                                                                                                                                     
  Risk model for loan approval                                                                                                                                       
  # Requires 90 days of history to be statistically valid                                                                                                            
  applicant['monthly_income'].rolling(90).mean()                                                                                                                     
  A loan decision based on 10 days of data is dangerous. NaN = "not enough history, reject or defer."                                                                
                                                                                                                                                                     
  Regulatory capital calculations                                                                                                                                    
  # Basel III requires exactly N days of data                                                                                                                        
  # A partial window would be non-compliant                                                                                                                          
  exposure['daily_value'].rolling(250).std()  # 1 trading year                                                                                                       
  Regulators require a specific lookback period. Partial windows would fail an audit.                                                                                
                                                                                                                                                                     
  Volatility-based margin calls                                                                                                                                      
  # Margin call triggered if 20-day volatility exceeds threshold                                                                                                     
  # Partial window understates true volatility — dangerous                                                                                                           
  position['daily_pnl'].rolling(20).std()                                                                                                                            
  Calling margin too early (or not at all) because of a 3-day "volatility" estimate could cause real losses. 
  
# cell 30

In banking, pct_change() is how you detect anomalies:
"This customer's daily transfer volume just jumped 500% — flag for review."

 Banking example:                                                                                                                                                   
                                                                                                                                                                     
  For fraud detection, pct_change() is more useful. A customer who normally spends $200/day suddenly spending $1,000
  is a +400% spike — far more suspicious than a customer who normally
  spends $10,000 jumping to $10,800 (+8%), even though the absolute dollar increase might be similar.
                                                                                                                          
flagged_sorted['error_diff'] = flagged_sorted['error_count'].diff()
                                                                                                                                                                     
  diff() subtracts the previous row's value from the current one:                                                                                                    
                                                                                                                                                                     
  error_count:  1, 2, 5, 1, 1                                                                                                                                        
  error_diff:   NaN, +1, +3, -4, 0                                                                                                                                   
  - Row 1: 2 - 1 = +1 (one more error than previous)
  - Row 2: 5 - 2 = +3 (spike!)                                                                                                                                       
  - Row 3: 1 - 5 = -4 (dropped back down)
  - First row is always NaN — nothing to subtract from.                                                                                                              
                                                                                                                                                                     
  ---                                                                                                                                                                
  flagged_sorted['error_pct_change'] = flagged_sorted['error_count'].pct_change().round(2)                                                                           
                                                                                                                                                                     
  pct_change() asks the same question but as a percentage:                                                                                                           
                                                                                                                                                                     
  error_count:     1,   2,    5,    1,    1                                                                                                                          
  error_pct:     NaN, 1.0, 1.50, -0.80, 0.0                                                                                                                          
  - Row 1: (2-1)/1 = +100% (doubled)                                                                                                                                 
  - Row 2: (5-2)/2 = +150% (big spike)                                                                                                                               
  - Row 3: (1-5)/5 = -80% (dropped)                                                                                                                                  
                                                                                                                                                                     
  ---             
  When to use which:                                                                                                                                                 
                                                                                                                                                                     
  - diff() — when the absolute number matters. Going from 1 error to 4 errors (+3) is the same signal whether the baseline was 1 or 100.
  - pct_change() — when relative change matters. A jump from 1 → 5 (+400%) is more alarming than 100 → 104 (+4%),
  - even though both are +4 in absolute terms.  

| Row | error_count | diff | pct_change | What happened |
|-----|-------------|------|-----------|---------------|
| 1 | 2 | +1 | +1.0 (100%) | Doubled from previous |
| 2 | 5 | +3 | +1.5 (150%) | Spiked — 150% increase |
| 3 | 1 | -4 | -0.8 (-80%) | Dropped back to normal |
| 4-8 | 1 | 0 | 0.0 | Flat — stable |
| 9 | 2 | +1 | +1.0 (100%) | Another jump |

Row 2 → 3 shows a -4 diff and -80% change. In fraud detection, that kind of spike-then-drop pattern is exactly
what triggers alerts: "Transaction volume jumped 150% then immediately dropped — possible structuring."


## 31
  Rolling vs Expanding — the core difference:                                                                                                                        
   
  - .rolling(5) — always looks at the last 5 rows only (fixed window)                                                                                                
  - .expanding() — looks at everything from row 0 up to now (grows over time)

 flagged_sorted['expanding_avg'] = (                                                                                                                                
      flagged_sorted['error_count']                                                                                                                                  
      .expanding()                                                                                                                                                   
      .mean()                                                                                                                                                        
      .round(2)   
  )

  Rolling vs Expanding — the core difference:                                                                                                                        
   
  - .rolling(5) — always looks at the last 5 rows only (fixed window)                                                                                                
  - .expanding() — looks at everything from row 0 up to now (grows over time)
                                                                                                                                                                     
  Looking at the output:                                                                                                                                             
  Row 0:  window = [1]              → 1/1    = 1.00                                                                                                                  
  Row 1:  window = [1, 2]           → 3/2    = 1.50                                                                                                                  
  Row 2:  window = [1, 2, 5]        → 8/3    = 2.67
  Row 3:  window = [1, 2, 5, 1]     → 9/4    = 2.25                                                                                                                  
  Row 4:  window = [1, 2, 5, 1, 1]  → 10/5   = 2.00
  Row 5:  window = [1,2,5,1,1,1]    → 11/6   = 1.83                                                                                                                  
  ...keeps growing                                 
                                                                                                                                                                     
  No NaNs — because even 1 value is enough for an expanding window.                                                                                                  
                                                                                                                                                                     
  Also notice the difference in the output table:                                                                                                                    
                                                                                                                                                                     
  - rolling_avg_errors at Row 7 = 1.0 (only sees last 5 rows, all 1s)                                                                                                
  - expanding_avg at Row 7 = 1.62 (remembers the spike of 5 back at Row 2)
                                                                                                                                                                     
  Rolling forgets old data. Expanding never forgets.                                                                                                                 
                                                                                                                                                                     
  ---                                                                                                                                                                
  Banking example:
                  
  - Rolling → "What's this customer's average spend over the last 30 days?" (recent behavior for fraud)
  - Expanding → "What's this customer's lifetime average spend?" (full history for credit scoring or KYC profiling)                                                  
                                                                                                                                                                     
  A new customer's expanding average is very sensitive to early transactions — one big LC in month 1 will pull the average up for a long time. That's exactly why    
  credit history length matters in risk models. 
  
| Tool        | Window size          | Banking analogy |
|-------------|----------------------|-----------------|
| rolling(5)  | Always last 5        | "Last 5 transactions average" |
| expanding() | Grows: 1, 2, 3, 4... | "Lifetime average up to now" |

| | Rolling                         | Expanding |
|---|---------------------------------|-----------|
| Sensitivity | High — reacts to recent changes | Low — smooths over time |
| Memory | Short — forgets old data        | Infinite — remembers everything |
| Banking use | "Recent trend" — fraud alerts   | "Lifetime average" — customer scoring |

In banking terms: your credit card company uses rolling to detect "this week looks weird compared to last week" 
and expanding to know "this customer averages $2,000/month since they opened the account."

# cell 32
  Banking example:

This is exactly how banks track exposure per counterparty or per currency. "How much total USD exposure has accumulated so
far?" vs "How much GBP?" — you need separate running totals, not one mixed number. A compliance officer watching EUR exposure
limits doesn't care about JPY transactions inflating the count.

======Day 64 Summary======

| Tool      | What it does  | Banking use case  |
| .cumsum() | Running total | AML thresholds, cumulative exposure |
| .rolling(window) | Fixed-size moving window | 30-day avg volume, trend detection |
| min_periods= | Start computing before window is full | New account monitoring |
| .expanding() | Growing window from start | Lifetime average, customer scoring |
| .diff() | Change from previous row | Spike detection |
| .pct_change() | Percentage change from previous | Anomaly alerts ("500% jump!") |
| groupby + cumsum | Running total per group | Per-currency/per-customer tracking |
| groupby + rolling | Moving average per group | Per-counterparty risk trends |

| Window type  | Remembers             | Best for |
|--------------|-----------------------|----------|
| rolling(N)   | Last N rows only      | Recent trends, anomaly detection |
| expanding()  | Everything from start | Lifetime metrics, stable averages |
| cumsum()     | Running total         | Thresholds, cumulative monitoring |