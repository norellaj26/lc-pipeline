| Chart       | Question it answers                        |
|-------------|--------------------------------------------|
| Scatterplot | "Are these two numbers related?"           |
| Lineplot    | "How does this number change over time?"   |
| FacetGrid   | "Show me the same chart, one per category" |

A scatterplot is the most basic statistical chart. Each transaction becomes one dot, positioned by two of its
attributes.
The shape of the cloud of dots tells you whether the two attributes are related.

For your pipeline, a useful question is: "Do larger LCs take longer to validate?"
Or in trade finance language, do high-value transactions tend to be more complex documents that fail more checks?

We'll use amount (numeric) and error_count (numeric) as our two axes. Each LC becomes one dot.
If big-amount LCs cluster at the top (lots of errors), that's a real risk pattern.

The data prep
You already have amount_clean and error_count in your DataFrame. We just need to filter to positives (for log scale)
and drop NaN ( # 34)

| Piece                                  | What it does                                           |
|----------------------------------------|--------------------------------------------------------|
| sns.scatterplot(data=df, x=..., y=...) | Each row = one dot                                     |
| hue='severity'                         | Color dots by the severity column                      |
| palette={'CRITICAL': ..., ...}         | Custom dictionary mapping category → hex color         |
| alpha=0.7                              | Slight transparency — lets overlapping dots be visible |
| ax.set_xscale('log')                   | Same log trick from Day 69                             |

| Pattern                                 | What it means                                          |
|-----------------------------------------|--------------------------------------------------------|
| All severities mixed across all amounts | Errors don't depend on transaction size                |
| Critical dots cluster at high amounts   | Big LCs have more critical errors — concentration risk |
| Green dots only at low amounts          | Only small LCs are clean — process scaling issue       |
| No relationship visible                 | Amount and error count are independent                 |

CELL # 54

| Piece                                  | What it does                                           |
|----------------------------------------|--------------------------------------------------------|
| sns.scatterplot(data=df, x=..., y=...) | Each row = one dot                                     |
| hue='severity'                         | Color dots by the severity column                      |
| palette={'CRITICAL': ..., ...}         | Custom dictionary mapping category → hex color         |
| alpha=0.7                              | Slight transparency — lets overlapping dots be visible |
| ax.set_xscale('log')                   | Same log trick from Day 69                             |

Always use alpha between 0.3 and 0.7 for scatterplots with more than ~50 points.

| Pattern                                 | What it means                                          |
|-----------------------------------------|--------------------------------------------------------|
| All severities mixed across all amounts | Errors don't depend on transaction size                |
| Critical dots cluster at high amounts   | Big LCs have more critical errors — concentration risk |
| Green dots only at low amounts          | Only small LCs are clean — process scaling issue       |
| No relationship visible                 | Amount and error count are independent                 |

What the scatterplot is telling you
====================================
The first thing to notice is that the dots form horizontal bands, not a diagonal cloud.
Each band corresponds to a specific number of errors (0, 1, 2, 3, 4, 5).
This shape happens because error_count is a small integer (only six possible values),
so dots can only land at integer Y positions.

This is a known limitation of scatterplots when categories are imbalanced. Two ways to handle it if it ever bothers you:

| Solution                                    | What it does                                            |
|---------------------------------------------|---------------------------------------------------------|
| Increase dot size for rare categories       | sns.scatterplot(..., size='severity', sizes={...})      |
| Plot rare categories LAST so they're on top | Use ax.scatter() in a separate call after, with alpha=1 |
| Filter to one severity at a time            | Use multiple panels with FacetGrid (Chunk 5 today!)     |

Cell # 55 - Time series with lineplot

we can ask: "Is the validation problem getting worse over time, or is it stable?"

This question matters in real banking because regulators want to see trend lines.
If you can show "flagged percentage was 70% in January, dropped to 45% by March," that's a story of operational
improvement.
If it's flat at 64%, that's a chronic issue. Same metric, different story, depending on the time dimension.

| Piece                                | What it does                                  |
|--------------------------------------|-----------------------------------------------|
| pd.to_datetime(..., errors='coerce') | Convert string to datetime, bad values → NaT  |
| .dt.to_period('M')                   | Floor to month (e.g., 2026-01-15 → 2026-01)   |
| .dt.to_timestamp()                   | Convert period back to datetime for plotting  |
| .groupby('month')                    | Group all LCs by their month                  |
| .agg(total_lcs=..., flagged_lcs=...) | Named aggregations — one per metric           |
| lambda s: (s == 'FLAGGED').sum()     | Custom counter for flagged status             |
| .assign(flagged_pct=...)             | Compute percentage from the two columns above |
| .reset_index()                       | Move 'month' from index to column for seaborn |

Cell # 56

Reading what you just plotted
The chart shows the rolling average climbing from ~7 errors/day in early January to ~13 errors/day by April — a clear
upward trend even though daily counts swing wildly between 2 and 18. Without the rolling average, your eye would just
see chaos. Without the daily line, you'd lose the sense of how noisy the signal really is. Both lines together = honest
visualization.
In real banking, this pattern matters because regulators and risk committees ask: "Is the trend going up or down?" The
rolling average answers that. Daily line shows them you're not cherry-picking. Eso es la base de cualquier monthly risk
report. 📊
One pro tip you'll see in every senior-level chart: the rolling line is thicker (linewidth=2.5) than the daily line, AND
less transparent. Visual hierarchy via line weight, not just color. The reader's eye automatically follows the bolder
line. Subtle but professional. ✨

Cell # 57 -58 FacetGrid — small multiples

FacetGrid is the chart that changes how you analyze data. It answers questions of the form: "Show me the same chart,
broken down by category."
Concrete example: instead of one big histogram of LC amounts, what if you want to see one separate histogram per
currency? Or one per LC form? With everything we've learned so far, you'd have to manually create subplots, loop through
categories, plot each one. That's tedious. FacetGrid does it in one line.
This is sometimes called a "trellis chart" or "small multiples" — a phrase Edward Tufte made famous in the 1980s. Tufte
argued that small repeated charts let your eye compare patterns instantly, faster than any single complex chart. He was
right. Trade finance reporting picked it up: "compare amount distribution by currency" or "compare error count by
region". Always small multiples

| Concept   | What it does                                         |
|-----------|------------------------------------------------------|
| FacetGrid | A grid of small charts, one per category             |
| col=      | Each value of this column becomes a column of charts |
| row=      | Each value of this column becomes a row of charts    |
| .map()    | Apply a plotting function across all sub-charts      |

You're literally telling seaborn "draw the same chart for each subset of the data."
It handles iteration, layout, spacing, axis sharing — all automatic. ✨

The key conceptual shift: with bins=15, seaborn picks bin edges per panel based on each panel's data range. With
bins=log_bins, we force EVERY panel to use the same edges — so a $10M LC lands in the same bin position whether it's
USD, EUR, GBP, or JPY. Eso es lo que permite comparison across panels. 🎯
This is the FacetGrid wisdom hidden in plain sight: when you compare distributions across categories, you need shared
X-axis structure. Shared scale, shared bins, otherwise your eye gets fooled by panels using different scales. Tufte rule
#1 of small multiples: "the eye must be able to compare." 📐

| Currency | Shape signature                                            | Banking interpretation                             |
|----------|------------------------------------------------------------|----------------------------------------------------|
| GBP      | Tall peak at $10⁷-$10⁸, one outlier at $10¹⁰               | Clean distribution + the whale we already knew     |
| JPY      | Same peak, BUT with a tiny bar at $10⁻³ AND the $10⁹ whale | Both data quality issues confirmed in one currency |
| USD      | Cleanest of all — peak at $10⁷-$10⁸, no extreme outliers   | Most disciplined data source                       |
| EUR      | Peak at $10⁷-$10⁸, sub-cent bar visible at $10⁻³           | Same tiny-amount bug as JPY                        |

The visual confirms what your boxplot from Day 69 already showed numerically: JPY and EUR carry the sub-cent bug, JPY
and GBP carry the whales, USD is the cleanest. But now your eye sees it instantly without needing to read whisker
positions. Esto es exactly por qué Tufte preached small multiples for 40 years. ✅

There's also a subtle finding: the SHAPES of the main peaks (around $10⁶-$10⁸) are very similar across all four
currencies. Same "typical LC size" across the board. Confirms our Day 69 finding that the data generator normalized
amounts across currencies. Different data quality issues, same underlying distribution. That's the kind of nuance only
small multiples can deliver. 📊

Cell # 59 Two-dimensional FacetGrid

Question: "How does the amount distribution differ between CLEAN and FLAGGED LCs, broken down by currency?" This answers
a real banking question — do flagged LCs have systematically different amount profiles than clean ones, per currency?

| Piece                                 | What it does                                                  |
|---------------------------------------|---------------------------------------------------------------|
| row='validation_status'               | Each unique status (CLEAN, FLAGGED) becomes a row             |
| col='currency'                        | Each currency becomes a column                                |
| height=3, aspect=1.3                  | Each panel is 3 inches tall, 3.9 wide — wide rectangles       |
| margin_titles=True                    | Status labels go on right edge, currency on top — saves space |
| grid.figure.suptitle(...)             | Title for the WHOLE grid, like your dashboard from Day 68     |
| grid.figure.subplots_adjust(top=0.92) | Reserves top 8% for the suptitle                              |

The result will be a 2×4 grid: top row showing CLEAN distribution per currency, bottom row showing FLAGGED. Each
currency in its own column. Eight small charts, one image, comparing across two dimensions simultaneously. 🎨
margin_titles=True is a quality-of-life parameter worth memorizing. Without it, every panel would have its full label "
validation_status = FLAGGED | currency = USD" on top, which becomes visual noise. With it, you get clean axis-labels (
currency on top, status on right margin) — much more breathing room. 🧹

What you'll likely see
If amount and validation status are independent (likely, based on yesterday's scatterplot finding), the CLEAN row and
FLAGGED row will look very similar within each currency. That's actually a useful negative finding — "flagged LCs are
not skewed toward specific amount sizes."
But if there's a difference (FLAGGED row has more outliers, or different peak), that's a real signal. Run it and we'll
read it together. 📊
After this chart, Day 71 closes con dignidad y mañana hacemos Day 72: styling, themes, exports. Then Day 73 is the
capstone dashboard. Vamos. 🚀

| Chart                         | Skill unlocked                              | When you'll use it |
|-------------------------------|---------------------------------------------|---------------------|
| Scatterplot with hue + alpha  | Find relationships between two numeric vars | Risk concentration analysis |
| Lineplot with rolling average | Time-series trends with noise reduction     | Daily/weekly KPI tracking |
| 1D FacetGrid                  | Same chart, one per category                | Compare distributions across groups |
| 2D FacetGrid (row × col)      | Two-dimensional category breakdowns         | Cross-tab analysis |
| Log bins inside FacetGrid     | Fair comparison across panels               | Skewed financial data |
| margin_titles=True            | Clean two-dimensional grid headers          | Always with row + col combined |
