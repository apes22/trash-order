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
│   └── Print modes (PAR sheet, Order sheet)
├── Scheduling Guide (/schedule)
│   ├── Sling API integration (employees, shifts)
│   ├── Toast API integration (sales data)
│   ├── Fairness-based shift generation
│   └── Push to Sling
└── Pricing Matrix (/pricing)
    ├── MenuItem and RecipeLine tables
    ├── Recipe builder per menu item
    ├── Auto-calculated COGS, profit, margin per size
    └── Summary view with color-coded margins
```

### Data Flow: Ordering Guide → Pricing Matrix
```
Ordering Guide Item
├── pricePerPkg          ($81.84 for a 20 lb bag)
├── Buying Unit          ("bag")
├── Units/Pack           (1)
├── Price/Buying Unit    ($81.84) = pricePerPkg / unitsPerPack
├── Costing Unit         ("oz")
├── Cost Units/Pack      (320) = 20 lbs × 16 oz/lb
└── Price/Costing Unit   ($0.26) = pricePerPkg / costingUnitsPerPack
                              ↓
Pricing Matrix Recipe Line
├── Raw Material: "candy, Andes mints topping"
├── Qty per size: Tiny=0.5oz, Small=0.9oz, Regular=1.2oz, Shake=1.2oz
├── Cost per size: $0.13, $0.23, $0.31, $0.31
└── Feeds into → COGS → Profit → Margin
```

### Column Reference: Ordering Guide

| Column | Editable | Source | Purpose |
|---|---|---|---|
| Vendor | Yes | Manager | Who you buy from (SGC, Walmart, etc.) |
| Item | Yes | Manager | Product name |
| Pack Size | Yes | Manager | What the package looks like ("24 12 oz", "1 20 lb") |
| Brand | Yes | Manager | Product brand |
| Buying Unit | Yes | Manager | What you order in ("case", "bag", "box") |
| Units/Pack | Yes | Manager | How many buying units per pack |
| Price/Pkg | Yes | Manager | What you pay per pack |
| Price/Buy Unit | Calculated | System | = Price/Pkg ÷ Units/Pack |
| Costing Unit | Yes | Manager | What you cost recipes in ("oz", "each") |
| Cost Units/Pack | Yes | Manager | How many costing units per pack |
| Price/Cost Unit | Calculated | System | = Price/Pkg ÷ Cost Units/Pack (feeds pricing matrix) |
| Last Price | Read-only | System | Previous Price/Pkg (auto-saved on price change) |
| Change | Read-only | System | Delta from last price (red=up, green=down) |
| PAR | Yes (per store) | Manager | Target stock level |
| On Hand | Yes (per store) | Manager/Crew | Current inventory count |
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
- **Rewrote to unified Python platform (FastAPI + SQLAlchemy)** — matches MRKT pattern
- Single Python Dockerfile, no Node runtime
- Dashboard with tool cards
- Sling scheduler mounted at /sling-api
- Added Pricing Matrix module (menu items, recipe builder, COGS/profit/margin)
- Summary view with color-coded margins (green >80%, yellow 70-79%, orange 60-69%, red <60%)
- Added Buying Unit / Costing Unit distinction for accurate recipe costing
- Auto-migration system for database schema changes

## Active URLs
- **Production:** https://tic-management.onrender.com
- **GitHub:** https://github.com/apes22/trash-order
- **Sling API:** https://tic-management.onrender.com/sling-api/
