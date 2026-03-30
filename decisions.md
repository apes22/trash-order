# TIC Management Platform -- Decisions

## Context
Unified management platform for Trash Ice Cream (TIC) locations. Started as a digital ordering guide, expanded to include scheduling and pricing tools. All tools share one URL, one login, one database, and one deployment -- modeled after the MRKT project architecture.

## Tech Stack

| Technology | Choice | Why |
|---|---|---|
| Backend | Python FastAPI + SQLAlchemy | Matches MRKT pattern. Sling scheduler was already Python. Single runtime = simple Docker. |
| Database | PostgreSQL (Render managed) | Production-grade. Shared across all tools. Auto-creates tables on startup. |
| Frontend | Vanilla HTML/CSS/JS | Simple, no build tools. Each tool is a separate HTML page. |
| Auth | JWT with PIN codes | Two roles: Manager (full access) and Crew (on-hand entry only). 90-day token persistence. |
| Deployment | Render (Docker) | Python-only Dockerfile. Auto-deploys from GitHub. Matches MRKT/bookings pattern. |
| Hosting | https://tic-management.onrender.com | Single URL for all tools. |

## Architecture

### Multi-Tool Platform
```
TIC Management
├── Dashboard (tool picker)
├── Ordering Guide (/order)
│   ├── Items, Stores, StoreInventory tables
│   ├── Per-store PAR levels and On Hand counts
│   ├── Suggested Order calculation
│   ├── Print modes (PAR sheet, Order sheet)
│   └── Delivery schedule badges per store
├── Scheduling Guide (/schedule)
│   ├── Sling API integration (employees, shifts)
│   ├── Toast API integration (sales data)
│   ├── Fairness-based shift generation
│   └── Push to Sling
└── Pricing Matrix (/pricing)
    ├── MenuItem and RecipeLine tables
    ├── Recipe builder per menu item
    ├── Auto-calculated COGS, profit, margin per size
    ├── Summary view with color-coded margins
    └── Costs flow from ordering guide Price/Costing Unit
```

### Data Flow: Ordering Guide → Pricing Matrix
```
Ordering Guide Item
├── Buying Unit          ("gallon")
├── Units/Pack           (2.5)
├── Price/Pkg            ($32.50)
├── Price/Buying Unit    ($13.00) = pricePerPkg / unitsPerPack
├── Costing Unit         ("oz")
├── Cost Units/Pack      (320) = AUTO-CONVERTED: 2.5 gal × 128 oz/gal
└── Price/Costing Unit   ($0.1016) = pricePerPkg / costUnitsPerPack
                              ↓
Pricing Matrix Recipe Line
├── Raw Material: "ice cream, chocolate"
├── Qty per size: Tiny=3oz, Small=6oz, Regular=9oz, Shake=9oz
├── Cost per size: $0.30, $0.61, $0.91, $0.91
└── Feeds into → COGS → Profit → Margin
```

### Unit Conversion Table
```
oz = 1        (base unit)
lb = 16 oz
pint = 16 oz
gallon = 128 oz
```
Cost Units/Pack auto-calculates when Buying Unit and Costing Unit differ.
Example: Buying Unit=gallon, Units/Pack=2.5, Costing Unit=oz → 320 oz

### Column Reference: Ordering Guide

| Column | Editable | Source | Purpose |
|---|---|---|---|
| Sub-Category | Yes (Manager) | Manager | Groups items within a category (candy, cereal, cookies, etc.) |
| Vendor | Yes (Manager) | Manager | Who you buy from (SGC, Walmart, etc.) |
| Item | Yes (Manager) | Manager | Product name (cleaned, no prefix) |
| Pack Size | Yes (Manager) | Manager | What the package looks like ("24 12 oz", "1 20 lb") |
| Brand | Yes (Manager) | Manager | Product brand |
| Buying Unit | Dropdown | Manager | What you order in (each, gallon, pint, lb, oz, jar, pack) |
| Buying Units/Pack | Yes (Manager) | Manager | How many buying units per pack |
| Price/Pkg | Yes (Manager) | Manager | What you pay per pack |
| Last Price | Auto | System | Previous Price/Pkg (auto-saved on price change) |
| Change | Auto | System | Delta from last price (red=up, green=down) |
| Price/Buying Unit | Calculated | System | = Price/Pkg ÷ Units/Pack |
| Costing Unit | Dropdown | Manager | What you cost recipes in (each, oz, lb, pint, gallon, jar, pack) |
| Cost Units/Pack | Auto-calculated | System | Auto-converts from Buying Unit to Costing Unit |
| Price/Costing Unit | Calculated | System | = Price/Pkg ÷ Cost Units/Pack (feeds pricing matrix) |
| PAR | Yes (per store, Manager) | Manager | Target stock level |
| On Hand | Yes (per store, Manager+Crew) | Manager/Crew | Current inventory count |
| Order | Calculated | System | = max(0, PAR - On Hand) |

