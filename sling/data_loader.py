"""
Load and parse the raw data files.

Functions to load shifts, sales, hourly summaries, and derive active employees
with their role classifications from Sling group membership.
"""

import json
import os
import requests
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

from sling.config import (
    LEAD_POSITIONS,
    CASHIER_POSITIONS,
    SCHEDULABLE_POSITIONS,
    MANAGEMENT_POSITIONS,
    LOCATION_FULL_NAMES,
    LEAD_GROUP_IDS,
    CASHIER_GROUP_IDS,
    MANAGEMENT_GROUP_IDS,
    SLING_BASE_URL,
    ROLE_LEAD_ONLY,
    ROLE_LEAD_ELIGIBLE,
    ROLE_CASHIER_ONLY,
    ROLE_MANAGEMENT,
)

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_shifts():
    """Load enriched shifts from sling_shifts_raw.json."""
    path = os.path.join(DATA_DIR, "sling_shifts_raw.json")
    with open(path) as f:
        data = json.load(f)
    return data.get("shifts", [])


def load_shifts_metadata():
    """Load the full shifts file including user_map, position_map, location_map."""
    path = os.path.join(DATA_DIR, "sling_shifts_raw.json")
    with open(path) as f:
        return json.load(f)


def load_sales():
    """Load order data from toast_sales_raw.json."""
    path = os.path.join(DATA_DIR, "toast_sales_raw.json")
    with open(path) as f:
        return json.load(f)


def load_hourly_summary():
    """Load hourly transaction summary from toast_hourly_summary.json."""
    path = os.path.join(DATA_DIR, "toast_hourly_summary.json")
    with open(path) as f:
        return json.load(f)


def normalize_location(location_name):
    """Convert full Sling location name to short name."""
    return LOCATION_FULL_NAMES.get(location_name, location_name)


def classify_employees_from_sling():
    """Pull employee role classifications from Sling group memberships.

    Fetches group members from the Sling API to determine each employee's role:
    - LEAD_ONLY: only in lead groups (always gets lead shifts)
    - LEAD_ELIGIBLE: in both lead AND cashier groups (rotates fairly)
    - CASHIER_ONLY: only in cashier groups (always cashier)
    - MANAGEMENT: admin/owner (excluded from scheduling)

    Returns:
        dict: {user_id: {"name": str, "role": str, "positions": set, "locations": set}}
    """
    token = os.getenv("SLING_AUTH_TOKEN", "").strip()
    if not token:
        print("WARNING: SLING_AUTH_TOKEN not set — classifying from shift history only")
        return {}

    headers = {"Authorization": token}

    # Get all users
    r = requests.get(f"{SLING_BASE_URL}/v1/users", headers=headers)
    if r.status_code != 200:
        print(f"WARNING: Sling API returned {r.status_code} — classifying from shift history only")
        return {}
    users = r.json()
    if not isinstance(users, list):
        print("WARNING: Sling API returned unexpected format — classifying from shift history only")
        return {}
    active_ids = {u['id'] for u in users if u.get('active', False)}
    user_names = {u['id']: f"{u['name']} {u['lastname']}" for u in users}

    # Track which groups each user belongs to
    user_groups = defaultdict(lambda: {"lead": set(), "cashier": set(), "management": set()})

    # Check lead groups
    for gid, gname in LEAD_GROUP_IDS.items():
        r = requests.get(f"{SLING_BASE_URL}/v1/groups/{gid}/users", headers=headers)
        if r.status_code == 200:
            for member in r.json():
                if member['id'] in active_ids:
                    user_groups[member['id']]["lead"].add(gname)

    # Check cashier groups
    for gid, gname in CASHIER_GROUP_IDS.items():
        r = requests.get(f"{SLING_BASE_URL}/v1/groups/{gid}/users", headers=headers)
        if r.status_code == 200:
            for member in r.json():
                if member['id'] in active_ids:
                    user_groups[member['id']]["cashier"].add(gname)

    # Check management groups
    for gid, gname in MANAGEMENT_GROUP_IDS.items():
        r = requests.get(f"{SLING_BASE_URL}/v1/groups/{gid}/users", headers=headers)
        if r.status_code == 200:
            for member in r.json():
                if member['id'] in active_ids:
                    user_groups[member['id']]["management"].add(gname)

    # Classify each user
    result = {}
    for uid in active_ids:
        groups = user_groups[uid]
        has_lead = bool(groups["lead"])
        has_cashier = bool(groups["cashier"])
        has_mgmt = bool(groups["management"])

        if has_mgmt and not has_lead and not has_cashier:
            role = ROLE_MANAGEMENT
        elif has_lead and has_cashier:
            role = ROLE_LEAD_ELIGIBLE
        elif has_lead:
            role = ROLE_LEAD_ONLY
        elif has_cashier:
            role = ROLE_CASHIER_ONLY
        else:
            role = ROLE_MANAGEMENT  # no schedulable groups

        # Determine locations from position prefixes
        locations = set()
        for pos in groups["lead"] | groups["cashier"]:
            if pos.startswith("DTB"):
                locations.add("Bentonville")
            elif pos.startswith("DTR"):
                locations.add("Rogers")

        result[uid] = {
            "user_id": uid,
            "name": user_names.get(uid, "Unknown"),
            "role": role,
            "positions": groups["lead"] | groups["cashier"],
            "locations": locations,
        }

    return result


