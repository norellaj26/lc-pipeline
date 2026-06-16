```python

## CEll 21
-----------
Why subplots matter
A single chart answers ONE question. A dashboard answers many questions at a glance. Watch the difference:

| Single chart                  | Dashboard (4 subplots) |
|--------------                 |------------------------|
| "Which validator fails most?" | PLUS "What's the severity breakdown?" |
| (bar chart only)              | PLUS "Which countries have issues?" |
|  | PLUS "Clean vs flagged ratio?" |

Day 67
------
fig, ax = plt.subplots()          # ONE Axes
ax.bar(...)

fig, axes = plt.subplots(2, 2)    # FOUR Axes in a 2x2 grid

Day 68
------
fig, axes = plt.subplots(2, 2)    # FOUR Axes in a 2x2 grid


Two changes:
------------
| Change           | Why |
|----------------- |-----|
| (2, 2) arguments | rows, columns — creates a grid |
| `axes` (plural)  | Now it's an ARRAY of 4 Axes, not one |

plt.subplots(2, 2) returns:

1 Figure (the whole canvas)
A 2×2 numpy array of 4 Axes objects 
( numpy -> Numerical Python )

Accessing individual charts

With 4 axes in a grid, you index them like a matrix:

| Position     | Index      | What's there |
|------------------------------------------
| Top-left     | axes[0, 0] | First chart |
| Top-right    | axes[0, 1] | Second chart |
| Bottom-left  | axes[1, 0] | Third chart |
| Bottom-right | axes[1, 1] | Fourth chart |

Visual mental model:
--------------------
       col 0         col 1
      ┌─────────┬─────────┐
row 0 │ [0, 0]  │ [0, 1]  │
      ├─────────┼─────────┤
row 1 │ [1, 0]  │ [1, 1]  │
      └─────────┴─────────┘
Same indexing as pandas .iloc[row, col]. Same as numpy arrays. Same as Excel cells conceptually. 

Why figsize grows with subplots
Rule of thumb:
--------------

| Grid               | figsize suggestion |
|-----               |-------------------|
| 1×1 (single)       | (10, 6) |
| 1×2 (side-by-side) | (14, 6) |
| 2×1 (stacked)      | (10, 10) |
| 2×2 (quad)         | (14, 10) |
| 3×3 (nine)         | (16, 14) |


┌─────────────┬─────────────┐
│  axes[0,0]  │  axes[0,1]  │    ← row 0
├─────────────┼─────────────┤
│  axes[1,0]  │  axes[1,1]  │    ← row 1
└─────────────┴─────────────┘


## CEll 22
------------

| Position            | Chart                             | Question it answers |
|----------|-------|---------------------|
| [0, 0] top-left     | Errors by validator (yesterday's) | "Where are the problems?" |
| [0, 1] top-right    | Clean vs Flagged pie/donut        | "How big is the backlog?" |
| [1, 0] bottom-left  | Errors by severity                | "How urgent is the backlog?" |
| [1, 1] bottom-right | Flagged transactions by country   | "Where do bad LCs come from?" |

That's literally the only conceptual change. ax → axes[0, 0]. Same methods, same parameters, same everything. 🎯
Why I shortened the title
"Errors Found by Validator — LC Pipeline" was perfect for a standalone chart. 
But inside a dashboard, the dashboard title will say "LC Pipeline" — so repeating it in every subplot is noise.
 Una regla de deck design:

| Context | Title style |
|---------|-------------|
| Standalone chart | Full descriptive title |
| Subplot in dashboard | Short, specific to subplot |
| Dashboard itself | Grand context title (e.g., "LC Pipeline Overview") |

"Errors by Validator" is enough when the reader already knows they're looking at an LC pipeline dashboard. 
Less ink, clearer hierarchy. ✨

## CEll 23
------------

Pie chart with a twist — why the "donut"
Pure pie charts get bad press in the data viz community, and with reason:


| Pie chart sin | Why it's a problem |
|---------------|-------------------|
| Hard to compare slices of similar size | 48% vs 52% looks identical |
| No zero baseline | Humans can't read angles well |
| Fails for 5+ categories | Becomes unreadable confetti |

BUT — for 2-3 categories with dramatically different sizes, pie charts ARE fine. 36% vs 64% is visually obvious. 
And the donut variant (pie with a hole) has one huge advantage: you can put the total in the center, turning it into a KPI card.
Cuando tienes 2 categorías grandes y claras + quieres mostrar un total → donut chart es la jugada correcta. 🍩

## CELL 24
-----------

 Parameter by parameter:                                                      
                                                                                                                                                           
  ┌────────────┬──────────────────────┬───────────────────────────────────────────────────────────┐
  │ Parameter  │        Value         │                       What it does                        │
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤                                                        
  │ values     │ [128, 72]            │ the slice sizes                                           │
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤                                                        
  │ labels     │ ['FLAGGED', 'CLEAN'] │ text on each slice                                        │
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤
  │ colors     │ crimson / green      │ RAG colors from your pipeline                             │
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤
  │ autopct    │ '%1.0f%%'            │ prints 64% / 36% on each slice                            │                                                        
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤
  │ startangle │ 90                   │ first slice starts at 12 o'clock, not 3 o'clock           │                                                        
  ├────────────┼──────────────────────┼───────────────────────────────────────────────────────────┤                                                        
  │ wedgeprops │ {'width': 0.4}       │ this is what makes it a donut — cuts a hole in the middle │
  └────────────┴──────────────────────┴───────────────────────────────────────────────────────────┘                                                        
                                                                                
  Without wedgeprops={'width': 0.4} it's a plain pie. That one parameter punches the hole.                                                                 
                                                                                
  Banking context: Donut charts are the default for portfolio health dashboards — 
  compliance teams everywhere use the center hole to drop a KPI number     
  (like 64% flagged). You'll see this exact layout in trade finance MIS reports.

## CELL 25
----------

Severity breakdown
Position: axes[1, 0] (bottom-left)
Business question
"Of all 237 errors, how urgent are they?"
The Pareto chart top-left tells us WHERE errors come from (LEI vs SHIP vs AMT). 
This new chart tells us HOW BAD they are overall. Different question, different chart. 
Cada subplot answers ONE question — never overload. 🎯

The data prep
For this we go back to the source-of-truth pattern from Day 66. Cada error individual has its own severity, not just the validator's mode:

| Step | What it does |
|------|-------------|
| .query("...")    | Filter to flagged rows only |
| ['error_codes']  | Grab the comma-separated string column |
| .str.split(', ') | "LEI004, BIC002" → ["LEI004", "BIC002"] |
| .explode()       | One error per row, NOT per transaction |
| .map(error_severity_map) | Each code → its real severity from source of truth |
| .value_counts()  | Final counts per severity tier |



## CELL 26
----------

Why I named it bars2 (not bars)
Because bars from the top-left chart still exists in memory. If you reuse bars, no immediate bug — but it's a code smell. 
Distintos charts = distintas variables. Cuando luego haces dashboards de 6+ charts, esto te salva. 🏷️
Why no legend on this one
The X-axis labels (CRITICAL, HIGH, MEDIUM, LOW) ARE already the severity names. 
A legend mapping color → severity would be redundant — the bars are literally labeled with their severity. 
Don't add legends that repeat the X-axis. Es ruido visual. 🎨


Banking context

| Pattern               | What it tells compliance |
|---------|-------------------------|
| HIGH dominates (>50%) | Recoverable issues — train the data entry team |
| CRITICAL dominates    | Escalation — root-cause analysis required THIS WEEK |
| Even spread           | Diverse problems — need multiple workstreams |
| LOW dominates         | Cosmetic issues — low priority, schedule cleanup |

In real banking, this exact chart drives resourcing decisions. CRITICAL backlog of 80 errors? You staff a war room. 
LOW backlog of 80 errors? You add it to next quarter's backlog. Same number, totally different response. 🏦


 can u read # 25                                                                                                                            
                                                                                                                                             
● Reading the notebook now.                                                                                                                  
                                                                                                                                             
  Read 1 file (ctrl+o to expand)             
                                                                                                                                             
● Got it. Here's cell 25:                                                                                                                    
                                                                                                                                             
  # Get severity for EVERY error code (one row per error)                                                                                    
  flagged_errors = (                                                                                                                         
      df.query("validation_status == 'FLAGGED'")                                                                                             
        ['error_codes']                                                                                                                      
        .str.split(', ')                                                                                                                     
        .explode()                                                                                                                           
  )               

  error_severity_map = {code: info['severity'] for code, info in ALL_ERROR_CODES.items()}

  severity_counts = flagged_errors.map(error_severity_map).value_counts()                                                                    
  severity_counts
                                                                                                                                             
  What it does — three steps:

  Step 1 — Flatten the error codes.                                                                                                          
  Each flagged LC row has a string like "LEI004, DATE007". .str.split(', ') turns that into a list ["LEI004", "DATE007"]. .explode() then
  breaks the list apart so each code becomes its own row — 237 rows total, one per error.                                                    
                  
  Step 2 — Build the severity lookup.                                                                                                        
  {code: info['severity'] for code, info in ALL_ERROR_CODES.items()} is a dict comprehension reading straight from your config source of
  truth. Result: {'AMT001': 'CRITICAL', 'LEI004': 'HIGH', ...}.                                                                              
   
  Step 3 — Map + count.                                                                                                                      
  .map(error_severity_map) swaps each code for its severity label. .value_counts() counts how many errors land at each level.
                                                                                                                                             
  Banking analogy: This is exactly how a compliance officer triages a batch of LC discrepancies before the 5-day UCP 600 examination window  
  closes. You don't treat all 237 equally — you sort by urgency first. 158 HIGH + 45 CRITICAL = 203 that need same-day attention; the 3 LOW  
  ones go to the bottom of the pile.                                                                                                         
                  
❯ # 26 pls                                                                                                                                   
                                                                                                                
● Let me re-read the notebook — cell 26 may have been added since I last loaded it.                                                          
                                                                                                                                             
  Read 1 file (ctrl+o to expand)                                                                                                             
                                                                                                                                             
● Cell 26:                                                                                                                                   
                                                                                                                                             
  # Match colors to severities, in the order they appear                    
  severity_bar_colors = [SEVERITY_COLORS[sev] for sev in severity_counts.index]                                                              
                                                                                                                                             
  # THE DASHBOARD CELL — everything here together                                                                                            
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))                                                                                           
                                                                                                                                             
  # Top-left: validator bars
  bars = axes[0, 0].bar(...)                                                                                                                 
  ...             

  # Top-right: donut
  axes[0, 1].pie(...)

  # Bottom-left: severity bars  ← NEW                                                                                                        
  bars2 = axes[1, 0].bar(severity_counts.index, severity_counts.values, color=severity_bar_colors)
  axes[1, 0].bar_label(bars2, padding=3)                                                                                                     
  axes[1, 0].set_title('Errors by Severity (237 total)')                                                                                     
  axes[1, 0].set_xlabel('Severity')
  axes[1, 0].set_ylabel('Error Count')                                                                                                       
                                                                                                                                             
  What's new vs cell 24:
                                                                                                                                             
  Line 1 — severity_bar_colors.                                                                                                              
  List comprehension: for each severity in severity_counts.index (HIGH, CRITICAL, MEDIUM, LOW — in that order), grab its color from
  SEVERITY_COLORS. This is simpler than the bar_colors trick in cell 10 — no .reindex() needed because you're reading directly from the data 
  you already have.
                                                                                                                                             
  axes[1, 0] — bottom-left slot of the 2×2 grid. The grid is:                                                                                
  [0,0] validator bars  |  [0,1] donut
  [1,0] severity bars   |  [1,1] (empty so far)                                                                                              
                                                                                                                                             
  bars2 — same pattern as cell 17: store the return value of .bar() so you can hand it to .bar_label(). The 2 in bars2 just distinguishes it
  from bars in the same cell.                                                                                                                
                  
  Banking read: The bottom-left panel answers the question a UCP 600 examiner asks first — "what's the urgency mix?" 158 HIGH + 45 CRITICAL  
  means 85% of errors need same-day resolution before the 5-day examination window closes. The 3 LOW ones are basically notes.
                                                                                                                                             
❯ #  29 pls                                                                                                                                  
                                                                            
  Read 1 file (ctrl+o to expand)                                                                                                             
                                                                                                                                             
● Cell 29 is the complete dashboard — same four panels as cell 28, with two new lines at the end:                                            
                                                                                                                                             
  fig.suptitle('LC Pipeline — Validation Dashboard', fontsize=16, fontweight='bold')                                                         
  plt.tight_layout(rect=[0, 0, 1, 0.96])                                                                                                     
  plt.show()                                                                                                                                 
                                                                                                                                             
  That's the only diff from cell 28. Let me break those two lines down:                                                                      
                                                                                                                                             
  fig.suptitle(...)                                                                                                                          
  sup = "super" — a title for the whole figure, not any single subplot. ax.set_title() titles one panel; fig.suptitle() titles all of them
  together. It sits above the 2×2 grid.                                                                                                      
   
  plt.tight_layout(rect=[0, 0, 1, 0.96])                                                                                                     
  tight_layout() alone auto-fixes spacing so panels don't overlap each other. The problem: it doesn't know about the suptitle you just added,
   so the title crashes into the top panels.                                                                                                 
                  
  rect=[left, bottom, right, top] tells tight_layout to work inside a smaller box — leave the top 4% (0.96 instead of 1.0) free for the      
  suptitle to breathe.
                                                                                                                                             
  # The rect coordinates are fractions of the figure (0–1):                                                                                  
  rect = [0,    0,    1,    0.96]                                                                                                            
         left  bottom right  top ← shrink layout to 96% height                                                                               
                                                                                                                                             
  Banking analogy: This is the executive summary header on a compliance report — the four panels are the detail sections, suptitle is the    
  cover page title that tells the audience exactly what they're looking at before they dig in.                                               


## Cell 22
                                                                                                                                             
                                                                                                                                                         
  status_counts = df['validation_status'].value_counts()                                                                                                   
                                                                                                                                                           
  axes[0, 1].pie(                                                                                                                                          
      status_counts.values,
      labels=status_counts.index,
      colors=['#DC143C', '#28A745'],
      autopct='%1.0f%%',                                                                                                                                   
      startangle=90,
      wedgeprops={'width': 0.4}                                                                                                                            
  )               
  axes[0, 1].set_title('Clean vs Flagged (200 LCs)')
                                                                                                                                                           
  ---
  status_counts = df['validation_status'].value_counts()                                                                                                   
  Counts how many rows per status. Result:              
  FLAGGED    128
  CLEAN       72                                                                                                                                           
  The index is the labels, the values are the slice sizes.
                                                                                                                                                           
  ---                                                                                                                                                      
  axes[0, 1].pie(...)
  You're inside the 2×2 dashboard — [0, 1] = top row, second column (top-right slot). Same .pie() method you'd call on ax, just targeting one specific     
  subplot.        
                                                                                                                                                           
  ---             
  The parameters one by one:                                                                                                                               
                            
  status_counts.values → [128, 72] — the raw numbers that determine how big each slice is.
                                                                                                                                                           
  labels=status_counts.index → ['FLAGGED', 'CLEAN'] — the text shown next to each slice. Pulled directly from the Series index so they stay in sync with   
  the values automatically.                                                                                                                                
                                                                                                                                                           
  colors=['#DC143C', '#28A745'] → red for FLAGGED, green for CLEAN. Order matches the order of status_counts.values — first value gets first color. This is
   the same RAG convention your whole pipeline uses.
                                                                                                                                                           
  autopct='%1.0f%%' → prints the percentage inside each slice. Breaking it down:                                                                           
  %1.0f  →  float, 0 decimal places  (64 not 64.0)
  %%     →  literal % sign (one % would be interpreted as a format character)                                                                              
  So you get 64% and 36% on the slices.                                                                                                                    
                                                                                                                                                           
  startangle=90 → where the first slice begins. Default is 0 = 3 o'clock (right side). 90 = 12 o'clock (top). Banking dashboards almost always start at 12 
  — it matches how people read clocks and pie charts naturally.                                                                                            
                                                                                                                                                           
  wedgeprops={'width': 0.4} → this is what makes it a donut. wedgeprops is a dict of styling options for the pie wedges. width controls the ring thickness 
  as a fraction of the radius:
  width=1.0  →  full pie (solid, no hole)                                                                                                                  
  width=0.4  →  ring that's 40% thick, 60% hollow center
  width=0.1  →  very thin ring                          
                                                                                                                                                           
  Visually:                                                                                                                                                
  width=1.0          width=0.4                                                                                                                             
    ████               ░███░                                                                                                                               
   ███████            ░░███░░                                                                                                                              
    ████               ░███░ 
    full pie            donut                                                                                                                              
                  
  ---                                                                                                                                                      
  Banking context: Donut charts are preferred over pie charts in compliance dashboards precisely because the hollow center gives you space to print a
  summary number — total transactions, total flagged, a KPI. You'll see this pattern in every Basel III or AML reporting tool.                             
                  
## Cell 26

● Cell 26:                                                                                                                                                 
                                                                                                                                                           
  # Match colors to severities, in the order they appear                                                                                                   
  severity_bar_colors = [SEVERITY_COLORS[sev] for sev in severity_counts.index]                                                                            
                                                                                                                                                           
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))                                                                                                         
   
  # Top-left: validator bars                                                                                                                               
  bars = axes[0, 0].bar(errors_per_validator.index, errors_per_validator.values, color=bar_colors)
  axes[0, 0].bar_label(bars, padding=3)                                                                                                                    
  axes[0, 0].set_title('Errors by Validator')
  axes[0, 0].set_xlabel('Validator')                                                                                                                       
  axes[0, 0].set_ylabel('Error Count')
  axes[0, 0].legend(handles=legend_elements, title='Severity', loc='upper right')                                                                          
   
  # Top-right: donut                                                                                                                                       
  axes[0, 1].pie( 
      status_counts.values,
      labels=status_counts.index,
      colors=['#DC143C', '#28A745'],                                                                                                                       
      autopct='%1.0f%%',
      startangle=90,                                                                                                                                       
      wedgeprops={'width': 0.4}
  )

  bars2 = axes[1, 0].bar(severity_counts.index, severity_counts.values, color=severity_bar_colors)                                                         
  axes[1, 0].bar_label(bars2, padding=3)
  axes[1, 0].set_title('Errors by Severity (237 total)')                                                                                                   
  axes[1, 0].set_xlabel('Severity')                                                                                                                        
  axes[1, 0].set_ylabel('Error Count')
                                                                                                                                                           
  plt.show()      

  ---
  What's new vs cell 24 — two additions:
                                                                                                                                                           
  1. severity_bar_colors — the first line
                                                                                                                                                           
  severity_bar_colors = [SEVERITY_COLORS[sev] for sev in severity_counts.index]
                                                                                                                                                           
  severity_counts (from cell 25) looks like this:                                                                                                          
  HIGH        158
  CRITICAL     45                                                                                                                                          
  MEDIUM       31 
  LOW           3
                 
  So severity_counts.index = ['HIGH', 'CRITICAL', 'MEDIUM', 'LOW']
                                                                                                                                                           
  The list comprehension loops through those severity names and pulls the hex color for each one directly from your dict:                                  
                                                                                                                                                           
  HIGH     → '#DC143C'                                                                                                                                     
  CRITICAL → '#8B0000'
  MEDIUM   → '#FFA500'
  LOW      → '#FFD700'                                                                                                                                     
   
  Result: ['#DC143C', '#8B0000', '#FFA500', '#FFD700']                                                                                                     
                  
  Compare with cell 10 — same goal, but simpler here:                                                                                                      
  Cell 10:  validator names → find severity → find color  (two lookups, needed .reindex())
  Cell 26:  severity names  → find color                  (one lookup, plain list comprehension)                                                           
  Cell 26 is simpler because severity_counts.index already contains the severity labels directly — no intermediate step needed.                            
                                                                                                                                                           
  ---                                                                                                                                                      
  2. The bottom-left panel — severity bars                                                                                                                 
                                                                                                                                                           
  bars2 = axes[1, 0].bar(severity_counts.index, severity_counts.values, color=severity_bar_colors)
  axes[1, 0].bar_label(bars2, padding=3)                                                                                                                   
  axes[1, 0].set_title('Errors by Severity (237 total)')
  axes[1, 0].set_xlabel('Severity')                                                                                                                        
  axes[1, 0].set_ylabel('Error Count')                                                                                                                     
   
  axes[1, 0] = bottom row, first column (bottom-left slot). Exact same ax.bar() pattern as cell 6 — just targeting a subplot instead of a standalone chart.
                  
  bars2 — stores the BarContainer so bar_label() can put numbers on top of each bar. Same pattern as cell 17, just a different variable name because bars  
  is already taken by the top-left chart.
                                                                                                                                                           
  ---             
  The dashboard grid so far after cell 26:

  | [0,0] Errors by Validator  |  [0,1] Donut            |
  | [1,0] Errors by Severity   |  [1,1] empty — next cell |                                                                                                
                                                                                                                                                           
  Cell 26 fills 3 of 4 panels. The bottom-right (country chart) comes in cell 28.       


## Cell 28

completes the dashboard by adding the bottom-right panel — the country chart. Everything else is identical to cell 26, so I'll focus on what's   
  new.                                                                                                                                                   
                                                                                                                                                           
  ---
  New data: flagged_by_country (from cell 27)                                                                                                              
                                                                                                                                                           
  XX     1
  GB     5                                                                                                                                                 
  TW     9        
  JP    14
  CH    16
  DE    19
  KR    24                                                                                                                                                 
  US    40
                                                                                                                                                           
  Sorted ascending on purpose — you'll see why in a second.                                                                                                
   
  ---                                                                                                                                                      
  New panel: axes[1, 1].barh()

  axes[1, 1].barh(
      flagged_by_country.index,   # country codes → Y axis                                                                                                 
      flagged_by_country.values,  # counts → X axis                                                                                                        
      color='#DC143C'                                                                                                                                      
  )                                                                                                                                                        
                  
  barh = horizontal bars. Axes are flipped vs bar:                                                                                                         
   
  ax.bar()   →  categories on X,  values on Y  (vertical bars ↑)                                                                                           
  ax.barh()  →  categories on Y,  values on X  (horizontal bars →)                                                                                         
                                                                                                                                                           
  So set_xlabel and set_ylabel are swapped too:                                                                                                            
  axes[1, 1].set_xlabel('Flagged Count')      # numbers → bottom                                                                                           
  axes[1, 1].set_ylabel('Applicant Country')  # labels → left side
                                                                                                                                                           
  Why ascending sort in cell 27?                                                                                                                           
  barh draws from bottom to top. Ascending order (smallest first) puts XX=1 at the bottom and US=40 at the top — the natural reading direction for a ranked
   list. If you used descending, US would be at the bottom and it'd feel upside-down.                                                                      
                  
  Why single color '#DC143C'?                                                                                                                              
  The comment in the code says it directly: country isn't a severity dimension. There's no "HIGH country" or "CRITICAL country" — just flagged counts.
  Color-coding by severity would be misleading here. One color, one story: volume by country.                                                              
   
  ---                                                                                                                                                      
  axes[1, 1].containers[0] — different from previous cells
                                                                                                                                                           
  Previous panels stored the BarContainer in a variable first:
  bars = axes[0, 0].bar(...)                                                                                                                               
  axes[0, 0].bar_label(bars, padding=3)
                                                                                                                                                           
  Here .barh() wasn't stored, so you reach back into the axes to grab it:
  axes[1, 1].bar_label(axes[1, 1].containers[0], padding=3)                                                                                                
                                                           
  .containers is a list of all bar groups on that axes. [0] = the first (and only) one. Functionally identical — just accessing it differently.            
                                                                                                                                                           
  ---                                                                                                                                                      
  Dashboard complete after cell 28:                                                                                                                        
                                                                                                                                                           
  | [0,0] Errors by Validator  |  [0,1] Clean vs Flagged donut |
  | [1,0] Errors by Severity   |  [1,1] Top Countries (barh)   |                                                                                           
                                                                                                                                                           
  All 4 panels filled. Cell 29 adds the title + tight_layout and that's the final version.      

## cell 29

fig.suptitle() in cell 29:                                                                                                    
                                                                                                                                                           
  fig.suptitle('LC Pipeline — Validation Dashboard', fontsize=16, fontweight='bold')                                                                       
  plt.tight_layout(rect=[0, 0, 1, 0.96])                                                                                                                   
                                                                                                                                                           
  ---                                                                                                                                                      
  The rect parameter defines how much of the figure tight_layout can use for the subplots. Format is [left, bottom, right, top] in figure coordinates (0 to
   1):                                                                                                                                                     
   
  rect=[0, 0, 1, 0.96]                                                                                                                                     
         ↑  ↑  ↑  ↑                                                                                                                                        
        left bottom right top
                                                                                                                                                           
  So: subplots can use from the left edge (0) to the right edge (1), from the bottom (0) up to 96% of the figure height (0.96).                            
   
  The top 4% is reserved for the suptitle.                                                                                                                 
                  
  ---                                                                                                                                                      
  Why it's needed:
                                                                                                                                                           
  fig.suptitle() sits above all subplots. Without rect, tight_layout expands the subplots to fill 100% of the figure — the title overlaps the top panels:
                                                                                                                                                           
  # Without rect        # With rect=[0,0,1,0.96]
                                                                                                                                                           
  [TITLE overlapping]   [      TITLE       ]   ← top 4%                                                                                                    
  |  panel  | panel  |  |  panel  | panel  |
  |  panel  | panel  |  |  panel  | panel  |   ← subplots in 96%                                                                                           
                                                                                                                                                           
  0.96 is a conventional value — just enough breathing room for one line of title text. If your title were two lines, you'd use something like 0.93.                                                                                                                     












```