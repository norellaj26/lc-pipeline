The
code:                                                                                                                                
df_time =
df.copy()                                                                                                                      
df_time['issue_date'] = pd.to_datetime(df_time['issue_date'],
errors='coerce')                                                           
df_time = df_time.dropna(subset=['issue_date'])

monthly = (                                                                                                                              
df_time                                                                                                                              
.assign(month=df_time['issue_date'].dt.to_period('M').dt.to_timestamp())
.groupby('
month')                                                                                                                    
.agg(            
total_lcs=('transaction_id', 'count'),
flagged_lcs=('validation_status', lambda s: (s == 'FLAGGED').sum())
)                                                                                                                                    
.assign(flagged_pct=lambda d: d['flagged_lcs'] / d['total_lcs'] * 100)
.reset_index()                                                                                                                       
)
   
---                                                                                                                                      
The trick everyone gets wrong first — .dt.to_period('M').dt.to_timestamp()

Why not just .dt.month? Because that gives you 1, 2, 3... — and January 2025 and January 2026 are the same bucket.
Felicidades, you just
merged two years.

to_period('M') collapses 2026-01-15 and 2026-01-28 into the same period 2026-01. Then .to_timestamp() converts it back
to 2026-01-01 — a
real datetime matplotlib can plot on a time axis. That two-step dance is the standard pattern for "bucket by month, keep
it plotable."
                                                                                                                                           
---             
Named aggregation — why the tuple syntax

.agg(
total_lcs=('transaction_id', 'count'), # output_name = (source_col,
function)                                                   
flagged_lcs=('validation_status', lambda s: (s == 'FLAGGED')
.sum())                                                                  
)

The simpler form would be .agg({'transaction_id': 'count'}) — but then your column is still named transaction_id. The
named-agg syntax   
lets you name the output directly. Cleaner, and you avoid renaming columns afterwards.

The lambda is needed because pandas has no built-in count_where_equals. (s == 'FLAGGED').sum() converts a boolean Series
to True/False   
and sums the Trues. Classic pandas move.
                                                                                                                                           
---             
Why the second .assign(flagged_pct=...) can't be inside .agg()

.assign(flagged_pct=lambda d: d['flagged_lcs'] / d['total_lcs'] * 100)

You can't do flagged_lcs / total_lcs inside .agg() because those columns don't exist yet at that moment — they're being
born by .agg().  
The second .assign() runs after, when the columns are alive and available. This is the functional chaining rule: you can
only reference  
what exists at that step.
                  
---
That suspicious 2019-01-01 row

0 2019-01-01 1 1 100.0%

One LC from 2019, flagged. That's a data quality artifact from your pipeline — one transaction has a wrong issue date.
Your validator    
missed it (or it's actually from 2019). Either way, it'll show up as a lonely point on the far left of your time series
chart. Ay dios   
mío.
                  
---
Banking context: In trade finance, a compliance team would run exactly this — monthly flagged-LC rate — as an early
warning metric. If
January spikes to 80% flagged, someone's getting a call. This is your flagged_pct column doing regulatory monitoring
duty.

✻ Churned for 54s

❯ :)) ty u explained pretty good ..Can u explain now cell # 56

● Cell 56 was already loaded when I read the notebook. Here it is:

np.random.seed(42)
fake_daily =
pd.DataFrame({                                                                                                              
'date': pd.date_range('2026-01-01', periods=90, freq='D'),
'errors_per_day': np.random.poisson(8, 90) + np.linspace(0, 5, 90).astype(
int)                                                       
})

fake_daily['rolling_7d'] = fake_daily['errors_per_day'].rolling(7).mean()

fig, ax = plt.subplots(figsize=(12,
5))                                                                                                  
sns.lineplot(data=fake_daily, x='date', y='errors_per_day', label='Daily', alpha=0.4,
ax=ax)                                           
sns.lineplot(data=fake_daily, x='date', y='rolling_7d', label='7-day rolling avg', linewidth=2.5, ax=ax)

