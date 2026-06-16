● sys.path is the list of directories Python searches when you do import something.                                             
                                                                                                                              
  By default, it doesn't include the parent directory (..), so if your notebook is at notebooks/02_advanced_pandas.ipynb and you
   try to import config.constants, Python won't find it — it only looks in notebooks/ and standard library locations.           
                                                                                                                                
  sys.path.insert(0, '..') manually adds the parent directory (lc_pipeline/) to the front of that search list, so Python can now
   find your project's modules:                                                                                                 

  notebooks/               ← notebook runs from here
    02_advanced_pandas.ipynb

  lc_pipeline/             ← after insert('..'), Python can now see this level
    config/
      constants.py
    validators/
      ...

  So after those two lines, import config.constants works from inside the notebook.

  The 0 means "insert at the front" — highest priority. If you used append instead, it would be checked last, after all other
  paths.


Tool                                 What it does

shape                                Rows × columns in one tuple
info()                               Dtypes, nulls, memory — health check
describe()                           Statistical snapshot of numerics
nunique()                            Cardinality per columnn
largest()                            Top N rows by a column
value_counts()                      in a loopProfile multiple categoricals fast



  Single [] — gives you a Series                                                                                                
                                                                                                                                
  report['transaction_id']                                                                                                      

  You're passing one string → pandas returns a Series (a single column, like a list with an index):

  0    LC-JZA7TZ
  1    LC-D84U89
  2    LC-CW790P
  ...
  Name: transaction_id, dtype: object

  A Series is 1-dimensional — just values, no table structure.


 Double [[]] — gives you a DataFrame
 
 report[['transaction_id', 'error_count']]

  You're passing a list of strings → pandas returns a DataFrame (a proper table):

    transaction_id  error_count
  0      LC-JZA7TZ            6
  1      LC-D84U89            6
  2      LC-CW790P            5

  A DataFrame is 2-dimensional — rows and columns.
  
df['col']            │ a string               │ a Series (1D)  
df[['col']]          │ a list with one string │ a DataFrame (2D)
df[['col1', 'col2']] │ a list of strings      │ a DataFrame (2D) 



----> can u explain usd_transactions = report[report['currency'] == 'USD']                                                          
                                                                                                                       
● This is called boolean indexing — one of the most important pandas patterns.                                                  
                                                                                                                                
  ---                                                                                                                           
  Break it down inside-out                                                                                                      
                                                                                                                                
  Step 1 — the inner part: report['currency'] == 'USD'                                                                        

  report['currency'] gives you a Series of all currency values:
  0    JPY
  1    USD
  2    GBP
  3    USD
  4    JPY
  ...

  == 'USD' compares every value against 'USD' and returns a boolean Series (True/False for each row):
  0    False
  1     True
  2    False
  3     True
  4    False
  ...
  
  This is called a mask — it marks which rows match your condition.
  
 Step 2 — the outer part: report[mask]
 
 You pass that mask into report[...]. Pandas keeps only the rows where the mask is True:

  transaction_id currency  ...
  1      LC-D84U89      USD
  3      LC-XYZ123      USD
  ...

  
 You can also store the mask separately (more readable)

  is_usd = report['currency'] == 'USD'   # the mask
  usd_transactions = report[is_usd]       # apply it

  Both are identical — the inline version just skips the variable.
  


usd_or_eur = report[report['currency'].isin(['USD', 'EUR'])]

  Step 1 — report['currency']                                                                                                   
                                                                                                                                
  Gets the currency column as a Series:                                                                                         
  0    JPY
  1    USD
  2    GBP
  3    EUR
  4    JPY
  ...

  Step 2 — .isin(['USD', 'EUR'])

  Checks each value: "is this value in my list?" → returns a boolean mask:
  0    False
  1     True   ← USD is in the list
  2    False
  3     True   ← EUR is in the list
  4    False
  ...

  Step 3 — report[mask]

  Keeps only the True rows:
    transaction_id currency
  1      LC-D84U89      USD
  3      LC-XYZ123      EUR
  ...
  
df[df['col'] == 'value'] 

