● A few alternatives:                                                                                                           
                                                                                                                                
  .str.find() — returns index of match, -1 if not found:                                                                        
  lei004_txns = flagged[flagged['error_codes'].str.find('LEI004') != -1]                                                        
                                                                                                                                
  .apply() with in:                                                                                                             
  lei004_txns = flagged[flagged['error_codes'].apply(lambda x: 'LEI004' in x)]                                                  
                                                                                                                                
  .loc[] — same logic, just explicit about label-based selection:                                                               
  lei004_txns = flagged.loc[flagged['error_codes'].str.contains('LEI004')]                                                      
                                                                                                                                
  .query() — but awkward for substring checks, not recommended here.                                                            
                                                                                                                                
  ---                                                                                                                           
  .str.contains() is the most idiomatic pandas way for this. The main reason to use an alternative:                             
                                                                                                                                
  - Use .apply(lambda x: 'LEI004' in x) if error_codes might contain lists or complex objects (plain Python in is more flexible
  than the string method).                                                                                                      
  - Use .str.find() if you also need to know where in the string the match is.
                                                                                                                                
  For your case, .str.contains() is the right call.                                                                             

```
| Parameter | What it does |
|-----------|-------------|
| na=False | NaN → treated as False (doesn't contain) |
| na=True | NaN → treated as True (assume it contains) |
| default | NaN → stays NaN (can break boolean filtering) |

                      Expression                       │      Inner [] contains      │     Result      │                    
  ├────────────────────────────────────────────────────────┼─────────────────────────────┼─────────────────┤                    
  │ flagged[flagged['error_codes'].str.contains('LEI004')] │ boolean Series (True/False) │ filters rows    │
  ├────────────────────────────────────────────────────────┼─────────────────────────────┼─────────────────┤                    
  │ german_banks[['col1', 'col2']]                         │ list of strings             │ selects columns

  Same outer [], but what you put inside determines whether pandas filters rows or selects columns.    


| Method                | What it checks             | Regex? |
|-------                |---------------             |--------|
| .str.contains('text') | Pattern anywhere in string | Yes (by default) |
| .str.startswith('text') | Matches beginning only   | No (literal only) |
| .str.endswith('text') | Matches end only           | No (literal only) |

Key detail: .str.contains() supports regex by default, while startswith/endswith are always literal. 
That's why we used .str.contains(r'[A-Za-z]$') instead of endswith — we needed a regex pattern, not a specific letter.

The full pattern is r'^.{4}([A-Z]{2})'. Breaking it down:                                                                     
                                                                                                                              
  r'^  .{4}  ([A-Z]{2})'                                                                                                        
       ^       ^                                                                                                                
       |       |                                                                                                                
       |       capture group (explained below)                                                                                  
       |                                                                                                                        
       any character, exactly 4 times
                                                                                                                                
  The . (dot) — in regex, dot means "any single character". So .{4} means "any 4 characters". In a SWIFT code like DEUTDEDB,    
  that skips the first 4 letters (the bank code DEUT).                                                                          
                                                                                                                                
  The {4} — a quantifier, means "repeat the previous thing exactly 4 times".                                                    
   
  The () parentheses — a capture group. .extract() needs a group to know what to pull out. Whatever is inside () is what gets   
  returned.       
                                                                                                                                
  ---             
  So for DEUTDEDB:
  ^ D E U T  D  E  D B                                                                                                          
    └──.{4}─┘ └[A-Z]{2}┘
     skip 4    capture these 2 → "DE" (country code)                                                                            
                                                                                                                                
  The parentheses tell pandas: "I don't care about the first 4 chars — give me just the 2 inside the group."                    
                                                                                                                                
❯ so assume we dont care[A-Z] so can we write (r'^[A-Z]{4}  as  r'^.{4} ?                                                       
                                                           
                                                                                                                                
● Yes, exactly right.                                                                                                         
                                                                                                                                
  r'^[A-Z]{4}([A-Z]{2})'   # match exactly 4 uppercase letters, then capture 2                                                  
  r'^.{4}([A-Z]{2})'       # match any 4 characters, then capture 2                                                             
                                                                                                                                
  Both skip the first 4 characters — the difference is strictness:                                                              
                                                                                                                                
  - [A-Z]{4} — only matches if those 4 chars are uppercase letters. Rejects 123TDEDB.                                           
  - .{4} — matches any 4 chars. 123TDEDB would still work.
                                                                                                                                
  For a SWIFT code validator (like in your constants.py), [A-Z]{4} is the right choice — you do care that the first 4 are       
  letters. The .{4} version would be too loose.                                                                                 
                                                                                                                                
  But your instinct is correct: when you only care about extracting a part and don't need to validate what came before it, .{4} 
  is a fine shorthand.
             
             
 | Mode   | Code                          | Returns             | Use when |
|-----    |----                           |---------            |----------|
| Default | .str.split(', ')              | Lists in one column | You want to chain .str.get() |
| Expand  | .str.split(', ', expand=True) | Multiple columns    | You want a proper DataFrame |   

| Method | What it does | Regex? | Example |
|--------|-------------|--------|---------|
| .str.contains() | Pattern anywhere | Yes (default) | .str.contains('LEI004', na=False) |
| .str.startswith() | Matches beginning | No | .str.startswith('DE') |
| .str.endswith() | Matches end | No | .str.endswith('FF') |
| .str.extract() | Pull out capture group | Yes (required) | .str.extract(r'^.{4}([A-Z]{2})') |
| .str.split() | Break apart | No | .str.split(', ', expand=True) |
| .str.get() | Index into list | No | .str.split(', ').str.get(0) |
| .str.replace() | Swap text | Yes (optional) | .str.replace(r'\[.*?\]', '', regex=True) |F
| .str.len() | Character count | No | .str.len() |  


| Category | Errors | Validator | Takeaway |
|----------|--------|-----------|----------|
| LEI | 92 | LeiValidator | Fake LEIs in test data → GLEIF rejects them |
| SHIP | 45 | ShipmentValidator | Missing ports + bad incoterms |
| AMT | 27 | AmountValidator | Zeros, negatives, bad formats |
| XVAL | 24 | CrossValidator | Same-party + country mismatches |
| DATE | 17 | DateValidator | Bad sequences + expired LCs |
| LC | 14 | LcValidator | Missing/short LC numbers + bad forms |
| BIC | 11 | SwiftValidator | Missing/malformed SWIFT codes |
| PTY | 7 | PartyValidator | Missing names/addresses |         

Day 52 Summary

| Tool | What you learned |
|------|-----------------|
| .str.contains() | Search for patterns, na=False for safety |
| .str.startswith() | Literal prefix matching, works in query() |
| .str.extract() | Regex capture groups → new columns (SWIFT country codes) |
| .str.split() | Break strings apart — lists or expand=True for columns |
| .str.get() | Index into split results |
| .str.replace() | Regex-powered text cleanup |
| .str.len() | Quick outlier detection with describe() |
| .explode() | One-row-per-item from lists — the split→explode→extract pattern 


exercise 1 |                                                               

| | Way 1: Import from config | Way 2: Parse from messages |
|---|---|---|
| Source | validation_rules.py (single source of truth) | error_messages string (derived output) |
| Reliability | Always correct — it IS the definition | Depends on string format not changing |
| Fragility | Breaks only if rules change | Breaks if __str__ format changes |
| Regex needed | None (just a dict) | Two capture groups |
| Speed | Faster (dict lookup) | Slower (regex on long strings) |
| Readability | .map(severity_map) — obvious | .str.extract(r'\]\s*([A-Z]+)\d') — cryptic |


## ==================== CROSSTAB ============================================
pd.crosstab builds a frequency table crossing two categorical columns. Here's what each piece does:
                                                                                                                                                       
  pd.crosstab(                                                                                                                                         
      report['issuing_bank_swift_country'],  # rows  → one row per country                                                                             
      report['validation_status'],           # cols  → one col per status (CLEAN / FLAGGED)                                                            
      normalize='index'                      # divide each row by its own row total                                                                    
  ).round(3) * 100                                                                                                                                     
                                                                                                                                                       
  Step by step:                                                                                                                                        
                  
  1. Without normalize — you'd get raw counts:                                                                                                         
  validation_status   CLEAN  FLAGGED
  DE                      7       20                                                                                                                   
  GB                     10        9
  ...                                                                                                                                                  
     
  2. normalize='index' — divides each row by its row total, turning counts into proportions (0–1):                                                     
  DE   →  7/27 = 0.259,  20/27 = 0.741                                                                                                                 
  GB   →  10/19 = 0.526,   9/19 = 0.474
  'index' means "normalize across columns within each row" — so every row sums to 1.0.                                                                 
                                                                                                                                                       
  3. .round(3) — round to 3 decimal places (0.259, not 0.2592592...).                                                                                  
                                                                                                                                                       
  4. * 100 — convert to percentages.                                                                                                                   
                                                                                                                                                       
  Final result: "Of all DE transactions, 25.9% are CLEAN and 74.1% are FLAGGED."                                                                       
   
  ---                                                                                                                                                  
  Why use crosstab instead of the manual groupby approach you wrote just above it?
                                                                                                                                                       
  Your manual approach (clean_per_country / total_per_country * 100) only shows the clean rate. crosstab gives you both columns in one table — and
  scales to more than 2 statuses automatically (e.g., if you added PENDING).                                                                           
                  
                                                                  
                                                                                 
● Neither is strictly "better" — they suit different situations:                                                                                       
                                                                                                                                                       
  ┌──────────┬──────────────────────────────────┬───────────────────────────────┐
  │          │          Manual groupby          │           crosstab            │                                                                      
  ├──────────┼──────────────────────────────────┼───────────────────────────────┤                                                                      
  │ Shows    │ One metric (clean rate)          │ All categories side by side   │                                                                      
  ├──────────┼──────────────────────────────────┼───────────────────────────────┤                                                                      
  │ Readable │ Explicit, you see each step      │ Compact, one line             │                                                                      
  ├──────────┼──────────────────────────────────┼───────────────────────────────┤                                                                      
  │ Flexible │ Easy to add custom logic         │ Limited to counts/proportions │                                                                      
  ├──────────┼──────────────────────────────────┼───────────────────────────────┤                                                                      
  │ Learning │ Forces you to understand groupby │ Hides the mechanics           │
  └──────────┴──────────────────────────────────┴───────────────────────────────┘                                                                      
                  
  In your specific case, both produce the same numbers. The crosstab is shorter and gives you both columns (CLEAN + FLAGGED) instead of just one.      
                  
  But since you're learning — the manual groupby version is more valuable to understand, because it shows you why the math works. crosstab is a        
  convenience wrapper you reach for once you already know what it's doing under the hood.
                                                                                                                                                       
  My take: learn the groupby way first (you already did), then use crosstab when you want a quick summary table to look at. Don't switch just because  
  it's shorter.
  
  
  3--
  | Currency | Your first try (% with AMT) | Correct answer (avg errors) |
|----------|---------------------------|---------------------------|
| EUR | 0.04 (4%) | 1.00 |
| GBP | 0.32 (32%) | 3.89 |
| JPY | 0.24 (24%) | 2.33 |
| USD | 0.19 (19%) | 3.00 |


======================  .nunique()  ============================================

.nunique() counts the number of unique (distinct) values in a Series or DataFrame column — ignoring NaN by default.

  Basic usage

  import pandas as pd

  s = pd.Series(["USD", "EUR", "USD", "GBP", "EUR", "EUR"])
  s.nunique()  # → 3  (USD, EUR, GBP)

  On a DataFrame

  df = pd.DataFrame({
      "currency": ["USD", "EUR", "USD", "GBP"],
      "status":   ["open", "open", "closed", "open"],
      "amount":   [1000, 2000, 1000, 500],
  })

  df.nunique()
  # currency    3
  # status      2
  # amount      3
  # dtype: int64

  Each column gets its unique count.

  NaN behavior

  By default, NaN is not counted as a unique value:

  s = pd.Series(["USD", "EUR", None, "USD", float("nan")])
  s.nunique()           # → 2  (NaN ignored)
  s.nunique(dropna=False)  # → 3  (NaN counted as one unique value)

  Common use cases

  Check for duplicates — if nunique() equals len(df), all values are distinct:
  df["lc_id"].nunique() == len(df)  # True → no duplicate IDs

  Spot low-cardinality columns — columns with few unique values are often categoricals:
  df.nunique().sort_values()
  # status      2   ← only 2 distinct values
  # currency    3
  # lc_id     200

  Per-group unique counts with groupby:
  df.groupby("status")["currency"].nunique()
  # open      3
  # closed    1

  ---
  In your LC pipeline context, .nunique() would be handy for sanity-checking things like how many distinct currencies, party countries, or issuing
  banks appear in the dataset.

❯ i want to see  transactions with  diverse error types                                                                                                
errors_exploded = (                                                                                                                                    
    flagged['error_codes']                                                                                                                             
    .str.split(', ') #  — splits each string into a list (no expand=True this time): 'LEI001, LEI004'   →  ['LEI001', 'LEI004']                        
    .explode() #  .explode() — unpacks each list into separate rows:                                                                                   
)                                                                                                                                                      

=========================== SPLIT() - EXPODE()- EXTRACT()- NUNIQUE() =================================

● After .explode(), the original row index is preserved — so each exploded row still knows which transaction it came from. That's the key to using
  .nunique() here.

  errors_exploded = (
      flagged['error_codes']
      .str.split(', ')
      .explode()
  )
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')

  # Count unique error categories per transaction
  diversity = (
      error_cat[0]                    # extract() returns a DataFrame → grab column 0
      .groupby(level=0)               # group by original row index (= transaction)
      .nunique()                      # how many distinct categories per transaction?
      .sort_values(ascending=False)   # most diverse first
      .rename("unique_error_types")
  )

  diversity.head()

  Example output:
  12    4    ← transaction at index 12 has 4 different error categories (LEI, SWIFT, AMT, DATE)
  7     3
  33    3
  ...

  Then to see the actual transactions:

  top_diverse = flagged.loc[diversity[diversity >= 3].index]
  top_diverse[['lc_id', 'error_codes']]

  ---
  Why groupby(level=0)?

  After .explode(), the index looks like this:

  12    LEI
  12    SWIFT
  12    AMT
  12    DATE
  7     SWIFT
  7     DATE
  ...

  level=0 groups by the outer index — i.e., the original transaction row. .nunique() then counts distinct categories within each group.

❯ what can we use instead level=0 ?                                                                                                                    

● You can pass the index name instead, if it has one.

  Check what your index is called:
  error_cat[0].index.name  # → 'lc_id', or None

  If it's named (e.g. 'lc_id'):
  .groupby('lc_id').nunique()

  If it's unnamed (None), level=0 is the clearest option. You could also reset the index first to turn it into a regular column:

  error_cat[0].reset_index().groupby('index').nunique()

  But that's more verbose — level=0 is the idiomatic way when the index is unnamed.

❯ flagged has transactioon_id but error_cat none                                                                                                       

● Right — after .explode() and .extract(), error_cat only has the numeric positional index, not transaction_id.

  Fix: carry transaction_id along before you explode:

  errors_exploded = (
      flagged.set_index('transaction_id')['error_codes']  # set transaction_id as index first
      .str.split(', ')
      .explode()
  )
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')

  diversity = (
      error_cat[0]
      .groupby('transaction_id')   # now you can use the name
      .nunique()
      .sort_values(ascending=False)
      .rename("unique_error_types")
  )

  Now the index of error_cat is transaction_id, so .groupby('transaction_id') works — and the result is labeled with real IDs instead of row numbers.

❯ KeyError: 'transaction_id'                                                                                                                           

● Let me check the actual column names in your data.

  Read 1 file (ctrl+o to expand)

● The column is transaction_id — so the KeyError means flagged doesn't have it as a column, it's probably already the index. Check:

  flagged.index.name   # likely 'transaction_id'
  flagged.columns.tolist()

  If transaction_id is already the index, just use level=0 (or the index name directly):

  errors_exploded = (
      flagged['error_codes']          # no need for set_index
      .str.split(', ')
      .explode()
  )
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')

  diversity = (
      error_cat[0]
      .groupby(level=0)               # use level=0 since it's already the index
      .nunique()
      .sort_values(ascending=False)
      .rename("unique_error_types")
  )

❯ can u look uo for flagged_issues.csv ?                                                                                                               
                                         
  Searched for 1 pattern, read 1 file (ctrl+o to expand)                                                                                               
                                                                                                                                                       
● transaction_id is a regular column (not the index). So the fix is straightforward — use set_index('transaction_id') when building errors_exploded:   
            
  flagged = pd.read_csv('.../flagged_issues.csv')                                                                                                      
                                                                                                                                                       
  errors_exploded = (                                                                                                                                  
      flagged.set_index('transaction_id')['error_codes']                                                                                               
      .str.split(', ')                                                                                                                                 
      .explode()                                                                                                                                       
  )
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')                                                                                                
                                                                                                                                                       
  diversity = (
      error_cat[0]                                                                                                                                     
      .groupby('transaction_id')
      .nunique()                                                                                                                                       
      .sort_values(ascending=False)
      .rename("unique_error_types")                                                                                                                    
  )                                                                                                                                                    
   
  This works because set_index('transaction_id') promotes it to the index before exploding, so it's preserved through all the chained operations.      
                  
❯ or without using set_index , can u use directly report ?                                                                                             
                                                           
● Yes — just reference flagged['transaction_id'] as the groupby key directly:                                                                          
                                                                                                                                                       
  errors_exploded = (                                                                                                                                  
      flagged['error_codes']                                                                                                                           
      .str.split(', ')                                                                                                                                 
      .explode()  
  )
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')                                                                                                
   
  diversity = (                                                                                                                                        
      error_cat[0]
      .groupby(flagged['transaction_id'])   # pass the column directly
      .nunique()                                                                                                                                       
      .sort_values(ascending=False)
      .rename("unique_error_types")                                                                                                                    
  )               

  groupby() accepts a Series as a key — it lines up with error_cat[0] by the positional index.                                                         
   
❯ it works now , can u explain why we use error_+cat[0] in detail ?                                                                                    
                                                                    
● .str.extract() always returns a DataFrame, even when you only capture one group.                                                                     
                                                                                                                                                     
  error_cat = errors_exploded.str.extract(r'^([A-Z]+)')                                                                                                
  type(error_cat)   # → DataFrame                                                                                                                      
  error_cat                                                                                                                                            
          0                                                                                                                                            
  0     LEI                                                                                                                                            
  1     LEI
  2    SWIFT                                                                                                                                           
  3     AMT       
  ...                                                                                                                                                  
     
  The column is named 0 (integer) because you didn't name the capture group. So error_cat[0] selects that column — giving you a Series, which is what  
  .groupby().nunique() needs.                                                                                                                          
   
  ---                                                                                                                                                  
  Two ways to avoid [0]:
                        
  1. Name the capture group in the regex:
  error_cat = errors_exploded.str.extract(r'^(?P<category>[A-Z]+)')                                                                                    
  # now the column is named 'category'                             
  error_cat['category'].groupby(...).nunique()                                                                                                         
                                              
  2. Use .str.extract(...)[0] inline:                                                                                                                  
  errors_exploded.str.extract(r'^([A-Z]+)')[0].groupby(...).nunique()                                                                                  
                                                                                                                                                       
  ---                                                                                                                                                  
  Why does .extract() return a DataFrame at all?                                                                                                       
                                                
  Because regex can have multiple capture groups:                                                                                                      
  # two groups → two columns                                                                                                                           
  errors_exploded.str.extract(r'^([A-Z]+)(\d+)')
  #     0    1                                                                                                                                         
  # 0  LEI  001                                                                                                                                        
  # 1  LEI  004
  # 2  AMT  002                                                                                                                                        
                  
  So pandas always returns a DataFrame to be consistent — whether you have 1 group or 10.   
          
========================== TRANSFORM() =========================
.transform() in Pandas                                                                                                              
                        
  .transform() applies a function to a Series or DataFrame and returns the same shape back — every row gets a value, aligned to the   
  original index. That's the key difference from other methods:                                                                       
                                                                                                                                      
  ┌──────────────┬──────────────────────────────────────────────────┐                                                                 
  │    Method    │                     Returns                      │                                                                 
  ├──────────────┼──────────────────────────────────────────────────┤                                                                 
  │ .apply()     │ whatever the function returns (can change shape) │
  ├──────────────┼──────────────────────────────────────────────────┤                                                                 
  │ .agg()       │ a reduced/summarized result (fewer rows)         │
  ├──────────────┼──────────────────────────────────────────────────┤                                                                 
  │ .transform() │ same shape as input — one value per original row │
  └──────────────┴──────────────────────────────────────────────────┘                                                                 
                  
  ---                                                                                                                                 
  The Mental Model
                                                                                                                                      
  df['col'].transform(func)
  # For every value in 'col', apply func and put the result back                                                                      
  # in the same position — the output is always len(df) rows                                                                          
                                                                                                                                      
  ---                                                                                                                                 
  Examples in Your LC Pipeline Context                                                                                                
                                                                                                                                      
  1. Normalize a column (same as what _clean_whitespace does, but with transform)
                                                                                                                                      
  Your current code:
  df[col] = df[col].str.strip()                                                                                                       
                  
  With .transform():                                                                                                                  
  df[col] = df[col].transform(lambda x: x.strip() if isinstance(x, str) else x)
                                                                                                                                      
  Not better here — .str.strip() is cleaner. But it shows the concept.                                                                
                                                                                                                                      
  ---                                                                                                                                 
  2. Group-level info kept at row level — the real power                                                                              
                                                                                                                                      
  This is where .transform() shines. Say you want to flag currencies that appear only once (possibly a data entry error):
                                                                                                                                      
  # How many times does each currency appear?
  df['currency_count'] = df['currency'].transform('count')                                                                            
  # Every row gets the total count of its own currency group
  # USD rows → 95, EUR rows → 60, KRW rows → 1, etc.                                                                                  
                                                                                                                                      
  You can't do this with .groupby().agg() easily because that collapses the rows. .transform() fans the result back out to every row. 
                                                                                                                                      
  ---                                                                                                                                 
  3. Flag outlier amounts per currency group

  # Mean amount for each currency group, broadcast back to every row
  df['currency_mean_amount'] = (                                                                                                      
      df.groupby('currency')['amount']                                                                                                
      .transform('mean')                                                                                                              
  )                                                                                                                                   
                  
  # Now you can compare each row's amount to its currency's mean                                                                      
  df['is_outlier'] = df['amount'] > df['currency_mean_amount'] * 3
                                                                                                                                      
  Each USD row gets the USD mean. Each EUR row gets the EUR mean. Same shape, row-aligned.                                            
                                                                                                                                      
  ---                                                                                                                                 
  4. Normalize amounts within currency group
                                                                                                                                      
  # Scale each amount relative to its currency's max (0.0 to 1.0)
  df['amount_normalized'] = (                                                                                                         
      df.groupby('currency')['amount']
      .transform(lambda x: x / x.max())                                                                                               
  )               
                                                                                                                                      
  ---             
  5. Clean a column with a custom function (replacing your loop style)
                                                                                                                                      
  Your _clean_unicode loops over characters. With .transform() you could apply a whole cleaning function per cell:
                                                                                                                                      
  def clean_cell(val):
      if not isinstance(val, str):                                                                                                    
          return val
      for old, new in UNICODE_REPLACEMENTS.items():                                                                                   
          val = val.replace(old, new)
      return val
                                                                                                                                      
  df[col] = df[col].transform(clean_cell)
                                                                                                                                      
  Same result as your nested loop, but more explicit about "one cell in, one cell out."                                               
   
  ---                                                                                                                                 
  When to use .transform() vs alternatives
                                          
  - Use .transform() when: you need group-level stats (mean, count, max) but want the result aligned back to every row — not
  collapsed.                                                                                                                          
  - Use .str.method() when: you're doing simple string ops on a whole column (faster, more readable).
  - Use .apply() when: you need to work row-by-row across multiple columns, or your function changes shape.                           
                                                                                                                                      
  The group+broadcast pattern (groupby().transform()) is the most useful case in real data work — and could be handy in your          
  ReportService when computing severity distributions per currency or party group.     
  
 ====================== mean() =============================

In Python, True == 1 and False == 0. That's not a convention — it's how booleans actually work at the type level (bool is a subclass
   of int).                                                                                                                           
                                                                                                                                      
  So when you have a boolean Series:
                                                                                                                                      
  is_flagged = [True, False, True, True, False]
  #              1      0     1     1     0                                                                                           
                                                                                                                                      
  .mean() does exactly what it always does — sum divided by count:                                                                    
                                                                                                                                      
  sum   = 1 + 0 + 1 + 1 + 0 = 3                                                                                                       
  count = 5                                                                                                                           
  mean  = 3 / 5 = 0.6
                                                                                                                                      
  That 0.6 means 60% of rows are flagged. Multiply by 100 → 60.0.                                                                     
   
  ---                                                                                                                                 
  You can verify this yourself:

  import pandas as pd

  s = pd.Series([True, False, True, True, False])                                                                                     
   
  print(s.sum())    # 3   ← counts the Trues                                                                                          
  print(s.count())  # 5   ← total rows
  print(s.mean())   # 0.6 ← 3/5                                                                                                       
                                                                                                                                      
  So is_flagged.mean() * 100 is always the flagged percentage — no extra column needed.    
  
  ======================= lambda ===========================
  
In the .agg() call, each named aggregation normally takes a string like 'sum', 'mean', 'count'. But those are fixed — you can't do  
  math on the result inside them.                                                                                                   
                                                                                                                                      
  A lambda lets you write custom logic instead:                                                                                       
                                                                                                                                      
  flagged_pct=('is_flagged', lambda x: (x.mean() * 100).round(2))                                                                     
  #                          └───────┘  └──────────────────────┘
  #                          "use a      what to do with the                                                                          
  #                          custom fn"  group's values                                                                               
                                                                                                                                      
  x here is the is_flagged column for one currency group — pandas passes each group's slice to your function automatically.           
                                                                                                                                      
  So if you're on the USD group:                                                                                                      
  x = [True, False, True, True, False, True]   ← just USD rows
  lambda runs: x.mean() * 100 → 66.67                                                                                                 
  Then EUR group:                                                                                                                     
  x = [False, False, True]   ← just EUR rows                                                                                          
  lambda runs: x.mean() * 100 → 33.33                                                                                                 
                                                                                                                                      
  Pandas collects all the results and builds the final column.                                                                        
                                                                                                                                      
  ---                                                                                                                                 
  Why not just use 'mean'?                                                                                                            
                                                                                                                                      
  flagged_pct=('is_flagged', 'mean')   # gives 0.6
  flagged_pct=('is_flagged', lambda x: x.mean() * 100)  # gives 60.0                                                                  
                  
  'mean' gives you the raw ratio. The lambda lets you multiply by 100 and round — things a plain string shortcut can't do.                                              
         
         
======================= Challenge 6  ==========    

Your lambda returns a whole value_counts() Series — .agg() needs a scalar (single value) back. Add .idxmax() to get just the top
  error code:                                                                                                                         
                                                                                                                                      
  most_common_error=('error_codes', lambda x: x.dropna().str.split(', ').explode().value_counts().idxmax())                           
                                                                                                                                      
  What each step does on one currency group:                                                                                          
                  
  x                        # ['AMT001, AMT002', 'AMT001', NaN, 'DAT001, AMT001']                                                      
  x.dropna()               # ['AMT001, AMT002', 'AMT001', 'DAT001, AMT001']  ← skip valid rows                                        
  .str.split(', ')         # [['AMT001','AMT002'], ['AMT001'], ['DAT001','AMT001']]                                                   
  .explode()               # ['AMT001', 'AMT002', 'AMT001', 'DAT001', 'AMT001']  ← one per row                                        
  .value_counts()          # AMT001: 3, DAT001: 1, AMT002: 1                                                                          
  .idxmax()                # 'AMT001'  ← just the top one ✓                                                                           
                                                                                                                                      
  .dropna() is important — rows with no errors have NaN in error_codes, and .str.split() on NaN would give you errors.                
                  
  If a currency group has zero flagged rows (all NaN), .idxmax() will crash. Handle it safely:                                        
                  
  most_common_error=('error_codes', lambda x: (                                                                                       
      x.dropna().str.split(', ').explode().value_counts().idxmax()                                                                    
      if x.notna().any() else None
  ))                                                                                                                                  
                  
❯ i asked opus , he gave me this                                                                                                      
 most_common_error=('error_codes', lambda x:                                                                                          
    x[x != ''].str.split(', ').explode().value_counts().index[0]                                                                      
    if x[x != ''].any() else 'NONE'                                                                                                   
    )                                                                                                                                 
used x[x != '']  for dropna() but used directly index[0] instead idxmax() what u showed me is more clean                              
                                                            
                  
● Yes, both work but yours (with .idxmax()) is cleaner. Here's why each difference matters:
                                                                                                                                      
  x.dropna() vs x[x != '']                                                                                                            
                                                                                                                                      
  x.dropna()       # removes NaN (float missing values from pandas)                                                                   
  x[x != '']       # removes empty strings '' but NOT NaN                                                                             
                                                                                                                                      
  dropna() is more correct here — when a row has no errors, pandas stores it as NaN, not ''. The x != '' filter could miss those and  
  cause a .str.split() crash on NaN values.                                                                                           
                                                                                                                                      
  ---             
  .idxmax() vs .index[0]
                                                                                                                                      
  .value_counts().idxmax()   # returns the label with the highest count
  .value_counts().index[0]   # returns the first index label (which happens to be the top since value_counts sorts descending)        
                                                                                                                                      
  Both give the same result because value_counts() sorts descending by default. But .idxmax() is more explicit — it says "give me the 
  label of the maximum" rather than relying on sort order as a side effect.                                                           
                                                                                                                                      
  ---             
  else None vs else 'NONE'
                          
  Minor preference — None is the proper "no value" in Python/pandas, while 'NONE' is a string that could accidentally look like a real
   error code if someone scans the output quickly.                                                                                    
 
 
 The key takeaway from this challenge: inside .agg(), every lambda must return one value. 
 When you have a function that naturally returns many values (like value_counts()), you need to reduce it —
  .index[0] for the name, .iloc[0] for the count, .max() for the biggest, etc.
| Your lambda returns... | Fix |
|----------------------|-----|
| A Series | .index[0] or .iloc[0] |
| A DataFrame | Won't work in agg — rethink |
| A single value | Perfect, agg is happy |    


================================= groupby().filter() ====================================================

groupby().filter() keeps or drops entire groups based on a condition applied to the group as a whole.                                      
                                                                                                                                             
  Basic idea                                                                                                                                 
   
  df.groupby("column").filter(lambda group: condition)                                                                                       
                                                                                                                                             
  The lambda receives each group as a DataFrame. If it returns True, the group is kept. If False, the group is dropped.                      
                                                                                                                                             
  ---                                                                                                                                        
  Example 1 — Keep groups with more than 1 row                                                                                               
                                                                                                                                             
  import pandas as pd
                                                                                                                                             
  df = pd.DataFrame({
      "country": ["US", "US", "UK", "DE"],
      "amount":  [1000, 2000, 500, 800]                                                                                                      
  })
                                                                                                                                             
  df.groupby("country").filter(lambda g: len(g) > 1)                                                                                         
    country  amount
  0      US    1000                                                                                                                          
  1      US    2000
  UK and DE each had only 1 row → dropped. US had 2 rows → kept.                                                                             
   
  ---                                                                                                                                        
  Example 2 — Keep groups where all values meet a condition
                                                                                                                                             
  df.groupby("country").filter(lambda g: g["amount"].min() > 600)
    country  amount                                                                                                                          
  0      US    1000
  1      US    2000
  UK has 500 which is < 600 → entire UK group dropped. DE has 800 but only 1 row, min is 800 > 600 → kept.                                   
                                                                                                          
  Wait — let me redo with clearer data:                                                                                                      
                                                                                                                                             
  df = pd.DataFrame({                                                                                                                        
      "country": ["US", "US", "UK", "UK"],                                                                                                   
      "amount":  [1000, 2000, 500,  800]
  })                                                                                                                                         
   
  df.groupby("country").filter(lambda g: g["amount"].min() > 600)                                                                            
    country  amount
  0      US    1000
  1      US    2000                                                                                                                          
  UK min is 500 → entire UK group dropped (both rows).
                                                                                                                                             
  ---                                                                                                                                        
  Contrast with .apply() and boolean indexing
                                                                                                                                             
  ┌─────────────────────────────────┬───────────────────────────────────────┐
  │            Approach             │             What it does              │                                                                
  ├─────────────────────────────────┼───────────────────────────────────────┤
  │ groupby().filter()              │ Drops/keeps whole groups              │
  ├─────────────────────────────────┼───────────────────────────────────────┤
  │ groupby().apply()               │ Transforms each group, returns result │                                                                
  ├─────────────────────────────────┼───────────────────────────────────────┤                                                                
  │ Boolean indexing df[df.col > x] │ Drops/keeps individual rows           │                                                                
  └─────────────────────────────────┴───────────────────────────────────────┘                                                                
                  
  ---                                                                                                                                        
  Relevant to your LC pipeline
                                                                                                                                             
  You could use this to flag all transactions in a group where any one transaction has a critical error:
                                                                                                                                             
  # Drop all transactions from any currency that has a zero-amount entry
  df.groupby("currency").filter(lambda g: (g["amount"] > 0).all())                                                                           
                  
  The key rule: the condition is about the group, the result affects all rows in the group.  
  
================================ .loc =========================================

df.loc[row_filter, column_filter] — two slots, comma-separated.                                                                            
                                                                                                                                           
  df.loc[rows, columns]                                                                                                                      
                                                                                                                                             
  ---                                                                                                                                        
  Your example broken down                                                                                                                   
                                                                                                                                             
  df.loc[df["error_codes"].str.contains("AMT", na=False), "transaction_id"]
  #      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^                                                                  
  #                    rows (boolean mask)                  column to keep                                                                   
                                                                                                                                             
  ┌─────────┬───────────────────────────────────────┬─────────────────────────┐                                                              
  │  slot   │             what you put              │      what it does       │                                                              
  ├─────────┼───────────────────────────────────────┼─────────────────────────┤                                                              
  │ rows    │ df["error_codes"].str.contains("AMT") │ keep only AMT rows      │
  ├─────────┼───────────────────────────────────────┼─────────────────────────┤
  │ columns │ "transaction_id"                      │ return only that column │                                                              
  └─────────┴───────────────────────────────────────┴─────────────────────────┘
                                                                                                                                             
  ---
  Simpler examples to build intuition
                                                                                                                                             
  # All rows, one column          
  df.loc[:, "transaction_id"]                                                                                                                
                                                                                                                                             
  # One row by index label, all columns
  df.loc[3, :]                                                                                                                               
                                                                                                                                             
  # All rows, multiple columns    
  df.loc[:, ["transaction_id", "error_codes", "severity"]]                                                                                   

  # Filtered rows, multiple columns                                                                                                          
  df.loc[df["severity"] == "CRITICAL", ["transaction_id", "severity"]]
                                                                                                                                             
  ---
  loc vs df[...]
                                                                                                                                             
  df[df["severity"] == "CRITICAL"]["transaction_id"]   # chained — works but not recommended
  df.loc[df["severity"] == "CRITICAL", "transaction_id"]  # one operation — preferred                                                        
                                                                                                                                             
  Chaining df[...][...] can cause a SettingWithCopyWarning if you later try to assign values. .loc avoids that because it's a single         
  operation on the original DataFrame.                                                                                                       
                                                                                                                                                                                                                         