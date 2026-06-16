| Tool       | Philosophy                                                           | Example             |
|------------|----------------------------------------------------------------------|---------------------|
| Matplotlib | "Tell me everything, I'll do exactly what you say"                   | 8 lines per chart   |
| Seaborn    | "I know what statistical charts usually need, I'll fill in defaults" | 1-2 lines per chart |

| Line                             | What it does                            |
|----------------------------------|-----------------------------------------|
| import seaborn as sns            | Standard alias, every tutorial uses sns |
| sns.set_theme(style='whitegrid') | Activates seaborn defaults globally     |
| style='whitegrid'                | Light grid lines for readability        |

| style     | background | grid lines        |                                                                                                       
  |-----------|------------|-------------------|                                                                                                       
| whitegrid | white      | subtle gray lines |
| darkgrid  | gray       | white lines       |                                                                                                       
| white     | white      | none              |
| dark      | gray       | none              |                                                                                                       
| ticks     | white      | axis ticks only   |

* Side effect of set_theme(): it changes ALL matplotlib charts going forward, not just seaborn ones.
* Your future plt.plot() calls will also get the new aesthetics. Es global, not local.

## Cell # 45

Part 1 — Data prep (lines 1–3)

Why this step exists: seaborn doesn't accept a Series. It wants a proper DataFrame with named columns — one column for
categories, one for values.
This is called long-format (or tidy) data.

errors_per_validator from cell 5 is a
Series:                                                                                                            
LEI
92                                                                                                                                               
SHIP
45                                                                                                                                               
AMT
27                                                                                                                                               
...       
The validator names are the index, counts are the values. Seaborn can't reference those by column name.

reset_index() promotes the index into a real
column:                                                                                                     
| error_codes |
count |                                                                                                                                  
|-------------|-------|                                                                                                                                  
| LEI |
92 |                                                                                                                                  
| SHIP | 45 |
| AMT | 27 |

