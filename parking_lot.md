# TIC Management Platform -- Parking Lot

Deferred features and future ideas. Things we're explicitly NOT doing right now but want to track.

---

## Completed
- [x] Multi-store support (Bentonville, Rogers)
- [x] Manager/Crew role-based access
- [x] Price tracking (last price, change column)
- [x] Collapsible categories
- [x] Mobile-responsive ordering guide
- [x] Combined platform (ordering + scheduling + pricing)
- [x] Python backend (FastAPI + SQLAlchemy, replaces Node/Prisma)
- [x] Render deployment with Postgres
- [x] Pricing matrix with recipe builder and margin analysis
- [x] Summary view with color-coded margins
- [x] Buying Unit / Costing Unit distinction
- [x] Auto-migration for database schema changes
- [x] Move from localStorage to a backend (database)
- [x] User authentication (manager vs. crew access)
- [x] Real-time sync across devices
- [x] Cloud backup of data
- [x] Recipe/build sheet integration (how much of each item goes into each menu item)

---

## Phase 2 -- Near-Term Enhancements

### Ordering Guide
- [ ] Audit all 107 items: verify prices, pack sizes, weights against invoices
- [ ] Fill in Costing Unit and Cost Units/Pack for all items
- [ ] Bulk import/export (CSV or JSON) for easier data management
- [ ] Notes column (data exists in DB, not displayed yet)

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

### Pricing Matrix
- [ ] CYO pricing model (base price + per-topping surcharge with tiered pricing)
- [ ] Recipe templates (shared packaging across menu items)
- [ ] Target COGS % field per menu item (flag items that exceed target)
- [ ] Export pricing summary as PDF
- [ ] Duplicate menu item (copy recipe from existing)
- [ ] Seasonal/limited-time items flag

### Scheduling
- [ ] Auto-refresh staffing curves (currently manual JSON files)
- [ ] Schedule history (what was generated/pushed previously)
- [ ] Availability editing in the tool (currently read-only from Sling)

---

## Phase 3 -- Multi-Location & Growth

- [ ] More stores beyond Bentonville and Rogers
- [ ] Per-store pricing variations
- [ ] Cross-store inventory transfer tracking
- [ ] Location-specific notes
- [ ] Save inventory snapshots with timestamps
- [ ] Order history log (what was ordered, when)
- [ ] Trend tracking -- usage over time
- [ ] Average usage calculation to suggest PAR levels
- [ ] Cost tracking -- total order cost estimate
- [ ] Budget alerts (order exceeds $ threshold)

---

## Phase 4 -- Infrastructure & Platform

- [ ] Per-user accounts with email/password (replace shared PINs)
- [ ] Role-based access per tool (e.g., scheduling only for certain managers)
- [ ] Audit log (who changed what, when)
- [ ] Automated backups / JSON export
- [ ] Mobile-native app (PWA)
- [ ] Integration with vendor ordering systems (auto-submit orders)
- [ ] Barcode/QR scanning for inventory count
- [ ] Photo upload for items (visual identification)

---

## Future Dashboard Tools

- [ ] Sales Dashboard -- Toast POS data visualization, hourly/daily/weekly trends
- [ ] Labor Cost Calculator -- combine scheduling + hourly wages
- [ ] Waste Tracker -- log waste, see impact on COGS
- [ ] Recipe Cards -- printable build instructions for each menu item
- [ ] Training Checklists -- onboarding tasks per role
