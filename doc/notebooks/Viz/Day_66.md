
======================== DAY 68 ======================
1_  why we need to do that  .str.split(', ')    ->  Split string into list  ["LEI004", "DATE007"]    

* Because the CSV stores multiple errors as one string in one cell

 | transaction_id   | error_codes          |                                                                                                                
  |------------------|----------------------|                                                                                                                
  | LC-0OXFQ8        | "LEI004, DATE007"    |  ← one string, two errors
  | LC-Q2Y9V8        | "LEI004, SHIP002"    |  ← one string, two errors                                                                                      
  | LC-ZCOTOH        | NaN                  |  ← clean, no errors 

  If you try to count validators directly on that column, pandas sees "LEI004, DATE007" as one value — not two. 
  You'd get garbage counts.                  
                                                                                                                                                           
  .str.split(', ') converts it:                                                                                                                            
                  
  "LEI004, DATE007"  →  ["LEI004", "DATE007"]                                                                                                              
                  
  Then .explode() does the heavy lifting — it takes that list and makes one row per item:                                                                  
   
  LC-0OXFQ8  →  LEI004                                                                                                                                     
  LC-0OXFQ8  →  DATE007   ← now each error is its own row  
  
  The full chain in cell 5 is:                                                                                                                             
  one string per LC  →  split  →  list per LC  →  explode  →  one row per error  →  extract prefix  →  count
=========================================================================================================

* 2_  What fig, ax = plt.subplots() actually does

Step 1 — plt.subplots() runs first (the right side)

Matplotlib creates two objects in memory:

- A Figure — the blank canvas (the entire window/image)
- An Axes — the actual chart area inside that canvas (with x-axis, y-axis, plot area)

Nothing is drawn on screen yet. These are just Python objects sitting in RAM.

Step 2 — tuple unpacking (the left side)

plt.subplots() returns a tuple: (figure_object, axes_object)

Python unpacks
it:                                                                                                                                               
fig = figure_object # the canvas
ax = axes_object # the chart area inside it

This is identical to writing:
result =
plt.subplots()                                                                                                                                          
fig = result[0]        
ax = result[1]
                  

Nothing is drawn yet

At fig, ax = plt.subplots(), the screen is still blank. You've only built the container. The drawing happens on the next
lines:

fig, ax = plt.subplots()          # build container — nothing visible
ax.bar(errors_per_validator.index, errors_per_validator.values)  # paint bars onto
ax                                                                            
plt.show()                        # render to screen
===============================================================================================================   

# 3_  .str.extract(r'^([A-Z]+)', expand=False)  -> expand= False?

● expand=False controls the return type, not the values. 

it's defensive — you're saying "I know this regex has one capture group, give me a Series, not a DataFrame." Without it, if pandas' 
 default ever changes, or you copy this pattern somewhere that expects a Series, it breaks silently.

*  Rule of thumb: when your regex has one group → expand=False. 
*  When it has multiple groups → expand=True (you want each group as its own column). 

 The Series inherits the name error_codes from the column it came from. 
 The DataFrame doesn't know what to call the column, so it just numbers it 0. 

without  expand=False column name is '0' 

 But in general — if you ever needed to merge or reference that column by name after the extract, 
 expand=False saves you from writing .rename(columns={0: 'validator'}) afterward.

==================================================================================================================== 

# 4_ what does plt.show() do other than rendering ?

1. Renders the figure to screen — you know this one.                                                                                                     
2. Clears the current figure from matplotlib's internal state — this is the hidden one.  

After plt.show(), the figure is gone from memory.


Banking analogy

Think of preparing a regulatory report:

┌─────────────┬──────────────────────────────────────────────┐
│ Code │ Analogy │                                                                                                   
├─────────────┼──────────────────────────────────────────────┤
│ fig │ The blank report document │
├─────────────┼──────────────────────────────────────────────┤
│ ax │ The table/chart section inside that document
│                                                                                                   
├─────────────┼──────────────────────────────────────────────┤                                                                                                   
│ ax.bar(...) │ Filling in the data
│                                                                                                   
├─────────────┼──────────────────────────────────────────────┤                                                                                                   
│ plt.show()  │ Printing and sending it │
└─────────────┴──────────────────────────────────────────────┘

