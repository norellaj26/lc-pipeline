
DAY 72 - Polish, Themes & Export

| Skill                    | What it gives you |
|--------------------------|-------------------|
| Custom themes & palettes | Your project's visual identity |
| Annotations              | Highlight specific points with arrows + text |
| PDF export               | Professional-grade output for reports |

Chunk 1 — Why themes matter (the brutal truth)

When you produce 10 charts for a presentation, two things kill credibility instantly:

1. Inconsistent styling — chart 1 has gridlines, chart 2 doesn't, chart 3 uses different fonts
2. Default matplotlib look — the audience subconsciously thinks "this looks like a tutorial"

Real banking decks have a visual language. Same fonts, same color palette, same grid
style across every chart. The viewer's eye stops fighting with style differences and
focuses on the data story. Tufte calls this "data ink" — every visual element should
serve communication, nothing should distract.

Two functions in seaborn give you global theme control:

| Function          | Scope                              |
|-------------------|------------------------------------|
| sns.set_theme()   | Sets style + context globally      |
| sns.set_palette() | Sets default colors globally       |

These are stateful — once called, ALL future charts use those settings until you change them. 
Es como CSS for matplotlib. 🎨

sns.set_theme(
    style='whitegrid',     # Background style
    context='talk',        # Element scaling
    palette='Set2',        # Default colors
    font='sans-serif',     # Font family
    font_scale=1.0         # Multiplier on all text
)

style controls the chart background. Five options:

| Style       | Look                 | Best for |
|-------------|----------------------|----------|
| 'whitegrid' | White bg + grid      | Most reports (your default) |
| 'darkgrid'  | Gray bg + grid       | Slide decks with dark backgrounds |
| 'white'     | White bg, no grid    | Minimalist, when grid distracts |
| 'dark'      | Gray bg, no grid     | Stylized presentations |
| 'ticks'     | White bg, just ticks | Scientific publications |

context scales ALL elements (line widths, font sizes, marker sizes) for different output sizes:

| Context    | Scale       | When to use |
|------------|-------------|-------------|
| 'paper'    | Smallest    | Academic publications |
| 'notebook' | Default     | Interactive exploration |
| 'talk'     | 1.3x larger | Presentations, slides |
| 'poster'   | 1.6x larger | Conference posters |


Pro tip:

context='talk' is the single biggest improvement you can apply to charts going into
slide decks. It scales every element (lines, fonts, markers) by ~1.3x so the chart
remains readable when projected on a screen across a conference room. You don't have
to manually tweak font sizes per chart — set context once and forget it.

Pair it with font_scale=0.9 if 'talk' feels too heavy on smaller charts. 0.9 dials
back the multiplier slightly without losing the readability boost.

SEVERITY_COLORS = {
    'CRITICAL': '#8B0000',
    'HIGH':     '#DC143C',
    'MEDIUM':   '#FFA500',
    'LOW':      '#FFD700',
    'NONE':     '#28A745',
}

Now we extend it into a project palette with semantic roles:

PIPELINE_PALETTE = {
    # Severity (RAG)
    'critical': '#8B0000',
    'high':     '#DC143C',
    'medium':   '#FFA500',
    'low':      '#FFD700',
    'none':     '#28A745',
    # Status
    'flagged':  '#DC143C',
    'clean':    '#28A745',
    # Neutral / structural
    'primary':   '#1F4E79',  # Deep banking blue (titles, headers)
    'secondary': '#7F7F7F',  # Gray (axis text, gridlines)
    'accent':    '#5B9BD5',  # Light blue (highlights)
    'background': '#FFFFFF',
    'text':      '#262626',
}

Pro tip:

The "uniform color" choice here is intentional. On Day 66 we used severity-coded
colors to ADD information (the bars also told you the validator's typical severity).
Today we're focused on theme/style fundamentals, so we strip the severity-coding
to isolate the visual change.

Rule of thumb in real BI work: only add color dimensions that ENCODE meaning.
Color for decoration is noise. Color for severity is signal. Same hex, different
purpose, totally different professional value.

  Cell 60 — PIPELINE_PALETTE
  The interesting part isn't the colors, it's the duplicates:

  'flagged':    '#DC143C',  # same hex as 'high'
  'clean':      '#28A745',  # same hex as 'none'

  Why define the same color twice? Because the code that colors a donut chart reads PALETTE['flagged'], and the
  code that colors a bar reads PALETTE['high']. Two different charts, two different questions, same answer — but
  the code tells you why it's red without you having to remember that "high = flagged in this context." Opus
  called this semantic naming. The hex is a detail. The name is the contract.
  
  Cell 61 — sns.set_theme()

  You knew style=. The new one is context=:

  style    → changes WHAT the background looks like (grid, ticks, white)
  context  → changes HOW BIG everything is (fonts, lines, markers)
  The four contexts, from smallest to largest: 'paper' → 'notebook' → 'talk' → 'poster'.

  'talk' means: "I'm putting this on a slide, people are reading from 3 meters away." Then font_scale=0.9 dials
  it back just slightly — because 'talk' alone can make your axis labels look like they're shouting.

  The other thing that matters: this must run before plt.subplots(). Seaborn sets a global state. If you call it
  after you've already opened a figure, that figure is already dressed — the theme applies to the next one.
  
  Cell 62 — the replot

  This line:
  color=[PIPELINE_PALETTE['high']] * len(errors_per_validator)

  Why a list, not just the string? You could write color='#DC143C' and get the same result today. But ax.bar()
  accepts either a string (one color for all) or a list (one color per bar). The Day 66 severity-colored version
  passed a list of different colors. This version passes a list of the same color repeated.

  Opus wrote it as a list on purpose — so the pattern is identical whether the bars are all one color or each a
  different one. Same structure, you just swap the contents.
  
Cell # 63

Chunk 5 — Annotations: highlighting WHAT MATTERS

Now we add the magic that turns "a chart" into "a chart that tells you what to
think." Annotations let you point at specific data points with arrows and short
explanatory text.

Real banking decks DEFAULT to annotated charts. Look at any McKinsey, BCG, or
Goldman report: every important chart has 1-3 annotations highlighting the
business takeaway. The reader doesn't have to figure out the insight — the
chart literally TELLS them.

For your validator chart, the obvious annotation is: "LEI dominates at 39% of
all errors" pointing at the LEI bar. That's the headline insight.

Decoding ax.annotate() — the parameter that confuses everyone:

| Parameter   | What it does                                                    |
|-------------|-----------------------------------------------------------------|
| text=       | The label content. \n inserts a line break inside the label.    |
| xy=         | Coordinates where the ARROW TIP lands (the data point)          |
| xytext=     | Coordinates where the TEXT LABEL sits (offset from arrow)       |
| fontsize=   | Text size, in points (independent of font_scale)                |
| color=      | Text + arrow color (use palette for consistency)                |
| fontweight= | 'bold' for emphasis, 'normal' for body, 'light' for de-emphasis |
| arrowprops= | DICT controlling arrow style (separate object)                  |

The xy / xytext separation is the key concept. Think of it like: "I want to
SAY something OVER HERE (xytext) but POINT AT something OVER THERE (xy)."
The arrow is automatically drawn between the two.
Pro tip — the annotation arrow styles you should know:

| arrowstyle | Look                | When to use                       |
|------------|---------------------|-----------------------------------|
| '->'       | Simple thin arrow   | Most cases — clean, professional  |
| '-|>'      | Filled triangle tip | Bolder emphasis                   |
| '<->'      | Bidirectional       | Comparing two points              |
| 'fancy'    | Decorative          | Avoid in banking/serious reports  |
| 'wedge'    | Thick wedge         | Emphasis without being loud       |

Always use '->' as default. Save fancier styles for when the SPECIFIC visual
emphasis adds value — otherwise you're decorating, not communicating.

Also: NEVER place an annotation on top of a bar/data point. Always offset to
empty space so the annotation doesn't obscure data. The xy/xytext separation
exists exactly for this — text in empty space, arrow points to data.

Cell # 64

Chunk 6 — Grid customization & axis polish

Now we tighten the small details. Three things make a chart look "consultancy-grade"
vs "good but obviously matplotlib":

1. Grid lines are too dark by default — distract from data
2. Y-axis ticks should match the data's natural rhythm (not arbitrary 20s)
3. Spines (the 4 borders around the chart) often need hiding for cleaner look

These are 3 small CSS-level adjustments. Each one alone is invisible. All three
together = chart looks expensive.

Decoding ax.grid() parameters:

| Parameter        | What it does                                          |
|------------------|-------------------------------------------------------|
| axis='y'         | Show only HORIZONTAL gridlines (Y-axis ticks)         |
| axis='x'         | Show only VERTICAL gridlines (X-axis ticks)           |
| axis='both'      | Default — both directions                             |
| visible=False    | Hide gridlines on this axis                           |
| alpha=0.3        | Transparency 0.0 (invisible) to 1.0 (fully solid)     |
| color=           | Hex code or named color                               |

Why 0.3 alpha for gridlines? Because gridlines should be SUBTLE reference markers,
not visual elements. The reader's eye should land on the BARS, not on the gridlines.
A 0.3-alpha line is barely visible up close but provides enough structure to read
values at a glance. This is straight out of Tufte's "data ink" principle.


Decoding ax.spines:

Spines are the 4 lines that form the border of your chart area. By default,
matplotlib draws all 4. Real charts often only need 2 (left + bottom = the axes).

| Spine             | Purpose                                             |
|-------------------|-----------------------------------------------------|
| spines['top']     | Top border — usually unnecessary, hide it           |
| spines['right']   | Right border — usually unnecessary, hide it         |
| spines['left']    | Y-axis line — KEEP, but soften the color            |
| spines['bottom']  | X-axis line — KEEP, but soften the color            |

Hiding top + right is THE standard "modern minimalist" chart look. You'll see this
in every Bloomberg, Reuters, FT, and consultancy chart published since ~2015.
It's one of those tiny details that immediately signals "professional output."


ax.set_axisbelow(True) — the bug nobody warns you about:

Default matplotlib behavior: gridlines render OVER bars/lines/anything.
This means a 0.3-alpha gridline cuts visually across your beautiful crimson bar.
Looks like a printer artifact.

set_axisbelow(True) tells matplotlib: "draw the grid FIRST, then bars on top."
Bars become solid, gridlines stay in the background where they belong.

Always pair ax.grid(...) with ax.set_axisbelow(True). Muscle memory rule.

Pro tip — what NOT to do with grids:

| Anti-pattern              | Why it's bad                                |
|---------------------------|---------------------------------------------|
| Heavy black gridlines     | Distracts, looks like a school worksheet    |
| Both X and Y gridlines    | Visual noise — pick the relevant axis only  |
| Gridlines AT each tick    | Cluttered when many categories              |
| Default alpha=1.0         | Too prominent, fights with data             |
| No grid at all            | Reader can't estimate values                |

The Goldilocks zone: ONE direction (whichever axis carries the value), low alpha,
neutral color, behind the data. Lo aprendes una vez, lo aplicas siempre.


Side-by-side comparison Chunk 5 vs Chunk 6:

| Element             | Chunk 5 (good)         | Chunk 6 (consultancy-grade) |
|---------------------|------------------------|------------------------------|
| Top border          | Visible solid line     | Gone — chart breathes        |
| Right border        | Visible solid line     | Gone — chart breathes        |
| Vertical gridlines  | Faintly visible        | Gone — no clutter            |
| Horizontal grid     | Clear lines            | Soft gray, subtle reference  |
| Bars                | Crisp                  | Crisp + grid behind them     |
| Overall feel        | "Good chart"           | "Where did this come from?"  |

This is the moment when people stop asking "did you make this?" and start
asking "what tool did you use?" — they assume Tableau or Power BI. They
don't realize matplotlib can look this clean. That's BI engineer territory.

Cell # 65

Chunk 7 — Saving as high-quality PDF for board reports

PNG is fine for slides and email. But for PDFs, regulatory submissions, and
print materials, you want VECTOR format. Two key advantages:

1. Infinite zoom — vector graphics never pixelate, no matter the print size
2. Smaller files — vector definitions are tiny vs. high-DPI pixel images
3. Editable downstream — designers can open .pdf in Illustrator and tweak

Banks ALWAYS use PDF for anything going to:
- Board meetings (printed handouts)
- Regulatory submissions (FATF, Basel III filings)
- External auditors
- Legal documents

PNG is for screens, PDF is for paper. Different use cases, different formats.

Decoding the savefig differences:

| Format | dpi parameter        | Why                                       |
|--------|----------------------|-------------------------------------------|
| PDF    | NOT NEEDED (vector)  | Vector — no pixels, no DPI concept        |
| PNG    | dpi=300 (recommended)| Pixels — 300 DPI = print-grade quality    |
| SVG    | NOT NEEDED (vector)  | Same as PDF, but for web                  |
| JPG    | dpi=300              | NEVER use for charts — compresses text    |

Why PNG dpi=300 matters: at 100 DPI (default), a 10x6 inch chart becomes a
1000x600 pixel image. On modern screens, that looks fine. But when projected
or printed at 8.5x11 inch full page size, it pixelates badly. dpi=300 produces
3000x1800 pixels — print-grade.

Banking submissions specifically: regulators sometimes require dpi=600 for
financial charts. Always check the submission guidelines before exporting.


Pro tip — the bbox_inches='tight' debate:

bbox_inches='tight' trims the white margin around your chart automatically.
Without it, savefig adds ~10% padding on every side, which looks empty in
embedded contexts (Word docs, slide decks).

When NOT to use 'tight':
- When the chart is meant to align precisely with other elements on a page
  (e.g., 6x4 inch chart at fixed coordinates in a layout)
- When the surrounding whitespace is INTENTIONAL for design

In banking: 99% of the time, use 'tight'. Designers will adjust spacing
themselves in their layout software.


Open both files outside the notebook to verify:

| File                | Open with           | What you should see                  |
|---------------------|---------------------|--------------------------------------|
| validator_chart.pdf | Browser / Acrobat   | Crisp, infinite-zoom-clean chart     |
| validator_chart.png | Image viewer        | High-resolution image, ~150KB-500KB  |

Try zooming way in on each one. The PDF stays sharp at any zoom level — text
remains crisp, lines stay smooth. The PNG eventually shows pixels at extreme
zoom — that's normal, but at 300 DPI it takes a lot of zooming before it
matters for any practical use.


Today's deliverables and skills locked in:

| Skill                           | Where you proved it                |
|---------------------------------|------------------------------------|
| Custom seaborn theme            | Chunk 4 — global whitegrid + talk  |
| Project palette as constants    | PIPELINE_PALETTE dict              |
| Annotations with arrows         | Chunk 5 — LEI 39% callout          |
| Grid customization (subtle)     | Chunk 6 — alpha 0.3 horizontal     |
| Spine cleanup (top/right hidden)| Chunk 6 — modern minimalist look   |
| Axis below data (set_axisbelow) | Chunk 6 — bars solid, grid behind  |
| PDF export (vector)             | Chunk 7 — board-grade output       |
| PNG export at 300 DPI           | Chunk 7 — print-grade screen image |

Pro tips you can take to your portfolio:

| Insight                                                              |
|----------------------------------------------------------------------|
| context='talk' is THE single biggest deck-readability boost          |
| Top + right spines hidden = "consultancy modern" look                |
| Gridlines: low alpha, single direction, behind data — Tufte rule    |
| Annotations with xy/xytext = "arrow points there, text sits here"   |
| PDF for paper, PNG for screen — never JPG for charts                |
| Save PDF without dpi (vector), PNG with dpi=300 (raster)            |
| Always pair set_axisbelow(True) with grid customization             |