### Two User Roles

| | Manager (PIN: configurable) | Crew (PIN: configurable) |
|---|---|---|
| View all tools | Yes | Yes |
| Edit item details | Yes | No (read-only) |
| Edit prices | Yes | No |
| Set PAR levels | Yes | No |
| Enter On Hand | Yes | Yes |
| Add/delete items | Yes | No |
| Reset data | Yes | No |
| Create menu items | Yes | No |
| Edit recipes | Yes | No |
| View pricing matrix | Yes | Yes |

### Delivery Schedule
| Store | Order Day | Cutoff | Delivery Day |
|---|---|---|---|
| Bentonville | Monday | 5 PM | Tuesday |
| Bentonville | Thursday | 5 PM | Friday |
| Rogers | Sunday | 5 PM | Monday |
| Rogers | Thursday | 5 PM | Friday |

## Decisions Made

### Session 1 (2026-03-27) — Ordering Guide
- Extracted 107 items from 3-page PDF order guide
- Built vanilla JS frontend with inline editing
- PAR, On Hand, Suggested Order on one view (not separate tabs)
- Two print modes: PAR sheet and Order sheet
- Collapsible categories, search, sortable columns
- Column visibility toggles
- Categories: BEVERAGE, ICE CREAM, TRASH TOPPINGS, PAPERGOODS, JOB SUPPLIES, NOT FOR INVENTORY
- GitHub Pages for initial hosting (later replaced by Render)

### Session 2 (2026-03-28) — Production Backend + Multi-Tool
- Moved to Express + Prisma + Postgres on Render (multi-store support)
- Manager/Crew PIN auth with JWT tokens
- Price tracking (last price, change column with red/green)
- Combined ordering guide + sling scheduler into one app
- Rewrote to unified Python platform (FastAPI + SQLAlchemy) — matches MRKT pattern
- Single Python Dockerfile, no Node runtime
- Dashboard with tool cards
- Sling scheduler mounted at /sling-api
- Added Pricing Matrix module (menu items, recipe builder, COGS/profit/margin)
- Summary view with color-coded margins (green >80%, yellow 70-79%, orange 60-69%, red <60%)
- Added Buying Unit / Costing Unit distinction for accurate recipe costing
- Auto-migration system for database schema changes

### Session 3 (2026-03-29) — UI Consistency & Polish
- Standardized Dashboard button across all three tools
- Standardized Manager/Crew role banner across all tools
- Added draggable column resizing to ordering guide table headers
- Added sub-category column (auto-parsed from item name prefixes, QuickBooks-style)
- Draggable column reordering (saved to localStorage)
- Dynamic column visibility toggles (generated from COLUMNS array)
- Predefined dropdown selects for Buying Unit and Costing Unit (each, gallon, pint, lb, oz, jar, pack)
- Auto unit conversion: Cost Units/Pack calculated from Buying Unit → Costing Unit (gallon→oz = ×128, lb→oz = ×16, etc.)
- Per-category sorting (sort Ice Cream independently from Trash Toppings)
- Column header text wrapping for compact view
- Delivery schedule badges per store (order/delivery days shown next to store selector)
- Unified location selector across ordering guide and scheduling (same blue dropdown)
- Role detection from JWT token (fallback when localStorage missing)

### Session 4 (2026-03-30) — Mobile Responsiveness
- Full mobile audit and fixes across all three tools
- Ordering guide: header stacking, delivery badge wrapping, login card responsive, dashboard stacks
- Pricing matrix: hamburger menu for sidebar drawer, horizontal scroll tables, responsive price cards
- Scheduling guide: horizontal scroll for 7-day grid, header wrapping, mobile button sizes
- Location selector unified to dropdown in scheduling (matching ordering guide)

## Active URLs
- **Production:** https://tic-management.onrender.com
- **GitHub:** https://github.com/apes22/trash-order
- **Sling API:** https://tic-management.onrender.com/sling-api/