# plt.subplots() is just saying: "Give me a blank document with one chart section ready."
                  
---                                                                                                                                                              
The key insight: fig and ax are objects. That's why you then call methods on ax like ax.bar(), ax.set_title() — you're
telling that specific object what to do.


# cell 7
All three are called on ax — the Axes object — because the labels belong to the chart area, not the canvas. Same object,
same OOP pattern.

Cell 7 is building a severity map — a lookup table that connects each validator to its severity level. Here's what each
step does:

Step 1 — build the DataFrame from
ALL_ERROR_CODES                                                                                                                
severity_map = pd.DataFrame([
{'error_code': code, 'severity':
info['severity']}                                                                                                           
for code, info in ALL_ERROR_CODES.items()         
])                                                                                                                                                               
ALL_ERROR_CODES is your source of truth in validation_rules.py — a dict like {'LEI001': {'severity': 'HIGH', ...}, ...}.
This list comprehension loops through it
and pulls out just the code and severity, then pd.DataFrame() turns that list into a table.

Step 2 — add the validator prefix
severity_map['validator'] = severity_map['error_code'].str.extract(
r'^([A-Z]+)')                                                                                 
Same regex you used in cell 4 — strips the letters off the front of the code (LEI001 → LEI). Now you know which
validator each code belongs to.

The result looks like this:

┌────────────┬──────────┬───────────┐                                                                                                                            
│ error_code │ severity │ validator
│                                                                                                                            
├────────────┼──────────┼───────────┤
│ LEI001 │ HIGH │ LEI │
├────────────┼──────────┼───────────┤
│ LEI002 │ HIGH │ LEI
│                                                                                                                            
├────────────┼──────────┼───────────┤
│ DATE001 │ MEDIUM │ DATE
│                                                                                                                            
└────────────┴──────────┴───────────┘

Why build this? The next cell will use it to color the bars by severity — HIGH bars red, MEDIUM orange, etc. You need
this map to know which color to assign to  
each validator.

validator_severity = (                                                                                                                                           
severity_map
.groupby('
validator')['severity']                                                                                                                            
.agg(lambda s: s.mode().iloc[0])
)

# CELL 8

What it's doing

Goal: For each validator (LEI, DATE, AMT...), find its most common severity level.

Step by step:

.groupby('validator') — split the table into groups, one per validator. LEI gets all LEI rows, DATE gets all DATE rows,
etc.

['severity'] — inside each group, look only at the severity column.

.agg(...) — for each group, run a function and collapse it to one value.
   
---                                                                                                                                                              
.agg() in detail

.agg() means aggregate — take many rows and produce one result per group.

You can pass it a named function or a lambda:

┌────────────────┬──────────────────────────────────┬──────────────────────┐                                                                                     
│ What you pass │ Example │ Result │
├────────────────┼──────────────────────────────────┼──────────────────────┤                                                                                     
│ Named function │ .agg('mean')                     │ average of the group │
├────────────────┼──────────────────────────────────┼──────────────────────┤
│ Named function │ .agg('sum')                      │ sum of the group

├────────────────┼──────────────────────────────────┼──────────────────────┤
│ Lambda │ .agg(lambda s: s.mode().iloc[0]) │ your custom logic
│                                                                                     
└────────────────┴──────────────────────────────────┴──────────────────────┘

Here the lambda is: lambda s: s.mode().iloc[0]

- s is the Series of severity values for that group (e.g. ['HIGH', 'HIGH', 'MEDIUM'])
- .mode() returns the most frequent value(s) as a Series — could be more than one if there's a tie
- .iloc[0] takes the first one to guarantee a single value
                                                                                                                                                             
Banking analogy

Imagine you have 200 LC transactions grouped by applicant country. You want one risk label per country — the most common
severity seen. .agg() is exactly that
operation: many rows in, one verdict out.

When .mode() runs on ['HIGH', 'MEDIUM', 'CRITICAL'] — every value appears exactly once. There's no winner. That's a
three-way tie.
   
                                                                                                                                                            
What .mode() returns on a tie

When tied, .mode() returns all tied values, sorted alphabetically:

pd.Series(['HIGH', 'MEDIUM', 'CRITICAL']).mode()

# → ['CRITICAL', 'HIGH', 'MEDIUM']   ← alphabetical order

Then .iloc[0] blindly grabs the first one → CRITICAL.

Not because CRITICAL is the most common. Because C comes before H and M.
                  
                                                                                                                                                             
Why this is fragile

.mode() + .iloc[0] was written to handle ties silently — it doesn't crash, doesn't warn you, just picks. For most
validators with many codes of the same
severity, it works fine. For XVAL with 3 codes of 3 different severities, it's basically alphabetical sorting pretending
to be statistics.
                  
---                                                                                                                                                              
The robust fix (for later)

For regulatory reporting you'd want worst-wins logic instead:

SEVERITY_ORDER = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}

