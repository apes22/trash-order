"""
Fairness tracker: monitors lead vs cashier assignment equity
among LEAD_ELIGIBLE employees only.

The hierarchy:
- CASHIER_ONLY employees always get cashier shifts (no fairness tracking)
- LEAD_ONLY employees always get lead shifts (no fairness tracking)
- LEAD_ELIGIBLE employees rotate between lead and cashier — fairness
  is tracked and enforced only within this group.
"""

from collections import defaultdict

from sling.config import (
    LEAD_POSITIONS,
    CASHIER_POSITIONS,
    SCHEDULABLE_POSITIONS,
    ROLE_LEAD_ELIGIBLE,
)
from sling.data_loader import load_shifts, normalize_location


def analyze_historical_fairness(shifts=None, location=None, employees=None):
    """Analyze lead vs cashier fairness among LEAD_ELIGIBLE employees only.

    Args:
        shifts: List of shift dicts. If None, loads from file.
        location: Optional — filter to a specific location (short name).
        employees: Optional — list of employee dicts with 'role' field.
                   If provided, only tracks fairness for LEAD_ELIGIBLE employees.

    Returns:
        dict: Keyed by user_name, each containing:
            - user_id, user_name, total_shifts, lead_shifts, cashier_shifts
            - lead_percentage (float 0-100)
            - fairness_score (float): deviation from group average
    """
    if shifts is None:
        shifts = load_shifts()

    # If we have employee data, get the set of lead-eligible user IDs
    lead_eligible_ids = None
    if employees:
        lead_eligible_ids = {
            e["user_id"] for e in employees
            if e.get("role") == ROLE_LEAD_ELIGIBLE
        }

    user_data = defaultdict(lambda: {
        "user_id": None,
        "user_name": None,
        "total_shifts": 0,
        "lead_shifts": 0,
        "cashier_shifts": 0,
        "locations": set(),
    })

    for shift in shifts:
        pos = shift.get("position_name", "")
        if pos not in SCHEDULABLE_POSITIONS:
            continue

        loc = normalize_location(shift.get("location_name", ""))
        if location and loc != location:
            continue

        uid = shift.get("user_id")

        # Only track lead-eligible employees if we have that info
        if lead_eligible_ids is not None and uid not in lead_eligible_ids:
            continue

        name = shift.get("user_name", "")

        rec = user_data[name]
        rec["user_id"] = uid
        rec["user_name"] = name
        rec["total_shifts"] += 1
        rec["locations"].add(loc)

        if pos in LEAD_POSITIONS:
            rec["lead_shifts"] += 1
        elif pos in CASHIER_POSITIONS:
            rec["cashier_shifts"] += 1

    # Calculate lead percentages
    results = {}
    for name, rec in user_data.items():
        if rec["total_shifts"] == 0:
            continue
        rec["lead_percentage"] = (rec["lead_shifts"] / rec["total_shifts"]) * 100
        rec["locations"] = sorted(rec["locations"])
        results[name] = rec

    # Group average lead percentage (among lead-eligible only)
    if results:
        avg_lead_pct = sum(r["lead_percentage"] for r in results.values()) / len(results)
    else:
        avg_lead_pct = 50.0

    for name, rec in results.items():
        rec["fairness_score"] = round(rec["lead_percentage"] - avg_lead_pct, 1)
        rec["lead_percentage"] = round(rec["lead_percentage"], 1)

    return results


def get_lead_priority(employees=None, location=None):
    """Get lead-eligible employees sorted by who most deserves a lead shift.

    Only includes LEAD_ELIGIBLE employees. Sorted by lead_percentage ascending
    (lowest first = most deserving of next lead shift).

    Args:
        employees: List of employee dicts with 'role' field.
        location: Optional location filter.

    Returns:
        list[dict]: Fairness records for lead-eligible employees only.
    """
    fairness = analyze_historical_fairness(location=location, employees=employees)

    # Sort by lead percentage ascending (lowest first = most deserving)
    priority = sorted(fairness.values(), key=lambda r: r["lead_percentage"])

    return priority


def print_fairness_report(location=None, employees=None):
    """Print a formatted fairness report for lead-eligible employees."""
    fairness = analyze_historical_fairness(location=location, employees=employees)

    if not fairness:
        print(f"  No lead-eligible employees with shift data{f' for {location}' if location else ''}.")
        return

    avg_pct = sum(r["lead_percentage"] for r in fairness.values()) / len(fairness)

    loc_label = f" ({location})" if location else ""
    print(f"\n  FAIRNESS ANALYSIS — Lead-Eligible Employees{loc_label}")
    print(f"  Only employees who can work BOTH lead and cashier are tracked here.")
    print(f"  Group average lead %: {avg_pct:.1f}%")
    print(f"  {'─' * 72}")
    print(f"  {'Name':<25} {'Lead':>5} {'Cash':>5} {'Total':>6} {'Lead%':>6} {'Score':>7}  Priority")
    print(f"  {'─' * 25} {'─' * 5} {'─' * 5} {'─' * 6} {'─' * 6} {'─' * 7}  {'─' * 10}")

    for rec in sorted(fairness.values(), key=lambda r: r["lead_percentage"]):
        name = rec["user_name"]
        lead = rec["lead_shifts"]
        cash = rec["cashier_shifts"]
        total = rec["total_shifts"]
        pct = rec["lead_percentage"]
        score = rec["fairness_score"]

        if score < -10:
            priority = "*** HIGH"
        elif score < -5:
            priority = "** MED"
        elif score < 0:
            priority = "* LOW"
        else:
            priority = ""

        print(f"  {name:<25} {lead:>5} {cash:>5} {total:>6} {pct:>5.1f}% {score:>+6.1f}  {priority}")

    print()