Step 1 — the inner part creates a boolean mask:  
 df['col'] == 'value'                                                                                              
  # Returns a Series of True/False for every row:                                                                   
  # 0    True     
  # 1    False
  # 2    True

Step 2 — the outer df uses that mask to filter rows:
 df[ True/False Series ]
  # Keeps only rows where the mask is True

So df[df['col'] == 'value'] means: "give me the rows of df where col equals value".

  The reason df appears twice is that you're doing both things at once — generating the mask from df, then applying
  it to df. You could also write it as two separate lines:

  mask = df['col'] == 'value'   # Step 1
  result = df[mask]              # Step 2

  Same result, just more explicit.
  

 here are more examples for each:                                              
                                                                                                                  
  ---                                                                                                               
  Boolean Indexing                                                                                                  
  # != (not equal)                                                                                                  
  non_usd = report[report['currency'] != 'USD']                                                                     
                  
  # Multiple conditions — each must be wrapped in ()
  high_error_flagged = report[
      (report['error_count'] > 3) &
      (report['validation_status'] == 'FLAGGED')
  ]

  # OR — either condition is enough
  warn_or_critical = report[
      (report['severity'] == 'WARNING') |
      (report['severity'] == 'CRITICAL')
  ]

  ---
  isin()
  # Exclude a set of values using ~  (tilde = NOT)
  non_major = report[~report['currency'].isin(['USD', 'EUR', 'GBP'])]

  # Works on any column
  problem_severities = report[report['severity'].isin(['WARNING', 'CRITICAL'])]

  ---
  between()
  # error_count between 1 and 3 (inclusive)
  low_error = report[report['error_count'].between(1, 3)]

  # NOT between — use ~ again
  extreme_error = report[~report['error_count'].between(1, 3)]

  ---
  query()
  # Reference a Python variable inside query with @
  min_errors = 2
  result = report.query("error_count > @min_errors and severity == 'CRITICAL'")

  # String contains
  result = report.query("error_codes.str.contains('SWIFT')", engine='python')

  report.query(                                                                                                     
      "error_codes.str.contains('SWIFT')",  # condition                                                             
      engine='python'                        # required for .str methods inside query()
  )

  Why engine='python'?
  By default query() uses a faster engine (numexpr) that doesn't understand .str methods. Switching to
  engine='python' tells pandas to evaluate it as regular Python, which supports .str.

---
  The equivalent without query():
  report[report['error_codes'].str.contains('SWIFT')]

  ---
  More str examples you can use the same way:
  # starts with
  report[report['error_codes'].str.startswith('AMT')]

  # ends with
  report[report['error_codes'].str.endswith('001')]

  # case-insensitive contains
  report[report['error_codes'].str.contains('swift', case=False)]

  # combine with another condition
  report[
      report['error_codes'].str.contains('SWIFT') &
      (report['severity'] == 'CRITICAL')
  ]

  ---
  The ~ (tilde) is worth remembering — it flips any boolean mask, so ~isin() means "not in", ~between() means
  "outside the range".
  
GROUP BY
 GroupBy works in three steps — split, apply, combine:

Split — divide your DataFrame into groups (by currency, by severity, etc.)
Apply — do something to each group (count, sum, mean)
Combine — merge results back into one table


groupby('currency') splits the DataFrame into groups first — one group per unique currency value. Then     
  .mean() operates on each group separately.                                                                                    
                                                                                                                                
  So internally pandas is doing:                                                                                                
                                                                                                                                
  1. Split — find all rows where currency == 'USD', all where currency == 'EUR', etc.                                           
  2. Apply — calculate mean() of error_count within each group
  3. Combine — return one result per group                                                                                      
                                                                                                                                
  USD group: [3, 1, 2]  → mean = 2.0                                                                                            
  EUR group: [2, 4]     → mean = 3.0                                                                                            
  GBP group: [1]        → mean = 1.0                                                                                            
                                                                                                                                
  The "quantity" (how many rows per currency) is implicit — pandas counts the rows in each group automatically to compute the   
  mean. You never have to tell it explicitly.     
  