def get_active_employees(min_shifts=3):
    """Derive active employees from shift history + Sling role classification.

    Returns:
        list[dict]: Each dict has:
            - user_id (int)
            - user_name (str)
            - role (str): LEAD_ONLY, LEAD_ELIGIBLE, CASHIER_ONLY, or MANAGEMENT
            - total_shifts (int)
            - positions (list[str]): Distinct positions they've worked
            - locations (list[str]): Distinct locations (short names)
            - lead_shifts (int)
            - cashier_shifts (int)
            - last_shift_date (str)
    """
    shifts = load_shifts()

    # Get role classifications from Sling
    role_data = classify_employees_from_sling()

    # Group shifts by user
    user_data = defaultdict(lambda: {
        "user_id": None,
        "user_name": None,
        "role": ROLE_CASHIER_ONLY,
        "total_shifts": 0,
        "positions": set(),
        "locations": set(),
        "lead_shifts": 0,
        "cashier_shifts": 0,
        "last_shift_date": "",
    })

    for shift in shifts:
        pos = shift.get("position_name", "")
        if pos not in SCHEDULABLE_POSITIONS:
            continue

        uid = shift.get("user_id")
        name = shift.get("user_name", "")
        loc = normalize_location(shift.get("location_name", ""))
        shift_date = shift.get("shift_date", "")

        rec = user_data[uid]
        rec["user_id"] = uid
        rec["user_name"] = name
        rec["total_shifts"] += 1
        rec["positions"].add(pos)
        rec["locations"].add(loc)

        if pos in LEAD_POSITIONS:
            rec["lead_shifts"] += 1
        elif pos in CASHIER_POSITIONS:
            rec["cashier_shifts"] += 1

        if shift_date > rec["last_shift_date"]:
            rec["last_shift_date"] = shift_date

    # Merge role classification from Sling
    for uid, rec in user_data.items():
        if uid in role_data:
            rec["role"] = role_data[uid]["role"]
            # Use Sling locations if shift history is sparse
            if not rec["locations"] and role_data[uid]["locations"]:
                rec["locations"] = role_data[uid]["locations"]

    # Filter to active employees and convert sets to lists
    employees = []
    for uid, rec in user_data.items():
        if rec["total_shifts"] >= min_shifts and rec["role"] != ROLE_MANAGEMENT:
            rec["positions"] = sorted(rec["positions"])
            rec["locations"] = sorted(rec["locations"])
            employees.append(rec)

    employees.sort(key=lambda e: e["user_name"])
    return employees
