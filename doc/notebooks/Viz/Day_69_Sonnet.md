 Day 69 — Distributions: Histograms & Boxplots
                                                                                                                                                           
  The data quality discovery
                                                                                                                                                           
  Before drawing anything, df['amount'].describe() revealed the column was dtype: object (string), not numeric.                                            
   
  Root cause — two problems mixed in the same column:                                                                                                      
                  
  | Problem                        | Example value      | Fix                          |                                                                   
  |--------------------------------|--------------------|------------------------------|                                                                   
  | Comma-formatted numbers        | "49,543,534.00"    | .str.replace(',', '')        |                                                                   
  | Literal invalid string         | "INVALID" (row 47) | pd.to_numeric(errors='coerce')|                                                                  
                                                                                                                                                           
  The clean pattern:                                                                                                                                       
  amount_clean = (                                                                                                                                         
      df['amount']
      .str.replace(',', '', regex=False)
      .pipe(pd.to_numeric, errors='coerce')
  )                                                                                                                                                        
  # Result: 199/200 valid, 1 NaN (the "INVALID" row)
                                                                                                                                                           
  .pipe() lets you chain a standalone function into a method chain — reads left to right instead of inside out.                                            
                                                                                                                                                           
  ---                                                                                                                                                      
  Histograms — ax.hist()                                                                                                                                   
                                                                                                                                                           
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.hist(data, bins=30, color='#DC143C', edgecolor='black')                                                                                               
                                                                                                                                                           
  The outlier problem: one $10B LC stretches the x-axis so far that all other bars get squished into the first few bins. Three solutions:                  
                                                                                                                                                           
  | Approach         | Code                                          | Tradeoff                          |                                                 
  |------------------|-----------------------------------------------|-----------------------------------|                                                 
  | Hard cap         | data[data < 200_000_000]                      | Simple but arbitrary threshold    |
  | Log scale        | ax.set_xscale('log') + np.logspace bins       | Keeps all data, less intuitive    |                                                 
  | P5–P95 trim      | data[(data >= p5) & (data <= p95)]            | Principled, self-documenting      |                                                 
                                                                                                                                                           
  Log scale bins — must match the scale:                                                                                                                   
  log_bins = np.logspace(                                                                                                                                  
      np.log10(data.min()),                                                                                                                                
      np.log10(data.max()),
      30                   
  )                                                                                                                                                        
  ax.hist(data, bins=log_bins)
  ax.set_xscale('log')                                                                                                                                     
  Without np.logspace, bins are evenly spaced in linear space — useless on a log axis.

  P5–P95 title pattern:                                                                                                                                    
  p5  = amount_clean.quantile(0.05)
  p95 = amount_clean.quantile(0.95)                                                                                                                        
  ax.set_title(rf'Distribution — P5 to P95 (${p5/1e6:.1f}M to ${p95/1e6:.1f}M)')                                                                           
  Note: rf'' = raw f-string. The r prevents Python from treating \$ as an escape sequence. Needed because matplotlib interprets $...$ as LaTeX math mode.
                                                                                                                                                           
  ---                                                                                                                                                      
  Boxplots — ax.boxplot()                                                                                                                                  
                                                                                                                                                           
  fig, ax = plt.subplots(figsize=(8, 6))
  ax.boxplot(data, vert=True)
                                                                                                                                                           
  What one boxplot shows — 5 stats in one chart:                                                                                                           
                                                                                                                                                           
  | Element        | What it is                          | Your data          |                                                                            
  |----------------|-------------------------------------|--------------------|                                                                            
  | Bottom whisker | min (or P5 if outliers exist)       | ~$700K             |
  | Bottom of box  | Q1 (25th percentile)                | $6.6M              |                                                                            
  | Line in box    | Median (50th percentile)            | $18.7M             |
  | Top of box     | Q3 (75th percentile)                | $36.4M             |                                                                            
  | Top whisker    | max (or P95 if outliers exist)      | ~$50M              |                                                                            
  | Dots           | Outliers beyond 1.5× IQR           | $10B, -$50K        |                                                                             
                                                                                                                                                           
  Same outlier problem as histograms — same fix:                                                                                                           
  # Log scale for boxplot (note: yscale not xscale — boxplot is vertical)                                                                                  
  positive_amounts = amount_clean[amount_clean > 0].dropna()  # log can't handle 0 or negatives                                                            
  ax.boxplot(positive_amounts)                                                                                                                             
  ax.set_yscale('log')                                                                                                                                     
                                                                                                                                                           
  ---                                                                                                                                                      
  Multi-category boxplot — the real power                                                                                                                  
                                                                                                                                                           
  One chart compares distributions across categories. Data must be a list of arrays — one per box:
                                                                                                                                                           
  data_per_currency = [
      df_valid.query('currency == @cur')['amount_clean'].values                                                                                            
      for cur in currencies                                                                                                                                
  ]
                                                                                                                                                           
  ax.boxplot(data_per_currency, tick_labels=currencies, vert=True)
  ax.set_yscale('log')
                                                                                                                                                           
  Note: labels= was renamed to tick_labels= in matplotlib 3.9 — use tick_labels to avoid deprecation warning.
                                                                                                                                                           
  What the currency comparison revealed:                                                                                                                   
   
  | Currency | Median     | Has $10B outlier? |                                                                                                            
  |----------|------------|-------------------|                                                                                                            
  | JPY      | $18.6M     | YES               |
  | USD      | $21.7M     | no                |                                                                                                            
  | EUR      | $24.0M     | no                |
  | GBP      | $22.7M     | YES               |                                                                                                            
                  
  ---                                                                                                                                                      
  Config fix applied today
                                                                                                                                                           
  Log scale surfaced tiny amounts (~$0.01) invisible to the other charts. Root cause: AMOUNT_RULES['min_value'] was Decimal('0.01'). Fixed to:
                                                                                                                                                           
  # config/validation_rules.py
  'min_value': Decimal('1000.00'),  # UCP 600: op costs $500-$2000, no real LC below $1000                                                                 
                                                                                                                                                           
  AMT004 ("Amount below minimum allowed") was already wired — only the threshold needed changing. No validator code touched.                               
                                                                                                                                                           
  ---                                                                                                                                                      
  Histogram vs Boxplot — when to use which

  | Question                              | Use        |
  |---------------------------------------|------------|                                                                                                   
  | What does the shape look like?        | Histogram  |
  | Where is the center and spread?       | Boxplot    |                                                                                                   
  | Are there outliers?                   | Boxplot    |
  | Compare distributions by category    | Boxplot    |                                                                                                    
  | Show frequency peaks and valleys      | Histogram  |
                                                                                                                                                           
  ---             