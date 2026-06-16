

Day 74 — Streamlit Intro (Part A — first half)

Today's Part A covers chunks 1-4. Tomorrow Part B covers chunks 5-8.
Slower pace = more room for stats prep in the afternoon.

                                       |
|----------------------------------------------------------------|
| 1. What Streamlit IS (and why it exists)                       |
| 2. Installation + first script                                 |
| 3. The fundamental Streamlit pattern                           |
| 4. Displaying text, data, and a first chart                    |
| 5. Layout primitives (columns, sidebar, tabs)                  |
| 6. Interactive widgets (sliders, selectbox)                    |
| 7. Connecting widgets to your data                             |
| 8. Mini-app: filter your validation report                     |

Chunk 1 — What Streamlit is (and why it exists)

Up until now, every chart you built lives in a notebook or a saved PNG.
That's perfect for analysis, but a STATIC PNG can't be queried. Your
boss can't click "show me only USD transactions" and watch the chart
update.

Streamlit solves this. It turns Python scripts into INTERACTIVE WEB APPS
without touching HTML, CSS, or JavaScript. You write Python, Streamlit
renders a browser app.

The mental shift — notebook vs streamlit app:

| Notebook                              | Streamlit app                   |
|---------------------------------------|---------------------------------|
| Cells run sequentially when you click | Whole script reruns on every    |
|                                       | user interaction                |
| Output appears below cells            | Output appears in browser       |
| You're the only user                  | Anyone with the URL is a user   |
| Charts are static images              | Charts can be dynamic           |
| Edit code → reload notebook           | Edit code → page auto-refreshes |
| .ipynb file                           | .py file                        |

The script is just a normal Python file. No special syntax to learn.
You import streamlit, call its functions to render UI, and Streamlit
handles the rest.

Why Streamlit specifically (vs alternatives):

| Tool            | Strength                       | Weakness                   |
|-----------------|--------------------------------|----------------------------|
| Streamlit       | Easiest, Python-native         | Not great for complex apps |
| Dash (Plotly)   | More control, callback model   | Steeper learning curve     |
| Flask + JS      | Full control                   | Need to learn web stack    |
| Tableau/PowerBI | Drag-drop, no code             | Not Python integrated      |
| Jupyter widgets | Stays in notebook              | Limited UI options         |

For a BI engineer who already knows pandas + matplotlib, Streamlit gives
you 80% of dashboard power for 10% of the learning effort. That's the
sweet spot. Banks adopt it widely because data scientists can ship apps
without involving frontend engineers. Internal tools, monitoring dashboards,
model demos — all common Streamlit use cases.


Chunk 2 — Installation + first script

Time to install Streamlit and run "hello world."
# In your terminal (NOT in the notebook), run:
# pip install streamlit

# Verify it installed:
# streamlit --version
# Should show: Streamlit, version 1.X.X

After installation, create a NEW file in your project:

streamlit_apps/
└── 01_hello_streamlit.py

Don't put this in notebooks/ — Streamlit apps are .py scripts, not .ipynb.
They live in their own folder. Same project, different file type.

If streamlit_apps/ doesn't exist yet, create it now. Project structure:

lc_pipeline/
├── config/
├── models/
├── validators/
├── services/
├── utils/
├── data/
├── notebooks/                  ← Jupyter exploration (Days 65-73)
└── streamlit_apps/             ← NEW — Streamlit apps (Days 74-78)
    └── 01_hello_streamlit.py   ← First file


Decoding the new Streamlit functions:

| Function            | What it does                                 |
|--------------------|------------------------------------------ -----|
| st.slider(label, min, max, default) | Renders slider, returns current value|
| st.divider()       | Horizontal line separator                     |
| st.caption(text)   | Small gray text (footer/note style)           |
| f'{age}'           | Live value of the slider, updates on rerun    |

The MAGIC line is `age = st.slider(...)`. It does TWO things at once:
1. Renders the slider widget in the browser
2. Returns whatever value the user has it set to

