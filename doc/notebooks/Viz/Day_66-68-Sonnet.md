Day 66 — First Charts: Bar Chart + Color + Legend                                                                                                      
                                                                                                                                                           
  The two matplotlib styles                                                                                                                                
                                                                                                                                                           
  # Style 1 — pyplot (state machine) — avoid this                                                                                                          
  plt.plot([1, 2, 3], [4, 5, 6])                                                                                                                           
  plt.title("My chart")                                                                                                                                    
  plt.show()                                                                                                                                               
                                                                                                                                                           
  # Style 2 — OOP — always use this                                                                                                                        
  fig, ax = plt.subplots()                                                                                                                                 
  ax.plot([1, 2, 3], [4, 5, 6])                                                                                                                            
  ax.set_title("My chart")                                                                                                                                 
  plt.show()                                                                                                                                               
                                                                                                                                                           
  fig = the whole window. ax = the chart inside it. OOP scales — when you have multiple charts, you need explicit references. pyplot's global state breaks 
  down.                                                                                                                                                    
                                                                                                                                                           
  ---                                                                                                                                                      
  Data prep — errors per validator                                                                                                                         
                                                                                                                                                           
  errors_per_validator = (                                                                                                                                 
      df.query("validation_status == 'FLAGGED'")                                                                                                           
        ['error_codes']                                                                                                                                    
        .str.split(', ')      # "LEI004, DATE007" → ["LEI004", "DATE007"]                                                                                  
        .explode()            # one row per error code                                                                                                     
        .str.extract(r'^([A-Z]+)', expand=False)  # "LEI004" → "LEI"                                                                                       
        .value_counts()                                                                                                                                    
  )                                                                                                                                                        
                                                                                                                                                           
  LEI     92                                                                                                                                               
  SHIP    45                                                                                                                                               
  AMT     27
  XVAL    24                                                                                                                                               
  DATE    17                                                                                                                                               
  LC      14
  BIC     11                                                                                                                                               
  PTY      7                                                                                                                                               
   
  ---                                                                                                                                                      
  Basic bar chart 

  fig, ax = plt.subplots()
  ax.bar(errors_per_validator.index, errors_per_validator.values)                                                                                          
   
  ax.set_title('Errors Found by Validator — LC Pipeline')                                                                                                  
  ax.set_xlabel('Validator')
  ax.set_ylabel('Error Count')                                                                                                                             
  plt.show()      

  Pattern: ax.bar(x_data, y_data) — index = bar positions, values = bar heights.                                                                           
   
  ---                                                                                                                                                      
  Color coding by severity
                          
  Step 1 — severity color map (source of truth):
  SEVERITY_COLORS = {                                                                                                                                      
      'CRITICAL': '#8B0000',   # Dark red
      'HIGH':     '#DC143C',   # Crimson red                                                                                                               
      'MEDIUM':   '#FFA500',   # Orange                                                                                                                    
      'LOW':      '#FFD700',   # Gold  
      'NONE':     '#28A745',   # Green                                                                                                                     
  }                                   
                                                                                                                                                           
  Step 2 — most common severity per validator (from config, not hardcoded):
  from config.validation_rules import ALL_ERROR_CODES                                                                                                      
                                                     
  severity_map = pd.DataFrame([                                                                                                                            
      {'error_code': code, 'severity': info['severity']}                                                                                                   
      for code, info in ALL_ERROR_CODES.items()                                                                                                            
  ])                                                                                                                                                       
  severity_map['validator'] = severity_map['error_code'].str.extract(r'^([A-Z]+)')                                                                         
                                                                                  
  validator_severity = (                                                                                                                                   
      severity_map      
      .groupby('validator')['severity']                                                                                                                    
      .agg(lambda s: s.mode().iloc[0])   # most common severity per validator
  )
                                                                                                                                                           
  AMT → CRITICAL   BIC → HIGH   DATE → HIGH   LC → CRITICAL
  LEI → HIGH       PTY → MEDIUM  SHIP → HIGH   XVAL → CRITICAL                                                                                             
                                                                                                                                                           
  Step 3 — map to colors in the right order:                                                                                                               
  bar_colors = (                                                                                                                                           
      validator_severity                                                                                                                                   
      .reindex(errors_per_validator.index)  # match chart's bar order
      .map(SEVERITY_COLORS)                                          
      .tolist()                                                                                                                                            
  )                                                                                                                                                        
                                                                                                                                                           
  .reindex() is critical — it aligns the severity series to match the exact order of bars in the chart. Without it, colors would be mismatched.            
                                                                                                                                                           
  ---
  Legend with Patch proxies                                                                                                                                
                           
  ax.bar() doesn't create legend entries automatically. You build fake colored rectangles (Patches) as proxies:
                                                                                                                                                           
  from matplotlib.patches import Patch
                                                                                                                                                           
  unique_severities = validator_severity.reindex(errors_per_validator.index).unique()                                                                      
   
  legend_elements = [                                                                                                                                      
      Patch(facecolor=SEVERITY_COLORS[sev], label=sev)
      for sev in unique_severities                                                                                                                         
  ]
                                                                                                                                                           
  ax.legend(handles=legend_elements, title='Severity (most common)')

  Three legend positions:                                                                                                                                  
   
  | Code                                              | Result               |                                                                             
  |---------------------------------------------------|----------------------|                                                                             
  | ax.legend(handles=..., title=...)                 | matplotlib picks best|
  | ax.legend(..., loc='upper right')                 | force top-right      |                                                                             
  | ax.legend(..., bbox_to_anchor=(1.05, 1), loc='upper left') + plt.tight_layout() | outside chart |                                                      
                                                                                                                                                           
  bbox_to_anchor=(1.05, 1) = place legend starting 5% to the right of the chart. Always pair with plt.tight_layout() so it doesn't get clipped.            
                                                                                                                                                           
  ---                                                                                                                                                      
  Day 67 — figsize, Bar Labels, Saving

  figsize

  fig, ax = plt.subplots(figsize=(10, 6))   # width × height in inches
                                                                                                                                                           
  Common sizes:
                                                                                                                                                           
  | Use case        | figsize      |                                                                                                                       
  |-----------------|--------------|
  | Default         | (6.4, 4.8)   |                                                                                                                       
  | Standard slide  | (10, 6)      |                                                                                                                       
  | Widescreen      | (16, 9)      |
                                                                                                                                                           
  ---             
  Bar labels — ax.bar_label()                                                                                                                              
                                                                                                                                                           
  # ax.bar() returns a BarContainer object — store it
  bars = ax.bar(errors_per_validator.index, errors_per_validator.values, color=bar_colors)                                                                 
                  
  # Pass the container to bar_label                                                                                                                        
  ax.bar_label(bars, padding=3)
                                                                                                                                                           
  ax.bar() doesn't just draw — it returns a BarContainer. You store it in bars so you can hand it to ax.bar_label(). padding=3 = 3 points of space between 
  bar top and label.
                                                                                                                                                           
  ---             
  Saving to file
                                                                                                                                                           
  fig.savefig('../data/output/errors_by_validator.png', dpi=300, bbox_inches='tight')
  plt.show()   # call AFTER savefig — show() clears the figure                                                                                             
                                                                                                                                                           
  dpi=300 = high resolution (print quality). bbox_inches='tight' = no clipping of labels or legends.                                                       
                                                                                                                                                           
  In production code use pathlib:                                                                                                                          
  from config import settings
  fig.savefig(settings.OUTPUT_DIR / 'errors_by_validator.png', dpi=300, bbox_inches='tight')
                                                                                                                                                           
  ---
  Day 68 — Subplots: The 2×2 Dashboard                                                                                                                     
                                                                                                                                                           
  Creating a subplot grid
                                                                                                                                                           
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))
                                                                                                                                                           
  axes is now a 2D array. Access each panel by position:                                                                                                   
   
  | Position    | Code          | Chart             |                                                                                                      
  |-------------|---------------|-------------------|                                                                                                      
  | Top-left    | axes[0, 0]    | Errors by Validator|
  | Top-right   | axes[0, 1]    | Clean vs Flagged  |                                                                                                      
  | Bottom-left | axes[1, 0]    | Errors by Severity|
  | Bottom-right| axes[1, 1]    | Countries         |                                                                                                      
                  
  ---                                                                                                                                                      
  Top-right: Donut chart
                                                                                                                                                           
  status_counts = df['validation_status'].value_counts()
  # FLAGGED: 128    CLEAN: 72                                                                                                                              
   
  axes[0, 1].pie(                                                                                                                                          
      status_counts.values,
      labels=status_counts.index,                                                                                                                          
      colors=['#DC143C', '#28A745'],   # Flagged=red, Clean=green
      autopct='%1.0f%%',              # percentage inside each slice                                                                                       
      startangle=90,                  # start at 12 o'clock
      wedgeprops={'width': 0.4}       # makes it a donut (not a full pie)                                                                                  
  )                                                                                                                                                        
  axes[0, 1].set_title('Clean vs Flagged (200 LCs)')                                                                                                       
                                                                                                                                                           
  wedgeprops={'width': 0.4} = the donut trick. Width is a fraction of the radius — 0.4 = 40% thick ring.                                                   
                                                                                                                                                           
  ---                                                                                                                                                      
  Bottom-left: Severity breakdown

  flagged_errors = (
      df.query("validation_status == 'FLAGGED'")                                                                                                           
        ['error_codes']
        .str.split(', ')                                                                                                                                   
        .explode()
  )
  error_severity_map = {code: info['severity'] for code, info in ALL_ERROR_CODES.items()}
  severity_counts = flagged_errors.map(error_severity_map).value_counts()                                                                                  
                                                                                                                                                           
  HIGH        158                                                                                                                                          
  CRITICAL     45                                                                                                                                          
  MEDIUM       31                                                                                                                                          
  LOW           3
                                                                                                                                                           
  severity_bar_colors = [SEVERITY_COLORS[sev] for sev in severity_counts.index]
                                                                                                                                                           
  bars2 = axes[1, 0].bar(severity_counts.index, severity_counts.values, color=severity_bar_colors)                                                         
  axes[1, 0].bar_label(bars2, padding=3)                                                                                                                   
  axes[1, 0].set_title('Errors by Severity (237 total)')                                                                                                   
                                                                                                                                                           
  ---
  Bottom-right: Horizontal bar — barh()                                                                                                                    
                                                                                                                                                           
  flagged_by_country = (
      df.query("validation_status == 'FLAGGED'")                                                                                                           
        ['applicant_country']
        .value_counts()                                                                                                                                    
        .head(10)
        .sort_values()    # ascending — biggest bar ends up at top after flip                                                                              
  )                                                                                                                                                        
   
  US    40    KR    24    DE    19    CH    16                                                                                                             
  JP    14    TW     9    GB     5    XX     1                                                                                                             
                                                                                                                                                           
  axes[1, 1].barh(flagged_by_country.index, flagged_by_country.values, color='#DC143C')                                                                    
  axes[1, 1].bar_label(axes[1, 1].containers[0], padding=3)                                                                                                
                                                                                                                                                           
  .barh() = horizontal bar. Country isn't a severity dimension so all bars get the same color. .containers[0] = the BarContainer when you didn't store the 
  return value.                                                                                                                                            
                                                                                                                                                           
  ---             
  Dashboard title + layout

  fig.suptitle('LC Pipeline — Validation Dashboard', fontsize=16, fontweight='bold')
  plt.tight_layout(rect=[0, 0, 1, 0.96])  # leave 4% at top for suptitle                                                                                   
  plt.show()                                                                                                                                               
                                                                                                                                                           
  fig.suptitle() = title for the whole figure (above all subplots). plt.tight_layout(rect=[...]) = auto-spacing that respects the suptitle space. Without  
  rect, tight_layout would overlap the suptitle.
                                                                                                                                                           
  fig.savefig('../data/output/dashboard_v1.png', dpi=300, bbox_inches='tight')

  ---