ax.set_title('Daily Error Counts — Synthetic
Demo')                                                                                      
plt.tick_params(axis='x',
rotation=30)                                                                                                 
plt.show()
                                                                                                                                         
---
Why fake data at all?

Cell 55 exposed the problem — your real data has 4 month buckets, most of them in January 2026. You can't teach a time
series with 4
points. So this cell builds 90 days of synthetic data to demonstrate the pattern, not the pipeline data. Honest about it
too: it's called
fake_daily.
                                                                                                                                           
---                                                                                                                                    
np.random.seed(42) — why bother?

"Random" numbers in numpy aren't actually random — they come from a deterministic algorithm. The seed is the starting
point. Same seed =
same sequence every run. Without it, the chart looks different every time you run the notebook, which is annoying when
you're teaching.  
42 is just tradition at this point.
                                                                                                                                           
---                                                                                                                                    
Why Poisson and not just randint?

np.random.poisson(8, 90)   # 90 days, avg 8 errors/day

You could use np.random.randint(0, 16, 90) and get similar-looking numbers. But Poisson is the correct distribution
for "count of        
independent events in a time period." Pipeline errors, bank transaction failures, document discrepancies — they all
follow Poisson. The 8
is the lambda (mean). Using the right distribution isn't pedantry here — it's what makes the chart look realistic
instead of like a     
fence.

  ---

+ np.linspace(0, 5, 90).astype(int) — the secret ingredient

Without this, the chart is just flat noise around 8. This adds a slow upward trend: +0 on day 1, +5 on day 90. Simulates
a system that's
slowly degrading — more realistic, and it makes the rolling average visually useful because you can actually see it
tracking the trend.

linspace(0, 5,

90) → [0.0, 0.056, 0.112, ..., 5.0]                                                                                       
    .astype(int)        → [0, 0, 0, ..., 5]    ← stepped, not smooth

---                                                                                                                                      
.rolling(7).mean() — the signal/noise split

The first 6 rows will be NaN — you need 7 days of data before the first average can be computed. That's why the rolling
line starts a
week into the chart. Nothing broken.
                                                                                                                                         
---                                                                                                                                      
The visual trick: two lineplots, two personalities

sns.lineplot(..., alpha=0.4)          # daily → faded, noisy, background
sns.lineplot(..., linewidth=2.5)      # 7-day → bold, smooth, the actual story

alpha=0.4 says "this is noise, don't focus on it." linewidth=2.5 says "this is the signal." You're teaching the eye
where to look before
the brain even processes the legend.
                                                                                                                                           
---                                                                                                                                    
plt.tick_params(axis='x', rotation=30) — the odd one out

Everything else uses ax.something(). This one uses plt.. Both work here because plt.tick_params operates on the current
active axes,
which is ax. It's a bit inconsistent — in production code you'd use ax.tick_params(axis='x', rotation=30). Same result,
but cleaner.
   
---                                                                                                                                      
Banking context: Rolling averages are everywhere in your world. Basel III uses a 250-day rolling window for VaR. LCR
stress scenarios use
30 days. AML monitoring uses rolling thresholds over 90 days. The 7-day rolling here is the same concept — cancel daily
noise, expose   
the trend. The math is identical, the stakes are just lower when it's a learning notebook.

✻ Crunched for 39s

❯ ty:) now cell # 57 pls

● Cell 57 was already in memory. Here it is — and the first thing to notice:

positive_amounts = df_facet['amount_clean']   # ← BOOM

This cell crashes. df_facet was never defined. Cell 58 (df_facet2) is the fixed version. So cell 57 is a broken draft
that got left in   
the notebook. Worth knowing so you don't wonder why it errors.
                                                                                                                                           
---             
What it's trying to do — FacetGrid