NESTED GROUP BY 
 Same split-apply-combine, but now pandas splits by two keys — every unique combination of currency + severity.              
                                                                                                                                
  USD + HIGH:   [T001, T005]       → count = 2                                                                                  
  USD + MEDIUM: [T002]             → count = 1                                                                                  
  EUR + HIGH:   [T003, T006, T007] → count = 3                                                                                  
  EUR + LOW:    [T004]             → count = 1                                                                                  
                  
  The result is a MultiIndex Series:                                                                                            
                  
  currency  severity                                                                                                            
  EUR       HIGH      3
            LOW       1
  USD       HIGH      2
            MEDIUM    1

  The indentation shows the hierarchy — EUR has two sub-groups (HIGH, LOW), USD has two sub-groups (HIGH, MEDIUM).              
   
  Think of it like a folder structure:                                                                                          
  EUR/            
    HIGH/   → 3 transactions                                                                                                    
    LOW/    → 1 transaction 
  USD/                                                                                                                          
    HIGH/   → 2 transactions
    MEDIUM/ → 1 transaction                                                                                                     
                           
  Any combination that doesn't exist in the data simply won't appear in the result.                                             
                   
| Method | Counts NaN? | Use when |
|--------|-------------|----------|
| `size()` | Yes | "How many rows in each group?" |
| `count()` | No | "How many non-null values?" |   

 ======= .AGG =======

.agg (aggregate) applies one or more summary functions to a DataFrame or GroupBy object.                        
                                                                                                                    
  Basic usage:                                                                                                      
  df["amount"].agg("sum")          # single function
  df["amount"].agg(["sum", "mean", "max"])  # multiple functions                                                    
                                                                                                                    
  Most useful with groupby:                                                                                         
  df.groupby("currency")["amount"].agg(["sum", "mean", "count"])                                                    
  This gives you a summary row per group (e.g., per currency).                                                      
                                                                                                                    
  Apply different functions to different columns:                                                                   
  df.groupby("currency").agg({                                                                                      
      "amount":   ["sum", "mean"],                                                                                  
      "lc_value": "max"                                                                                             
  })                                                                                                                
                                                                                                                    
  Use a custom function:                                                                                            
  df["amount"].agg(lambda x: x.max() - x.min())  # range                                                            
   
  ---                                                                                                               
  The key idea: .agg reduces many rows down to summary values. It's the pandas equivalent of SQL's SELECT 
  SUM(amount), AVG(amount) FROM ... GROUP BY currency.                                                              
         
## Transform()

  report['currency_avg_errors'] = report.groupby('currency')['error_count'].transform('mean')
  You're adding a new column to report. Since report has N rows, you need N values back — .agg() would give you fewer rows and  
  pandas couldn't align them. .transform() gives you exactly N rows, so the assignment works directly.                          
                                                                                                                                
  Rule of thumb: use .agg() when you want a summary table, use .transform() when you want to add a derived column back onto the 
  original DataFrame.  
  
  ---                                                                                                                           
  Step 1 — Filter rows above their currency average
  above_avg = report[report['error_count'] > report['currency_avg_errors']]                                                     
  Remember from the previous line, currency_avg_errors holds the mean error count for each row's currency group. Here we're
  comparing each row's own error_count against that group mean.                                                                 
                                                                                                                                
  So if USD transactions average 3.0 errors:
  - A USD row with error_count = 5 → included (5 > 3.0)                                                                         
  - A USD row with error_count = 2 → excluded (2 > 3.0 is False)                                                                
                                                                                                                                
  The result above_avg is a filtered DataFrame of only the "worse than average for their currency" transactions.                
                                                                                                                                
  ---                                                                                                                           
  Step 2 — Drop the temporary column                                                                                            
  report.drop(columns='currency_avg_errors', inplace=True)
  currency_avg_errors was only created to enable the filter above — it's not a meaningful output column. So it gets removed
  immediately after use.                                                                                                   
                                                                                                                                
  inplace=True modifies report directly instead of returning a new DataFrame.
                                                                                                                                
  ---             
  The overall pattern: create a helper column → use it → clean it up. This is a common pandas idiom when you need a derived     
  value for a one-time filter but don't want it polluting your final DataFrame.                                                 
   

