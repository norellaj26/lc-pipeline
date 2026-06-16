```python
======================== DAY 67 ================================================================================

| figsize | When to use |
|---------------|--------------------------------------| 
| (6.4, 4.8)    | matplotlib default — notebooks |
| (10, 6)       | your cell 16 — roomier, still basic |                                                              
| (16, 9)       | presentations / PowerPoint slides |                                                              
| (8.5, 11)     | PDF reports, US letter page |

## Cell 16

| Improvement            | Effect                                              |
|------------------------|-----------------------------------------------------|
| figsize=(10,6)         | Wider canvas — bars breathe                         |
| loc='upper right'      | Legend snapped cleanly to corner                    |
| Same data, same colors | Chart integrity preserved                           |
| Cell ran in 60ms       | Matplotlib is fast — performance never your problem |   

##  Cell 16

padding=3 and default integer formatting works perfectly here because counts ARE integers.
But if you were charting amounts:

| Improvement            | Effect                                              |
|------------------------|-----------------------------------------------------|
| figsize=(10,6)         | Wider canvas — bars breathe                         |
| loc='upper right'      | Legend snapped cleanly to corner                    |
| Same data, same colors | Chart integrity preserved                           |
| Cell ran in 60ms       | Matplotlib is fast — performance never your problem |

## Cell 17

| Data type             | Format          | Why                                              |
|-----------------------|-----------------|--------------------------------------------------|
| Counts (37 errors)    | Default integer | No decimals needed                               |
| Currency ($1,234,567) | fmt='${:,.0f}'  | Thousands separator, no decimals for big amounts |
| Percentages (12.5%)   | fmt='%.1f%%'    | One decimal + literal % sign                     |
| Ratios (0.42)         | fmt='%.2f'      | Two decimals for precision                       |

| Element                             | Status | Communication value              |
|-------------------------------------|--------|----------------------------------|
| Title                               | ✅      | Tells you what you're looking at |
| Axis labels                         | ✅      | Tells you what the numbers mean  |
| Color coding                        | ✅      | Tells you the urgency level      |
| Legend                              | ✅      | Tells you what colors mean       |
| Value labels                        | ✅      | Tells you EXACT counts           |
| figsize                             | ✅      | Comfortable to read              |
| Total: 92+45+27+24+17+14+11+7 = 237 | ✅      | Matches pipeline stats           |

| Change                        | What it does                             |
|-------------------------------|------------------------------------------|
| bars = ax.bar(...)            | Capture the bar collection in a variable |
| ax.bar_label(bars, padding=3) | Auto-place value labels on top           |

Decoding ax.bar_label()

| Parameter             | What it does                                                    |
|-----------------------|-----------------------------------------------------------------|
| bars                  | The bar collection (each rectangle) — that's why we captured it |
| padding=3             | Space between bar top and label, in points (3 ≈ small gap)      |
| (label_type='edge')   | Default — labels on top edge                                    |
| (label_type='center') | Optional — labels INSIDE the bar                                |
| (fmt='%.0f')          | Optional — number format string ('%.1f' for one decimal)        |

## Cell 18

fig.savefig('errors_by_validator.png', dpi=300, bbox_inches='tight')

* Decoding each parameter
  | Parameter | What it does | Why it matters |
  |-----------|-------------|-------------- --|
  | 'errors_by_validator.png' | Filename + extension | Extension determines format |
  | dpi=300 | Dots per inch resolution | 300 = print quality, 100 = screen-only |
  | bbox_inches='tight'       | Trim whitespace around chart | No ugly margins |


* File format = the extension## 19
  Matplotlib reads the extension and auto-picks the format. No need to specify type:

| Extension | Format                | Best for                                |
|-----------|-----------------------|-----------------------------------------|
| .png      | Raster (pixels)       | Screenshots, web, slides                |
| .jpg      | Raster (compressed)   | Photos — NEVER for charts (blurry text) |
| .pdf      | Vector (math curves)  | Reports, print, infinite zoom           |
| .svg      | Vector (web-friendly) | Websites, embedding                     |

* The pro rule for banking: PDFs for reports, PNGs for slides/email. Never JPG for charts — JPG compression destroys
  text edges.
  Auditors will side-eye you for blurry chart text in a regulatory submission. Yo lo he visto pasar. 🫣

The DPI rule

| DPI    | Use case                               |
|--------|----------------------------------------|
| 72-100 | Screen only (web, notebook)            |
| 150    | Decent print, presentations            |
| 300    | High-quality print, regulatory reports |
| 600    | Glossy publications                    |

Default matplotlib DPI is 100 — fine for screen, blurry on print. Always bump to 300 for anything you'll share.
Marginal cost (slightly bigger file), enormous quality gain. ⚡
bbox_inches='tight' — the "trim the fat" trick
Without this, savefig adds white margins around the chart that look like wasted space when embedded in a Word doc or
slide.
With 'tight', matplotlib intelligently crops to where the actual content ends. Always include it. Sin excepción. 🎯

Where does the file go?
Without a path,
it lands in the current working directory — wherever Jupyter/PyCharm thinks you're running from. Usually the notebook's
folder.

## Cell 19

That ../ says "go up one level from notebooks/, then into data/output/."
Same place your validation_report.csv lives. Charts as deliverables = output folder. Logical separation.

## CELL 20

* If you called plt.show() first, matplotlib would clear the figure from memory -> can u explain more

● When you call plt.show(), matplotlib renders the figure to your screen and then releases it — it considers the
figure "done."

Think of it like printing a document in Word:

- plt.show() = sending to printer — Word clears the print queue after
- fig.savefig() = Save As PDF — must happen before you print, while the document is still in memory

So if you do:

plt.show()                # figure rendered + cleared
fig.savefig('chart.png')  # ← saving an empty canvas, nothing there

vs the correct order:

fig.savefig('chart.png')  # saved while figure is still in
memory                                                                                        
plt.show()                # now render to screen, then clear

In Jupyter specifically it's sometimes more forgiving, but in a real Python script this will burn you every time.
The habit of save → show is the right  
one to build now.

| loc string     | position                 |                                                                                                          
 - - - - - - - - - - - - - - - - - - - - - - -                                                                                                   
| 'best'         | auto-picks least overlap |                                                                                                          
| 'upper right'  | top-right corner         |                                                                                                          
| 'upper left'   | top-left corner          |                                                                                                          
| 'lower right'  | bottom-right corner      |                                                                                                          
| 'lower left'   | bottom-left corner       |                                                                                                          
| 'center'       | dead center              |
| 'center left'  | middle of left edge      |                                                                                                          
| 'center right' | middle of right edge     |
| 'upper center' | top center               |                                                                                                          
| 'lower center' | bottom center            |                                                                                                          
| 'right'        | same as center right     |

You can also use numbers instead of strings — loc=1 = 'upper right', loc=2 = 'upper left', etc. But strings are more
readable, use those.

| ✅ Skill                                 |
|-----------------------------------------|
| figsize control                         |
| Value labels with bar_label             |
| Export to PNG at 300 DPI                |
| Fail-fast vs silent-fallback philosophy | 


##  Cell 18 is:                                                                                                                                              
                                                                                                                                                           
  fig.savefig('errors_by_validator.png', dpi=300, bbox_inches='tight')                                                                                     
                                                                                                                                                           
  bbox_inches='tight' tells matplotlib: "before saving, shrink-wrap the bounding box around everything visible."                                           
                  
  Without it, matplotlib saves exactly the figure's fixed dimensions — which can cause two problems:                                                       
                  
  # Without bbox_inches='tight'                                                                                                                            
                  
  |        figure boundary (fixed)         |                                                                                                               
  |   [chart]  [LEGEND gets cut off here→  |
                                                                                                                                                           
  # With bbox_inches='tight'
                                                                                                                                                           
  |  [chart]  [LEGEND]  |  ← boundary expands to fit everything                                                                                            
   
  It measures all elements — title, axis labels, legend, tick marks — then adjusts the saved image boundary to fit them all in. Nothing clipped, no        
  excessive whitespace.

  The connection to cell 15: remember when you placed the legend outside the chart with bbox_to_anchor=(1.05, 1)? That legend now lives outside the axes
  box. bbox_inches='tight' is what saves it — without it, the exported PNG would cut the legend off exactly at the figure's edge.

  Same reason plt.tight_layout() is needed when displaying, bbox_inches='tight' is needed when saving. Same problem, different context.                    



                                                                                                                  
```