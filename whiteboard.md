# TIC Management Platform -- Whiteboard

Working notes, ideas in progress, and open questions.

---

## Current State (2026-03-29)

Production platform live at https://tic-management.onrender.com. Three tools behind a unified dashboard with PIN auth.

### What's Built
```
trash_order/
├── backend/
│   ├── main.py           # FastAPI app, mounts all routers, serves static files
│   ├── database.py       # SQLAlchemy models + auto-migrations
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
│   ├── app.js            # Ordering guide logic
│   ├── styles.css, data.js
│   ├── schedule/index.html  # Sling scheduler UI
│   └── pricing/index.html   # Pricing matrix UI
├── Dockerfile            # python:3.11-slim, gunicorn + uvicorn
├── render.yaml           # Render blueprint (Docker + Postgres)
└── requirements.txt
```

### Database Models
```
Items (ordering guide catalog, shared across stores)
├── category, vendor, pack_size, brand, item
├── unit (buying unit), units_per_pack
├── price_per_pkg, last_price_per_pkg
├── costing_unit, costing_units_per_pack
├── → Calculated: pricePerBuyingUnit = price_per_pkg / units_per_pack
├── → Calculated: pricePerCostingUnit = price_per_pkg / costing_units_per_pack
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
2. Manager sets Costing Unit = "oz"                  → oz
3. Manager sets Cost Units/Pack = 320                → 320
4. System calculates Price/Costing Unit              → $0.26/oz
5. In Pricing Matrix, manager adds recipe line:
   - Raw material: "candy, Andes mints topping"
   - Qty Regular: 1.2 oz
6. System calculates cost: 1.2 × $0.26 = $0.31
7. Sum all recipe lines = COGS per size
8. Margin = (Retail Price - COGS) / Retail Price
```

---

## Open Questions

### Data Cleanup
- Many items still need Costing Unit and Cost Units/Pack filled in
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