| Tool | What it does | Size of result |
|------|-------------|----------------|
| `groupby().count()` | Count per group | Reduced (one row per group) |
| `groupby().sum()` | Sum per group | Reduced |
| `groupby().mean()` | Average per group | Reduced |
| `groupby().agg()` | Multiple functions at once | Reduced |
| `groupby().agg(name=(...))` | Named aggregations | Reduced + clean column names |
| `groupby().transform()` | Broadcast result back to every row | Same size as original |
| `groupby().filter()` | Keep/drop entire groups | Same or smaller |
| `size()` vs `count()` | size counts NaN, count skips NaN | Reduced |

## Lambda
 Lambda is just a one-line anonymous function. These two are identical:                                                        
                                                                                                                                
  # Normal function                                                                                                             
  def is_big(g):                                                                                                                
      return len(g) > 50                                                                                                        
                                                                                                                                
  # Lambda equivalent                                                                                                           
  lambda g: len(g) > 50                                                                                                         
                  
  lambda g: — g is the parameter                                                                                                
  len(g) > 50 — the return value (no return keyword needed)
  
  ---
  Simple lambda examples:                                                                                                       
                                                                                                                                
  # Double a number
  double = lambda x: x * 2                                                                                                      
  double(5)  # → 10
                                                                                                                                
  # Add two numbers                                                                                                             
  add = lambda x, y: x + y
  add(3, 4)  # → 7                                                                                                              
                                                                                                                                
  # Check if a string is uppercase
  lambda s: s.isupper()                                                                                                         
                                                                                                                                
  ---                                                                                                                           
  Where lambdas shine — passing a function as an argument:                                                                      
                                                                                                                                
  # sorted() with a key
  words = ["banana", "apple", "kiwi"]                                                                                           
  sorted(words, key=lambda w: len(w))  # → ['kiwi', 'apple', 'banana']                                                          
                                                                                                                                
  # map() — apply to every element                                                                                              
  list(map(lambda x: x ** 2, [1, 2, 3]))  # → [1, 4, 9]
                                                                                                                                
  # filter() — keep elements where True
  list(filter(lambda x: x > 2, [1, 2, 3, 4]))  # → [3, 4]                                                                       
                                                                                                                                
  ---
  Rule of thumb: use a lambda when the function is short and only needed once. If it's longer than one expression or reused,    
  write a proper def — it's more readable.                                                                                      
                                                               
# print(f"Currencies kept: {big_currencies['currency'].unique()}")

 This is an f-string — a way to embed expressions directly inside a string.                                                  
                                                                                                                                
  The f prefix tells Python: anything inside {} is code, evaluate it and insert the result.                                     
                                                                                                                              
  So it's equivalent to:                                                                                                        
  result = big_currencies['currency'].unique()
  print("Currencies kept: " + str(result))   
  
big_currencies -> the filtered DataFrame (only currencies with >50 rows)
 ['currency']  ->  select just the currency column   
 .unique() ->  return an array of distinct values, no duplicates 
  If USD and EUR had >50 rows, output would be:                                                                                 
  Currencies kept: ['USD' 'EUR']



  Output column      │          Source          │ Function │               Meaning                │                             
  ├──────────────────┼──────────────────────────┼──────────┼──────────────────────────────────────┤
  │ total_txn        │ transaction_id           │ count    │ how many transactions per currency   │                             
  ├──────────────────┼──────────────────────────┼──────────┼──────────────────────────────────────┤
  │ total_errors     │ error_count              │ sum      │ total errors across all transactions │                             
  ├──────────────────┼──────────────────────────┼──────────┼──────────────────────────────────────┤
  │ avg_errors       │ error_count              │ mean     │ average errors per transaction       │                             
  ├──────────────────┼──────────────────────────┼──────────┼──────────────────────────────────────┤                             
  │ avg_tolerance    │ tolerance_percent        │ mean     │ average tolerance %                  │
  ├──────────────────┼──────────────────────────┼──────────┼──────────────────────────────────────┤                             
  │ avg_presentation │ presentation_period_days │ mean     │ average presentation days   
  
# What percentage of its currency's errors does each transaction represent?
report['pct_of_currency_errors'] = (
    report['error_count'] /
    report.groupby('currency')['error_count'].transform('sum') * 100
).round(2)

