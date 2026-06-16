DataCleaner
│
├── clean(df) → df           ← public entry point (like validate())
│
├── _clean_unicode(df)       ← em-dashes, non-breaking spaces
├── _clean_whitespace(df)    ← strip leading/trailing, collapse doubles
├── _normalize_case(df)      ← currency, country codes → uppercase

● loc stands for label-based location. You can use it in several ways:                                                 
                                         
  Single cell                                                                                                          
  df.loc[1, 'lc_number']          # row 1, column 'lc_number'                                                          
                                                                                                                       
  Entire row                                                                                                           
  df.loc[1]                        # all columns of row 1

  Entire column
  df.loc[:, 'lc_number']          # all rows, lc_number column
                                   # same as df['lc_number']

  Slice of rows
  df.loc[1:5, 'lc_number']        # rows 1 to 5, lc_number column

  Multiple columns
  df.loc[1, ['lc_number', 'amount']]   # row 1, two columns

  With a condition
  df.loc[df['amount'] > 50000]    # all rows where amount > 50000


  df.iloc[0]                    # first row (position 0)                                                               
  df.iloc[0, 1]                 # first row, second column  
  df.iloc[0:5]                  # rows 0,1,2,3,4  ← 5 NOT included (like normal Python)                                
  df.iloc[:, 0]                 # all rows, first column                                                               
  df.iloc[0:3, 0:2]             # first 3 rows, first 2 columns

  ---
  Key difference:

  df.loc[1, 'lc_number']    # row with INDEX LABEL 1, column named 'lc_number'
  df.iloc[1, 0]             # row at POSITION 1, column at POSITION 0

  This matters when your index is not 0,1,2,3... For example if you filtered the DataFrame:

  flagged = df[df['amount'] > 50000]
  # flagged might have index labels: 3, 7, 12, 45...

  flagged.loc[3]     # row with label 3  ✅
  flagged.iloc[0]    # first row (label 3) ✅ same result here
  flagged.loc[0]     # ❌ KeyError — no label 0 in flagged

| Tool | When to use |
|---|---|
| `df[df['col'] == 'value']` | Simple single condition |
| `&`, `|`, `~` with parentheses | Combining conditions |
| `isin(['a', 'b', 'c'])` | Matching against a list |
| `between(low, high)` | Numeric ranges |
| `query("...")` | Clean readable filtering |
