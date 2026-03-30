# TIC Management Platform -- Whiteboard

Working notes, ideas in progress, and open questions.

---

## Current State (2026-03-30)

Production platform live at https://tic-management.onrender.com. Three tools behind a unified dashboard with PIN auth. UI consistency pass done. Mobile responsive across all tools. Sub-categories, unit conversion, draggable columns, and per-category sorting added.

### What's Built
```
trash_order/
├── backend/
│   ├── main.py           # FastAPI app, mounts all routers, serves static files
│   ├── database.py       # SQLAlchemy models + auto-migrations + unit conversion
│   ├── auth.py           # JWT PIN auth (manager/crew)
│   ├── ordering.py       # Ordering guide API (items, stores, inventory, seed, reset)
│   └── pricing.py        # Pricing matrix API (menu items, recipe lines, COGS calc)
├── sling/                # Sling scheduler (FastAPI sub-app, mounted at /sling-api)
│   ├── api.py            # Schedule generation, employee list, fairness, push to Sling
│   ├── scheduler.py      # Core scheduling algorithm
│   ├── fairness_tracker.py, constraints.py, data_loader.py
│   ├── sling_connector.py, toast_connector.py
│   ├── config.py, hours_config.py, staffing_model.py
│   └── data/             # Historical JSON (shifts, sales, staffing curves)
├── public/
│   ├── index.html        # Dashboard + ordering guide (same page, show/hide)
│   ├── app.js            # Ordering guide logic (dynamic columns, drag reorder, per-cat sort)
│   ├── styles.css, data.js
│   ├── schedule/index.html  # Sling scheduler UI
│   └── pricing/index.html   # Pricing matrix UI (sidebar + recipe builder + mobile hamburger)
├── Dockerfile            # python:3.11-slim, gunicorn + uvicorn
├── render.yaml           # Render blueprint (Docker + Postgres)
└── requirements.txt
```

### Database Models
```
Items (ordering guide catalog, shared across stores)
├── category, sub_category, vendor, pack_size, brand, item
├── unit (buying unit), units_per_pack
├── price_per_pkg, last_price_per_pkg
├── costing_unit, costing_units_per_pack
├── → Auto: costUnitsPerPack via unit conversion (gallon→oz = ×128, lb→oz = ×16, pint→oz = ×16)
├── → Calculated: pricePerBuyingUnit = price_per_pkg / units_per_pack
├── → Calculated: pricePerCostingUnit = price_per_pkg / costUnitsPerPack
│
Stores → StoreInventory (per-store PAR and On Hand)
│
MenuItem → RecipeLine (pricing matrix recipes)
├── qty per size × pricePerCostingUnit = cost per line
└── Sum all lines = COGS → Profit → Margin
```

### Pricing Matrix: How Costs Flow
```
1. Manager sets Price/Pkg in Ordering Guide         → $81.84
2. Manager sets Buying Unit = "lb", Units/Pack = 20
3. Manager sets Costing Unit = "oz"
4. System auto-converts Cost Units/Pack              → 320 (20 lb × 16 oz/lb)
5. System calculates Price/Costing Unit              → $0.26/oz
6. In Pricing Matrix, manager adds recipe line:
   - Raw material: "candy, Andes mints topping"
   - Qty Regular: 1.2 oz
7. System calculates cost: 1.2 × $0.26 = $0.31
8. Sum all recipe lines = COGS per size
9. Margin = (Retail Price - COGS) / Retail Price
```

---

## Open Questions

### Session 3-4 New Features (2026-03-29/30)
- Sub-category column (QuickBooks-style, auto-parsed from item name prefixes)
- Draggable column reorder (order saved to localStorage)
- Dynamic column visibility toggles (generated from COLUMNS array, all columns listed)
- Predefined dropdown selects: Buying Unit / Costing Unit (each, gallon, pint, lb, oz, jar, pack)
- Auto unit conversion: Cost Units/Pack calculated from Buying Unit → Costing Unit
- Per-category independent sorting
- Column header text wrapping
- Delivery schedule badges per store (order/delivery days)
- Unified location selector (blue dropdown) across ordering guide and scheduling
- Role detection from JWT token (fallback when localStorage missing)
- Mobile responsiveness: all three tools audited and fixed
- Pricing matrix: hamburger menu, sidebar drawer, horizontal scroll tables
- Scheduling: horizontal scroll 7-day grid, responsive header

### Data Cleanup
- Items need Buying Unit, Costing Unit, and Units/Pack filled in (auto-conversion handles the rest)
- Some prices from original PDF extraction need verification
- totalWeightOz values don't always match pack size math

### Pricing Matrix
- Should CYO pricing be modeled differently? (base + per-topping surcharge)
- Do different menu items share recipe "templates" (e.g., all sundaes use same packaging)?
- How to handle seasonal/limited items?

### Scheduling
- Sling API token needs to stay current (stored in Render env vars)
- Toast API tokens for both locations are set up
- Should scheduling data (staffing curves) be refreshed automatically?

### Platform
- Should there be per-user accounts instead of shared PINs?
- Mobile UX for inventory counting -- is the current layout good enough?
- Should the pricing matrix summary be accessible from the dashboard?
- Cache-busting for static files (browser caching caused confusion during deploys)
- Sub-categories auto-parsed but some may need manual cleanup