grid = sns.FacetGrid(
data=df_facet,                                                                                                                       
col='currency',
col_wrap=2,
height=4,                                                                                                                            
sharex=True,
sharey=False                                                                                                                         
)               
grid.map(sns.histplot, 'amount_clean', bins=log_bins, color='#DC143C')

Why FacetGrid instead of plt.subplots(1, 4) and filtering manually?

With subplots you'd
write:                                                                                                               
for i, cur in enumerate(currencies):
subset = df[df['currency'] == cur]
axes[i].hist(subset['amount_clean'], ...)

FacetGrid does that loop for you. You say "split by currency, one panel per value" — it handles the filtering, the
layout, the titles.
The code shrinks from 8 lines to 3. That's the entire point.
                  
---                                                                                                                                      
np.logspace — building the bins correctly

log_bins = np.logspace(
np.log10(
positive_amounts.min()),                                                                                                    
np.log10(positive_amounts.max()),
15
)

Why not just bins=15? Because with 15 equal-width bins on data that spans $5K to $10B, the first 14 bins are all crammed
near zero and   
bin 15 is the entire right half of the planet. Log bins space the edges geometrically — each bin covers the same ratio,
not the same
dollar amount. Same reason you did this in cell 37.
                  
---
sharex=True — the comment says "NOW we share"

That implies there was a version before this where sharex=False. Without shared axes, each panel picks its own x range —
USD might go
0→50M, JPY might go 0→10B. Visually different ranges look like different distributions even if they're not. sharex=True
forces the same  
axis on all panels so you're actually comparing apples to apples. In a compliance dashboard, that matters — you can't
present misleading
scale differences to a regulator.
                  
---
for ax in grid.axes.flatten(): ax.set_xscale('log')

grid.axes is a 2D array — think of it as a table of panels (rows × columns). .flatten() unrolls it into a simple list so
you can loop
over every panel with one for. Then you set log scale on each individually, because FacetGrid has no built-in set_xscale
method — you    
have to reach into the axes yourself.
                                                                                                                                           
---             
Banking context: Faceted charts are standard in risk reporting — same metric, one panel per
currency/region/counterparty. A credit risk
team looking at LC exposure would show exactly this: amount distribution by currency, shared axis, log scale. The $10B
JPY outlier is    
visible in its panel without distorting the USD panel next to it.
                                                                                                                                           
---             
tl;dr: Cool cell, wrong variable name, cell 58 fixes it. The concepts (FacetGrid, log bins, shared axes) are solid — the
execution just
has a typo in the variable.

✻ Crunched for 37s

❯ i have forgetten to write another cell before that now can u read cell # 57 and 58 ?

● Let me re-read the notebook to get the current state.

● Bash(python3
-c "                                                                                                                        
import json…)
⎿ Total cells: 113

     --- Cell index 105 ---                                                                                                                
     … +53 lines (ctrl+o to expand)

● Bash(python3 -c "                                            
import
json…)                                                                                                                        
⎿ === Cell index 106 (type:
markdown) ===                                                                                               
FacetGrid — small multiples
… +66 lines (ctrl+o to expand)

● Got it — the missing cell is there, it just has no ## 57 label. Here's what's actually in the notebook:
               
---                                                                                                                                      
Cell 57 — the first attempt (no label, sharex=False, plain bins)

df_facet =
df.copy()                                                                                                                     
df_facet['amount_clean'] =
amount_clean                                                                                                  
df_facet = df_facet.query("amount_clean > 0").dropna(
subset=['amount_clean', 'currency'])                                                
df_facet = df_facet[df_facet['currency'].isin(['USD', 'EUR', 'GBP', 'JPY'])]

grid =
sns.FacetGrid(                                                                                                                    
data=df_facet,                                                                                                                       
col='currency',                                                                                                                      
col_wrap=2,                                                                                                                          
height=4,                                                                                                                            
sharex=False, # ← the
problem                                                                                                   
sharey=False                                                                                                                         
)

grid.map(sns.histplot, 'amount_clean', bins=15, color='#DC143C')  # ← also a problem

