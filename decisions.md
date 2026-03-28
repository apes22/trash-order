# TIC Ordering Guide -- Decisions

## Context
Digital ordering guide for Trash Ice Cream (TIC) locations. Replaces a static 3-page PDF spreadsheet that was printed and hung on clipboards in the back room / inventory room at each location. The tool needs to support PAR setting, inventory counting, and suggested order calculation, with the ability to print clean PDFs.

## Tech Stack

| Technology | Choice | Why |
|---|---|---|
| Frontend | Vanilla HTML/CSS/JS | "Keep it simple to start" -- no build tools, no framework. Just open `index.html` in a browser. Easy for non-technical staff to use. |
| Data Storage | localStorage | Simplest persistence for a single-browser tool. No backend needed yet. |
| Print/PDF | Browser print (Cmd+P > Save as PDF) | Native, no dependencies. Landscape layout with `@media print` styles. |
| Deployment | Local file | Just open the HTML file. No hosting needed yet. |

## Decisions Made

### Architecture
- **Single-page app, no build tools** -- The app is 4 files (`index.html`, `styles.css`, `app.js`, `data.js`) that run directly in the browser. No npm, no bundler, no framework.
- **localStorage for persistence** -- Data survives browser refreshes. "Reset Data" button restores the original 107 items from `data.js`.
- **Categories as a property, not separate tables** -- Each item has a `category` field. Categories render as collapsible sections with colored headers. Easier to add new categories without restructuring.

### UI/UX
- **All three columns on one view** -- PAR, On Hand, and Suggested Order are all visible simultaneously. Originally built as separate tabs, but user wanted them unified. Suggested Order auto-calculates as `max(0, PAR - On Hand)`.
- **All item details are inline editable** -- Vendor, Item, Pack Size, Brand, Unit, and Price cells are text inputs styled to look like plain text until hover/focus. No modal needed for simple edits.
- **Two print modes** -- "Print PAR Sheet" hides On Hand & Order columns (for reference/setting PARs). "Print Order Sheet" shows everything with values (the actual ordering guide after inventory).
- **Column visibility toggles** -- Checkboxes in the header let the user hide/show any column. Affects both screen and print. Item column is always visible.
- **Sortable columns** -- Click any column header to sort asc/desc within each category. Active sort column is highlighted blue.
- **Search bar** -- Filters items across all categories by item name, vendor, brand, or pack size.
- **Enter key navigates down same column** -- For fast data entry during PAR setting or inventory counting.
- **Modal still used for Add Item** -- New items need a category selector and all fields, so a modal makes sense. Delete is available from the modal or the inline X button.

### Data
- **107 items extracted from the original PDF** -- Organized into 5 categories: BEVERAGE (6), FOOD (62), PAPERGOODS (11), JOB SUPPLIES (8), NOT FOR INVENTORY (20).
- **Data should be verified** -- Prices, pack sizes, and weights were extracted from a PDF screenshot. Some values may be approximate. Everything is editable.
- **Items sorted alphabetically by name within category** -- Default sort. User can re-sort by any column.

## Session 1 Status (2026-03-27)

### Completed
- [x] Extracted all 107 items from 3-page PDF order guide
- [x] Built full single-page app with 4 files
- [x] PAR, On Hand, Suggested Order columns (unified view)
- [x] Inline editing for all item detail fields
- [x] Two print modes (PAR sheet, Order sheet)
- [x] Search bar with live filtering
- [x] Sortable columns with direction indicators
- [x] Column visibility toggles for print customization
- [x] Add/delete items via modal
- [x] localStorage persistence with reset option
- [x] Category-grouped layout with color-coded headers
- [x] Print-friendly CSS (landscape, compact, clean)
- [x] Project setup (decisions, parking lot, whiteboard, memory)

## Next Steps
- Verify extracted data against original PDF (prices, pack sizes, weights)
- Test print output and adjust column widths / font sizes as needed
- Explore multi-location support if needed