This is "declarative UI" — you describe WHAT should be on the page, and
Streamlit figures out HOW to keep it in sync. No event handlers needed.

After saving the file, watch the magic:

1. Streamlit auto-detects the file change
2. Top-right of browser shows: "File change. Rerun. Always rerun."
3. Click "Always rerun" — Streamlit will auto-reload on every save
4. The slider appears
5. Move the slider → "You picked: X" updates instantly
6. Look at the timestamp at the bottom — it changes EVERY time you move
   the slider

The timestamp is the proof. The whole script reruns on every interaction,
top to bottom, including that datetime.now() call. Y aún así, the page
update is instant. Streamlit is doing smart diffing under the hood.

Pro tip — the "Always rerun" button is your best friend:

Click it ONCE per session. After that, every time you save your .py file:
1. Streamlit detects the change
2. Reruns the script automatically
3. Page updates without any manual click

This turns your editor into a live preview. Save = see. Save = see.
Tightest feedback loop possible. Esto es porqué Streamlit es tan rápido
para iterar — tu IDE + browser become ONE workflow.


# streamlit_apps/02_first_data_app.py

Decoding the new Streamlit primitives:

| Function                    | What it does                            |
|-----------------------------|-----------------------------------------|
| st.set_page_config(...)     | Browser tab title, icon, page layout    |
| layout='wide'               | Use full browser width (vs centered)    |
| st.markdown('*text*')       | Render markdown — *italic*, **bold**, etc|
| st.columns(4)               | Returns 4 column "containers"           |
| with col1:                  | All st.* calls inside go in that column |
| st.metric(label, value)     | Big-number KPI display widget           |
| st.dataframe(df)            | Sortable, scrollable interactive table  |
| use_container_width=True    | Stretch to fill available width         |

Two patterns to lock in:

1. set_page_config goes FIRST, ONCE. If you call it twice or after other
   st.* calls, Streamlit throws an error.

2. The "with col:" pattern is how you place content in specific columns.
   Without it, everything stacks vertically. With it, you control layout.

* Pro tip — st.metric vs st.write for numbers

You COULD do: st.write(f"Total LCs: {len(df)}")
And it would work — but it would render as plain text.

st.metric() renders a styled KPI card with:
- Big bold number (the value)
- Small label above
- Optional delta indicator (up/down arrow if you provide it)

For dashboard headlines, ALWAYS use st.metric. It looks like Bloomberg
terminal cards. Free professional polish. ✨

Bonus — st.metric supports a delta argument for showing change:
st.metric('Errors', 237, delta='-12 vs last week')
That renders a green ↓ arrow — universal "good change" indicator.

he file is fresh in my context — let me walk you through it.                                                  
                                                                                                               
  The file has four distinct ideas:                                                                              
                                                                                                                 
  ---                                                                                                            
  1. st.set_page_config() — line 11                                                                              
                                                                                                                 
  st.set_page_config(page_title='LC Pipeline Dashboard', page_icon='📊', layout='wide')
                                                                                                                 
  Must be the first Streamlit call in every app — before any st.write, before anything. Streamlit throws an error
   if you put it later. It sets the browser tab and switches to full-width layout instead of the narrow centered 
  default.                              
                                                                                                                 
  ---                                                                                                            
  2. st.columns() + st.metric() — lines 26-41                                                                    
                                                                                                                 
  col1, col2, col3, col4 = st.columns(4)
  with col1:                                                                   
      st.metric('Total LCs', len(df))                                           
                                        
  st.columns(4) splits the page into 4 equal horizontal slots and returns them. with col1: means "everything
  inside this block renders in column 1." st.metric() is Streamlit's KPI card — big number, label, done. You'll  
  see this pattern on every finance dashboard ever made.
                                                                                                                 
  Why with instead of col1.metric(...)? Both work. with is cleaner when you have multiple things in one column.  
                                                                                
  ---                                                                                                            
  3. Path(__file__).parent.parent — line 22 (the fix)
                                                                                                                 
  DATA_PATH = Path(__file__).parent.parent / 'data' / 'output' / 'validation_report.csv'
                                                                                                                 
  __file__ = this script. .parent = streamlit_apps/. .parent again = lc_pipeline/. Then you navigate down to the
  CSV. Always resolves correctly regardless of where you launched Streamlit from.                                
                                        
  ---                                                                                                            
  4. st.dataframe() — line 47                                                                                    
                                                                               
  st.dataframe(df.head(20), use_container_width=True)                                                            
                                        
  Renders a sortable, scrollable table in the browser. use_container_width=True makes it stretch to fill the
  column instead of having a fixed pixel width. Compare to st.write(df) which also works but gives you less      
  control over sizing.                  
 