Then df_for_chart.columns = ['validator', 'count'] renames the columns to something meaningful
(pandas named the first one error_codes by default, which isn't what you want).

| argument          | what it does                                               |
  |-------------------|------------------------------------------------------------|                                                                         
| data=df_for_chart | pass the whole DataFrame — seaborn reads columns by name   |
| x='validator'     | which column goes on the x-axis                            |                                                                         
| y='count'         | which column determines bar height                         |
| hue='validator'   | color each bar differently based on this column            |                                                                         
| palette='Reds_r'  | red color palette, reversed (dark red = most errors first) |                                                                         
| ax=ax             | draw into the matplotlib ax you created above              |                                                                         
| legend=False      | hue auto-generates a legend — suppressed since x already   |                                                                         
|                   | shows the same info                                        |    

The _r suffix on 'Reds_r' means reversed — without it, the palette goes light→dark left to right,
so LEI (the worst, 92 errors) would get a light pink. Reversed = darkest red on the left = visual severity matches the
data.

# matplotlib (cell 11) — you pass raw arrays

ax.bar(errors_per_validator.index, errors_per_validator.values, color=bar_colors)

# seaborn (cell 45) — you pass column names, seaborn reads the DataFrame

sns.barplot(data=df_for_chart, x='validator', y='count', ...)

| Matplotlib needs         | Seaborn needs                            |
|--------------------------|------------------------------------------|
| ax.bar(x_array, y_array) | sns.barplot(data=df, x='col1', y='col2') |
| Two separate variables   | One DataFrame, named columns             |
| Manual color mapping     | hue='col3' auto-colors                   |
| Maual aggregation        | Built-in mean/median per group           |

The mental shift — long-format DataFrames
Seaborn HEAVILY prefers long-format data. Instead of arrays of x and y, it wants ONE DataFrame with named columns.
Why? Because once you have a DataFrame, faceting, hue grouping, and statistical aggregation become trivial:

====== Cell # 46 ======

| Palette          | When to use                                            |
|------------------|--------------------------------------------------------|
| Reds_r           | Severity-themed bars (darkest = worst)                 |
| Blues, Greens    | Single-hue gradients                                   |
| viridis, plasma  | Colorblind-safe perceptually uniform                   |
| RdYlGn           | Red-Yellow-Green (DON'T use for colorblind audiences!) |
| RdYlGn_r         | Reversed — green = good (your RAG palette)             |
| coolwarm         | Diverging — for correlations (positive vs negative)    |
| Set1, Set2, Set3 | Categorical (no ordering)                              |

| family      | data type                      | examples from your pipeline       |                                                                  
  |-------------|--------------------------------|-----------------------------------|                                                                  
| sequential  | one direction (more = darker)  | error counts, amounts             |                                                                  
| diverging   | two directions from a midpoint | correlation, positive vs negative |                                                                  
| categorical | no order, just "different"     | lc_form types, currency, country  |  

One real addition on coolwarm: in banking it's used almost exclusively for correlation matrices — risk factor
correlations,
portfolio asset correlations.
Dark blue = strong positive, dark red = strong negative, white = zero.
You'll hit this when you get to the ML phase and start looking at feature correlations.

======= Cell # 47 ========

| import       | does                                                  |
  |--------------|-------------------------------------------------------|                                                                    
| re           | regex — extract validator prefix from error codes     |
| combinations | generates all unique pairs from a list                |                                                                    
| Counter      | dict that starts at 0 for any key, built for counting |

Step 1 — Get error codes per transaction

errors_per_tx = (
df.query("validation_status == '
FLAGGED'")                                                                                                           
['error_codes']
.str.split(', ')
)

Result is a Series where each row is a list of error codes for that transaction:

row
3 →  ['LEI004', 'DATE007']                                                                                                                          
row
4 →  ['LEI004', 'SHIP002']                                                                                                                          
row 7 →  ['AMT001', 'SHIP002', 'XVAL003']

Step 2 — Empty counter

pair_counts = Counter()

Counter is a special dict where any key you haven't touched yet starts at 0 automatically. So
pair_counts[('LEI', 'SHIP')] += 1 works even the first time
— no KeyError, no if key not in dict guards needed.

Step 3 — The loop (the heart of the cell)

for codes in errors_per_tx:
validators_in_tx = sorted(set(re.match(r'^([A-Z]+)', code).group(1) for code in
codes))                                                              
for a, b in combinations(validators_in_tx, 2):
pair_counts[(a, b)] += 1

Three things happen inside the loop:

3a — Extract the validator prefix with
regex:                                                                                                            
re.match(r'^([A-Z]+)', code).group(1)

# 'LEI004' → 'LEI'

# 'DATE007' → 'DATE'

# 'SHIP002' → 'SHIP'

^([A-Z]+) means: from the start of the string, grab one or more uppercase letters. .group(1) returns just the captured
part.

3b — set() +
sorted():                                                                                                                                   
sorted(set(...))
A transaction could have LEI004 AND LEI005 — two LEI errors. Without set() you'd count LEI twice and generate ('LEI', '
LEI') as a pair, which is         
meaningless. sorted() ensures the pair is always in the same order — ('LEI', 'SHIP') not sometimes ('SHIP', 'LEI').

3c — combinations(...,
2):                                                                                                                               
Generates every unique 2-item pair from the
list:                                                                                                        
['LEI', 'SHIP', 'AMT']  →  (LEI, SHIP), (LEI, AMT), (SHIP, AMT)
['LEI', 'DATE']         →  (LEI,
DATE)                                                                                                                   
The 2 means pair size. combinations([A,B,C], 2) gives you all possible pairs without repetition and without caring about
order.

Step 4 — Top 10

print(pair_counts.most_common(10))

Counter.most_common(n) returns the n highest-frequency entries as a list of (key, count) tuples — no sorting needed,
it's built in.

Banking angle

This is co-occurrence analysis — the same technique used in AML monitoring. If LEI + SHIP always appear together in
flagged transactions, that pattern
points to a specific applicant profile or country with systemic problems in both areas, not random errors. A compliance
team would use exactly this      
output to decide where to investigate first — not "fix all LEI errors" but "fix the applicant segment that generates
LEI + SHIP together.

* what combinations is hiding:
* ============================

# Manual version of combinations(validators_in_tx, 2)

for i in range(len(
validators_in_tx)):                                                                                                                   
for j in range(i+1, len(validators_in_tx)):
pair_counts[(validators_in_tx[i], validators_in_tx[j])] += 1

With ['AMT', 'SHIP', 'XVAL']:               
i=0 (AMT):  j=1 → (AMT, SHIP), j=2 → (AMT,
XVAL)                                                                                                        
i=1 (SHIP): j=2 → (SHIP,
XVAL)                                                                                                                           
i=2 (XVAL): loop ends (j starts at 3, nothing left)

j always starts at i+1 — that's the trick that avoids duplicates like (SHIP, AMT) and self-pairs like (AMT, AMT).

Should you learn it? Read it once, understand the i+1 trick, then move on. In real code you'll always use combinations —
it's cleaner and less           
error-prone. The manual version matters if you ever work in a language that doesn't have it (Java, Go, older SQL), which
in banking back-end work is     
totally possible.

Starting state: pair_counts = {}
                                                                                                                                                           
---             
Transaction 1 — codes: ['LEI004', 'LEI005', 'SHIP002']

# regex extracts prefixes:

# LEI004 → LEI

# LEI005 → LEI ← duplicate!

# SHIP002 → SHIP

# set() removes the duplicate:

{'LEI', 'SHIP'}

# sorted() locks the order:

['LEI', 'SHIP']

# combinations(['LEI', 'SHIP'], 2) → only one pair possible:

('LEI', 'SHIP')

# counter after tx1:

pair_counts = { ('LEI', 'SHIP'): 1 }
                                                                                                                                                           
---
Transaction 2 — codes: ['LEI004', 'DATE007']

# prefixes:  LEI, DATE

# set():     {'LEI', 'DATE'}

# sorted():  ['DATE', 'LEI']   ← alphabetical, D before L

# combinations → one pair:

('DATE', 'LEI')

# counter after tx2:

pair_counts = { ('LEI', 'SHIP'): 1, ('DATE', 'LEI'): 1 }
                                                                                                                                                           
---
Transaction 3 — codes: ['AMT001', 'SHIP002', 'XVAL003']

# prefixes:  AMT, SHIP, XVAL

# set():     {'AMT', 'SHIP', 'XVAL'}

# sorted():  ['AMT', 'SHIP', 'XVAL']

# combinations → THREE pairs:

('AMT', 'SHIP')
('AMT', 'XVAL')
('SHIP', 'XVAL')

# counter after tx3:

pair_counts = {
('LEI', 'SHIP'):  1,
('DATE', 'LEI'):  1,
('AMT', 'SHIP'):  1,
('AMT', 'XVAL'):
1,                                                                                                                                 
('SHIP', 'XVAL'): 1
}
                  
---
After 128 flagged transactions, ('LEI', 'SHIP') might be at 38 — that's the pair you investigate first.

The key insight: 3 validators in one transaction = 3 pairs counted.
The more errors per transaction, the more pairs generated. combinations handles the
math so you don't have to write nested loops manually.

================================== ================Cell # 48 ============ =========================================

What cell #47 left us with

pair_counts is a Counter of sorted validator
pairs:                                                                                                       
{('LEI', 'SHIP'): 25, ('AMT', 'LEI'): 17, ('LEI', 'XVAL'):
12, ...}                                                                                       
Key point: only ONE direction per pair — ('AMT', 'LEI') is there, ('LEI', 'AMT') is NOT. Pairs were always stored with
the smaller string first.
                                                                                                                                                            
---                                                                                                                                                       
Step 1 — Collect every unique validator name

all_validators = sorted({v for pair in pair_counts for v in pair})

# → ['AMT', 'BIC', 'DATE', 'LC', 'LEI', 'PTY', 'SHIP', 'XVAL']

for pair in pair_counts iterates over the tuple keys → ('AMT', 'LEI'), ('LEI', 'SHIP'),
etc.                                                              
for v in pair then unpacks each element inside the
tuple.                                                                                                 
The set {} deduplicates, sorted() alphabetizes.
                                                                                                                                                            
---
Step 2 — Build a long-format DataFrame

pair_df = pd.DataFrame([
{'validator_a': a, 'validator_b': b, 'count': n}                                                                                                      
for (a, b), n in pair_counts.items()
])

Turns each Counter entry into one flat row:

| validator_a | validator_b | count |
  |-------------|-------------|-------|                                                                                                                     
| AMT         | LEI         | 17    |
| LEI         | SHIP        | 25    |                                                                                                                     
| ...         | ...         | ...   |

This is the long format seaborn and pivot expect.
                                                                                                                                                            
---             
Step 3 — Pivot to a square matrix

matrix = pair_df.pivot(index='validator_a', columns='validator_b', values='count').fillna(0)

pivot() reshapes: validator_a becomes rows, validator_b becomes columns, count fills the cells.

But right now it's triangular, not square — AMT→LEI has a value, but LEI→AMT doesn't exist yet (the pair was only stored
one way):

           AMT   LEI  SHIP                                                                                                                                  

AMT 0 17
11                                                                                                                                  
LEI 0 0 25 ← no AMT column here yet
SHIP 0 0 0
                  
---                                                                                                                                                       
Step 4 — Make it symmetric

matrix = matrix.add(matrix.T, fill_value=0)

matrix.T transposes rows↔columns. .add(..., fill_value=0) adds element-by-element, treating missing cells as 0.

Effect: mirrors the upper triangle onto the lower triangle. Now matrix['LEI']['AMT'] == matrix['AMT']['LEI'] == 17.

Banking analogy: this is like an AML rule-correlation table — if LEI and SHIP fire together 25 times, that's a signal
that a specific group of            
counterparties has systematic document problems, not random errors.
                                                                                                                                                            
---             
Step 5 — Force order + clean up

matrix = matrix.reindex(index=all_validators, columns=all_validators, fill_value=0)
matrix = matrix.fillna(0).astype(int)

reindex() guarantees all 8 validators appear in both rows AND columns, in the same alphabetical order. Without this, the
heatmap's rows and columns could
be in different orders and the labels would be
misaligned.                                                                                                
.astype(int) converts the 0.0 floats from fillna to clean integers.
                                                                                                                                                            
---
Final result — an 8×8 symmetric table:

validator_b AMT BIC DATE LC LEI PTY SHIP XVAL
validator_a                                                                                                                                               
AMT 0 0 1 4 17 1 11 6
LEI 17 5 7 9 0 1 25
12                                                                                                     
...

The diagonal is all zeros — a validator can't co-occur with itself. Cell #49 feeds this matrix directly into
sns.heatmap().

✻ Sautéed for 42s

❯ can u explain this more clear with an example with workflow ? all_validators = sorted({v for pair in pair_counts for v
in pair})                       
⎿ ⧉ Selected 1 lines from notebooks/06_visualization.ipynb in PyCharm

● Let's use a tiny pair_counts with just 3 entries so you can trace every step:

pair_counts = {                                                                                                                                           
('AMT', 'LEI'):
17,                                                                                                                                   
('LEI', 'SHIP'):
25,                                                                                                                                  
('AMT', 'SHIP'):
11,                                                                                                                                  
}
   
---                                                                                                                                                       
The loop runs in two layers — read it left to right:

{v for pair in pair_counts for v in pair}

Layer 1 — for pair in pair_counts

Iterating a dict gives you its keys — which here are tuples:

pair = ('AMT', 'LEI')    # iteration
1                                                                                                                    
pair = ('LEI', 'SHIP')   # iteration
2                                                                                                                    
pair = ('AMT', 'SHIP')   # iteration 3

Layer 2 — for v in pair

Now unpack each tuple, one element at a time:

pair = ('AMT', 'LEI')  → v = 'AMT', v = 'LEI'
pair = ('LEI', 'SHIP') → v = 'LEI', v = '
SHIP'                                                                                                          
pair = ('AMT', 'SHIP') → v = 'AMT', v = 'SHIP'

All the v values collected so far (as a list, before deduplication):

['AMT', 'LEI', 'LEI', 'SHIP', 'AMT', 'SHIP']

{ } — set literal removes duplicates:

{'AMT', 'LEI', 'SHIP'} # order is random in a set

sorted(...) — puts them in alphabetical order:

all_validators = ['AMT', 'LEI', 'SHIP']
                                                                                                                                                            
---
Full workflow in one picture:

pair_counts keys Layer 1 Layer 2 set {} sorted()
────────────────────── ────────── ───────────── ─────────────
──────────────────                                                             
('AMT', 'LEI')     ──► pair #1 ──►   'AMT', 'LEI'
──┐                                                                                               
('LEI', 'SHIP')    ──► pair #2 ──►   'LEI', 'SHIP' ──┼──► {'AMT',
──► ['AMT',                                                                       
('AMT', 'SHIP')    ──► pair #3 ──►   'AMT', 'SHIP' ──┘     'LEI',        'LEI',                                                                      
'SHIP'}       'SHIP']
                                                                                                                                                            
---                                                                                                                                                       
Why do you need this?

Cell #48 needs all_validators to force the final matrix to have the same 8 names in the same order on both rows and
columns. If you skip this, the
heatmap's row labels and column labels can be in different orders and the numbers land in the wrong squares.

Görseldeki Hücre 48 ("Building the matrix") kısmının amacı, bir önceki hücrede (47) tespit edilen ikili hata kodlarının
birlikte görülme frekanslarını alıp, analiz etmesi kolay, simetrik bir kare matrise (tabloya) dönüştürmektir.

İşte adım adım detaylı açıklaması:

1. Benzersiz Değerlerin Bulunması
   Python
   all_validators = sorted({v for pair in pair_counts for v in pair})
   Burada veri setinde geçen tüm benzersiz doğrulayıcı (validator) isimleri tespit ediliyor. pair_counts içinde ('
   LEI', 'SHIP') gibi ikililer var. Kod bu ikililerin içindeki her bir elemanı alıyor, küme (set - {}) parantezi
   sayesinde mükerrer olanları otomatik olarak siliyor ve sorted() ile alfabetik sıraya diziyor (AMT, BIC, DATE, LC,
   LEI...).

2. Uzun Formatlı Veri Çerçevesi (DataFrame) Oluşturma
   Python
   pair_df = pd.DataFrame([
   {'validator_a': a, 'validator_b': b, 'count': n}
   for (a, b), n in pair_counts.items()
   ])
   Önceki hücreden gelen pair_counts değişkeni bir Python Sözlüğü (Counter) formatında. Bunu pandas kütüphanesini
   kullanarak satır ve sütunlardan oluşan bir DataFrame'e dönüştürüyor. Veri üç sütunlu bir liste haline geliyor:
   Birinci kod (validator_a), ikinci kod (validator_b) ve birlikte kaç kez görüldükleri (count).

3. Matrisin İskeletini Kurma (Pivot)
   Python
   matrix = pair_df.pivot(index='validator_a', columns='validator_b', values='count').fillna(0)
   Bu adımda yukarıdaki uzun liste, bir "Pivot tabloya" çevriliyor. Satırlara validator_a sütununa da validator_b
   yerleştiriliyor. Kesişim noktalarına ise aralarındaki ilişki sayısı (count) yazılıyor. Eğer iki kod veri setinde hiç
   birlikte geçmemişse orası boş kalıyor (NaN). .fillna(0) komutu ile bu boş kalan yerlere 0 yazılıyor.

4. Simetrik Hale Getirme
   Python
   matrix = matrix.add(matrix.T, fill_value=0)
   Tabloyu köşegene (çapraz eksene) göre ayna görüntüsü olacak şekilde simetrik yapıyor. Bir önceki hücredeki
   hesaplamada A ve B kodları sayılırken örneğin ('LEI', 'AMT') sayılmış olabilir ama ('AMT', 'LEI') sayılmamış
   olabilir. Tablonun transpozu (devriği) olan matrix.T ile orijinal tablo toplanarak her iki tarafın da aynı değere
   sahip olması garantileniyor. (Yani AMT satırı ile LEI sütununun kesişimi neyse, LEI satırı ile AMT sütununun kesişimi
   de aynı sayı oluyor).

5. Sıralamayı Zorlama ve Doldurma
   Python
   matrix = matrix.reindex(index=all_validators, columns=all_validators, fill_value=0)
   Satır ve sütunların sırasını, 1. adımda oluşturduğumuz tam listeye (all_validators) göre zorluyor. Eğer pivot işlemi
   sırasında bazı kodlar sadece satırda kalıp sütunda oluşmadıysa (veya tam tersi), eksik kalan satır/sütunları tabloya
   dahil edip içlerine 0 basıyor. Bu, kusursuz bir "kare matris" elde etmek için kritik bir adım.

6. Son Temizlik
   Python
   matrix = matrix.fillna(0).astype(int)
   Son bir güvenlik önlemi olarak, yeniden indeksleme (reindex) sırasında oluşabilecek olası boşluklar tekrar 0 ile
   dolduruluyor. Ardından .astype(int) komutu ile matrisin içindeki tüm sayılar ondalıklı (float) formattan tam sayı (
   integer) formatına dönüştürülüyor; çünkü "sayım" yapıyoruz, 1.5 kez görülme gibi bir durum söz konusu olamaz.

Sonuç olarak print(matrix) komutuyla, ekranın en altında gördüğün o düzenli, okunması çok kolay olan tablo ekrana
yazdırılıyor.

Here is the code in question:Pythonall_validators = sorted({v for pair in pair_counts for v in pair})
To make this clear, let's create a simplified example and walk through the workflow step-by-step.
The Setup: Our Example DataImagine pair_counts (which is a Python Dictionary/Counter) 
has just three pairs of error codes and their frequencies.Pythonpair_counts = {
    ('LEI', 'SHIP'): 25,
    ('AMT', 'LEI'): 17,
    ('DATE', 'LEI'): 7
}
The Workflow: Breaking down the codeThe code executes from the inside out. Here is exactly what Python does behind the scenes:

Step 1: for pair in pair_counts (The Outer Loop)
When you loop over a dictionary in Python, it automatically grabs the keys and ignores the values (the numbers).
So, Python pulls out the pairs one by one:pair = ('LEI', 'SHIP')pair = ('AMT', 'LEI')pair = ('DATE', 'LEI')

Step 2: for v in pair (The Inner Loop)For each pair grabbed in Step 1, 
Python looks inside the tuple and pulls out the individual strings
(v stands for "validator"):From ('LEI', 'SHIP') $\rightarrow$ 
it extracts 'LEI' and then 'SHIP'From ('AMT', 'LEI') $\rightarrow$ 
it extracts 'AMT' and then 'LEI'From ('DATE', 'LEI') $\rightarrow$ 
it extracts 'DATE' and then 'LEI'

Step 3: { ... } (The Set Comprehension)Those curly braces {} surrounding the loops tell Python to throw all those extracted strings into a Set. 
A set is a special collection in Python that automatically destroys duplicates.
If we just threw them in a normal list, 
it would look like this:['LEI', 'SHIP', 'AMT', 'LEI', 'DATE', 'LEI'] (Notice 'LEI' repeats 3 times)
Because we used {} to make a set, Python filters it instantly:{'LEI', 'SHIP', 'AMT', 'DATE'}Step 4: sorted( ... ) 
(The Alphabetical Sort)Sets don't have a specific order. So, the final step wraps the set in the sorted() function. 
This takes our unique items, arranges them alphabetically, and outputs them as a clean, organized list.
The final output assigned to all_validators becomes:Python['AMT', 'DATE', 'LEI', 'SHIP']

SummaryIf you were to write this exact same logic out the "long way" without using the one-line shorthand, 
it would look like this:

# Create an empty set to hold unique values
unique_validators = set()

# Outer loop: go through the keys in the Counter
for pair in pair_counts:
    ## Inner loop: go through the two items in the tuple
    for v in pair:
        # Add the item to the set (duplicates are ignored)
        unique_validators.add(v)

# Sort the final set alphabetically
all_validators = sorted(unique_validators)

The one-liner you asked about is just the Pythonic, compressed version of that exact loop!


# Burada veri setinde geçen tüm benzersiz doğrulayıcı (validator) isimleri tespit ediliyor.
# küme (set - {}) parantezi sayesinde mükerrer olanları otomatik olarak siliyor
# ve sorted() ile alfabetik sıraya diziyor (AMT, BIC, DATE, LC, LEI...).