# Show flagged transactions with their percentage
report.query("validation_status == 'FLAGGED'")[
    ['transaction_id', 'currency', 'error_count', 'pct_of_currency_errors']
].nlargest(10, 'error_count')


● Block 1 — Creating the percentage column:

  report['pct_of_currency_errors'] = (                                                                                          
      report['error_count'] /
      report.groupby('currency')['error_count'].transform('sum') * 100                                                          
  ).round(2)                                                                                                                    
   
  Three parts working together:                                                                                                 
                  
  report['error_count'] — each row's individual error count. Say row 0 (USD) has 4 errors.                                      
   
  report.groupby('currency')['error_count'].transform('sum') — total errors for that row's currency group, broadcast back to    
  every row (remember transform keeps original shape). Say all USD rows together have 80 errors total.
                                                                                                                                
  The math:                                                                                                                     
  4 / 80 * 100 = 5.0
  So this USD transaction is responsible for 5% of all USD errors.                                                              
                                                                  
  Every row gets its own percentage relative to its currency group — not relative to the whole dataset.                         
                                                                                                                                
  .round(2) — rounds to 2 decimal places.                                                                                       
                                                                                                                                
  ---             
  Block 2 — Filtering and displaying:
                                                                                                                                
  report.query("validation_status == 'FLAGGED'")
  .query() is just a cleaner way to filter. Equivalent to:                                                                      
  report[report['validation_status'] == 'FLAGGED']                                                                              
                                                  
  [['transaction_id', 'currency', 'error_count', 'pct_of_currency_errors']]                                                     
  Select only these 4 columns — drops everything else from the view.                                                            
                                                                                                                                
  .nlargest(10, 'error_count')                                                                                                  
  Sort by error_count descending and keep only the top 10 rows. Equivalent to:                                                  
  .sort_values('error_count', ascending=False).head(10)                                                                         
           
  ---                                                                                                                           
  Put together — what this answers:                                                                                             
                                                                                                                                
  ▎ "Among flagged transactions, which 10 have the most errors — and how much of their currency's total errors do they account  
  for?"                                                                                                                         
                  
  This is useful for spotting outliers — a transaction with 5% of all USD errors is a much bigger problem than one with 0.1%. 
  
##  why we use [['transaction_id', 'currency', 'error_count', 'pct_of_currency_errors']]  double [] ?                             
                                                                                                    
● The outer [] is the row filter (standard pandas indexing).                                                                    
                                                                                                                              
  The inner [] is a Python list of column names you want to keep.                                                               
                                                                                                                                
  df[ ['col1', 'col2'] ]                                                                                                        
  #  ^                ^  — outer brackets: pandas indexing                                                                      
  #    ^            ^    — inner brackets: Python list                                                                          
                                                                                                                                
  ---                                                                                                                           
  Compare the two:                                                                                                              
                                                                                                                                
  df['currency']          # single [] → returns a Series (one column)
  df[['currency']]        # double [] → returns a DataFrame (one column, but still a table)                                     
                                                                                                                                
  df[['currency', 'error_count']]  # double [] → DataFrame with two columns                                                     
                                                                                                                                
  You need the inner list because pandas indexing accepts either:                                                               
  - a single string → gives you one column as a Series
  - a list of strings → gives you multiple columns as a DataFrame                                                               
                                                                 
  So double [[]] is really just:                                                                                                
  cols = ['transaction_id', 'currency', 'error_count', 'pct_of_currency_errors']                                                
  report.query("...")[cols]                                                     
                                                                                                                                
  The double bracket is just the shorthand for passing that list inline.  

## -> what is inplace ?
 report.drop(columns='pct_of_currency_errors', inplace=True)                                               
                                                     
                                                                                                                                
