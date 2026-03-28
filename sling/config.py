"""
Configuration and constants for the Sling Scheduler.

Location mappings, position mappings, and location-specific prefixes.
"""

# ── Sling Location IDs → Names ──────────────────────────────────────────
LOCATION_MAP = {
    22486556: "Rogers",
    22486557: "Bentonville",
    22816911: "Kitchen Production",
}

# Reverse: name → ID
LOCATION_ID_MAP = {v: k for k, v in LOCATION_MAP.items()}

# Full Sling names → short names
LOCATION_FULL_NAMES = {
    "Trash Ice Cream - Rogers": "Rogers",
    "Trash Ice Cream - Bentonville": "Bentonville",
    "Kitchen Production": "Kitchen Production",
}

# ── Position IDs → Names ────────────────────────────────────────────────
POSITION_MAP = {
    22486991: "Delivery Service Driver",
    22486558: "Barback",
    22486559: "Bartender",
    22486560: "Busser",
    22486561: "Server",
    22486562: "Host",
    22486564: "General Manager",
    22486565: "DTR-Shift Leader",
    22486566: "Driver",
    22486568: "Chef",
    22486569: "Runner",
    22486570: "Cook",
    22486571: "DTB-Shift Leader",
    22486572: "DTB-Senior Shift Leader",
    22486575: "Area Manager",
    22486577: "Admin-Full Access",
    22486576: "Production Kitchen",
    22486573: "Owner-Full Access",
    22486574: "Unit Manager",
    22522544: "DTB-Cashier",
    22522600: "DTR-Cashier",
    22522601: "Owner",
    24511789: "Unknown Position",
    22486578: "Toast",
}

# ── Location-specific position prefixes ─────────────────────────────────
# DTB = Bentonville, DTR = Rogers
LOCATION_PREFIX = {
    "Bentonville": "DTB",
    "Rogers": "DTR",
}

PREFIX_TO_LOCATION = {v: k for k, v in LOCATION_PREFIX.items()}

# ── Role classification ─────────────────────────────────────────────────
LEAD_POSITIONS = {
    "DTB-Shift Leader",
    "DTR-Shift Leader",
    "DTB-Senior Shift Leader",
}

CASHIER_POSITIONS = {
    "DTB-Cashier",
    "DTR-Cashier",
}

# Management/admin positions (excluded from auto-scheduling)
MANAGEMENT_POSITIONS = {
    "Area Manager",
    "General Manager",
    "Unit Manager",
    "Owner-Full Access",
    "Admin-Full Access",
    "Owner",
}

# Positions we schedule for (lead + cashier)
SCHEDULABLE_POSITIONS = LEAD_POSITIONS | CASHIER_POSITIONS

# ── Sling group IDs for role classification ─────────────────────────────
LEAD_GROUP_IDS = {
    22486565: "DTR-Shift Leader",
    22486571: "DTB-Shift Leader",
    22486572: "DTB-Senior Shift Leader",
}

CASHIER_GROUP_IDS = {
    22522544: "DTB-Cashier",
    22522600: "DTR-Cashier",
}

MANAGEMENT_GROUP_IDS = {
    22486575: "Area Manager",
    22486577: "Admin-Full Access",
    22486573: "Owner-Full Access",
    22486574: "Unit Manager",
}

# Employee role types:
#   LEAD_ONLY     - only in lead groups, always gets lead shifts
#   LEAD_ELIGIBLE - in BOTH lead AND cashier groups, rotates fairly
#   CASHIER_ONLY  - only in cashier groups, always gets cashier shifts
#   MANAGEMENT    - excluded from scheduling
ROLE_LEAD_ONLY = "LEAD_ONLY"
ROLE_LEAD_ELIGIBLE = "LEAD_ELIGIBLE"
ROLE_CASHIER_ONLY = "CASHIER_ONLY"
ROLE_MANAGEMENT = "MANAGEMENT"

# Role overrides — for employees whose Sling group membership doesn't
# match their actual role. Fix these in Sling when possible.
# Format: {user_id: role}
ROLE_OVERRIDES = {
    # Nellie Lopez — should be LEAD_ELIGIBLE but only in cashier groups in Sling
    # TODO: Add her to Shift Leader group in Sling
}

# ── Scheduling defaults ─────────────────────────────────────────────────
# Operating hours — evening-only operations
DEFAULT_OPEN_HOUR = 17  # 5 PM
DEFAULT_CLOSE_HOUR = 24  # midnight

# Hours to treat as "previous evening" (after-midnight closing transactions)
# These get folded into the evening shift, not scheduled as separate shifts
LATE_NIGHT_HOURS = {0, 1, 2, 3}

# Shift length constraints (hours)
MIN_SHIFT_HOURS = 4
MAX_SHIFT_HOURS = 8
PREFERRED_SHIFT_HOURS = 6

# Max hours per employee per week
DEFAULT_MAX_WEEKLY_HOURS = 30

# Target transactions per staff member per hour
# (will be overridden by historical data)
DEFAULT_TRANSACTIONS_PER_STAFF = 8

# Days of the week in schedule order (Mon-Sun)
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

# ── Sling API ───────────────────────────────────────────────────────────
SLING_BASE_URL = "https://api.getsling.com"

# ── Toast API ───────────────────────────────────────────────────────────
TOAST_BASE_URL = "https://ws-api.toasttab.com"
TOAST_AUTH_URL = f"{TOAST_BASE_URL}/authentication/v1/authentication/login"
TOAST_ORDERS_URL = f"{TOAST_BASE_URL}/orders/v2/ordersBulk"
