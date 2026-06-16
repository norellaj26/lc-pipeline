```python


## DAY 69

| Data type                              | Example                           | Best chart |
|----------------------------------------|-----------------------------------|-----------|
| Categorical (discrete)                 | Validator names (LEI, SHIP, ...)  | Bar chart |
| Continuous (numeric)                   | LC amounts ($50K, $120K, $50M...) | Histogram |
| Comparing continuous across categories | Amounts BY currency               | Boxplot |

The critical question that drives chart choice: "Do my X-values have a finite list, or could they be any number?"

Finite list (8 validators, 4 severities) → bar chart
Infinite possibilities ($0 to $∞) → histogram

* Why histograms exist
Before we draw one, let me show you why you need them.
Imagine I ask: "What's the typical LC amount in your pipeline?"
You could run df['amount'].mean() and get a single number — let's say $2.8M. But that hides EVERYTHING:

| Pipeline A                    | Pipeline B |
|-------------------------------|-----------|
| All 200 LCs are exactly $2.8M | 190 LCs at $500K + 10 LCs at $45M |
| Mean = $2.8M                  | Mean = $2.8M |
| Very boring, very stable      | Wildly concentrated risk |

Same mean, totally different business reality. A histogram reveals which scenario you're actually in. 
That's why it's called a "distribution" — shows how values are distributed across the range, not just the average

| Statistic             | What it means |
|-----------------------|--------------|
| Median                | Middle value — half above, half below |
| P95 (95th percentile) | "95% of our LCs are smaller than this" |
| P99                   | "1% of our LCs are bigger than this — these are the whales" |
| Max                   | Single biggest exposure |
| Histogram shape       | Are risks concentrated or spread? |#

## cell # 31

● Cell 31:                                                                                                                                                 
                                                                                                                                                         
  # df['amount'].describe()                                                                                                                                
  # df['amount'].astype(float).describe()
  pd.to_numeric(df['amount'], errors='coerce').describe()                                                                                                  
                                                                                                                                                           
 
  Why the two commented lines are crossed out:                                                                                                             
                                              
  df['amount'].describe() — amount is stored as a string (dtype: str). .describe() on a string column gives you string stats (count, unique, top, freq) —
  useless for numbers.                                                                                                                                     
   
  df['amount'].astype(float).describe() — crashes. Values like "49,543,534.00" have commas, .astype(float) can't parse them and raises a ValueError.       
                  
                                                                                                                                                   
  pd.to_numeric(df['amount'], errors='coerce')
                                              
  The safe conversion. errors='coerce' means: if a value can't be converted → turn it into NaN instead of crashing. Then .describe() works on the numbers
  that did convert.                                                                                                                                        
   
                                                                                                                                                    
  The output — reading scientific notation:

  count    9.300000e+01  →  93          ← only 93 of 200 converted!
  mean     2.349195e+08  →  ~$234M                                                                                                                         
  std      1.455606e+09  →  ~$1.4B      ← std > mean = massive spread                                                                                      
  min     -5.000000e+04  →  -$50,000    ← negative! validation error                                                                                       
  25%      4.899627e+06  →  ~$4.9M                                                                                                                         
  50%      2.069082e+07  →  ~$20.7M     ← median                                                                                                           
  75%      3.627773e+07  →  ~$36.3M                                                                                                                        
  max      1.000000e+10  →  $10B        ← outlier
                                                                                                                                                           
  Three red flags visible immediately:                                                                                                                     
   
  - count=93 — 107 rows failed conversion (they have commas — cell 33 investigates this)                                                                   
  - min=-50,000 — negative LC amount, caught by your AmountValidator
  - max=$10B with std=$1.4B — extreme outlier pulling the mean far from the median ($20M)                                                                  
                                                                                                                                                           
  This is exactly why you explore data before drawing it — the histogram in cell 32 will look broken because of these issues, and cells 33-38 fix them one 
  by one.    
  
Cell # 32

 ## 32                                                                                                                                                    
  amount_clean = pd.to_numeric(df['amount'], errors='coerce')                                                                                              

  fig, ax = plt.subplots(figsize=(10, 6))                                                                                                                  
   
  ax.hist(amount_clean.dropna(), bins=30, color='#DC143C', edgecolor='black')                                                                              
                  
  ax.set_title('LC Amount Distribution — 93 Valid Transactions')                                                                                           
  ax.set_xlabel('Amount (USD)')
  ax.set_ylabel('Number of LCs')

  plt.show()                                                                                                                                               
   
  Line by line:                                                                                                                                            
                  
  pd.to_numeric(df['amount'], errors='coerce')                                                                                                             
  Tries to convert every value in amount to a float. Anything it can't convert (like "49,543,534.00" — note the commas) becomes NaN. That's why you only
  get 93 — the other 107 rows had comma-formatted strings that pandas couldn't parse. Cell 34 fixes this.                                                  
                  
  ax.hist(amount_clean.dropna(), bins=30, ...)                                                                                                             
  Three things happening:
  - .dropna() — removes the NaNs before plotting (hist crashes on NaN)                                                                                     
  - bins=30 — splits the data range into 30 equal-width buckets; each bar = "how many LCs fall in this range"                                              
  - color / edgecolor — fill color vs. the thin black outline between bars (without edgecolor the bars blur together)
                                                                                                                                                           
  The banking angle: this is exactly the chart a risk officer pulls first — "what's our LC exposure profile?" A histogram with one giant bar on the left   
  and a long tail right means a few huge transactions are skewing the portfolio. That's precisely what you discovered in cells 36–37 (the $10B outlier).   
                                                                                                                                                           
  The title says "93 Valid" because that's the bug — fixed in cell 34 once you strip the commas.                                                           
                  
✻ Baked for 13s                                                                                                                                            
                                                     
❯ can u explain bins again                                                                                                                                 
                                                                                                                                                           
● Think of bins=30 as telling matplotlib: "divide the data range into 30 equal slices, then count how many LCs fall in each slice."                        
                                                                                                                                                           
  Your amount data goes from ~$0 to ~$10B. With bins=30, matplotlib cuts that range into 30 equal chunks:                                                  
   
  Chunk 1:  $0         → $333M   → count how many LCs land here → draw bar that tall                                                                       
  Chunk 2:  $333M      → $666M   → count...                                                                                                                
  Chunk 3:  $666M      → $1B     → count...
  ...                                                                                                                                                      
  Chunk 30: $9.67B     → $10B    → count...
                                                                                                                                                           
  Each bar's width = one chunk. Each bar's height = number of LCs in that chunk.                                                                           
   
  Why does the number matter?                                                                                                                              
                                                                                                                                                         
  bins=5    → 5 fat bars  → too vague, hides structure
  bins=30   → 30 bars     → good balance                                                                                                                   
  bins=300  → 300 thin bars → so granular it looks like noise
                                                                                                                                                           
  Banking analogy: it's like a credit risk bucket report. Instead of listing all 200 LC amounts individually, you group them — "$0–$5M bucket: 40 LCs,     
  $5M–$10M bucket: 35 LCs..." That's all a histogram is: a bucketed count.                                                                                 
                                                                                                                                                           
  The reason your cell 32 chart looked terrible (one giant bar on the left, everything else flat) is that with a $10B outlier in the data, each bin was    
  $333M wide — so 180+ normal LCs all squeezed into bin 1. That's what motivated the three strategies in cells 36–38.
  
Cell # 33

This is a diagnostic cell — you already knew something was wrong (93/200), now you're investigating why.                                                 
   
  df['amount'].dtype → str                                                                                                                                 
  The whole column is strings. pandas never auto-converted it, so "49,543,534.00" is just text with commas.
                                                                                                                                                           
  The three print lines                                                                                                                                    
  Just counting: 200 total, 93 worked, 107 became NaN after coerce. Confirms the bug is real.                                                              
                                                                                                                                                           
  failed_mask = converted.isna() & df['amount'].notna()
  This is the clever line. It finds rows where both conditions are true:                                                                                   
                                                                                                                                                           
  converted.isna()      → NaN after conversion  (conversion FAILED)
  df['amount'].notna()  → original value existed (it wasn't already null)                                                                                  
                  
  Without the second condition, you'd also grab rows that were originally empty — which aren't bugs, just missing data. The & isolates only the rows that  
  had a value but failed conversion — the actual culprits.
                                                                                                                                                           
  The output tells you everything:                                                                                                                         
  49,543,534.00  ← comma is the villain
  43,942,455     ← no decimal but still has comma                                                                                                          
                                                 
  Every failed row has commas. Diagnosis done → cell 34 fixes it with .str.replace(',', '').     
  
  
Cell # 34

.pipe() itself doesn't convert anything. It's just a delivery mechanism.                                                                   
                                                                                                                                                           
  .pipe(pd.to_numeric, errors='coerce')                                                                                                                    
   
  is literally the same as:                                                                                                                                
                  
  pd.to_numeric(series, errors='coerce')                                                                                                                   
                  
  pd.to_numeric is what does the conversion. .pipe() just passes the Series into it so you can keep the chain going instead of wrapping.                   
   
  Think of .pipe() as a middleman — it hands off, pd.to_numeric does the actual work.
  
 The fix is two chained steps:                                                                                                                            
                  
  .str.replace(',', '', regex=False)                                                                                                                       
  Strips every comma from the string. "49,543,534.00" → "49543534.00". The regex=False tells pandas "treat the comma as a literal character, not a regex 
  pattern" — faster and safer.                                                                                                                             
   
  .pipe(pd.to_numeric, errors='coerce')                                                                                                                    
  .pipe(func) passes the Series as the first argument to func. So this is identical to:
  pd.to_numeric(that_series, errors='coerce')                                                                                                              
  The only reason to use .pipe() here is readability — it keeps everything in one clean top-to-bottom chain instead of wrapping the outside. That's exactly
   what the commented line below shows — same result, less readable.                                                                                       
                                                                                                                                                           
  The output: 199 (was 93)                                                                                                                                 
  One row is still NaN — that's a genuinely missing/corrupt value, not a comma issue. 93 → 199 just by stripping commas.                                   
                                                                                                                                                           
  describe() — worth knowing these numbers:                                                                                                                
  min  = -50,000      ← negative LC amount → validator should catch this                                                                                   
  50%  =  ~$18.7M     ← median LC                                                                                                                          
  max  =  $10B        ← the outlier that broke your histogram    



## Cell # 36                                                                                                                                                    
  amount_normal = amount_clean[amount_clean < 200_000_000].dropna()                                                                                      
                                                                                                                                                           
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.hist(amount_normal, bins=30, color='#DC143C', edgecolor='black')                                                                                      
  ax.set_title(f'LC Amounts < $200M — {len(amount_normal)} of 200 Transactions')                                                                           
  ax.set_xlabel('Amount (USD)')
  ax.set_ylabel('Number of LCs')                                                                                                                           
  plt.show()                                                                                                                                               
   
  Strategy 1: just cut the outliers out.                                                                                                                   
                  
  amount_clean[amount_clean < 200_000_000]                                                                                                                 
  Boolean filter on a Series — same pattern as filtering a DataFrame but on one column. Keeps only rows where the value is under $200M. The $10B outlier
  disappears entirely.                                                                                                                                     
                  
  200_000_000                                                                                                                                              
  Python lets you use _ as a visual separator in numbers — purely cosmetic, means the same as 200000000. Much easier to read.
                                                                                                                                                           
  .dropna()                                                                                                                                                
  After filtering, any NaN rows that slipped through get removed before hitting hist().                                                                    
                                                                                                                                                           
  f'... {len(amount_normal)} ...'                                                                                                                          
  Dynamic title — instead of hardcoding "197 transactions", you let Python count and insert it. If the data changes, the title updates automatically. Good 
  habit.                                                                                                                                                   
                  
  The tradeoff of this strategy:                                                                                                                           
  Simple and fast, but you're deleting real data. If that $10B LC is legitimate (a sovereign trade deal, a commodities mega-contract), you've just lied
  about your portfolio. That's why cells 37–38 offer safer alternatives — log scale shows everything, percentile filter keeps outliers in the dataset but  
  off-screen.     
  
## 37                                                                                                                                                    
  import numpy as np                                                                                                                                       
  positive_amounts = amount_clean[amount_clean > 0].dropna()                                                                                               
   
  log_bins = np.logspace(                                                                                                                                  
      np.log10(positive_amounts.min()),
      np.log10(positive_amounts.max()),                                                                                                                    
      30          
  )

  ax.hist(positive_amounts, bins=log_bins, color='#DC143C', edgecolor='black')
  ax.set_xscale('log')
                                                                                                                                                           
  Strategy 2: show ALL data, just change the scale.                                                                                                        
                                                                                                                                                           
  amount_clean[amount_clean > 0]                                                                                                                           
  Log scale can't handle zero or negatives (log of 0 is undefined, log of negative doesn't exist). That's why this filters differently from cell 36 — not
  removing outliers, just removing mathematically impossible inputs.                                                                                       
   
  The np.logspace block — the key idea:                                                                                                                    
  np.logspace(start, stop, num) creates num points evenly spaced on a log scale. You feed it log10 of your min and max:
                                                                                                                                                           
  positive_amounts.min() ≈ $50,000    → log10 = 4.7                                                                                                        
  positive_amounts.max() = $10,000,000,000 → log10 = 10                                                                                                    
                                                                                                                                                           
  So it generates 30 bin edges evenly spread between 10^4.7 and 10^10 — each bin covers roughly one order of magnitude.                                    
                                                                                                                                                           
  Why log bins AND set_xscale('log')? Why both?                                                                                                            
  They solve different problems:
  - set_xscale('log') — changes how the axis is drawn (visual)                                                                                             
  - log_bins — changes where the bin edges are placed (data)                                                                                               
                                                                                                                                                           
  If you used linear bins with a log axis, the left bars (small amounts) would look tiny and squished, the right bars huge. Log bins make every bar the    
  same visual width on a log axis.                                                                                                                         
   
  Banking angle: this is standard in credit risk reporting. LC amounts span 5 orders of magnitude — from a $50K SME trade deal to a $10B sovereign         
  contract. Log scale is the only way to show both on the same chart without one making the other invisible.
  
## Cell # 38    

  p5 = amount_clean.quantile(0.05)                                                                                                                       
  p95 = amount_clean.quantile(0.95)                                                                                                                        
   
  amount_middle = amount_clean[(amount_clean >= p5) & (amount_clean <= p95)].dropna()                                                                      
                  
  fig, ax = plt.subplots(figsize=(10, 6))                                                                                                                  
  ax.hist(amount_middle, bins=30, color='#DC143C', edgecolor='black')
  ax.set_title(rf'LC Amount Distribution — P5 to P95 (\${p5/1e6:.1f}M to \${p95/1e6:.1f}M)')                                                               
   
  Strategy 3: keep the outliers in the dataset, just don't plot them.                                                                                      
                  
  .quantile(0.05) / .quantile(0.95)                                                                                                                        
  Percentiles. quantile(0.05) = the value where 5% of your data falls below it. quantile(0.95) = 95% falls below it. So you're keeping the middle 90% of
  transactions and leaving the extreme edges off the chart — without deleting a single row from amount_clean.                                              
                  
  (amount_clean >= p5) & (amount_clean <= p95)                                                                                                             
  Two conditions joined with & — both must be true. Same pattern you saw in cell 33's failed_mask.
                                                                                                                                                           
  The title line — three things packed in:
  rf'... \${p5/1e6:.1f}M ...'                                                                                                                              
  - rf — raw f-string. The r tells Python "don't process backslashes", so \$ reaches matplotlib literally. Matplotlib uses $...$ for LaTeX math mode, so \$
   tells it "this is just a dollar sign, not math"                                                                                                         
  - p5/1e6 — converts dollars to millions (1e6 = 1,000,000)                                                                                                
  - :.1f — format as float, 1 decimal place → $4.2M not $4234521.123                                                                                       
                                                                                                                                                           
  Why this is the regulatory-safe option:                                                                                                                  
  In banking, you never delete data for a chart. An auditor asks "where's that $10B LC?" — with strategy 1 (cell 36) it's gone. Here it's still in         
  amount_clean, just outside the plot window. Your dataset is untouched.                                                                                   
                                                                              
  
● ## cell # 39   

  fig, ax = plt.subplots(figsize=(8, 6))                                                                                                                 
                                                                                                                                                           
  ax.boxplot(amount_clean.dropna(), vert=True)                                                                                                             
                                                                                                                                                           
  ax.set_title('LC Amount Distribution — Boxplot')                                                                                                         
  ax.set_ylabel('Amount (USD)')

  plt.show()

  New chart type — the boxplot. Simple call, but a lot of information packed in.                                                                           
   
  What a boxplot draws — the five-number summary:                                                                                                          
                  
          |         ← max whisker (Q3 + 1.5×IQR)
      ┌───┐                                                                                                                                                
      │   │         ← Q3 (75th percentile)                                                                                                                 
      │───│         ← median (50th percentile)                                                                                                             
      │   │         ← Q1 (25th percentile)                                                                                                                 
      └───┘       
          |         ← min whisker (Q1 - 1.5×IQR)                                                                                                           
          o         ← outlier dot (anything beyond the whiskers)                                                                                           
                                                                                                                                                           
  The 1.5×IQR rule — how whiskers are calculated:                                                                                                          
  - IQR = Q3 − Q1 (the box height)                                                                                                                         
  - Whisker top = Q3 + 1.5×IQR                                                                                                                             
  - Whisker bottom = Q1 − 1.5×IQR
  - Anything outside those bounds → plotted as individual dots (outliers)                                                                                  
   
  vert=True                                                                                                                                                
  Draws the box vertically (amount on Y-axis). vert=False flips it horizontal — you'll use that in cell 43 for the currency comparison.
                                                                                                                                                           
  Why this chart looks terrible:
  Same $10B problem as cell 32. The box (where 50% of your data lives, roughly $6M–$36M) gets squished into a tiny sliver at the bottom because the Y-axis 
  has to stretch to $10B. That's exactly why cell 40 adds set_yscale('log').                                                                               
   
  Banking angle: boxplots are standard in risk dashboards. A Basel III VaR report shows exactly this — median exposure, IQR as the "normal range", and     
  outlier dots flagged for stress testing.


● ## Cell # 40                                                                                                                                                    
  positive_amounts = amount_clean[amount_clean > 0].dropna()                                                                                             
                                                                                                                                                           
  ax.boxplot(positive_amounts, vert=True)
  ax.set_yscale('log')                                                                                                                                     
                  
  ax.set_title('LC Amount Distribution — Boxplot (log scale)')                                                                                             
  ax.set_ylabel('Amount (USD, log scale)')
                                                                                                                                                           
  Short cell — one fix from cell 39, one key difference from cell 37.                                                                                      
   
  amount_clean[amount_clean > 0]                                                                                                                           
  Same reason as cell 37 — log scale breaks on zero and negatives. That -$50,000 row has to go before you touch log scale.
                                                                                                                                                           
  ax.set_yscale('log') ← the one fix
  Stretches the Y-axis logarithmically so the box (your $6M–$36M range) is no longer squished at the bottom. The $10B outlier dot still appears, but now   
  the whole distribution is readable.                                                                                                                      
   
  Notice: set_yscale here, set_xscale in cell 37                                                                                                           
  Because the axis that carries your amounts flips between chart types:
                                                                                                                                                           
  Histogram  → amounts on X-axis → set_xscale('log')
  Boxplot    → amounts on Y-axis → set_yscale('log')                                                                                                       
                  
  Same data, same problem, same solution — just applied to the correct axis depending on chart orientation. Easy thing to get wrong the first time.        

## Cell # 41         

  df_valid = df.copy()                                                                                                                                   
  df_valid['amount_clean'] = amount_clean                                                                                                                  
  df_valid = df_valid[df_valid['amount_clean'] > 0].dropna(subset=['amount_clean'])
                                                                                                                                                           
  currencies = df_valid['currency'].value_counts().head(5).index.tolist()
  data_per_currency = [                                                                                                                                    
      df_valid.query('currency == @cur')['amount_clean'].values
      for cur in currencies
  ]
                                                                                                                                                           
  This cell is pure data prep — no chart yet. Getting the data into the shape matplotlib's boxplot() needs.                                                
                                                                                                                                                           
  df.copy() then add amount_clean column                                                                                                                   
  You can't filter rows by amount_clean if it only exists as a standalone Series. Attaching it to a copy of df lets you filter rows and keep all other
  columns (like currency) aligned. The .copy() avoids mutating the original df.                                                                            
   
  .dropna(subset=['amount_clean'])                                                                                                                         
  The subset argument means "only drop rows where this specific column is NaN" — not rows where any column is NaN. Without it, you'd lose rows that have
  valid amounts but happen to be missing some other field.                                                                                                 
                  
  value_counts().head(5).index.tolist()                                                                                                                    
  A chain you'll use a lot:
  value_counts() → Series sorted by frequency                                                                                                              
  .head(5)       → keep top 5                
  .index         → grab the currency labels (not the counts)                                                                                               
  .tolist()      → convert to plain Python list             
  Output was only 4 (['JPY', 'USD', 'EUR', 'GBP']) — your data only has 4 currencies.                                                                      
                                                                                                                                                           
  The list comprehension — the key prep step:                                                                                                              
  data_per_currency = [                                                                                                                                    
      df_valid.query('currency == @cur')['amount_clean'].values                                                                                            
      for cur in currencies                                                                                                                                
  ]                                                                                                                                                        
  Builds one numpy array per currency. The @cur syntax is pandas query() referencing a Python variable. .values converts the Series to a plain numpy array
  — that's what ax.boxplot() expects when you pass multiple boxes.                                                                                         
                                                                                                                                                           
  Result: a list of 4 arrays, one per currency, ready to hand to cell 43.

● ## Cell # 42                                                                                                                                                    
  for cur in currencies:                                                                                                                                 
      amounts = df_valid.query('currency == @cur')['amount_clean']                                                                                         
      print(f"{cur}: median = {amounts.median():,.0f}, max = {amounts.max():,.0f}")
  JPY: median = 18,567,802, max = 10,000,000,000                                                                                                           
  USD: median = 21,689,596, max = 49,963,328    
  EUR: median = 24,020,032, max = 49,690,891                                                                                                               
  GBP: median = 22,671,503, max = 10,000,000,000
                                                                                                                                                           
  Short cell — just a sanity check before plotting.
                                                                                                                                                           
  :,.0f — the format spec:                                                                                                                                 
  ,    → add thousand separators  (18567802 → 18,567,802)                                                                                                  
  .0f  → zero decimal places      (no cents)                                                                                                               
  Makes the numbers human-readable in the print output.                                                                                                    
                                                                                                                                                           
  What the output is actually telling you:                                                                                                                 
  The medians are all similar ($18M–$24M) — that's your normal LC range across currencies. But look at the max:                                            
                                                                                                                                                           
  JPY max = $10,000,000,000  ← outlier                                                                                                                     
  GBP max = $10,000,000,000  ← outlier                                                                                                                     
  USD max =     $49,963,328  ← clean
  EUR max =     $49,690,891  ← clean                                                                                                                       
                  
  JPY and GBP both have the $10B outlier. So in cell 43, those two boxes will have a high outlier dot while USD and EUR won't. You know this before looking
   at the chart — that's exactly why you run the sanity check.

● ## Cell # 43                                                                                                                                                    
  fig, ax = plt.subplots(figsize=(10, 6))                                                                                                                
                                                                                                                                                           
  ax.boxplot(data_per_currency, tick_labels=currencies, vert=True)                                                                                         
  ax.set_yscale('log')                                                                                                                                     
                                                                                                                                                           
  ax.set_title('LC Amount Distribution by Currency — Top 4 (log scale)')
  ax.set_xlabel('Currency')
  ax.set_ylabel('Amount, log scale')
                                                                                                                                                           
  plt.show()
                                                                                                                                                           
  The payoff cell — cells 41 and 42 were just prep for this one line.                                                                                      
   
  ax.boxplot(data_per_currency, tick_labels=currencies)                                                                                                    
  Two arguments doing all the work:
  - data_per_currency — the list of 4 arrays from cell 41. matplotlib sees a list → draws one box per array, side by side                                  
  - tick_labels=currencies — labels each box with its currency name (['JPY', 'USD', 'EUR', 'GBP'])                                                         
                                                                                                                                                           
  Without tick_labels you'd get 1, 2, 3, 4 on the X-axis instead of currency names.                                                                        
                                                                                                                                                           
  set_yscale('log')
  Same reason as cell 40 — JPY and GBP have $10B outliers. Without log scale those two boxes collapse into flat lines at the bottom.                       
                                                                                                                                                           
  How the three cells connect:
  Cell 41 → built data_per_currency  (list of arrays, one per currency)                                                                                    
  Cell 42 → confirmed JPY/GBP have $10B outliers  (sanity check)       
  Cell 43 → draws all 4 boxes in one call  (the actual chart)                                                                                              
                                                                                                                                                           
  What the chart tells you:                                                                                                                                
  All four medians sit around the same level ($18M–$24M) — confirming currency doesn't drive LC size. But JPY and GBP each show a high outlier dot at $10B,
   exactly as cell 42 predicted. The chart just visualizes what you already knew from the sanity check.     
  

cell # 37

 Step 1 — Filter to positive amounts only

  positive_amounts = amount_clean[amount_clean > 0].dropna()
                                                                                                                                                           
  You can't take log(-50,000) — it's mathematically undefined. Same for log(0). So you drop the one negative amount (the intentionally bad row) and any NaN
   before touching log.                                                                                                                                    
                                                                                                                                                           
            
  Step 2 — Build logarithmically-spaced bins
                                                                                                                                                           
  log_bins = np.logspace(
      np.log10(positive_amounts.min()),   # start exponent                                                                                                 
      np.log10(positive_amounts.max()),   # stop exponent                                                                                                  
      30                                  # how many bins
  )                                                                                                                                                        
                  
  np.logspace(start, stop, n) generates n numbers evenly spaced on a log scale — meaning each step is a constant multiplier, not a constant addition.      
   
  In your data:                                                                                                                                            
                  
  | Value         | log10 |                                                                                                                                
  |---------------|-------|                                                                                                                                
  | min ≈ $50K    |  4.7  |
  | max ≈ $10B    | 10.0  |                                                                                                                                
                  
  So np.logspace(4.7, 10.0, 30) produces 30 bin edges from ~$50K to $10B, where each bin is roughly 3× wider than the previous one. That's why the bins    
  look equal-width on screen — the x-axis stretches exponentially.
                                                                                                                                                           
  Compare the two approaches:

  | Approach          | Bin edges                        | Problem?                              |
  |-------------------|----------------------------------|---------------------------------------|                                                         
  | Regular bins      | $0, $333M, $666M, $1B...         | 95% of data crushed into leftmost bin |
  | Log bins (cell37) | $50K, $150K, $500K, $1.5M, $5M… | Every order of magnitude gets space   |                                                          
                                                                                                                                                           
                                                                                                                                                    
  Step 3 — Draw histogram + set log x-axis                                                                                                                 
                                                                                                                                                           
  ax.hist(positive_amounts, bins=log_bins, ...)
  ax.set_xscale('log')                                                                                                                                     
                  
  You need both. Here's why:                                                                                                                               
   
  - bins=log_bins → bins are correctly sized in log space                                                                                                  
  - ax.set_xscale('log') → the x-axis labels also stretch logarithmically so the bins look equal width
                                                                                                                                                           
  Without set_xscale('log'), the axis would still be linear and the log bins would look weirdly unequal on screen. Together, they make the chart visually  
  honest.                                                                                                                                                  
                                                                                                                                                           
             
  Banking context
                 
  In trade finance, LC amounts span 5+ orders of magnitude:
                                                                                                                                                           
  - A cocoa export from Ecuador: $80,000                                                                                                                   
  - Samsung buying TSMC chips: $45,000,000                                                                                                                 
  - Airbus delivering 20 planes to Emirates: $4,000,000,000                                                                                                
                                                                                                                                                           
  A linear scale would compress Samsung and the cocoa exporter into the same tiny sliver on the left while the Airbus deal sits alone on the right. Log    
  scale is the standard in banking risk dashboards (VaR charts, exposure distributions) precisely because portfolios always have this kind of spread. Your 
  pipeline has the same shape — one $10B outlier and a healthy cluster of $5M–$50M normal LCs.                                                             
                  
✻ Crunched for 38s                
                                                                                          
❯ why we use log10() ?                                                                                                                                     
                                                                                                                                                           
● Great question. Let's start with what log10() actually does.                                                                                             
                                                                                                                                                           

  What log10 means                                                                                                                                         
                  
  log10(x) asks: "10 to the power of WHAT gives me x?"                                                                                                     
                                                                                                                                                           
  log10(100)       = 2    because 10² = 100                                                                                                                
  log10(1,000)     = 3    because 10³ = 1,000                                                                                                              
  log10(1,000,000) = 6    because 10⁶ = 1,000,000                                                                                                          
  log10(10B)       = 10   because 10¹⁰ = 10,000,000,000                                                                                                    
                                                                                                                                                           
  The result is the exponent — the order of magnitude. That's the key.                                                                                     
                  
                                                                                                                                                      
  Why log10 and not ln or log2?
                               
  There's nothing mathematically wrong with ln() or log2(). They'd all work. But log10 is the natural choice here for one reason:
                                                                                                                                                           
  humans count zeros in base 10.                                                                                                                           
                                                                                                                                                           
  When a compliance officer says "this LC is in the millions" or "that exposure is in the billions" — they're thinking in powers of 10. log10 maps directly
   onto that intuition:
                                                                                                                                                           
  | Amount     | log10 | What a banker says   |
  |------------|-------|----------------------|                                                                                                            
  | $1,000     | 3     | "thousands"          |
  | $10,000    | 4     | "tens of thousands"  |                                                                                                            
  | $1,000,000 | 6     | "millions"           |
  | $1,000,000,000 | 9 | "billions"           |                                                                                                            
                                                                                                                                                           
  So when np.logspace(4.7, 10, 30) spaces bins from exponent 4.7 to exponent 10, you're literally saying: "give me evenly spaced stops between the         
  fifty-thousand range and the ten-billion range." That's readable. np.logspace(15.8, 33.2, 30) with natural log would produce the same bins but the       
  numbers mean nothing to you.                                                                                                                             
                  

  The two-step in cell 37

  log_bins = np.logspace(
      np.log10(positive_amounts.min()),  # convert dollar → exponent                                                                                       
      np.log10(positive_amounts.max()),  # convert dollar → exponent
      30                                                                                                                                                   
  )               
                                                                                                                                                           
  np.logspace() expects exponents as input, not raw dollar amounts. So you use log10() to translate your min/max from dollar space into exponent space,    
  hand those exponents to logspace, and it hands you back 30 bin edges in dollar space.
                                                                                                                                                           
  It's just a unit conversion. Same reason you convert km to miles before plugging into a formula that expects miles.   
  

 can u explain this -> where each bin is roughly 3× wider than the previous one.                                                                          
                                                                                                                                                           
● Sure — and I'll also correct myself: I said "3×" but the actual multiplier for your data is closer to 1.5×. The concept is right, the number was sloppy. 
  Let me show you why.                                                                                                                                     
                                                                                                                                                           
                                                                                                                                                     
  Linear bins vs log bins — the core difference
                                                                                                                                                           
  Linear bins add a fixed amount each step:
                                                                                                                                                           
  $0  →  $333M  →  $666M  →  $1B  →  ...   (+$333M each time)
                                                                                                                                                           
  Log bins multiply by a fixed ratio each step:                                                                                                            
                                                                                                                                                           
  $50K  →  $76K  →  $115K  →  $175K  →  $265K  →  ...   (×1.52 each time)                                                                                  
                                                                                                                                                           
  That constant multiplier is what "evenly spaced on a log scale" means.                                                                                   
                                                                                                                                                           
                                                                                                                                                   
  Where does 1.52 come from?
                                                                                                                                                           
  Your data runs from ~$50K to $10B with 30 bins.
                                                                                                                                                           
  log10($50K)  ≈  4.7
  log10($10B)  = 10.0                                                                                                                                      
   
  range of exponents  = 10.0 - 4.7 = 5.3                                                                                                                   
  steps between bins  = 30 - 1    = 29
                                                                                                                                                           
  step size = 5.3 / 29 ≈ 0.183                                                                                                                             
   
  multiplier = 10^0.183 ≈ 1.52                                                                                                                             
                  
  So every bin edge is previous × 1.52. That's what np.logspace is doing under the hood — producing a geometric sequence with that ratio baked in.         
                                                                                                                                                    
  Why this makes the bars look equal-width
                                          
  On a linear x-axis, these bins would look increasingly wide as you go right — because the dollar gaps keep growing:
                                                                                                                                                           
  Bin 1 width:  $76K  - $50K  =  $26K
  Bin 5 width:  $265K - $175K =  $90K    ← already 3.5× wider                                                                                              
  Bin 15 width: ≈ $10M difference                                                                                                                          
  Bin 29 width: ≈ $3B difference          ← gigantic                                                                                                       
                                                                                                                                                           
  On a log x-axis, each order of magnitude gets the same horizontal space, so a bin that spans $50K → $76K looks the same width as one that spans $5B →    
  $7.6B. The visual stretching of the axis exactly cancels out the growing bin widths.                                                                     
                                                                                                                                                           
  That's why you need both bins=log_bins and ax.set_xscale('log') — they are solving two halves of the same problem. 
```    