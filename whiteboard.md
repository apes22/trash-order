# TIC Ordering Guide -- Whiteboard

Working notes, ideas in progress, and open questions.

---

## Current State (2026-03-27)

Functional single-page web app. All 107 items from the original PDF loaded. Three core functions working: Set PAR, Collect Inventory, Suggested Order. Printable as PDF in two modes.

### What's Built
```
index.html ─── Main page, modal for adding items
styles.css ─── Layout + print styles (landscape)
app.js ─────── Rendering, inline editing, search, sort, column toggles
data.js ────── 107 items across 5 categories (INITIAL_DATA)
```

### Data Model
```javascript
{
  id: Number,           // auto-increment
  category: String,     // BEVERAGE | FOOD | PAPERGOODS | JOB SUPPLIES | NOT FOR INVENTORY
  vendor: String,       // SGC, Walmart, Webstaurant, Coca-Cola, Sam's, Amazon, etc.
  packSize: String,     // "24 12 oz", "1 20 lb", "4 4.5#", etc.
  brand: String,        // Coca-Cola, TRTopper, Great Value, etc.
  item: String,         // "candy, Andes mints topping", etc.
  unit: String,         // each, ozs, tub, pint, pack, case, gal, jar, roll
  totalWeightOz: Number,
  pricePerPkg: Number,
  perLbPint: Number,    // stored but not displayed yet
  perOzUnit: Number,    // stored but not displayed yet
  notes: String,        // stored but not displayed yet
  par: Number,          // user-set target stock level
  onHand: Number,       // current inventory count
  // suggestedOrder = max(0, par - onHand) -- calculated, not stored
}
```

### Workflow
1. Manager sets PAR levels for each item (how many you want to have)
2. Crew counts inventory and enters On Hand values
3. App calculates Suggested Order (PAR - On Hand)
4. Print Order Sheet as PDF, hang on clipboard or hand to person placing orders

---

## Open Questions

### Data Accuracy
- Some prices and pack sizes from the PDF were hard to read. Need to audit against actual invoices or the original spreadsheet. Especially page 2 (ice cream, syrups) and page 3 (job supplies).
- Total Weight column values don't always match Pack Size math -- need to verify if total weight includes packaging.

### Multi-Location
- How many locations will use this? Do they all carry the same items?
- Do PARs differ by location? (Probably yes -- a busy location needs more stock)
- Is there a "master" item list that all locations share?

### Printing
- What paper size are they printing on? (Assumed letter landscape)
- How many columns need to fit on the printout? The column toggles help here.
- Do they want blank lines on the PAR sheet for writing by hand, or just the current values?

### Future Direction
- Should this eventually become a hosted web app (so multiple devices can access it)?
- Is there interest in mobile inventory counting (phone/tablet in the walk-in)?
- Any integration with existing systems? (POS, vendor portals, accounting)

---

## Architecture Notes

### Why No Framework
Vanilla JS was chosen deliberately. The app is simple enough that React/Vue would add complexity without benefit. The entire app is ~800 lines across 4 files. A non-technical person can open `index.html` and it just works.

### localStorage Limits
- ~5-10 MB per domain (varies by browser)
- Our data is ~50-100 KB -- plenty of room
- Risk: clearing browser data loses everything
- Mitigation for later: add JSON export/import, or move to a backend

### Print Strategy
Two CSS approaches for print modes:
- `.print-par` class on `<body>` hides `.col-onhand` and `.col-order`
- `.print-order` class renders inputs as plain text (no borders)
- Column toggles also affect print (hidden columns stay hidden)
- `@page { size: landscape }` forces landscape orientation

### Sort & Search
- Sort is per-category (each category's items sort independently)
- Search filters across all categories, hides empty categories
- Both are client-side, instant (no debounce needed at this data size)