grid.set_titles('Currency:
{col_name}')                                                                                                  
grid.set_axis_labels('Amount (USD)', 'Number of LCs')

for ax in
grid.axes.flatten():                                                                                                           
ax.set_xscale('log')

plt.show()

Cell 58 — the corrected version

)

grid.map(sns.histplot, 'amount_clean', bins=15, color='#DC143C')  # ← also a problem

grid.set_titles('Currency: {col_name}')
grid.set_axis_labels('Amount (USD)', 'Number of LCs')

for ax in grid.axes.flatten():
ax.set_xscale('log')

plt.show()

positive_amounts = df_facet['amount_clean']
log_bins = np.logspace(
np.log10(positive_amounts.min()),
np.log10(positive_amounts.max()),
15
)

grid = sns.FacetGrid(
data=df_facet,
col='currency',
col_wrap=2,
height=4,
sharex=True, # ← fixed
sharey=False
)

grid.map(sns.histplot, 'amount_clean', bins=log_bins, color='#DC143C')  # ← fixed

  ---
Two bugs, two fixes — this is the whole lesson

Bug 1: sharex=False → each panel picks its own x-axis range.

JPY has an outlier at $10B, so its panel stretches to 10B. USD maxes at ~50M. With sharex=False, the log scale on each
panel auto-fits to
that panel's data alone — so JPY and USD look similar in spread even though they're not. You're comparing different
rulers.

sharex=True forces one shared x-axis across all four panels. Now the JPY panel will show most bars crowded left and one
outlier way right
— which is the truth.

Bug 2: bins=15 on a log scale → ugly uneven bars.

bins=15 tells histplot to create 15 equal-width buckets. On a log scale, equal-width means the first 14 bins are
invisible slivers near
zero and the last bin swallows everything above $1M. The chart is technically correct and visually useless.

np.logspace(min, max, 15) creates 15 bin edges spaced geometrically — each edge is the same multiple of the previous
one. The bins match
the scale you're plotting on. The bars look proportional.

linspace bins: |-----|-----|-----|-----| ← equal width in dollars
logspace bins: |-|--|----|---------| ← equal width in log space

  ---
col_wrap=2 — the layout parameter

You have 4 currencies. Without col_wrap, FacetGrid puts them all in one row: 4 panels wide, very thin. col_wrap=2 says "
wrap to a new row
after 2 columns" → 2×2 grid. That's it.

  ---
Banking context: This exact comparison — same metric, same scale, split by currency — is what a treasury risk team shows
when reporting
LC exposure across books. sharex=False would be an audit finding. Fair comparison requires a shared axis.

✻ Sautéed for 41s

❯ cell # 59 pls

● Bash(python3
-c "                                                                                                                        
import
json…)                                                                                                                      
⎿ Cell index
111:

## 59

df_facet2 =
df.copy()                                                                                                                 
… +31 lines (ctrl+o to expand)

● Here it is — this is the 2D FacetGrid, leveling up from cell 58.

df_facet2 =
df.copy()                                                                                                                    
df_facet2['amount_clean'] =
amount_clean                                                                                                 
df_facet2 = df_facet2.query("amount_clean > 0").dropna(
subset=['amount_clean', 'currency', 'validation_status'])                         
df_facet2 = df_facet2[df_facet2['currency'].isin(['USD', 'EUR', 'GBP', 'JPY'])]

log_bins = np.logspace(...)

grid =
sns.FacetGrid(                                                                                                                    
data=df_facet2,
row='validation_status',
col='currency',
height=3,
aspect=1.3,
sharex=True,
sharey=False,                                                                                                                        
margin_titles=True
)

grid.map(sns.histplot, 'amount_clean', bins=log_bins, color='#DC143C')

for ax in grid.axes.flatten():
ax.set_xscale('log')

grid.set_axis_labels('Amount (USD)', 'Number of LCs')
grid.figure.subplots_adjust(
top=0.88)                                                                                                    
grid.figure.suptitle('LC Amounts — by Currency × Validation Status', fontsize=14)
plt.show()
   