❯ for page config or the page concept that i use . can i tke it to central place and use it everytime so i dont  
  have to write all again everytime?                                                                             
                                                                                                                 
● Good instinct — that's exactly the right architectural question to ask.                                        

  Short answer: partially yes.                                                                                   
   
  st.set_page_config() cannot be shared — Streamlit requires it to be called directly in each script, first line,
   every time. No way around it. That's a Streamlit rule, not a Python rule.
                                                                                                                 
  But the values inside it can live in one place:                                                                
   
  # config/settings.py  ← already exists in your project!                                                        
  PAGE_CONFIG = {                                                                                                
      'page_title': 'LC Pipeline Dashboard',                                                                     
      'page_icon': '📊',                                                                                         
      'layout': 'wide'                                                                                           
  }                                                                                                              
   
  Then in every app:                                                                                             
  from config.settings import PAGE_CONFIG
  st.set_page_config(**PAGE_CONFIG)      
                                   
  Change the title once in settings.py → updates everywhere. That's your single source of truth principle applied
   to Streamlit. Fits perfectly with how your project is already structured.                                     
   
  For anything else that repeats — like a standard header or logo — you can put that in a helper function in     
  utils/ and call it from each app. That part can be fully centralized.
                                                                                                                 
  So: config values → settings.py. The st.set_page_config() call itself → stays in each file, no choice. 🙂      
   
✻ Baked for 9s                                                                                                   
                  
❯ so for example i have 10 different concepts and i bamed all. so which i want to use i can call it right ?      
                                                                                                            
● Exactly. Classic Python — define once, import anywhere.                                                        
                                                                                                                 
  # config/settings.py                                                                                           
  PAGE_CONFIGS = {                                                                                               
      'dashboard': {                                                                                             
          'page_title': 'LC Pipeline Dashboard',                                                                 
          'page_icon': '📊',
          'layout': 'wide'
      },                                                                                                         
      'report': {
          'page_title': 'Validation Report',                                                                     
          'page_icon': '📋',
          'layout': 'centered'
      },
      'monitoring': {
          'page_title': 'Live Monitor',                                                                          
          'page_icon': '🔴',
          'layout': 'wide'                                                                                       
      }           
  }                                                                                                              
   
  Then in each app:                                                                                              
  from config.settings import PAGE_CONFIGS
  st.set_page_config(**PAGE_CONFIGS['dashboard'])
                                                 
  02_first_data_app.py calls 'dashboard', 03_report.py calls 'report', etc. One place to maintain, each app picks
   what it needs.                                                                                                


============= Chunk 5 — Layout primitives: the sidebar pattern - 03_dashboard_with_sidebar

Decoding the layout pattern:

| Piece                        | What it does                              |
|------------------------------|-------------------------------------------|
| with st.sidebar:             | Open a "scope" — everything inside lands  |
|                              | in the sidebar (left panel)               |
| Indented st.* calls          | Render in the sidebar                     |
| Non-indented st.* calls      | Render in the main area (right side)      |
| Block ends (dedent)          | Back to drawing in main area              |

The `with` block is the SAME pattern Python uses for files (with open(...))
and locks (with threading.Lock()). Streamlit borrowed it for layout scopes.
Familiar Python idiom, applied to UI.

You can have MULTIPLE with-blocks in one app — sidebar can be opened,
closed, opened again. Each block adds to the sidebar in order.

Pro tip — sidebar best practices