● inplace=True means modify the original DataFrame directly instead of returning a new one.                                   
                                                                                                                                
  ---                                                                                                                           
  Without inplace (default):                                                                                                    
  report = report.drop(columns='pct_of_currency_errors')  # returns a new DataFrame                                             
                                                                                                                              
  With inplace=True:                                                                                                            
  report.drop(columns='pct_of_currency_errors', inplace=True)  # modifies report directly                                       
                                                                                         
  Both do the same thing — the difference is just whether you get a new object back or mutate the existing one. 

  ---                                                                                                                           
  inplace=True works on many pandas methods:                                                                                    
  df.drop(columns='x', inplace=True)                                                                                            
  df.rename(columns={'old': 'new'}, inplace=True)
  df.sort_values('amount', inplace=True)                                                                                        
  df.reset_index(inplace=True)                                                                                                  
                                                                                                                                
  ---                                                                                                                           
  One thing to know: many experienced pandas users actually avoid inplace=True and prefer the assignment style (report =        
  report.drop(...)) because:                                                                                                    
  - it's easier to chain operations                                                                                             
  - it's clearer what's happening                                                                                               
  - inplace=True doesn't actually save memory (common misconception)                                                            
                                                                                                                                
                                                                                     
                                         
# bucket pd.cut pd.qcut 

● pd.cut() splits a continuous numeric column into discrete buckets (like a histogram).

  ---                                                                                                                           
  bins=[-1, 0, 1, 2, 6]
                                                                                                                                
  Bins define the edges of each bucket. With 4 edges you get 3 intervals... with 5 edges you get 4 buckets:                   
                                                                                                                                
  (-1, 0]  →  'Clean'
   (0, 1]  →  '1 error'                                                                                                         
   (1, 2]  →  '2 errors'                                                                                                        
   (2, 6]  →  '3+ errors'                                                                                                       
                                                                                                                                
  The ( means exclusive (not included), ] means inclusive (included).                                                           
                                                                                                                                
  ---                                                                                                                           
  Why -1 as the first edge?
                                                                                                                                
  Because the default is (left, right] — left side is excluded. If the first bin was (0, 1], a row with error_count = 0 would
  fall outside all bins and become NaN.                                                                                         
                  
  Starting at -1 ensures 0 is captured: (-1, 0] includes 0.                                                                     
                  
  ---                                                                                                                           
  labels — the name assigned to each bucket:
                                                                                                                                
  ┌───────────────────┬──────────────┬─────────────┐
  │ error_count value │ falls in bin │ gets label  │                                                                            
  ├───────────────────┼──────────────┼─────────────┤                                                                            
  │ 0                 │ (-1, 0]      │ 'Clean'     │                                                                            
  ├───────────────────┼──────────────┼─────────────┤                                                                            
  │ 1                 │ (0, 1]       │ '1 error'   │
  ├───────────────────┼──────────────┼─────────────┤                                                                            
  │ 2                 │ (1, 2]       │ '2 errors'  │
  ├───────────────────┼──────────────┼─────────────┤                                                                            
  │ 3, 4, 5, 6        │ (2, 6]       │ '3+ errors' │
  └───────────────────┴──────────────┴─────────────┘                                                                            
   
  ---                                                                                                                           
  Result:         
         
  A new column error_bucket is added to report where every row gets a label instead of a raw number:
                                                                                                                                
  transaction_id  error_count  error_bucket
  TX001           0            Clean                                                                                            
  TX002           1            1 error
  TX003           2            2 errors                                                                                         
  TX004           5            3+ errors
                                                                                                                                
  ---                                                                                                                           
  Why is this useful?
                                                                                                                                
  Raw numbers are hard to summarize. Buckets let you do things like:
  report['error_bucket'].value_counts()                                                                                         
  # Clean       120                    
  # 1 error      40                                                                                                             
  # 2 errors     25                                                                                                             
  # 3+ errors    15
                                                                                                                                
  Much more readable than counting every distinct error_count value.
                                                                                                                                
❯ pd.cut ?                                                                                                                      
                                                                                                                                