.agg(lambda s: min(s, key=lambda x: SEVERITY_ORDER[x]))

This always picks the most serious severity, regardless of how many codes exist or how they tie.
                  
                                                                                                                                                            
The lesson: .agg() with a lambda gives you flexibility — but you own the logic. A silent tiebreaker is fine for a chart,
dangerous in a compliance report.

## Cell 10

 Cell #10 is the bar_colors builder — the one with .reindex().map().tolist().

  ---
  Here's what each line does, step by step:

  The problem it solves first: you have two Series with different sort orders.

  - validator_severity (cell #9) → sorted alphabetically by groupby: AMT, BIC, DATE, LC, LEI, PTY, SHIP, XVAL
  - errors_per_validator (cell #5) → sorted by frequency (most errors first): LEI, SHIP, AMT, XVAL, DATE, LC, BIC, PTY

  The bars on the chart follow errors_per_validator's order. If you just mapped colors from validator_severity, the colors would be misaligned — LEI's bar
  would get AMT's color.

  ---
  Line by line:

  bar_colors = (
      validator_severity
      .reindex(errors_per_validator.index)   # 1
      .map(SEVERITY_COLORS)                  # 2
      .tolist()                              # 3
  )

  1. .reindex(errors_per_validator.index)
  Reorders validator_severity to match the bar chart's order.
  Before: AMT→CRITICAL, BIC→HIGH, ... (alphabetical)
  After: LEI→HIGH, SHIP→HIGH, AMT→CRITICAL, ... (frequency order — same as bars)

  2. .map(SEVERITY_COLORS)
  Replaces each severity string with its hex color from the dict you defined in cell 1.
  LEI→HIGH becomes LEI→'#DC143C', AMT→CRITICAL becomes AMT→'#8B0000', etc.

  3. .tolist()
  Converts the pandas Series into a plain Python list. Matplotlib's color= parameter wants a list, not a Series.

  ---
  The output explained:

  ['#DC143C',  ← LEI   (HIGH, crimson)
   '#DC143C',  ← SHIP  (HIGH, crimson)
   '#8B0000',  ← AMT   (CRITICAL, dark red)
   '#8B0000',  ← XVAL  (CRITICAL, dark red)
   '#DC143C',  ← DATE  (HIGH, crimson)
   '#8B0000',  ← LC    (CRITICAL, dark red)
   '#DC143C',  ← BIC   (HIGH, crimson)
   '#FFA500']  ← PTY   (MEDIUM, orange)

  8 bars → 8 colors, in the exact same order. Matplotlib paints them left to right.

  ---
  Banking parallel: Every compliance dashboard you've ever seen uses exactly this logic. In AML systems, transaction risk scores map to RAG colors
  (Red/Amber/Green) — the score is the "severity", the color dict is the SEVERITY_COLORS, and .map() is what links them. Same pattern, different domain.



bar_colors = (                                                                                                                                                   
validator_severity
.reindex(
errors_per_validator.index)                                                                                                                         
.map(SEVERITY_COLORS)
.tolist()                                                                                                                                                    
)

Three steps chained together:


.reindex(errors_per_validator.index)

validator_severity is sorted alphabetically (AMT, BIC, DATE...). But your chart bars are ordered by error count (LEI
first, then SHIP, AMT...). These two orders
don't match.

.reindex() reorders validator_severity to match the bar order exactly — so color[0] lines up with bar[0], color[1] with
bar[1], etc.
                  
                                                                                                                                                            
.map(SEVERITY_COLORS)

Replaces each severity label with its hex color using the dict from cell 1:

SEVERITY_COLORS = {
'CRITICAL': '
#8B0000',                                                                                                                                       
'HIGH':     '#DC143C',
'MEDIUM':   '#FFA500',
...                                                                                                                                                          
}

So 'HIGH' becomes '#DC143C', 'MEDIUM' becomes '#FFA500', etc.
   
                                                                                                                                                            
.tolist()

ax.bar() expects a plain Python list of colors, not a pandas Series. This converts it.
                                                                                                                                                                   

The result is something like:

['#DC143C', '#DC143C', '#DC143C', '#FFA500', ...]

# LEI=HIGH   SHIP=HIGH   AMT=HIGH   DATE=MEDIUM

# cell 12

Why Patch?

Matplotlib's legend normally auto-detects what to show — but it can only do that for lines and scatter points. For bar
charts with custom colors, it doesn't know
what each color means. You have to tell it manually using proxy artists — objects that exist only to appear in the
legend, not on the chart.

Patch is the simplest proxy: a colored rectangle with a label.
                  
                                                                                                                                                           
Step by step:

.reindex(errors_per_validator.index) — same as cell 10, align to bar order.

.unique() — get only the severity levels that actually appear in this chart (no point showing NONE or LOW in the legend
if no validator has them).

The list comprehension builds one Patch per
severity:                                                                                                            
Patch(facecolor='#DC143C', label='HIGH')
Patch(facecolor='#FFA500',
label='MEDIUM')                                                                                                                       
...
                                                                                                                                                             
Then in the chart:
ax.legend(handles=legend_elements, title='Severity (most common)')

handles= is how you pass your manual proxy list to the legend. Without it, the legend would be empty.
                                                                                                                                                            
Banking analogy: Think of it like a map key on a risk report. The colored bars tell the story; the legend tells the
reader what the colors mean. The Patch       
objects are just the colored squares in that key — they represent data without being data.

"Cross-validation catches softer issues — country mismatches, same-party transactions. They're suspicious but not
deal-breakers.
The HARD errors come from format/content validators (LEI, BIC, DATE) where data is either structurally correct or it
isn't."


 1. .str.split(', ').explode()                                                                                                                            
  The CSV stores multiple errors as one string ("LEI004, DATE007"). split breaks it into a list, explode turns each list item into its own row. Without    
  this, pandas counts "LEI004, DATE007" as one value — garbage counts.                                                                                     
                                                                                                                                                           
  ---             
  2. fig, ax = plt.subplots()                                                                                                                              
  plt.subplots() creates two objects and returns them as a tuple. The left side unpacks that tuple: fig = the canvas (whole window), ax = the chart area   
  inside it. Nothing renders until plt.show().
                                                                                                                                                           
  ---             
  3. expand=False in .str.extract()                                                                                                                        
  Controls return type, not values. One capture group → pass expand=False → you get a Series (keeps the column name). Without it, you get a DataFrame with
  a nameless column 0. Saves you from writing .rename() afterward.
                                                                                                                                                           
  ---
  4. plt.show() does two things                                                                                                                            
  Renders to screen and clears the figure from matplotlib's internal state. After it runs, that fig is gone. If you call fig.savefig() after plt.show(),
  you get a blank file — save first, show second.
                                                                                                                                                           
  ---
  5. Cell 7 — labels belong to ax, not fig                                                                                                                 
  ax.set_title(), ax.set_xlabel(), ax.set_ylabel() — all on ax because they label the chart area, not the canvas. Same OOP pattern: you call methods on the
   object that owns the thing.
                                                                                                                                                           
  ---
  6. Cell 8 — severity_map from source of truth                                                                                                            
  Loops through ALL_ERROR_CODES (your config, not hardcoded) and builds a DataFrame with error_code + severity. Then extracts the validator prefix (LEI001 
  → LEI) with the same regex from cell 5. Purpose: build a lookup table so next cells can color bars by severity.
                                                                                                                                                           
  ---
  7. Cell 9 — .groupby().agg(lambda s: s.mode().iloc[0])                                                                                                   
  Groups all codes by validator, then picks the most common severity per group. The fragile part: if there's a tie, .mode() returns all tied values sorted 
  alphabetically and .iloc[0] blindly takes the first. CRITICAL wins ties not because it's worst — because C comes first. For a chart it's fine; in a
  compliance report, use worst-wins logic instead.                                                                                                         
                  
  ---                                                                                                                                                      
  8. Cell 10 — .reindex().map().tolist()
  validator_severity is alphabetical, bars are sorted by error count — they don't match. .reindex() re-sorts severity to match bar order.                  
  .map(SEVERITY_COLORS) swaps severity strings for hex colors. .tolist() converts Series → plain list (what matplotlib's color= expects).
                                                                                                                                                           
  ---             
  9. Cell 12 — Patch proxy artists                                                                                                                         
  Matplotlib auto-detects legend entries for lines/scatter, not for bars with custom colors. Patch is a colored rectangle that exists only for the legend —
   it represents data without being drawn on the chart. ax.legend(handles=legend_elements) is how you pass it in manually. Without handles=, the legend is
  empty.                                                                                                                                                   


● bbox_to_anchor is the coordinate system for placing the legend relative to the axes box. Here's the mental model:                                        
                                                                                                                                                           
  (0,1) -------- (1,1)                                                                                                                                     
    |               |                                                                                                                                      
    |   chart area  |
    |               |                                                                                                                                      
  (0,0) -------- (1,0)
                                                                                                                                                           
  (0,0) = bottom-left corner of the chart. (1,1) = top-right corner. These are the axes boundaries — not pixels.                                           
                                                                                                                                                           
  So bbox_to_anchor=(1.05, 1) means:                                                                                                                       
  - x = 1.05 → just past the right edge of the chart (1.0 would be exactly on the edge, 1.05 adds a small gap)
  - y = 1 → at the top                                                                                                                                     
                      
  And loc='upper left' tells matplotlib which corner of the legend box itself to stick at that coordinate. So the full instruction reads:                  
                                                                                                                                                           
  ▎ "Place the upper-left corner of the legend box at position (1.05, 1) — just outside the chart's top-right."                                            
                                                                                                                                                           
  That's why the legend ends up floating to the right, aligned with the top of the bars.                                                                   
                  
  Why plt.tight_layout() is required here:                                                                                                                 
  Once the legend is outside the axes, matplotlib doesn't automatically resize the figure to fit it — the legend gets clipped. tight_layout() recalculates
  spacing so nothing is cut off.                                                                                                                           
                  
  ---                                                                                                                                                      
  The two parameters always work as a pair:
                                                                                                                                                           
  | loc=         | bbox_to_anchor=  | result                         |
  |--------------|------------------|--------------------------------|                                                                                     
  | 'upper left' | (1.05, 1)        | legend outside, top-right      |                                                                                     
  | 'upper left' | (0.5, -0.1)      | legend outside, bottom-center  |                                                                                     
  | 'lower right'| (1.05, 0)        | legend outside, bottom-right   |                                                                                     
                  
  loc = which corner of the legend box is the "nail". bbox_to_anchor = where that nail goes on the canvas.                                                 
     
##  why we use x = 1.05 → instead 1                                                                                                                          
                                                                                
● Because x=1.0 puts the legend's left edge exactly on the chart's right edge — they touch, zero gap.                                                      
                                                                                                                                                           
  x=1.0  →  legend flush against the chart, touching it                                                                                                    
  x=1.05 →  legend with a small breathing gap to the right                                                                                                 
                                                                                                                                                           
  Visually:                                                                                                                                                
                                                                                                                                                           
  # x = 1.0  (touching)
  |  chart area  |[LEGEND]                                                                                                                                 
                                                                                                                                                           
  # x = 1.05  (gap)                                                                                                                                        
  |  chart area  |  [LEGEND]                                                                                                                               
                  ↑
               5% of axes width                                                                                                                            
   
  The 0.05 is not pixels or inches — it's 5% of the axes width. So on a wide chart it's a bigger gap, on a narrow chart a smaller one. It scales           
  automatically.  
                                                                                                                                                           
  In practice, 1.0 works but looks cramped. 1.05 is the conventional "just outside with breathing room" value — you'll see it copy-pasted across matplotlib
   docs everywhere for exactly this pattern.
                
```   