---                                                                                                                                      
Cell 58 vs Cell 59 — one extra dimension

Cell 58 split by one variable (col='currency') → 4 panels in a 2×2 grid.

Cell 59 splits by two
variables:                                                                                                         
row='validation_status'   → CLEAN /
FLAGGED                                                                                             
col='currency'            → USD / EUR / GBP / JPY

That gives you a 2×4 grid — 8 panels total. Each panel is one combination: "CLEAN + USD", "FLAGGED + USD", "CLEAN +
EUR"... The question
this chart answers: do CLEAN and FLAGGED LCs have different amount distributions per currency? If the FLAGGED row looks
different from   
the CLEAN row for JPY, there's a pattern worth investigating.
                                                                                                                                           
---             
validation_status added to dropna — why

.dropna(subset=['amount_clean', 'currency', 'validation_status'])

Cell 58 only dropped NaN for amount_clean and currency. Now validation_status is a faceting dimension too — if it's NaN,
which row does  
that LC go in? Neither. FacetGrid would silently ignore it or crash. You drop it explicitly so the grid is clean.
                                                                                                                                           
---             
aspect=1.3 — the shape knob

height=3 → each panel is 3 inches tall
aspect=1.3 → width = 3 × 1.3 = 3.9 inches wide

Without aspect, panels are square (1.0). With 4 columns, square panels would make the whole figure very wide. 1.3
stretches each panel   
slightly to give the x-axis more breathing room for the log scale labels.
                                                                                                                                           
---             
margin_titles=True — the clean one

Without it, every panel title would say "validation_status = CLEAN | currency = USD" inside the panel itself — takes up
half the chart.
With margin_titles=True, row labels go on the right margin (CLEAN / FLAGGED) and column labels go on top (USD / EUR /
GBP / JPY). One    
label per row, one per column. Much cleaner.
                                                                                                                                           
---             
grid.figure.subplots_adjust(top=0.88) + suptitle

suptitle adds one big title for the whole figure — not for one panel. The problem: by default, that title sits right on
top of the first
row of panels and overlaps. subplots_adjust(top=0.88) pushes the plot area down to 88% of the figure height, leaving 12%
of headroom for
the title. If you skip it, the title and the panels crash into each other.
                                                                                                                                           
---             
Banking context: This 2D split is a standard risk segmentation view — same metric, broken by two dimensions
simultaneously. A trade
finance analyst would use exactly this to ask: "Is there a currency where large-value LCs are disproportionately
flagged?" If JPY's      
FLAGGED row shows a spike at $10B but its CLEAN row doesn't, that's a pattern that goes to the credit committee.

sharex = True → 4 chart aynı x eksenini paylaşır
Yani GBP, JPY, USD, EUR hepsi 10⁻¹ ile 10⁸ arasında. Karşılaştırma adil — GBP'deki $10M bar ile USD'deki $10M bar tam
aynı pozisyonda.

sharex = False → her chart kendi x eksenini ayarlar
GBP'de max $500K varsa, GBP grafiği 10⁵'te biter. USD'de max $50M varsa, USD 10⁷'ye kadar uzanır. Artık
karşılaştıramazsın — aynı bar farklı yerlerde 😱

Bankacılık bağlantısı: Risk komitesi 4 para birimini karşılaştırıyorsa, sharex=False ile sunarsan "JPY transaction'ları
çok küçük" diyebilirler — ama aslında eksen farklıydı, yanılıyorlar. Manipüle edilmiş gibi görünür, kasıtlı olmasa bile.
😄

sharey=False ise neden True değil?
Y ekseni "kaç LC var" — GBP'de 40 LC, USD'de 200 LC olabilir. Y'yi paylaşsan GBP'nin barları cüce kalır. Her currency
kendi count'una göre serbestçe ölçeklenir — bu doğru. 👌