| Rule                               | Why                                  |
|------------------------------------|--------------------------------------|
| Keep widget labels SHORT           | Sidebar width is fixed (~300px)      |
| Group related filters together     | "Date range" widgets near each other |
| Use st.divider() between groups    | Visual breathing room                |
| Most important filter on TOP       | Users scan top-down                  |
| Reset/clear button at the BOTTOM   | "Done with all filters → reset"      |
| Caption text for hints             | st.caption() is your friend          |

Streamlit sidebars have a FIXED width. You CANNOT make them wider
through code alone (would require custom CSS injection). If you need
more horizontal space for controls, redesign — don't fight the framework.

The user can collapse the sidebar by clicking the < arrow at top-left.
That's a built-in Streamlit feature, no code needed. Users sometimes
want full screen for the data table, then re-expand the sidebar.


=============== Chunk 6 — Interactive widgets

Streamlit has dozens of input widgets. Today we focus on the four you'll
use 90% of the time:

| Widget              | Returns         | Best for                       |
|---------------------|-----------------|--------------------------------|
| st.selectbox        | One value       | Pick ONE from a list (currency)|
| st.multiselect      | List of values  | Pick MANY from a list (severity)|
| st.slider           | Number(s)       | Numeric ranges (amount limits) |
| st.checkbox         | True/False      | On/off toggles                 |

Each widget's call pattern is identical:
   value = st.WIDGET(label, options/range, default)

Key insight: the RETURN VALUE of each widget is whatever the user has
selected. You read it as a normal Python variable. No callbacks, no
event handlers, no .onChange() — just normal Python. That's the
Streamlit "rerun" model paying off again.

Decoding each widget call:

| Parameter | What it means                                           |
|-----------|---------------------------------------------------------|
| label=    | Text shown above the widget                              |
| options=  | List of choices the user can pick from                  |
| default=  | Pre-selected value(s) when page first loads             |
| index=    | For selectbox — INDEX of default in options list (0=first)|
| help=     | Tooltip that appears on hover (optional, not shown above)|

Two patterns to lock in:

1. options=['All'] + list(available_currencies)
   We prepend 'All' as a sentinel value meaning "no filter on this axis."
   When user picks 'All', we'll skip filtering by currency in Chunk 7.
   This is "the null option pattern" — common in dashboards.

2. default=available_severities
   We pre-select EVERYTHING by default. So opening the app shows ALL data.
   User has to ACTIVELY DESELECT severities to filter. This is friendlier
   than starting with everything deselected (which would show empty data).

   Banking dashboard default rule: "show all, let user narrow down."
   Empty-by-default frustrates users. Always default to showing data.

The "debug block" — why I added it:

Before plugging widget values into data filtering logic, we PRINT them
to verify the widgets are wired up correctly.

| Issue                        | What the debug block reveals     |
|------------------------------|----------------------------------|
| Selectbox returns wrong type | "Currency: USD" vs "Currency: 0" |
| Multiselect returns []       | Empty list when nothing chosen   |
| Filter not connected         | Widget changes, debug line stays |

This is "incremental construction" — verify EACH layer works before
adding the NEXT layer. Same pipeline-discipline as your validators.
We'll remove this debug block in Chunk 7 after filtering works.

Pro tip: when ANY Streamlit app feels broken, add a temporary
st.write(f'{some_variable}') somewhere. Streamlit becomes a live
debugger. No print statements, no breakpoints — just write the
variable to the page. Dirty but effective.

Pro tip — widget keys (you don't need it today, but worth knowing)

Every Streamlit widget has an INVISIBLE key. By default, Streamlit
generates keys based on widget type + label. So if you have TWO
selectboxes both labeled "Currency", Streamlit gets confused.

To fix that, pass an explicit key:
   selectbox(label='Currency', options=..., key='applicant_currency')
   selectbox(label='Currency', options=..., key='beneficiary_currency')

You won't hit this today (you have one of each widget). Pero cuando
construyas dashboards más complejos, dos sliders con el mismo label
crashean — y key resuelve.