● pd.cut() is a pandas function that cuts a numeric column into labeled intervals — turning continuous numbers into categories. 
                                                                                                                              
  ---                                                                                                                           
  Minimal example:                                                                                                              
  ages = [5, 15, 25, 45, 70]                                                                                                    
                                                                                                                              
  pd.cut(ages, bins=[0, 18, 60, 100], labels=['child', 'adult', 'senior'])                                                      
  # 5  → child                                                                                                                  
  # 15 → child
  # 25 → adult                                                                                                                  
  # 45 → adult    
  # 70 → senior                                                                                                                 
                  
  ---                                                                                                                           
  pd.cut vs pd.qcut — a common pair worth knowing:
                                                                                                                                
  ┌────────────┬────────────────────────────────────┬──────────────────────────────────┐
  │            │               pd.cut               │             pd.qcut              │                                        
  ├────────────┼────────────────────────────────────┼──────────────────────────────────┤
  │ You define │ the bin edges                      │ the number of equal-sized groups │
  ├────────────┼────────────────────────────────────┼──────────────────────────────────┤
  │ Bin sizes  │ can be unequal                     │ always equal (by row count)      │                                        
  ├────────────┼────────────────────────────────────┼──────────────────────────────────┤                                        
  │ Use when   │ you know the meaningful thresholds │ you just want to split evenly    │                                        
  └────────────┴────────────────────────────────────┴──────────────────────────────────┘                                        
                  
  # cut — you decide the boundaries                                                                                             
  pd.cut(df['score'], bins=[0, 50, 75, 100], labels=['low', 'mid', 'high'])                                                     
                                                                                                                                
  # qcut — pandas decides, splits into 4 equal groups                                                                           
  pd.qcut(df['score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])                                                                    
                                                                                                                                
  ---                                                                                                                           
  In your LC case, pd.cut is the right choice because the boundaries are meaningful: 0 errors = clean, 1 error, 2 errors, 3+ are
   specific business thresholds — not arbitrary equal splits.                                                                   
                  
❯ can u give an exp with pd.qcut ?                                                                                              
                                   
● import pandas as pd                                                                                                           
                                                                                                                                
  scores = [10, 25, 30, 45, 50, 60, 75, 80, 90, 95]                                                                             
                                                                                                                                
  pd.qcut(scores, q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])                                                                         
                  
  q=4 means split into 4 equal groups by row count. 10 values → 4 groups → ~2-3 rows each.                                      
                  
  pandas figures out the boundaries automatically:                                                                              
                  
  10  → Q1   (lowest 25%)
  25  → Q1                                                                                                                      
  30  → Q2
  45  → Q2                                                                                                                      
  50  → Q3        
  60  → Q3
  75  → Q4
  80  → Q4                                                                                                                      
  90  → Q4
  95  → Q4                                                                                                                      
                                                                                                                                
  ---
  To see the boundaries pandas chose:                                                                                           
  pd.qcut(scores, q=4)                                                                                                          
  # (9.999, 33.75]   → Q1
  # (33.75, 52.5]    → Q2                                                                                                       
  # (52.5, 78.75]    → Q3                                                                                                       
  # (78.75, 95.0]    → Q4                                                                                                       
                                                                                                                                
  ---                                                                                                                           
  Practical example with a DataFrame:
  df = pd.DataFrame({'score': scores})                                                                                          
                                      
  df['quartile'] = pd.qcut(df['score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])                                                   
  df.groupby('quartile')['score'].agg(['min', 'max', 'count'])                                                                  
            min   max  count                                  
  quartile                                                                                                                      
  Q1         10    30      3                                                                                                    
  Q2         45    50      2                                                                                                    
  Q3         60    75      2                                                                                                    
  Q4         80    95      3                                                                                                    
                                                                                                                                
  ---                                                                                                                           
  Key difference from pd.cut in one line:                                                                                       
  - pd.cut → you set the boundaries, group sizes may be unequal                                                                 
  - pd.qcut → pandas sets the boundaries to make group sizes equal


| Tool | What it does | Example |
|------|-------------|---------|
| Multi-column agg | Different functions per column | `agg(total=('col_a', 'sum'), avg=('col_b', 'mean'))` |
| Two-level groupby | Group by 2+ columns | `groupby(['currency', 'status'])` |
| transform + math | Percentages within groups | `error / transform('sum') * 100` |
| filter on stats | Keep groups by calculated condition | `filter(lambda g: g['col'].mean() > 1.2)` |
| pd.cut + groupby | Bucket continuous data then analyze | `pd.cut(col, bins=[...], labels=[...])` |

## DAY 51

.map() converts severity text to numbers so it sorts correctly (CRITICAL first, not alphabetically). 
Then ascending=[True, False] — severity ascending (0 first = CRITICAL), error count descending (most errors first within each severity).

  For each row, it looks up the severity value in the dictionary and replaces it with the mapped number:                        
                                                                                                                                
  severity      →   severity_rank                                                                                               
  'CRITICAL'    →   0                                                                                                           
  'HIGH'        →   1                                                                                                           
  'MEDIUM'      →   2                                                                                                           
  'LOW'         →   3                                                                                                           
  'NONE'        →   4
                                                                                                                                
  ---
  Why not just use the string directly?                                                                                         
                                                                                                                                
  Because strings can't be sorted meaningfully:
  # Sorting by 'severity' (string) — alphabetical, wrong order                                                                  
  'CRITICAL', 'HIGH', 'LOW', 'MEDIUM', 'NONE'  # ← not severity order
                                                                                                                                
  # Sorting by 'severity_rank' (number) — correct order                                                                         
  0, 1, 2, 3, 4  # ← CRITICAL first, NONE last                                                                                  
                                                                                                                                
  So the rank column exists purely to enable correct sorting:                                                                   
  report.sort_values('severity_rank')  # now sorted by actual severity                                                          
                                                                                                                                
  ---                                                                                                                           
  .map() with a dictionary is different from .replace():
                                                                                                                                
  ┌────────────────────┬─────────────────────────┬───────────────────────────┐
  │                    │       .map(dict)        │      .replace(dict)       │                                                  
  ├────────────────────┼─────────────────────────┼───────────────────────────┤
  │ Values not in dict │ becomes NaN             │ stays unchanged           │                                                  
  ├────────────────────┼─────────────────────────┼───────────────────────────┤
  │ Use when           │ transforming all values │ changing only some values │                                                  
  └────────────────────┴─────────────────────────┴───────────────────────────┘                                                  
                                                                                                                                
  # If a row has severity = 'UNKNOWN' (not in dict):                                                                            
  report['severity'].map(severity_order)     # → NaN                                                                            
  report['severity'].replace(severity_order) # → 'UNKNOWN' (unchanged)   
  

## Rank

# Rank transactions by error count (highest = rank 1)
report['error_rank'] = report['error_count'].rank(ascending=False, method='dense').astype(int) 

❯ ok first examine all rows 1 by 1 then sort the values and map ranks finally                                                  
                                                                                     
● Exactly. The three steps:                                                                                                     
                                                                                                                                
  1. Look at all rows                                                                                                           
  2. Sort                                                                                                                       
  3. Map ranks back                                                                                                             
                                                                                                                                
  ---                                                                                                                           
  Step 1 — read all rows:                                                                                                       
  row 0 → 3                                                                                                                     
  row 1 → 6
  row 2 → 6                                                                                                                     
  row 3 → 1                                                                                                                     
  row 4 → 6                                                                                                                     
  row 5 → 4                                                                                                                     
  row 6 → 6                                                                                                                     
                                                                                                                                
  Step 2 — sort descending:                                                                                                     
  6, 6, 6, 6, 4, 3, 1                                                                                                           
                                                                                                                                
  Step 3 — assign ranks (dense):                                                                                                
  6 → rank 1                                                                                                                    
  4 → rank 2                                                                                                                    
  3 → rank 3                                                                                                                    
  1 → rank 4      
                                                                                                                                
  Step 4 — map back:
  row 0 → 3 → rank 3
  row 1 → 6 → rank 1
  row 2 → 6 → rank 1                                                                                                            
  row 3 → 1 → rank 4                                                                                                            
  row 4 → 6 → rank 1                                                                                                            
  row 5 → 4 → rank 2                                                                                                            
  row 6 → 6 → rank 1
                                                                                                                                
  Yes, you got it perfectly.            


| Tool | What it does | Key parameter |
|------|-------------|---------------|
| `sort_values('col')` | Sort by one column | `ascending=False` for biggest first |
| `sort_values(['a','b'])` | Sort by multiple columns | `ascending=[True, False]` per column |
| `.map(dict)` | Convert text to sortable values | Severity → numbers |
| `rank()` | Assign position to each row | `method='dense'` for no gaps |
| `nlargest()` / `nsmallest()` | Quick top/bottom N | Shortcut for sort + head |
                                