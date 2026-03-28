# TIC Ordering Guide -- Parking Lot

Deferred features and future ideas. Things we're explicitly NOT doing right now but want to track.

---

## Phase 2 -- Near-Term Enhancements

### Data & Accuracy
- [ ] Audit all 107 items against original PDF for correct prices, pack sizes, weights
- [ ] Add per oz/unit and per lb/pint columns back as toggleable (currently in data but not displayed)
- [ ] Add Notes column (data exists, just not rendered in the table)
- [ ] Bulk import/export (CSV or JSON) for easier data management

### Print & Layout
- [ ] Fine-tune print layout -- test actual PDF output, adjust column widths and font sizes
- [ ] Print preview mode (show what the PDF will look like before printing)
- [ ] Option to print only items that need ordering (Order > 0)
- [ ] Configurable page breaks between categories

### UX Polish
- [ ] Drag-and-drop row reordering within categories
- [ ] Undo/redo for edits
- [ ] Keyboard shortcut to jump to search (Cmd+K or /)
- [ ] Tab key navigation between cells (spreadsheet-like)
- [ ] Highlight recently changed cells

---

## Phase 3 -- Multi-Location & History

### Multi-Location Support
- [ ] Location selector (each store has its own PAR levels and inventory)
- [ ] Shared item catalog across locations (same products, different PARs)
- [ ] Location-specific notes

### Order History
- [ ] Save inventory snapshots with timestamps
- [ ] Order history log (what was ordered, when)
- [ ] Trend tracking -- usage over time
- [ ] Average usage calculation to suggest PAR levels

### Backend / Cloud
- [ ] Move from localStorage to a backend (database)
- [ ] User authentication (manager vs. crew access)
- [ ] Real-time sync across devices
- [ ] Cloud backup of data

---

## Phase 4 -- Strategic Ideas

- [ ] Integration with vendor ordering systems (auto-submit orders)
- [ ] Cost tracking -- total order cost estimate
- [ ] Budget alerts (order exceeds $ threshold)
- [ ] Barcode/QR scanning for inventory count
- [ ] Mobile-optimized layout for counting inventory on a phone
- [ ] Photo upload for items (visual identification)
- [ ] Waste tracking alongside ordering
- [ ] Recipe/build sheet integration (how much of each item goes into each menu item)
