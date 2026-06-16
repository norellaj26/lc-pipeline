## ============================= # 2====================================== 

CURRENCY_INFO is a dict of dicts:                                                                                                                                       
               
  {                                                                                                                                                                       
      'USD': {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'},                                                                                                         
      'EUR': {'decimals': 2, 'name': 'Euro',      'symbol': '€'},                                                                                                         
      ...                                                                                                                                                                 
  }    

CURRENCY_INFO.items() — gives you pairs: 
  ('USD', {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'})                                                                                                            
  ('EUR', {'decimals': 2, 'name': 'Euro',      'symbol': '€'})

  {'code': code, **info} — builds one flat dict per currency:                                                                                                             
  {'code': 'USD', 'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}                                                                                                      
  The **info part "unpacks" the inner dict, merging its keys alongside code.                                                                                              
                                                                                                                                                                          
  [... for code, info in ...] — list comprehension, one dict per row.  

● CURRENCY_INFO = {                                                                                                                                                       
      'USD': {'decimals': 2, 'name': 'US Dollar'},                                                                                                                        
      'EUR': {'decimals': 2, 'name': 'Euro'},                                                                                                                             
  }                                                                                                                                                                       
                                                                                                                                                                          
  for code, info in CURRENCY_INFO.items():                                                                                                                                
      print(code, info)                                                                                                                                                   
                                                                                                                                                                          
  # USD {'decimals': 2, 'name': 'US Dollar'}                                                                                                                              
  # EUR {'decimals': 2, 'name': 'Euro'}
                                                                                                                                                                          
  .items() gives you each key-value pair, and code, info unpacks them — code gets the key, info gets the dict.   
    
                                                                                                                                                                      
  pd.DataFrame([...]) — turns that list of dicts into a DataFrame, each key becomes a column.  
  
  The key insight is **info — it spreads a nested dict into flat key-value pairs so pandas can use them as columns.  
  

Layer 2: .items() gives you pairs
for code, info in CURRENCY_INFO.items():
    # First iteration:  code = 'USD', info = {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}
    # Second iteration: code = 'EUR', info = {'decimals': 2, 'name': 'Euro', 'symbol': '€'}

# Without unpacking:
{'code': 'USD', 'info': {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}}
# → Nested! info is a dict inside a dict. Ugly.

# With **info unpacking:
{'code': 'USD', **{'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}}
# Python "spills" the inner dict into the outer one:
{'code': 'USD', 'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}
# → Flat! One level. Clean.

Layer 3: The **info unpacking
This is the trick. Watch what happens step by step:
python# Without unpacking:
{'code': 'USD', 'info': {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}}
# → Nested! info is a dict inside a dict. Ugly.

# With **info unpacking:
{'code': 'USD', **{'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}}
# Python "spills" the inner dict into the outer one:
{'code': 'USD', 'decimals': 2, 'name': 'US Dollar', 'symbol': '$'}
# → Flat! One level. Clean.

Think of ** like opening a suitcase and dumping the contents onto the table instead of putting the whole suitcase on the table.
Layer 4: The list comprehension wraps it all
python[
    {'code': 'USD', 'decimals': 2, 'name': 'US Dollar', 'symbol': '$'},
    {'code': 'EUR', 'decimals': 2, 'name': 'Euro', 'symbol': '€'},
    {'code': 'GBP', 'decimals': 2, 'name': 'British Pound', 'symbol': '£'},
    ...
]
```

A list of flat dictionaries — and `pd.DataFrame()` knows exactly how to turn that into a table:
 each dict becomes a row, each key becomes a column.

---

### Now the actual merge

You have two DataFrames:
```
report → 200 rows, has 'currency' column (USD, EUR, GBP, JPY)
currency_df → 10 rows, has 'code' column (USD, EUR, GBP, JPY, CHF, CAD, ...)****

## ============================= # 3 ======================================

| Parameter | What it means |
|-----------|--------------|
| left_on='currency' | "In the LEFT table (report), match on this column" |
| right_on='code' | "In the RIGHT table (currency_df), match on this column" |

If both columns had the same name, you'd just use on='currency' instead. 
But since yours are named differently (currency vs code), you need left_on / right_on.

And notice you now have both currency AND code in the result — 
they contain the same values (both are "USD", "GBP", etc.) but they came from different tables. 
That's a bit redundant. 
You have two options to keep it clean:

Option A: Drop the duplicate column after merge
merged = report.merge(currency_df, left_on='currency', right_on='code').drop(columns='code')

Option B: Rename before merging so both columns match
currency_df_renamed = currency_df.rename(columns={'code': 'currency'})  # on= works when names match!

Now the important part — **what just happened under the hood?**
```
report (200 rows)          currency_df (10 rows)
┌──────────┬──────────┐    ┌──────┬───────────┐
│ txn_id   │ currency │    │ code │ name      │
├──────────┼──────────┤    ├──────┼───────────┤
│ LC-ZCOTOH│ GBP      │──→ │ GBP  │ British £ │
│ LC-OH9SDB│ JPY      │──→ │ JPY  │ Yen ¥     │
│ LC-6GVWRD│ USD      │──→ │ USD  │ Dollar $  │
└──────────┴──────────┘    └──────┴───────────┘

pandas first builds a lookup table from currency_df:                                                                                                                          
                                                                                                                                                                                
  GBP → {name: 'British Pound', symbol: '£', decimals: 2}                                                                                                                       
  USD → {name: 'US Dollar',     symbol: '$', decimals: 2}                                                                                                                       
  ...                                                                                                                                                                           
                                                                                                                                                                                
  Then for every row in report, it looks up the matching code in that table and attaches the info.                                                                              
                                                                                                                                                                                
  So for your example — LC-ZCOTOC with GBP:                                                                                                                                     
  1. pandas sees currency = 'GBP'                                                                                                                                               
  2. finds GBP in currency_df                                                                                                                                                   
  3. copies name, symbol, decimals onto that row   

That's why left_on='currency', right_on='code' — it's telling pandas: "match these two column names together". 


## ============================= # 4 ======================================

 Short answer: **info = grab everything blindly. Manual = grab exactly what you need

The rule of thumb:
```
| Intent | Use |
|--------|-----|
| "Give me everything" | **info |
| "Give me exactly these columns" | Explicit keys |
| Unsure? | Explicit — safer, more readable |

## ============================= # 5 ======================================
 — .assign() creates a new column without modifying the original. It's the method version of df['new_col'] = ....
 
.assign() 
# These two do the same thing:

# Way 1: Direct assignment (mutates the DataFrame)
errors_series['error_code'] = errors_series['error_codes'].str.split(', ')

# Way 2: .assign() (returns a NEW DataFrame, original untouched)
errors_series.assign(error_code=errors_series['error_codes'].str.split(', '))
```
```
| | Direct assignment | .assign()                                   |
|---|-------------------|---------------------------------------------|
| Modifies original? | Yes        No — returns new copy                       |
| Chainable? | No                | Yes — can chain .assign().explode().merge() |
| Defensive? | No                | Yes — original is safe                      |
```

Same philosophy as `.copy()` and `frozen=True` — don't mutate things you might need again.

 Why copy()?                                                                                                                                                     
                                                                                                                                                                  
  flagged[['transaction_id', 'error_codes']] is a slice of flagged. Pandas may return a view (a window into the original) 
  instead of an independent object. If you  later modify errors_series, 
  pandas raises a SettingWithCopyWarning — or worse, silently modifies flagged too.
                                                                                                                                                                  
  .copy() makes errors_series a fully independent DataFrame, disconnected from flagged.                                                                           
   
  Relation to assign()?                                                                                                                                           
                  
  Here's the key: assign() always returns a new DataFrame — it never mutates the object it's called on. 
  So errors_series is never touched by assign().            
   
  flagged  →  .copy()  →  errors_series  →  .assign()  →  errors_exploded (new df)                                                                                
                ↑                                ↑                                                                                                                
           breaks the view link           always new df, never mutates
                                                                                                                                                                  
  So are they redundant with each other?                                                                                                                          
                                                                                                                                                                  
  Yes and no. Since assign() never mutates anyway, the copy() isn't protecting against assign() specifically. 
  The copy() protects the earlier reference — 
  it ensures errors_series itself is safe to pass around without worrying it's secretly a view of flagged.
                                                                                                                                                                  
  In practice: copy() = "safe to hold", assign() = "safe to transform".                                                                                           
   
## ============================= # 6 ======================================
  One side effect to know: when you use left_on/right_on with different names, the result keeps both columns 
  (e.g. you get both currency and code in the merged   
  DataFrame). With on=, there's only one column in the result since they were the same name to begin with.
  
  | Approach |     Tool        | Best for |
|---------  -|----            --|----------|
| .map(dict) | Series → Series | Adding ONE column |
| .merge(df) | DataFrame → DataFrame | Adding MULTIPLE columns |   

 -----------map(dict)-------------------
Series.map(dict) in pandas                                                                                                                                      
                                                                                                                                                                
  map() on a Series takes each value, looks it up as a key in the dict, and returns the corresponding value.                                                      
                                                                                                                                                                  
  s = pd.Series(['USD', 'GBP', 'JPY'])                                                                                                                            
                                                                                                                                                                
  symbol_map = {'USD': '$', 'GBP': '£', 'JPY': '¥'}                                                                                                               
   
  s.map(symbol_map)                                                                                                                                               
  # 0    $        
  # 1    £
  # 2    ¥

  That's it. It's a vectorized dictionary lookup.                                                                                                                 
   
  ---                                                                                                                                                             
  How it handles missing keys
                                                                                                                                                                  
  If a value isn't in the dict, it returns NaN:
                                                                                                                                                                  
  s = pd.Series(['USD', 'GBP', 'XYZ'])  # XYZ not in dict
  s.map(symbol_map)                                                                                                                                               
  # 0      $      
  # 1      £                                                                                                                                                      
  # 2    NaN   ← not found
                                                                                                                                                                  
  ---
  map(dict) vs merge()                                                                                                                                            
                      
  This is the most important thing to understand — they solve the same problem at different scales:
                                                                                                                                                                  
  ┌───────────────┬──────────────────────┬─────────────────────────────────┐
  │               │      map(dict)       │             merge()             │                                                                                      
  ├───────────────┼──────────────────────┼─────────────────────────────────┤
  │ Lookup source │ A Python dict        │ A full DataFrame                │
  ├───────────────┼──────────────────────┼─────────────────────────────────┤
  │ Adds columns  │ One at a time        │ Many at once                    │                                                                                      
  ├───────────────┼──────────────────────┼─────────────────────────────────┤                                                                                      
  │ Best when     │ Simple 1-to-1 lookup │ Multiple related columns to add │                                                                                      
  ├───────────────┼──────────────────────┼─────────────────────────────────┤                                                                                      
  │ Missing keys  │ Returns NaN          │ Drops row (inner) or NaN (left) │
  └───────────────┴──────────────────────┴─────────────────────────────────┘                                                                                      
                  
  Use map(dict) when you just need one column from a lookup:                                                                                                      
                  
  # Instead of merging the whole currency_df just for the symbol:                                                                                                 
  merged['symbol'] = merged['currency'].map({'USD': '$', 'GBP': '£', ...})                                                                                        
                                                                                                                                                                  
  Use merge() when the lookup table has multiple columns you want:                                                                                                
                                                                                                                                                                  
  # You want name, symbol, AND decimals → merge makes more sense                                                                                                  
  merged = report.merge(currency_df, left_on='currency', right_on='code')                                                                                         
                                                                                                                                                                  
  ---                                                                                                                                                             
  Where it fits in your project                                                                                                                                   
                               
  Your CURRENCY_INFO dict is a natural fit:
                                                                                                                                                                  
  from config.constants import CURRENCY_INFO
                                                                                                                                                                  
  # Extract just the symbols                                                                                                                                      
  symbol_map = {code: info['symbol'] for code, info in CURRENCY_INFO.items()}                                                                                     
  report['symbol'] = report['currency'].map(symbol_map)                                                                                                           
                  
  You could also use it for severity ordering — you have SEVERITY_ORDER in constants.py. Instead of merging, just map:                                            
                  
  severity_rank = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}                                                                                               
  errors_enriched['rank'] = errors_enriched['severity'].map(severity_rank)                                                                                        
  errors_enriched.sort_values('rank')                                                                                                                             
                                                                                                                                                                  
  ---                                                                                                                                                             
  Rule of thumb: if your lookup is already a dict and you only need one output column → map(dict). 
  If it's a DataFrame or you need multiple columns → merge().

================================= # 7 ====================================================================== 

The Four Merge Types
| how= | Keeps | Unmatched rows |
|------|-------|----------------|
| 'inner' | Only matches (DEFAULT) | Dropped silently |
| 'left' | All from LEFT table | Right columns = NaN |
| 'right' | All from RIGHT table | Left columns = NaN |
| 'outer' | Everything from BOTH | NaN where no match |

 Mental model:                                                                                                                                                                 
                                                                                                                                                                              
  - Inner = intersection (A ∩ B) — only the overlap
  - Outer = union (A ∪ B) — everything, NaN fills the gaps                                                                                                                      
                                                                                                                                                                                
  left and right are in between — one side is fully kept, the other side only contributes where it matches. 
  
================================= # 8 ======================================================================                                                                       
 Cell 8 — The Fix: LEFT Merge
                                                                                                                                                                                
  test_left = errors_exploded.merge(small_lookup, on='error_code', how='left')
                                                                                                                                                                                
  Adding how='left' changes the behavior: keep every row from the left DataFrame (errors_exploded), 
  and fill in columns from the right (small_lookup) where a match exists.     
   
  Result: 237 rows preserved, but severity and message are NaN for anything not in small_lookup.                                                                                
                  
  ┌────────────────┬──────────────────────┬───────────────────────┐                                                                                                             
  │    Behavior    │   Inner (default)    │         Left          │
  ├────────────────┼──────────────────────┼───────────────────────┤
  │ Row count      │ 45 (drops unmatched) │ 237 (keeps all)       │
  ├────────────────┼──────────────────────┼───────────────────────┤
  │ Missing lookup │ Row deleted          │ NaN in new columns    │                                                                                                             
  ├────────────────┼──────────────────────┼───────────────────────┤                                                                                                             
  │ Use when       │ Lookup is complete   │ Lookup may be partial │                                                                                                             
  └────────────────┴──────────────────────┴───────────────────────┘                                                                                                             
                  
  The key insight: a left merge is safer by default — you never silently lose rows. 
  The NaN values are visible and you can handle them explicitly (e.g. fillna('UNKNOWN')),     
  whereas dropped rows are invisible.    
  
  ❯ why should we use ( or when )  left / right ?     
 Think of it this way: the "side" tells you which DataFrame is the authority — the one whose rows must all survive.                                                            
                                                                                                                                                                                
  ---                                                                                                                                                                           
  The mental model                                                                                                                                                              
                                                                                                                                                                                
  result = A.merge(B, on='key', how='left')   # A is the authority                                                                                                            
  result = A.merge(B, on='key', how='right')  # B is the authority
                                                                                                                                                                                
  Ask yourself: "Which table am I trying to enrich, and which table am I pulling extra info from?"                                                                              
                                                                                                                                                                                
  - The table you're enriching → goes on the authority side                                                                                                                     
  - The table you're pulling from → goes on the other side
                                                                                                                                                                                
  ---             
  When to use LEFT (most common)
                                                                                                                                                                                
  ▎ "I have a main dataset. I want to attach extra info from a lookup. I must keep all my main rows."
                                                                                                                                                                                
  # Keep ALL errors, attach severity where possible
  errors_exploded.merge(error_lookup, on='error_code', how='left')                                                                                                              
                                                                                                                                                                                
  Use left when:
  - Enriching transactions with lookup data (currency, country, product info)                                                                                                   
  - The lookup might be incomplete                                                                                                                                              
  - Missing enrichment = NaN (acceptable), missing transaction row = not acceptable
                                                                                                                                                                                
  ---                                                                                                                                                                           
  When to use RIGHT                                                                                                                                                             
                                                                                                                                                                                
  ▎ Same logic as left, but you wrote the arguments in the opposite order.
                                                                                                                                                                                
  # These two are identical in outcome — just mirrored
  A.merge(B, how='left')   ==   B.merge(A, how='right')                                                                                                                         
                  
  In practice, right merge is rare. Most people just swap the DataFrame order and use left instead — 
  it's easier to read because the "important" table is always on the left.   
                  
  ---                                                                                                                                                                           
  Quick decision guide

  ┌─────────────────────────────────────┬─────────────────────────────────────────────┐
  │              Scenario               │                     Use                     │
  ├─────────────────────────────────────┼─────────────────────────────────────────────┤
  │ Enrich main data with a lookup      │ left                                        │
  ├─────────────────────────────────────┼─────────────────────────────────────────────┤
  │ Keep only rows that match in both   │ inner (default)                             │                                                                                         
  ├─────────────────────────────────────┼─────────────────────────────────────────────┤                                                                                         
  │ Combine everything, gaps become NaN │ outer                                       │                                                                                         
  ├─────────────────────────────────────┼─────────────────────────────────────────────┤                                                                                         
  │ Right merge                         │ Almost never — just swap order and use left │
  └─────────────────────────────────────┴─────────────────────────────────────────────┘                                                                                         
                  
  The rule of thumb: default to left unless you specifically want to drop unmatched rows (inner) or 
  keep everything from both sides (outer).  
  
  LEFT TABLE (errors)          RIGHT TABLE (small_lookup)
┌────────┬───────────┐       ┌───────────┬──────────┐
│ txn_id │error_code │       │error_code │ severity │
├────────┼───────────┤       ├───────────┼──────────┤
│ LC-001 │ LEI004    │       │ AMT001    │ CRITICAL │
│ LC-001 │ AMT001   ✦│───────│✦AMT001    │ CRITICAL │
│ LC-002 │ SHIP002   │       │ AMT002    │ CRITICAL │
│ LC-003 │ DATE007   │       │ AMT005    │ CRITICAL │
└────────┴───────────┘       │ ...       │ ...      │
                              └───────────┴──────────┘

✦ = the ONE match

INNER:  Only LC-001/AMT001 survives (1 row)
LEFT:   All 4 left rows survive, AMT001 gets severity, rest get NaN
RIGHT:  All 15 right rows survive, AMT001 gets txn_id, rest get NaN
OUTER:  Everything from both sides, NaN wherever no match    

The key decision in real work:
| Situation | Use |
|-----------|-----|
| "I need complete left data, enrich where possible" | LEFT |
| "Only rows that exist in both" | INNER |
| "Show me everything, I'll handle gaps" | OUTER |
| "I need complete right data" | RIGHT (rare) |      

In data engineering, left is the most common — you have your main dataset and you're adding context from a lookup. 
You never want to silently lose rows from your main data.     

================================= # 9 ======================================================================     

| validate=      | Meaning                              | Fails if... |
|-----------|---------|-------------|
| 'one_to_one' | Each key appears once in BOTH          | Duplicates anywhere |
| 'many_to_one' | Left can repeat, right must be unique | Right has duplicate keys |
| 'one_to_many' | Left must be unique, right can repeat | Left has duplicate keys |
| 'many_to_many' | No checks (dangerous!)               | Never fails |
 
 ** many_to_one is your best friend for lookup merges — it says "many transactions can share one error code definition, 
 but each error code should have exactly one definition." 
 If someone accidentally duplicated a row in error_lookup, this would crash loudly instead of silently doubling your data. 
 
 Day 54 Summary 
 
 | Concept | What you learned |
|---------|-----------------|
| pd.merge() | Combine two DataFrames on a shared key |
| on= | When both columns have the same name |
| left_on= / right_on= | When column names differ |
| how='inner' | Only matches (default — dangerous!) |
| how='left' | Keep all left rows, NaN where no match |
| how='right' | Keep all right rows (rare) |
| how='outer' | Keep everything from both sides |
| validate= | Safety net against duplicate keys |
| .assign() | Create new column without mutating original |
| **dict unpacking | Flatten nested dicts for DataFrame construction |  

| Principle | Why it matters |
|-----------|---------------|
| Default inner merge drops rows silently | Always specify how= explicitly |
| Use validate='many_to_one' for lookups | Catches duplicate keys before they multiply rows |
| .map(dict) for one column, .merge() for multiple | Right tool for the job |
| LEFT merge is most common in data engineering | Never lose your main data |      


Think about the relationship between the key column on each side before the merge happens.
                                                                                                                                                                                
  ---                                                                                                                                                                           
  one_to_one — each key is unique on BOTH sides                                                                                                                                 
                                                                                                                                                                                
  # transactions: each transaction_id appears once                                                                                                                            
  # report: each transaction_id appears once                                                                                                                                    
  transactions.merge(report, on='transaction_id', validate='one_to_one')                                                                                                        
  transactions          report
  LC-001  GBP           LC-001  VALID                                                                                                                                           
  LC-002  USD    →      LC-002  FLAGGED                                                                                                                                         
  LC-003  JPY           LC-003  VALID                                                                                                                                           
  Fails if LC-001 appears twice in either table — means your data has duplicates it shouldn't have.                                                                             
                                                                                                                                                                                
  ---                                                                                                                                                                           
  many_to_one — left repeats, right is unique (most common)                                                                                                                     
                                                                                                                                                                                
  # errors_exploded: LC-001 appears 3 times (has 3 errors)
  # error_lookup: each error_code appears exactly once                                                                                                                          
  errors_exploded.merge(error_lookup, on='error_code', validate='many_to_one')                                                                                                  
  errors_exploded        error_lookup                                                                                                                                           
  LC-001  AMT001         AMT001  "Amount zero"   CRITICAL                                                                                                                       
  LC-001  LEI004   →     LEI004  "LEI not found" HIGH    
  LC-002  AMT001         DATE002 "Bad format"    HIGH                                                                                                                           
  LC-003  LEI004                                                                                                                                                                
  Many transactions can share the same error code — that's fine. But error_lookup must have each code only once. Fails if AMT001 appears twice in error_lookup (corrupted lookup
   table).                                                                                                                                                                      
                                                                                                                                                                                
  ---             
  one_to_many — left is unique, right repeats                                                                                                                                   
                  
  # currency_df: each currency code appears once
  # transactions: USD appears in many rows                                                                                                                                      
  currency_df.merge(transactions, left_on='code', right_on='currency', validate='one_to_many')                                                                                  
  currency_df            transactions                                                                                                                                           
  USD  "$"  2            LC-001  USD                                                                                                                                            
  EUR  "€"  2     →      LC-002  USD
  GBP  "£"  2            LC-003  EUR                                                                                                                                            
                         LC-004  GBP                                                                                                                                            
  Same as many_to_one but mirrored. Usually you'd just swap the order and use many_to_one instead — functionally identical.                                                     
                                                                                                                                                                                
  ---                                                                                                                                                                           
  many_to_many — no checks at all (dangerous)
                                                                                                                                                                                
  A.merge(B, on='key', validate='many_to_many')  # never fails
                                                                                                                                                                                
  A              B              Result (all combinations!)
  X  foo         X  aaa         X  foo  aaa                                                                                                                                     
  X  bar   →     X  bbb    →    X  foo  bbb                                                                                                                                     
  Y  baz                        X  bar  aaa                                                                                                                                     
                                 X  bar  bbb                                                                                                                                    
                                 Y  ???  ???  ← Y has no match, dropped silently                                                                                                
                                                                                                                                                                                
  Both sides have duplicates → pandas creates the cartesian product of matching keys. 2 rows × 2 rows = 4 rows. Row counts explode silently. Almost always a bug.               
                                                                                                                                                                                
  ---                                                                                                                                                                           
  When to use each
                                                                                                                                                                                
  ┌────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
  │               Your situation               │                                 Use                                  │                                                         
  ├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ Merging two clean, deduplicated tables     │ one_to_one                                                           │
  ├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ Enriching transactions from a lookup table │ many_to_one                                                          │                                                         
  ├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ You don't know the relationship yet        │ Add validate='many_to_one' and let it tell you if something is wrong │                                                         
  ├────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                         
  │ many_to_many                               │ Almost never intentionally                                           │
  └────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────┘                                                         
                  
  The real value of validate= is as a data quality assertion — it makes the merge fail loudly instead of silently producing wrong row counts.                                   
 
 
  ================================DAY 55 ===============================================================
  
| Topic           | What it solves                                   |
|-----------------|---------------|
| Multi-key merge | When ONE column isn't enough to identify a match |
| Suffixes        | When both tables have columns with the same name |
| pd.concat()     | Stacking DataFrames vertically (not side-by-side) |
| Merge vs Concat | Knowing which tool to reach for |
         
============================== # 10 =============================================
Now about reset_index() — after a groupby().agg(), the grouped columns become the index, not regular columns:   

# Without reset_index():
#                              avg_errors  num_transactions
# currency  validation_status
# EUR       CLEAN                    0.00                17
#           FLAGGED                  1.48                27

# With reset_index():
#   currency  validation_status  avg_errors  num_transactions
# 0      EUR              CLEAN        0.00                17
# 1      EUR            FLAGGED        1.48                27      

Without it, currency and validation_status are trapped in the index — you can't merge on them, can't filter easily. 
reset_index() pulls them back as normal columns. You'll use this all the time after groupby.    


Merge vs Concat — When to use which?

| Tool | Direction | Purpose | Key needed? |
|------|-----------|---------|-------------|
| merge() | Horizontal (add columns) | Combine by matching key | Yes |
| concat() | Vertical (add rows) | Stack same-shaped data | No |

merge() = "I have extra INFO about my rows"
    report + currency details → wider table

concat() = "I have MORE rows of the same type"  
    clean + flagged → taller table   


Day 55 Summary    
    | Concept | What you learned |
|---------|-----------------|
| Multi-key merge | on=['col1', 'col2'] — both must match |
| reset_index() | Pull groupby keys back to regular columns |
| Chained merges | .merge(...).merge(...) — no temp variables |
| Column name collisions | _x/_y is a code smell — rename before merging |
| suffixes= | Quick fix, but rename is better |
| pd.concat() | Stack DataFrames vertically |
| ignore_index=True | Fresh 0-N index, no duplicates |
| .assign(source='tag') | Tag rows before concat for traceability |
| Merge vs Concat | Columns vs rows — different jobs |       

===================DAY 56 - PIVOT TABLES===================================

You already know groupby — it's powerful, but it produces long output. 
One column for the group, one for the value. 
Pivot tables give you wide output — groups become column headers,
making it easy to compare across categories at a glance.  

Think Excel pivot tables, but in code.
— groups become column headers

LONG (groupby)                    WIDE (pivot table)
| currency | status  | count |    | currency | CLEAN | FLAGGED |
|----------|---------|-------|    |----------|-------|---------|
| EUR      | CLEAN   | 17    |    | EUR      | 17    | 27      |
| EUR      | FLAGGED | 27    |    | GBP      | 19    | 28      |
| GBP      | CLEAN   | 19    |    | JPY      | 21    | 37      |
| GBP      | FLAGGED | 28    |    | USD      | 15    | 36      |
| JPY      | CLEAN   | 21    |
| JPY      | FLAGGED | 37    |
| USD      | CLEAN   | 15    |
| USD      | FLAGGED | 36    |
                               
| Parameter | Meaning                    | Analogy |
|-----------|---------|---------|
| values  | "What am I counting/summing?" | The data |
| index   | "What goes on the rows?"      | Row headers |
| columns | "What goes across the top?"   | Column headers |
| aggfunc | "How to combine?"             | sum, mean, count, etc. |     

CLEAN is always 0.0 — obvious, but confirms the data makes sense
GBP flagged = 2.39 — worst performer, when GBP breaks it breaks hard
Overall flagged = 1.85 — the average flagged transaction has almost 2 errors
Overall overall = 1.18 — across all 200 transactions, about 1.2 errors each
Bottom-right corner (1.18) — the single number summary of your entire pipeline    


Why multi-level columns appear                                                                                                                                                
                                                                                                                                                                                
  Single aggfunc='mean'                                                                                                                                                         
                                                                                                                                                                                
  When you pass one function, pandas knows there's only one aggregation. It uses the columns values directly as headers — no ambiguity:                                         
                                                                                                                                                                                
  validation_status  |  FLAGGED  |  VALID                                                                                                                                       
  currency           |           |                                                                                                                                              
  EUR                |   2.5     |  1.0
  USD                |   3.0     |  1.5                                                                                                                                         
                                                                                                                                                                                
  Each column header = just the validation_status value. Clean, flat.                                                                                                           
                                                                                                                                                                                
  ---                                                                                                                                                                           
  List aggfunc=['count', 'mean']
                                
  When you pass multiple functions, each cell now needs two numbers instead of one. Pandas can't fit both into a single column named FLAGGED — so it creates a two-level header
  to label both dimensions:                                                                                                                                                     
   
                    count              mean                                                                                                                                     
  validation_status FLAGGED  VALID    FLAGGED  VALID
  currency
  EUR               1        1        2.5      1.0
  USD               1        2        3.0      1.5                                                                                                                              
                                                                                                                                                                                
  - Level 0 = the aggregation function (count, mean)                                                                                                                            
  - Level 1 = the columns values (FLAGGED, VALID)                                                                                                                               
                                                                                                                                                                                
  This is called a MultiIndex on the columns axis.                                                                                                                              
   
  ---                                                                                                                                                                           
  The key insight 
                 
  ┌───────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┐
  │       What you pass       │                                  What pandas does                                   │                                                           
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ aggfunc='mean'            │ One result per cell → flat columns (just validation_status values)                  │                                                           
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ aggfunc=['count', 'mean'] │ Two results per cell → MultiIndex columns (function name + validation_status value) │                                                           
  └───────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────┘                                                           
                                                                                                                                                                                
  Pandas has to add the extra level because otherwise it'd have two columns both named FLAGGED — which is invalid.                                                              
                  
  ---                                                                                                                                                                           
  Accessing MultiIndex columns

  pivot['count']           # all "count" columns → flat DataFrame
  pivot['count']['FLAGGED'] # count for FLAGGED only → Series  
  
  ggfunc as a dict — different function per column                        
                                                                           
  What's different here                                                                                                                                                         
                                                                                                                                                                                
  No columns= argument this time. So instead of spreading values across a 2D grid, this just aggregates each values column separately per index group — like a groupby().agg(). 
                                                                                                                                                                                
  ---                                                                                                                                                                           
  The arguments   

  ┌──────────┬──────────────────────────────────────┬──────────────────────────────────────────┐
  │ Argument │                Value                 │                 Meaning                  │
  ├──────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
  │ values   │ ['error_count', 'tolerance_percent'] │ Two columns to aggregate                 │
  ├──────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
  │ index    │ 'currency'                           │ Group rows by currency                   │                                                                                
  ├──────────┼──────────────────────────────────────┼──────────────────────────────────────────┤
  │ aggfunc  │ {col: func, ...}                     │ Apply a specific function to each column │                                                                                
  └──────────┴──────────────────────────────────────┴──────────────────────────────────────────┘                                                                                
   
  ---                                                                                                                                                                           
  Why a dict for aggfunc?
                                                                                                                                                                                
  The dict lets you say: "use mean for error_count, but use something else for tolerance_percent."
                                                                                                                                                                                
  In your case both use 'mean', but the power is when they differ:                                                                                                              
                                                                                                                                                                                
  aggfunc={                                                                                                                                                                     
      'error_count': 'sum',        # total errors per currency
      'tolerance_percent': 'mean'  # average tolerance per currency                                                                                                             
  }
                                                                                                                                                                                
  If you wrote aggfunc='mean' instead, it would apply mean to both — same result here, but less explicit and less flexible.                                                     
   
  ---                                                                                                                                                                           
  Concrete example

  Source report:

  ┌──────────┬─────────────┬───────────────────┐                                                                                                                                
  │ currency │ error_count │ tolerance_percent │
  ├──────────┼─────────────┼───────────────────┤                                                                                                                                
  │ USD      │ 2           │ 0.05              │
  ├──────────┼─────────────┼───────────────────┤
  │ USD      │ 4           │ 0.10              │
  ├──────────┼─────────────┼───────────────────┤
  │ EUR      │ 1           │ 0.03              │
  ├──────────┼─────────────┼───────────────────┤                                                                                                                                
  │ EUR      │ 3           │ 0.07              │
  └──────────┴─────────────┴───────────────────┘                                                                                                                                
                  
  Result:

  ┌──────────┬─────────────┬───────────────────┐
  │ currency │ error_count │ tolerance_percent │
  ├──────────┼─────────────┼───────────────────┤
  │ EUR      │ 2.00        │ 0.05              │
  ├──────────┼─────────────┼───────────────────┤
  │ USD      │ 3.00        │ 0.08              │                                                                                                                                
  └──────────┴─────────────┴───────────────────┘
                                                                                                                                                                                
  Each row = one currency. Each cell = mean of that column for that currency group.                                                                                             
   
  ---                                                                                                                                                                           
  .round(2) at the end
                      
  Just rounds every value to 2 decimal places — purely cosmetic for display.
                                                                                                                                                                                
  ---
  Mental model                                                                                                                                                                  
                  
  ▎ dict aggfunc = "per-column instructions". The key is the column name, the value is what to do with it.
  
  So when do you pick one over the other?
```
| Feature | groupby | pivot_table |
|---------|---------|-------------|
| Output shape | Long (one row per group) | Wide (groups become columns) |
| margins/totals | Manual calculation | Built-in (margins=True) |
| Multiple aggfuncs | Named agg tuples | List or dict |
| Best for | Further analysis in code | Reports and visual comparison |
| Readability | Good for machines | Good for humans |
```

Think of it this way: **groupby for computing, pivot_table for presenting**. If you're feeding the result into another calculation, groupby. If someone's going to *look at it*, pivot table.

---

### Day 56 Summary
```
| Concept | What you learned |
|---------|-----------------|
| pd.pivot_table() | Long → wide format for readable summaries |
| values= | What to aggregate |
| index= | Row headers |
| columns= | Column headers (the "pivot" part) |
| aggfunc= | How to combine — string, list, or dict |
| margins=True | Adds totals row and column |
| Multi-level columns | Multiple aggfuncs create stacked headers |
| Column flattening | '_'.join(col) to fix multi-level names |
| aggfunc as dict | Different functions for differe<br/>nt columns |
| Pivot vs GroupBy | Presenting vs computing |                         

groupby vs pivot_table — when to pick which                                                                                                                                   
                                                                                                                                                                                
  Simple rule                                                                                                                                                                   
                                                                                                                                                                                
  ┌─────────────┬───────────────────────────────────────────────────────────────┐                                                                                               
  │     Use     │                         When you want                         │                                                                                               
  ├─────────────┼───────────────────────────────────────────────────────────────┤                                                                                               
  │ groupby     │ A list/Series result — one aggregation per group              │
  ├─────────────┼───────────────────────────────────────────────────────────────┤
  │ pivot_table │ A 2D grid result — groups spread across both rows AND columns │                                                                                               
  └─────────────┴───────────────────────────────────────────────────────────────┘    
  
  Pick groupby when
                   
  You're aggregating along one dimension — the result is a flat table:
                                                                                                                                                                                
  report.groupby('currency')['error_count'].mean()
  # currency                                                                                                                                                                    
  # EUR    2.0    
  # USD    3.0                                                                                                                                                                  
                  
  One axis, one question: "what's the average error count per currency?"   
  
  Pick pivot_table when
                                                                                                                                                                                
  You need to cross two categorical columns — one becomes rows, one becomes columns:
                                                                                                                                                                                
  pd.pivot_table(report, values='error_count',
                 index='currency', columns='validation_status', aggfunc='count')                                                                                                
  # validation_status  FLAGGED  VALID                                                                                                                                           
  # currency
  # EUR                1        1                                                                                                                                               
  # USD                1        2

  Two axes, one question: "how are errors distributed across currency AND status?"    

Ask yourself: do I need columns to represent a category?
                                                                                                                                                                                
  - No → groupby                                                                                                                                                                
  - Yes → pivot_table                                                                                                                                                           
                                                                                                                                                                                
  ---             
  One more signal
                 
  If you find yourself doing groupby → unstack(), that's a sign you actually wanted pivot_table from the start — they produce the same result, but pivot_table is more readable
  for that shape.                                                                                                                                                               
   
  # These are equivalent:                                                                                                                                                       
  report.groupby(['currency', 'validation_status'])['error_count'].count().unstack()                                                                                            
  pd.pivot_table(report, values='error_count', index='currency', columns='validation_status', aggfunc='count')

========================= Day 57 — Melt & Stack/Unstack. ============================= wide → long

WIDE (your data now)                    LONG (after melt)
| txn_id | app_country | ben_country |  | txn_id | party_role | country |
|--------|-------------|-------------|  |--------|------------|---------|
| LC-001 | US          | JP          |  | LC-001 | applicant  | US      |
| LC-002 | DE          | GB          |  | LC-001 | beneficiary| JP      |
                                        | LC-002 | applicant  | DE      |
                                        | LC-002 | beneficiary| GB      |


| Parameter   | Meaning                                                   | Your value |
|-------------|-----------------------------------------------------------|------------|
| id_vars     | "Keep these columns as-is"                                | transaction_id |
| value_vars  | "Stack THESE columns into rows"                           | the two country columns |
| var_name    | "Name for the column that says WHICH column it came from" | party_role |
| value_name  | "Name for the actual values"                              | country |

  
| Parameter | Think of it as... |
|-----------|-------------------|
| id_vars | "My row identifier — DON'T touch this" |
| value_vars | "The specific columns I want to stack" |

 The full picture

  long format (one row per party_role+country combo)
      ↓  groupby + size       → count occurrences                                                                                                                               
      ↓  reset_index          → flat DataFrame                                                                                                                                  
      ↓  pivot_table          → wide format (countries as rows, roles as columns)                                                                                               
      ↓  sort_values          → ranked by applicant count                                                                                                                       
                                                                                                                                                                                
  ---                                                                                                                                                                           
  Why groupby().size() first, then pivot_table?
                                                                                                                                                                                
  pivot_table can do the counting itself with aggfunc='count' — but only if your source data has a column to count. Here countries_long is likely in long format (one row per
  transaction), so groupby().size() first gives you an explicit count column that pivot_table can then simply reshape — no re-aggregation needed.                               
        
## =========== reset_index() — MultiIndex Series → DataFrame ============     

  What .size() actually returns                                                                                                                                                 
                                                                                                                                                                                
  After groupby(['party_role', 'country']).size() you get a Series with a MultiIndex (two levels of index):
  
  s = countries_long.groupby(['party_role', 'country']).size()                                                                                                                  
  print(s)        
                                                                                                                                                                                
  # party_role   country
  # applicant    UAE        5                                                                                                                                                   
  #              USA        3
  # beneficiary  UAE        2
  #              USA        4


  This is a Series. The "rows" are identified by two labels (party_role + country) — that's the MultiIndex. The values are the counts.   
  
 * What reset_index() does
                         
  It promotes the index levels into regular columns, turning the Series into a DataFrame:
                                                                                                                                                                                
  s.reset_index()
                                                                                                                                                                                
      party_role  country  0
  0   applicant   UAE      5                                                                                                                                                    
  1   applicant   USA      3                                                                                                                                                    
  2   beneficiary UAE      2
  3   beneficiary USA      4                                                                                                                                                    
                  
  The count column is named 0 by default (ugly). So you use name='count' to rename it:                                                                                          
   
  s.reset_index(name='count')                                                                                                                                                   
                  
      party_role  country  count
  0   applicant   UAE      5
  1   applicant   USA      3
  2   beneficiary UAE      2                                                                                                                                                    
  3   beneficiary USA      4
  
  Simpler example to build the intuition
                                                                                                                                                                                
  import pandas as pd
                                                                                                                                                                                
  s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
  print(s)
  # a    10
  # b    20
  # c    30                                                                                                                                                                     
   
  s.reset_index()                                                                                                                                                               
  #   index   0   
  # 0     a  10
  # 1     b  20
  # 2     c  30                                                                                                                                                                 
   
  The index a, b, c became a column called index. The values became a column called 0.                                                                                          
                  
  ---                                                                                                                                                                           
  With MultiIndex (exactly your case)
                                                                                                                                                                                
  s = pd.Series([5, 3, 2, 4],
                index=pd.MultiIndex.from_tuples(                                                                                                                                
                    [('applicant', 'UAE'), ('applicant', 'USA'),
                     ('beneficiary', 'UAE'), ('beneficiary', 'USA')],                                                                                                           
                    names=['party_role', 'country']
                ))                                                                                                                                                              
   
  print(s)                                                                                                                                                                      
  # party_role   country
  # applicant    UAE    5
  #              USA    3
  # beneficiary  UAE    2
  #              USA    4
                                                                                                                                                                                
  s.reset_index(name='count')
  #    party_role  country  count                                                                                                                                               
  # 0   applicant      UAE      5
  # 1   applicant      USA      3
  # 2 beneficiary      UAE      2
  # 3 beneficiary      USA      4
                                                                                                                                                                                
  Each index level becomes its own column. The Series values become the count column.                                                                                           
                                                                                                                                                                                
  ---                                                                                                                                                                           
  Mental model    
              
  ▎ reset_index() = "stop using labels as the identity of rows — move them into the table as regular columns, 
  and give me a plain 0,1,2... integer index instead."
  
WIDE → LONG                    LONG → WIDE
┌─────────────┐               ┌─────────────┐
│   melt()    │  regular cols │ pivot_table()│
│   stack()   │  index-based  │ unstack()    │
└─────────────┘               └─────────────┘

| Tool | Works on | Direction | Returns |
|------|----------|-----------|---------|
| melt() | Regular columns | Wide → Long | DataFrame |
| stack() | Column headers → index | Wide → Long | Series (usually) |
| pivot_table() | Values → column headers | Long → Wide | DataFrame |
| unstack() | Index → column headers | Long → Wide | DataFrame |

| Situation | Use |
|-----------|-----|
| "I have applicant_X and beneficiary_X columns, combine them" | melt() |
| "I have a pivot table, make it long for groupby" | stack() |
| "I want a summary table with groups as columns" | pivot_table() |
| "I have a MultiIndex, pull a level to columns" | unstack() |

| Concept | What you learned |
|---------|-----------------|
| pd.melt() | Stack specific columns into rows (wide → long) |
| id_vars | Columns to keep as identifiers |
| value_vars | Columns to stack into rows |
| var_name / value_name | Name the new columns |
| id_vars vs value_vars | Swap them and you get 9400 rows of chaos 😅 |
| .stack() | Column headers → index level (wide → long) |
| .unstack() | Index level → column headers (long → wide) |
| melt → groupby → pivot | Full circle: reshape, analyze, reshape back |
| Trade insight | US = net importer, GB/TW = net exporters |

# ==================  Day 58 is Apply & Map — custom transformations on rows, columns, and cells==============

| Tool | You already used it when... |
|------|----------------------------|
| .map(dict) | Mapping error codes → severity in Challenge 1 |
| .apply(lambda) | Inside .agg() lambdas for the risk summary |

Today we formalize them. There are three tools, and they work at different levels:
| Method | Works on | Input → Output |
|--------|----------|----------------|
| .map() | Single column (Series) | One value → one value |
| .apply() on Series | Single column | One value → one value |
| .apply() on DataFrame | Rows or columns | One row/column → one value |

.map() = a stamp machine. Takes one item, stamps it, returns one item. Fast, simple.
.apply() = a human worker. Can do anything — complex logic, multiple checks, conditionals. Flexible but slower.

* .map(dict) under the hood                                                                                                                                                   
                                                                                                                                                                                
  What it does                                                                                                                                                                  
                                                                                                                                                                                
  For each value in the Series, it does a dictionary lookup — replaces the value with whatever the dict maps it to.                                                             
                                                                                                                                                                              
  severity_map = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'NONE': 0}                                                                                                   
  report['severity'].map(severity_map)

  Internally, for each row it does exactly this:                                                                                                                                
   
  severity_map['CRITICAL']  # → 4                                                                                                                                               
  severity_map['HIGH']      # → 3
  severity_map['LOW']       # → 1

 What happens if a value is NOT in the dict?
                                                                                                                                                                                
  It becomes NaN — no error, just a missing value:
                                                                                                                                                                                
  severity_map = {'CRITICAL': 4, 'HIGH': 3}
                                                                                                                                                                                
  s = pd.Series(['CRITICAL', 'HIGH', 'UNKNOWN'])
  s.map(severity_map)                                                                                                                                                           
  # 0    4.0      
  # 1    3.0                                                                                                                                                                    
  # 2    NaN   ← not in dict
                                                                                                                                                                                
  ---             
  .map(dict) vs .map(function)
                                                                                                                                                                                
  .map() also accepts a function:
                                                                                                                                                                                
  s.map(lambda x: x.lower())   # applies function to each value
  s.map({'A': 1, 'B': 2})      # dict lookup for each value                                                                                                                     
                                                                                                                                                                                
  Same method, two modes. Dict mode is just a lookup table.                                                                                                                     
                                                                                                                                                                                
  ---                                                                                                                                                                           
  Mental model    
              
  ▎ .map(dict) = "for every value in this column, look it up in the dict and replace it with what you find."
  
  - x = 0 → "x is assigned 0" or "x gets 0"                                                                                                                                     
  - x == 0 → "x equals 0" or "x is equal to 0"
                                                                                                                                                                                
  The key word that distinguishes them out loud:                                                                                                                                
                                                                                                                                                                                
  ┌────────┬─────────────────────────────────┐                                                                                                                                  
  │ Symbol │               Say               │
  ├────────┼─────────────────────────────────┤
  │ =      │ "is assigned", "gets", "set to" │
  ├────────┼─────────────────────────────────┤
  │ ==     │ "equals", "is equal to"         │                                                                                                                                  
  └────────┴─────────────────────────────────┘         
  
| Logic complexity | Use |
|-----------------|-----|
| Direct lookup (A→1, B→2) | .map(dict) |
| Simple one-liner | .map(lambda x: ...) |
| Multi-line if/elif/else | .apply(named_function) |

.apply() — what it does
                                                                                                                                                                                
  .apply(func) calls the function once for each value in the Series, and collects the results into a new Series.                                                                
                                                                                                                                                                                
  ---                                                                                                                                                                           
  What happens row by row                                                                                                                                                     
                                                                                                                                                                                
  report['error_count']  →  [0, 1, 5, 3, 0, 2, ...]
                                                                                                                                                                                
  # apply calls classify_risk on each value:                                                                                                                                    
  classify_risk(0)  → 'no_risk'                                                                                                                                                 
  classify_risk(1)  → 'low_risk'                                                                                                                                                
  classify_risk(5)  → 'high_risk'
  classify_risk(3)  → 'medium_risk'                                                                                                                                             
  classify_risk(0)  → 'no_risk'
  classify_risk(2)  → 'low_risk'                                                                                                                                                
                                                                                                                                                                                
  # result:
  report['risk_level']  →  ['no_risk', 'low_risk', 'high_risk', 'medium_risk', 'no_risk', 'low_risk', ...]                                                                      
                                                                                                                                                                                
  ---
  So yes — it just calls the function                                                                                                                                           
                                     
  But specifically:
  - calls it once per value                                                                                                                                                     
  - passes the value as the argument
  - collects all return values into a new Series                                                                                                                                
                                                                                                                                                                                
  ---
  .apply() vs .map()                                                                                                                                                            
                  
  They feel similar but:                                                                                                                                                        
                  
  ┌────────────────┬────────────────────────────────┬──────────────────────────────────────────┐                                                                                
  │                │             .map()             │                 .apply()                 │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────────────┤                                                                                
  │ Works with     │ dict, Series, function         │ function only                            │
  ├────────────────┼────────────────────────────────┼──────────────────────────────────────────┤
  │ Typical use    │ simple lookup / transformation │ custom logic too complex for a one-liner │                                                                                
  ├────────────────┼────────────────────────────────┼──────────────────────────────────────────┤                                                                                
  │ On a Series    │ yes                            │ yes                                      │                                                                                
  ├────────────────┼────────────────────────────────┼──────────────────────────────────────────┤                                                                                
  │ On a DataFrame │ no                             │ yes (row or column wise)                 │
  └────────────────┴────────────────────────────────┴──────────────────────────────────────────┘                                                                                
                  
  In practice: use .map() for simple replacements, .apply() when you need a full function like classify_risk.                                                                   
                  
  ---                                                                                                                                                                           
  Mental model    
              
  ▎ .apply(func) = "run this function on every value in the column, give me back the results as a new column."
  

===== Vectorized vs Non-Vectorized===================

np.where() vs .apply()
                                                                                                                                                                  
  What np.where() does                                                                                                                                            
                                                                                                                                                                  
  np.where(condition, value_if_true, value_if_false)                                                                                                              
                                                                                                                                                                  
  It's a vectorized if/else — instead of looping row by row, it evaluates the condition on the entire column at once.                                             
                                                                                                                                                                  
  np.where(                                                                                                                                                       
      report['validation_status'] == 'CLEAN',   # condition  (True/False for every row)
      report['currency'] + ' transaction - clean',        # use this if True                                                                                      
      report['currency'] + ' transaction - ...'           # use this if False                                                                                     
  )                                                                                                                                                               
                                                                                                                                                                  
  Pandas evaluates all three arguments simultaneously across all rows — no looping.                                                                               
   
  ---                                                                                                                                                             
  Side-by-side comparison
                                                                                                                                                                  
  ┌──────────────┬────────────────────────────────────────────────────┬─────────────────────────────────────┐
  │              │                      .apply()                      │             np.where()              │
  ├──────────────┼────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ How it works │ Calls your function once per row                   │ Operates on whole columns at once   │
  ├──────────────┼────────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ Speed        │ Slower (Python loop under the hood)                │ Much faster (C loop under the hood) │                                                     
  ├──────────────┼────────────────────────────────────────────────────┼─────────────────────────────────────┤                                                     
  │ Readability  │ Very readable, feels like normal Python            │ Gets messy with complex logic       │                                                     
  ├──────────────┼────────────────────────────────────────────────────┼─────────────────────────────────────┤                                                     
  │ Best for     │ Complex logic, multiple conditions, custom objects │ Simple if/else on column values     │
  └──────────────┴────────────────────────────────────────────────────┴─────────────────────────────────────┘                                                     
                  
  ---                                                                                                                                                             
  When to use which
                   
  Use np.where() when your logic is a simple true/false split on column values:
  np.where(df['amount'] > 1000, 'high', 'low')                                                                                                                    
                                              
  Use .apply() when your logic is complex — multiple conditions, helper variables, hard to express as a one-liner:                                                
  # Your transaction_summary needed status + currency + errors + severity                                                                                         
  # np.where would've been one giant unreadable line                     
  report.apply(transaction_summary, axis=1)                                                                                                                       
                                                                                                                                                                  
  ---                                                                                                                                                             
  The key insight                                                                                                                                                 
                                                                                                                                                                  
  np.where() evaluates all three arguments before checking the condition — the true-branch and false-branch are both computed for every row, then it picks which
  to use.                                                                                                                                                         
   
  That's why it's fast — but it also means you can't use it when the false-branch would crash on certain rows (e.g. dividing by zero), because it computes that   
  branch even for rows where the condition is True.
                                                                                                                                                                  
❯ what is can u ewxplain more by saying ' It's a vectorized if/else — instead of looping row by row ' what is vectorized ?                                        
                                                                                                                           
● What "Vectorized" Means                                                                                                                                         
                                                                                                                                                                
  The non-vectorized way (what Python normally does)                                                                                                              
   
  Imagine you have 200 transactions and want to add 10 to each amount:                                                                                            
                  
  # Python loop — visits each row one at a time                                                                                                                   
  for i in range(len(df)):                                                                                                                                        
      df['amount'][i] = df['amount'][i] + 10
                                                                                                                                                                  
  Step 1 → go to row 0, read value, add 10, write back                                                                                                            
  Step 2 → go to row 1, read value, add 10, write back                                                                                                            
  Step 3 → go to row 2 ...                                                                                                                                        
  ...200 trips total                                                                                                                                              
   
  ---                                                                                                                                                             
  The vectorized way
                    
  df['amount'] = df['amount'] + 10
                                                                                                                                                                  
  Internally this says to the CPU: "here are 200 numbers, here is the instruction (+10), do them all at once."                                                    
                                                                                                                                                                  
  The CPU has special hardware (SIMD instructions) that can literally process multiple values in a single clock cycle — like a stamp that prints 8 numbers at once
   instead of 1.  
                                                                                                                                                                  
  ---             
  A physical analogy
                    
  Imagine stamping 200 envelopes with a date:
                                                                                                                                                                  
  - Non-vectorized = you pick up each envelope, stamp it, put it down, pick up the next one                                                                       
  - Vectorized = you have a machine that stamps 8 envelopes simultaneously in one press                                                                           
                                                                                                                                                                  
  Same result, massively faster.                                                                                                                                  
                                                                                                                                                                  
  ---                                                                                                                                                             
  Why .apply() is NOT vectorized

  report.apply(transaction_summary, axis=1)

  Under the hood pandas is doing:                                                                                                                                 
  for each row:
      call transaction_summary(row)  # Python function call overhead × 200                                                                                        
                                                                          
  It's still a loop — just hidden. Python function calls are expensive compared to raw C operations.                                                              
                                                                                                                                                                  
  ---                                                                                                                                                             
  Why np.where() IS vectorized                                                                                                                                    
                  
  np.where(report['validation_status'] == 'CLEAN', ...)

  NumPy sends the entire column (200 values) to a C function that processes them all in one shot — no Python function call per row, no loop visible or hidden.    
   
  ---                                                                                                                                                             
  The practical takeaway
                        
  ┌─────────────────────────────┬───────────────────────────────────────┐
  │            Code             │      What's happening underneath      │                                                                                         
  ├─────────────────────────────┼───────────────────────────────────────┤
  │ df['a'] + df['b']           │ Vectorized — C loop, very fast        │                                                                                         
  ├─────────────────────────────┼───────────────────────────────────────┤
  │ np.where(...)               │ Vectorized — C loop, very fast        │                                                                                         
  ├─────────────────────────────┼───────────────────────────────────────┤
  │ df.apply(fn, axis=1)        │ Not vectorized — Python loop, slower  │                                                                                         
  ├─────────────────────────────┼───────────────────────────────────────┤                                                                                         
  │ for i, row in df.iterrows() │ Not vectorized — Python loop, slowest │
  └─────────────────────────────┴───────────────────────────────────────┘                                                                                         
                  
  For 200 rows you'll never notice the difference. With 2 million rows, vectorized operations can be 10-100x faster.
  
 np.select() — Multiple Conditions
                                                                                                                                                                  
  The signature                                                                                                                                                   
                                                                                                                                                                  
  np.select(conditions, choices, default)                                                                                                                         
                                                                                                                                                                  
  It's like np.where() but for more than two outcomes — a vectorized if/elif/elif/else.                                                                           
                                                                                                                                                                  
  ---                                                                                                                                                             
  How it evaluates — row by row mentally
                                                                                                                                                                  
  For each row, it checks conditions in order, and uses the first one that is True:
                                                                                                                                                                  
  error_count == 0  → True?  use 'no_risk'    ✓ stop here                                                                                                         
  error_count <= 2  → True?  use 'low_risk'   ✓ stop here                                                                                                         
  error_count <= 4  → True?  use 'medium_risk'✓ stop here                                                                                                         
  none matched?     →        use default 'high_risk'                                                                                                              
                                                                                                                                                                  
  ---                                                                                                                                                             
  What happens when error_count = 5                                                                                                                               
                  
  error_count == 0  → 5 == 0  → False  ✗
  error_count <= 2  → 5 <= 2  → False  ✗                                                                                                                          
  error_count <= 4  → 5 <= 4  → False  ✗
  no condition matched → use default → 'high_risk'                                                                                                                
                  
  That's exactly why default='high_risk' exists — it's the catch-all for anything that didn't match any condition. Without it, numpy would fill unmatched rows    
  with 0 (its default default).
                                                                                                                                                                  
  ---             
  Equivalent plain Python
                                                                                                                                                                  
  if error_count == 0:
      return 'no_risk'                                                                                                                                            
  elif error_count <= 2:
      return 'low_risk'
  elif error_count <= 4:
      return 'medium_risk'
  else:                                                                                                                                                           
      return 'high_risk'   # ← this is the default
                                                                                                                                                                  
  default is literally the else branch.                                                                                                                           
   
  ---                                                                                                                                                             
  Quick comparison of the three
                                                                                                                                                                  
  ┌───────────────┬────────────────────────┬──────────────────────────────────────────────┐
  │               │       np.where()       │                 np.select()                  │                                                                       
  ├───────────────┼────────────────────────┼──────────────────────────────────────────────┤
  │ Outcomes      │ 2 (true/false)         │ Many                                         │
  ├───────────────┼────────────────────────┼──────────────────────────────────────────────┤
  │ Structure     │ condition, true, false │ list of conditions, list of choices, default │                                                                       
  ├───────────────┼────────────────────────┼──────────────────────────────────────────────┤                                                                       
  │ Equivalent to │ if/else                │ if/elif/elif/else                            │                                                                       
  └───────────────┴────────────────────────┴──────────────────────────────────────────────┘                                                                       
  
* Day 58 Summary         

| Tool | Works on | Best for | Speed |
|------|----------|----------|-------|
| .map(dict) | Series | Finite lookups (A→1, B→2) | Fast |
| .map(function) | Series | Simple transforms (str.lower) | Fast |
| .map(lambda) | Series | Quick one-liners | Fast |
| .apply(func) on Series | Series | Multi-line if/elif logic | Medium |
| .apply(func, axis=1) | DataFrame rows | Complex logic needing multiple columns | Slow |
| np.where() | DataFrame columns | Simple if/else | Very fast |
| np.select() | DataFrame columns | Multiple conditions | Very fast |

Need to transform values?
├── One column?
│   ├── Direct lookup? → .map(dict)
│   ├── Simple one-liner? → .map(lambda)
│   └── Complex logic? → .apply(named_function)
└── Multiple columns?
    ├── Simple if/else? → np.where()
    ├── Multiple conditions? → np.select()
    └── Really complex logic? → .apply(axis=1)

Principle: always try vectorized first (np.where, np.select). 
Only fall back to .apply(axis=1) when the logic is truly too complex to express in conditions.
On 200 rows it doesn't matter, but building the right habit now means you won't hit a wall at 2 million rows later.


==========================DAY 59 MULTI_INDEX=======================================

 MultiIndex — What It Is and Why It Exists
                                                                                                                                                                  
  What happened                                                                                                                                                   
                                                                                                                                                                  
  You grouped by two columns — currency and validation_status. The result has a row for every unique combination of the two:                                      
                  
  EUR + CLEAN                                                                                                                                                     
  EUR + FLAGGED   
  GBP + CLEAN
  ...                                                                                                                                                             
   
  A regular index is one label per row. A MultiIndex is two (or more) labels per row — one per groupby level.                                                     
                  
  ---                                                                                                                                                             
  Visualizing it  
                                                                                                                                                                  
                            count   mean
  currency  validation_status                                                                                                                                     
  EUR       CLEAN              12   0.00
            FLAGGED             8   2.50                                                                                                                          
  GBP       CLEAN              15   0.00                                                                                                                          
            FLAGGED             5   3.10
  ...                                                                                                                                                             
                  
  Notice EUR only appears once on the left — it "spans" both its rows. That's the MultiIndex visually. Each row is identified by a tuple: ('EUR', 'CLEAN'),       
  ('EUR', 'FLAGGED'), etc.
                                                                                                                                                                  
  ---             
  The tuple connection
                                                                                                                                                                  
  MultiIndex([('EUR',   'CLEAN'),
              ('EUR', 'FLAGGED'),                                                                                                                                 
              ... 
             names=['currency', 'validation_status'])
                                                                                                                                                                  
  Each entry in the index is literally a tuple — (currency_value, validation_status_value). The names tell you what each position in the tuple represents.        
                                                                                                                                                                  
  ---                                                                                                                                                             
  Why pandas creates it
                       
  When you group by one column → one label needed per row → regular Index
  When you group by two columns → two labels needed per row → MultiIndex                                                                                          
                                                                                                                                                                  
  It's pandas' way of saying "this row belongs to EUR AND CLEAN simultaneously".                                                                                  
                                                                                                                                                                  
  ---                                                                                                                                                             
  Accessing rows in a MultiIndex

  multi.loc['EUR']                    # all EUR rows
  multi.loc[('EUR', 'CLEAN')]         # exactly EUR + CLEAN row                                                                                                   
  multi.loc[('EUR', 'CLEAN'), 'mean'] # one specific value                                                                                                        
                                                                                                                                                                  
  ---                                                                                                                                                             
  Flattening it (when MultiIndex is inconvenient)                                                                                                                 
                  
  multi.reset_index()
                                                                                                                                                                  
  This turns the MultiIndex back into regular columns — currency and validation_status become normal DataFrame columns again. Often easier to work with           
  downstream.
  
 * loc[] with a MultiIndex                                                                                                                                         
                                                                                                                                                                
  Regular Index — you already know this                                                                                                                           
   
  df.loc[3]          # row where index == 3                                                                                                                       
  df.loc['EUR']      # row where index == 'EUR'                                                                                                                   
                                                                                                                                                                  
  One value → finds one row.                                                                                                                                      
                                                                                                                                                                  
  ---                                                                                                                                                             
  MultiIndex — you need a tuple to be specific
                                                                                                                                                                  
  With a MultiIndex, each row has two labels. So loc[] accepts a tuple to match both levels:
                                                                                                                                                                  
  multi.loc['EUR']                 # all rows where currency == 'EUR'
  multi.loc[('EUR', 'CLEAN')]      # exact row: EUR + CLEAN                                                                                                       
  multi.loc[('EUR', 'CLEAN'), 'mean']  # EUR + CLEAN row, only the 'mean' column                                                                                  
                                                                                                                                                                  
  ---                                                                                                                                                             
  Visualizing what each returns                                                                                                                                   
                               
  Given this MultiIndex DataFrame:
                                                                                                                                                                  
                                  count   mean
  currency  validation_status                                                                                                                                     
  EUR       CLEAN                  12    0.00
            FLAGGED                 8    2.50
  GBP       CLEAN                  15    0.00                                                                                                                     
            FLAGGED                 5    3.10
                                                                                                                                                                  
  multi.loc['EUR']
  # returns:
  #                    count  mean                                                                                                                                
  # validation_status
  # CLEAN                 12  0.00                                                                                                                                
  # FLAGGED                8  2.50                                                                                                                                
   
  multi.loc[('EUR', 'CLEAN')]                                                                                                                                     
  # returns:      
  # count    12.00
  # mean      0.00                                                                                                                                                
   
  multi.loc[('EUR', 'CLEAN'), 'mean']                                                                                                                             
  # returns:                                                                                                                                                      
  # 0.0
                                                                                                                                                                  
  ---             
  The rule
          
  ┌──────────────────────────┬──────────────────────────────────┐
  │  What you pass to loc[]  │           What you get           │                                                                                                 
  ├──────────────────────────┼──────────────────────────────────┤
  │ 'EUR'                    │ All rows matching level 0        │                                                                                                 
  ├──────────────────────────┼──────────────────────────────────┤
  │ ('EUR', 'CLEAN')         │ Exact row matching both levels   │                                                                                                 
  ├──────────────────────────┼──────────────────────────────────┤
  │ ('EUR', 'CLEAN'), 'mean' │ One specific value from that row │                                                                                                 
  └──────────────────────────┴──────────────────────────────────┘                                                                                                 
   
  The tuple drills deeper into the MultiIndex, one level at a time.                                                                                               
                  
* xs() — Cross Section                                                                                                                                          
                                                                                                                                                                  
  The problem it solves                                                                                                                                           
                                                                                                                                                                  
  With loc[], slicing by the second level of a MultiIndex is awkward:                                                                                             
                  
  # Getting all FLAGGED rows with loc[] is painful                                                                                                                
  multi.loc[(slice(None), 'FLAGGED'), :]  # ugly, hard to read                                                                                                    
                                                                                                                                                                  
  xs() (cross-section) was made exactly for this — slice by any level cleanly.                                                                                    
                                                                                                                                                                  
  ---                                                                                                                                                             
  Syntax          

  df.xs(key, level='level_name')
                                                                                                                                                                  
  ---
  Your example                                                                                                                                                    
                  
  multi.xs('FLAGGED', level='validation_status')

  "Give me all rows where validation_status == 'FLAGGED', regardless of currency."                                                                                
   
  Result:                                                                                                                                                         
           count  mean
  currency   
  EUR          8  2.50
  GBP          5  3.10                                                                                                                                            
  JPY          6  2.80
  USD          9  3.20                                                                                                                                            
                      
  Notice — the validation_status level disappears from the index. You selected on it, so it's consumed. Only currency remains.                                    
                                                                                                                                                                  
  ---                                                                                                                                                             
  loc[] vs xs() — when to use which                                                                                                                               
                                                                                                                                                                  
  ┌───────────────────────────────────────┬──────────────────────────────────────────────────┐
  │               Scenario                │                       Use                        │                                                                    
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ Slice by the first level              │ loc['EUR'] — simple, familiar                    │
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ Slice by the second (or deeper) level │ xs('FLAGGED', level='validation_status') — clean │                                                                    
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤                                                                    
  │ Slice by both levels (exact row)      │ loc[('EUR', 'CLEAN')]                            │                                                                    
  └───────────────────────────────────────┴──────────────────────────────────────────────────┘                                                                    
                  
  ---                                                                                                                                                             
  One-line summary
                  
  ▎ xs() lets you slice a MultiIndex by any level by name, without needing to know its position.

| Keep MultiIndex when... | Flatten when... |
|------------------------|-----------------|
| You need .xs() slicing | You want to merge with another DataFrame |
| You're doing .unstack() | You want to use query() for filtering |
| The hierarchy helps readability | You're feeding into a chart/export |
| You'll swaplevel() or sort_index() | You just want simple .loc[] access |

| Concept | What you learned |
|---------|-----------------|
| MultiIndex | Two+ levels of row/column labels |
| .loc['EUR'] | Select entire top-level group |
| .loc[('EUR', 'FLAGGED')] | Tuple for specific multi-level selection |
| .xs('FLAGGED', level=) | Cross-section — slice across any level |
| .swaplevel() | Flip the hierarchy |
| .sort_index() | Organize by index values |
| reset_index() | Escape back to flat DataFrame |
| When to use | Keep for slicing/reshaping, flatten for merging/filtering |