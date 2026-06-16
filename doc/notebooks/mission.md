Section 1: Data Preparation
Goal: Build a clean, enriched "one row per error" DataFrame that will power the entire report.
You need:

Start from flagged
Explode error_codes into individual errors
Merge with error_lookup to get true severity and message per error
Extract the validator category (LEI, AMT, SHIP, etc.)
Keep transaction_id, currency, error_count from the original

This is the foundation — everything else depends on it. You've done every piece before. Combine them into one clean pipeline.
When you're done, show me:

The shape of the result
.head(10) of the final DataFrame 


— I can see exactly what tools you have from notebooks 03-04. Let me walk through Section 1 step by step.         
                                                  
  ---                                                                                                                           
  The goal: transform this:                                                                                                     
  transaction_id  error_codes                                                                                                   
  LC-0OXFQ8       LEI004, DATE007       ← 1 row, 2 errors as a string                                                           
  LC-Q2Y9V8       LEI004, SHIP002                                                                                               
                                                                                                                                
  Into this:                                                                                                                    
  transaction_id  error_code  severity  message  category  currency  error_count                                                
  LC-0OXFQ8       LEI004      HIGH      LEI not found...  LEI   USD   2                                                         
  LC-0OXFQ8       DATE007     MEDIUM    LC validity...    DATE  USD   2                                                         
  LC-Q2Y9V8       LEI004      HIGH      LEI not found...  LEI   GBP   2                                                         
  LC-Q2Y9V8       SHIP002     HIGH      Port missing...   SHIP  GBP   2                                                         
                                                                                                                                
  ---                                                                                                                           
  Step 1 — Explode error_codes (you saw this in notebook 04, cell 5)                                                            
                                                                                                                                
  error_codes is a string like "LEI004, DATE007". You need to:
  - split it on ", " to get a list ["LEI004", "DATE007"]                                                                        
  - explode so each item becomes its own row                                                                                    
   
  ---                                                                                                                           
  Step 2 — Build the error_lookup (notebook 04, cell 4)
                                                                                                                                
  You already saw how to build it from ALL_ERROR_CODES — a DataFrame with error_code, message, severity.
                                                                                                                                
  ---
  Step 3 — Merge (notebook 04, cell 6)                                                                                          
                                      
  Merge the exploded errors with error_lookup on error_code. Use how='left' and validate='many_to_one' — the safe pattern you
  already know.                                                                                                                 
   
  ---                                                                                                                           
  Step 4 — Extract the category (this is the new piece)
                                                                                                                                
  From "LEI004" → extract "LEI". From "DATE007" → extract "DATE".
                                                                                                                                
  The pattern: everything before the digits. You'll use .str accessor — something like:                                         
  df['error_code'].str.extract(r'([A-Z]+)')                                                                                     
  # or                                                                                                                          
  df['error_code'].str[:3]   # if all prefixes are 3 chars... but check SHIP, XVAL — they differ                                
  Look at your error codes and decide which approach fits.                                      
                                                                                                                                
  ---                                                                                                                           
  Step 5 — Bring back transaction_id, currency, error_count                                                                     
                                                                                                                                
  After exploding, you lose currency and error_count because you only kept transaction_id and error_codes before exploding. You
  need to merge those back from flagged using transaction_id as the key.                                                        
                  
  ---                                                                                                                           
  The shape check at the end:
                                                                                                                                
  .head(10) should show you 10 rows where some transaction_id values repeat — that's proof the explode worked correctly. One
  transaction with 3 errors = 3 rows.                                                                                           
                  
  ---                                                                                                                           
  The pieces are all from notebooks 03-04. The only new thing is the string extraction in Step 4. Try combining them and share
  what you write — I'll help if you get stuck.                                                                                  
   