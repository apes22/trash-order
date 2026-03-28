"""
Main scheduling algorithm — staggered shift generation.

Uses historical staffing curves (sales + staffing by hour by day-of-week)
to generate staggered shifts that match real operating patterns.

Key rules:
- Shifts start 30 min before open, end 30 min after close
- Staffing levels per hour are driven by historical sales + staffing data
- Each hour must have at least 1 lead when store is open
- LEAD_ONLY employees always get lead, CASHIER_ONLY always cashier
- LEAD_ELIGIBLE employees rotate fairly based on historical lead %
- Staggered start/end times match real patterns (opener/bridge/closer)
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, date

from sling.config import (
    DAYS_OF_WEEK,
    LOCATION_PREFIX,
    DEFAULT_MAX_WEEKLY_HOURS,
    ROLE_LEAD_ONLY,
    ROLE_LEAD_ELIGIBLE,
    ROLE_CASHIER_ONLY,
)
from sling.hours_config import get_shift_window, get_shift_window_str
from sling.constraints import can_assign

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _load_staffing_curves():
    """Load the pre-built staffing curves."""
    path = os.path.join(DATA_DIR, "staffing_curves.json")
    with open(path) as f:
        return json.load(f)


def _get_hourly_needs(curves, location, day_of_week, shift_start_h, shift_end_h):
    """Get recommended staffing for each hour within the shift window.

    Returns:
        list[dict]: Sorted by hour, each with:
            hour, recommended_total, recommended_leads, recommended_cashiers,
            avg_transactions
    """
    loc_data = curves.get(location, {})
    day_data = loc_data.get(day_of_week, {})
    hours_data = day_data.get("hours", {})

    needs = []
    for h in range(shift_start_h, shift_end_h):
        hour_str = str(h)
        info = hours_data.get(hour_str, {})
        rec_total = info.get("recommended_total", 0)
        rec_leads = info.get("recommended_leads", 0)
        rec_cashiers = info.get("recommended_cashiers", 0)
        avg_txn = info.get("avg_transactions", 0)

        # Always at least 1 lead if store is open
        if rec_total > 0 and rec_leads == 0:
            rec_leads = 1
        # Total must be at least leads + cashiers
        if rec_total < rec_leads + rec_cashiers:
            rec_total = rec_leads + rec_cashiers

        needs.append({
            "hour": h,
            "recommended_total": rec_total,
            "recommended_leads": rec_leads,
            "recommended_cashiers": rec_cashiers,
            "avg_transactions": avg_txn,
        })

    return needs


def _build_staggered_shifts(hourly_needs, shift_start_h, shift_start_m,
                            shift_end_h, shift_end_m, shift_patterns=None):
    """Convert hourly staffing needs into staggered shift slots.

    Instead of one flat block, creates opener/bridge/closer shifts
    based on when staffing ramps up and down.

    Returns:
        list[dict]: Each with:
            start_h, start_m, end_h, end_m, role ("lead" or "cashier"),
            shift_type ("opener", "bridge", "closer"), hours (float)
    """
    if not hourly_needs:
        return []

    # Find max staff needed at any hour
    max_staff = max(n["recommended_total"] for n in hourly_needs)
    if max_staff == 0:
        return []

    # Build a staffing profile: for each hour, how many people needed
    profile = {}
    for n in hourly_needs:
        profile[n["hour"]] = n["recommended_total"]

    # Determine shift slots by analyzing where staff ramp up/down
    # Strategy: create shifts that cover contiguous hours where a person is needed
    shifts = []

    # --- OPENER: Lead from shift_start to mid-day handoff ---
    # The opener (always a lead) covers from 30min before open until volume drops
    # or the bridge/closer takes over
    opener_start_h, opener_start_m = shift_start_h, shift_start_m

    # Find where the opener can hand off — typically when evening crew arrives
    # Look at shift patterns if available
    if shift_patterns and "closer" in shift_patterns:
        closer_start = shift_patterns["closer"].get("avg_start", "17:00")
        parts = closer_start.split(":")
        handoff_h = int(parts[0])
    else:
        # Default: handoff around 5pm
        handoff_h = 17

    # Opener ends at handoff (but at least 4 hours, at most 8)
    opener_end_h = min(handoff_h, shift_start_h + 8)
    opener_end_h = max(opener_end_h, shift_start_h + 4)
    opener_hours = opener_end_h - shift_start_h + (shift_start_m == 30 and -0.5 or 0)

    shifts.append({
        "start_h": opener_start_h,
        "start_m": opener_start_m,
        "end_h": opener_end_h,
        "end_m": 0,
        "role": "lead",
        "shift_type": "opener",
        "hours": opener_end_h - opener_start_h - (0.5 if opener_start_m == 30 else 0),
    })

    # --- CLOSER: Lead from evening through close ---
    # The closer lead takes over and runs through end of night
    closer_start_h = handoff_h
    closer_end_h, closer_end_m = shift_end_h, shift_end_m

    closer_hours = (closer_end_h - closer_start_h) + (closer_end_m / 60)
    if closer_hours > 0:
        shifts.append({
            "start_h": closer_start_h,
            "start_m": 0,
            "end_h": closer_end_h,
            "end_m": closer_end_m,
            "role": "lead",
            "shift_type": "closer",
            "hours": closer_hours,
        })

    # --- CASHIER SHIFTS: Based on volume ramp ---
    # Look at each hour and determine when extra people are needed
    # Group consecutive hours where cashiers are needed into shifts

    cashier_hours = []
    for n in hourly_needs:
        if n["recommended_cashiers"] > 0:
            for c in range(n["recommended_cashiers"]):
                cashier_hours.append((n["hour"], c))

    if cashier_hours:
        # Group by "slot number" — how many concurrent cashiers
        # Find the peak number of cashiers needed
        peak_cashiers = max(n["recommended_cashiers"] for n in hourly_needs)

        for slot in range(peak_cashiers):
            # Find hours where this slot is needed
            slot_hours = [n["hour"] for n in hourly_needs
                          if n["recommended_cashiers"] > slot]

            if not slot_hours:
                continue

            # Group consecutive hours
            groups = []
            current = [slot_hours[0]]
            for h in slot_hours[1:]:
                if h == current[-1] + 1:
                    current.append(h)
                else:
                    groups.append(current)
                    current = [h]
            groups.append(current)

            for group in groups:
                c_start_h = group[0]
                c_end_h = group[-1] + 1

                # Extend to at least 4 hours if too short
                while c_end_h - c_start_h < 4 and c_end_h < shift_end_h:
                    c_end_h += 1

                # Snap to shift window
                c_start_m = 0
                c_end_m = 0
                if c_start_h <= shift_start_h:
                    c_start_h = shift_start_h
                    c_start_m = shift_start_m
                if c_end_h >= shift_end_h:
                    c_end_h = shift_end_h
                    c_end_m = shift_end_m

                c_hours = (c_end_h - c_start_h) + (c_end_m - c_start_m) / 60

                shifts.append({
                    "start_h": c_start_h,
                    "start_m": c_start_m,
                    "end_h": c_end_h,
                    "end_m": c_end_m,
                    "role": "cashier",
                    "shift_type": "bridge" if c_start_h < handoff_h else "closer",
                    "hours": c_hours,
                })

    return shifts


def _fmt_time(h, m):
    """Format hour:minute as readable time."""
    if h == 0 or h == 24:
        return f"12:{m:02d} AM"
    elif h < 12:
        return f"{h}:{m:02d} AM"
    elif h == 12:
        return f"12:{m:02d} PM"
    else:
        return f"{h - 12}:{m:02d} PM"


def generate_schedule(location, week_start_date, employees, staffing_needs=None,
                      fairness_data=None, max_weekly_hours=None,
                      shared_state=None):
    """Generate a proposed weekly schedule with staggered shifts.

    Uses staffing curves to determine how many people per hour, then
    creates staggered opener/bridge/closer shifts matching real patterns.

    Args:
        location: "Bentonville" or "Rogers"
        week_start_date: date for Monday of target week
        employees: List of employee dicts with 'role' field
        staffing_needs: Unused (kept for API compat) — uses staffing_curves.json
        fairness_data: List from fairness_tracker.get_lead_priority
        max_weekly_hours: Max hours per employee
        shared_state: Dict shared across locations to prevent conflicts.
                      Contains weekly_hours, daily_assignments, cross_location.

    Returns:
        list[dict]: Proposed shifts
    """
    if isinstance(week_start_date, str):
        week_start_date = datetime.strptime(week_start_date, "%Y-%m-%d").date()

    if max_weekly_hours is None:
        max_weekly_hours = DEFAULT_MAX_WEEKLY_HOURS

    prefix = LOCATION_PREFIX.get(location, "DTB")
    curves = _load_staffing_curves()

    # Filter employees by location and role
    loc_employees = [e for e in employees if location in e.get("locations", [])]
    lead_only = [e for e in loc_employees if e["role"] == ROLE_LEAD_ONLY]
    lead_eligible = [e for e in loc_employees if e["role"] == ROLE_LEAD_ELIGIBLE]
    cashier_only = [e for e in loc_employees if e["role"] == ROLE_CASHIER_ONLY]

    # Fairness lookup for lead-eligible
    fairness_lookup = {}
    if fairness_data:
        for rec in fairness_data:
            fairness_lookup[rec["user_name"]] = rec.get("lead_percentage", 50.0)

    # Use shared state if provided (for cross-location scheduling),
    # otherwise create local trackers
    if shared_state is None:
        shared_state = {
            "weekly_hours": defaultdict(float),
            "daily_assignments": defaultdict(set),
            "cross_location": defaultdict(dict),  # {name: {day: location}}
        }

    weekly_hours = shared_state["weekly_hours"]
    daily_assignments = shared_state["daily_assignments"]
    cross_location = shared_state["cross_location"]
    weekly_lead_count = defaultdict(int)

    proposed_shifts = []

    for day_offset, dow in enumerate(DAYS_OF_WEEK):
        day_date = week_start_date + timedelta(days=day_offset)
        date_str = day_date.strftime("%Y-%m-%d")

        # Get shift window from operating hours
        window = get_shift_window(location, dow)
        if not window:
            continue
        shift_start_h, shift_start_m, shift_end_h, shift_end_m = window

        # Get hourly needs from staffing curves
        hourly_needs = _get_hourly_needs(curves, location, dow,
                                         shift_start_h, shift_end_h)

        # Get shift patterns for this day
        day_data = curves.get(location, {}).get(dow, {})
        shift_patterns = day_data.get("shift_patterns", {})

        # Build staggered shift slots
        shift_slots = _build_staggered_shifts(
            hourly_needs, shift_start_h, shift_start_m,
            shift_end_h, shift_end_m, shift_patterns
        )

        # Now assign employees to shift slots
        block_assigned = set()

        # Sort: leads first (opener lead, then closer lead), then cashiers
        lead_slots = [s for s in shift_slots if s["role"] == "lead"]
        cashier_slots = [s for s in shift_slots if s["role"] == "cashier"]

        # --- Assign lead slots ---
        for slot in lead_slots:
            shift_hours = slot["hours"]
            start_str = _fmt_time(slot["start_h"], slot["start_m"])
            end_str = _fmt_time(slot["end_h"], slot["end_m"])

            assigned = False

            # Try LEAD_ONLY first
            available = [
                e for e in lead_only
                if (e["user_name"] not in block_assigned
                    and can_assign(e["user_name"], dow, shift_hours,
                                   weekly_hours, daily_assignments, max_weekly_hours,
                                   location=location,
                                   cross_location_assignments=cross_location,
                                   start_hour=slot["start_h"],
                                   end_hour=slot["end_h"],
                                   date_str=date_str))
            ]
            available.sort(key=lambda e: weekly_hours[e["user_name"]])

            if available:
                emp = available[0]
            else:
                # Try LEAD_ELIGIBLE (lowest lead % first)
                available = [
                    e for e in lead_eligible
                    if (e["user_name"] not in block_assigned
                        and can_assign(e["user_name"], dow, shift_hours,
                                       weekly_hours, daily_assignments, max_weekly_hours,
                                       location=location,
                                       cross_location_assignments=cross_location,
                                       start_hour=slot["start_h"],
                                       end_hour=slot["end_h"],
                                       date_str=date_str))
                ]
                available.sort(key=lambda e: (
                    fairness_lookup.get(e["user_name"], 50.0),
                    weekly_lead_count[e["user_name"]],
                ))
                emp = available[0] if available else None

            if emp:
                name = emp["user_name"]
                proposed_shifts.append({
                    "date": date_str,
                    "day": dow,
                    "start_time": start_str,
                    "end_time": end_str,
                    "start_hour": slot["start_h"],
                    "start_min": slot["start_m"],
                    "end_hour": slot["end_h"],
                    "end_min": slot["end_m"],
                    "employee": name,
                    "user_id": emp["user_id"],
                    "position": "Lead",
                    "sling_position": f"{prefix}-Shift Leader",
                    "location": location,
                    "shift_hours": shift_hours,
                    "shift_type": slot["shift_type"],
                })
                weekly_hours[name] += shift_hours
                daily_assignments[name].add(dow)
                weekly_lead_count[name] += 1
                block_assigned.add(name)
                cross_location[name][dow] = location

        # --- Assign cashier slots ---
        for slot in cashier_slots:
            shift_hours = slot["hours"]
            start_str = _fmt_time(slot["start_h"], slot["start_m"])
            end_str = _fmt_time(slot["end_h"], slot["end_m"])

            # Cashier pool: CASHIER_ONLY + LEAD_ELIGIBLE not already assigned today
            pool = [
                e for e in (cashier_only + lead_eligible)
                if (e["user_name"] not in block_assigned
                    and can_assign(e["user_name"], dow, shift_hours,
                                   weekly_hours, daily_assignments, max_weekly_hours,
                                   location=location,
                                   cross_location_assignments=cross_location,
                                   start_hour=slot["start_h"],
                                   end_hour=slot["end_h"],
                                   date_str=date_str))
            ]
            pool.sort(key=lambda e: weekly_hours[e["user_name"]])

            if pool:
                emp = pool[0]
                name = emp["user_name"]
                proposed_shifts.append({
                    "date": date_str,
                    "day": dow,
                    "start_time": start_str,
                    "end_time": end_str,
                    "start_hour": slot["start_h"],
                    "start_min": slot["start_m"],
                    "end_hour": slot["end_h"],
                    "end_min": slot["end_m"],
                    "employee": name,
                    "user_id": emp["user_id"],
                    "position": "Cashier",
                    "sling_position": f"{prefix}-Cashier",
                    "location": location,
                    "shift_hours": shift_hours,
                    "shift_type": slot["shift_type"],
                })
                weekly_hours[name] += shift_hours
                daily_assignments[name].add(dow)
                block_assigned.add(name)
                cross_location[name][dow] = location

    return proposed_shifts


def generate_all_locations(week_start_date, employees, fairness_data_by_location,
                           max_weekly_hours=None):
    """Generate schedules for ALL locations together.

    This ensures no employee is double-booked across locations on the same day.
    Shared state (weekly hours, daily assignments, cross-location tracking)
    flows between location schedule generations.

    Args:
        week_start_date: date for Monday of target week
        employees: List of all employee dicts
        fairness_data_by_location: Dict {location: fairness_data list}
        max_weekly_hours: Max hours per employee

    Returns:
        dict: {location: [shifts]}
    """
    # Shared state across all locations
    shared_state = {
        "weekly_hours": defaultdict(float),
        "daily_assignments": defaultdict(set),
        "cross_location": defaultdict(dict),
    }

    results = {}
    for location in ["Bentonville", "Rogers"]:
        fairness_data = fairness_data_by_location.get(location, [])
        schedule = generate_schedule(
            location=location,
            week_start_date=week_start_date,
            employees=employees,
            fairness_data=fairness_data,
            max_weekly_hours=max_weekly_hours,
            shared_state=shared_state,
        )
        results[location] = schedule

    return results


def print_schedule(schedule, location=None):
    """Print the proposed schedule in a readable format."""
    if not schedule:
        print("  No shifts to display.")
        return

    loc_label = f" — {location}" if location else ""
    print(f"\n  PROPOSED SCHEDULE{loc_label}")
    print(f"  {'═' * 95}")

    by_date = defaultdict(list)
    for shift in schedule:
        by_date[shift["date"]].append(shift)

    for date_str in sorted(by_date.keys()):
        shifts = by_date[date_str]
        day = shifts[0]["day"]

        # Get operating hours
        window_str = get_shift_window_str(location, day)
        hours_label = f"  Shift window: {window_str[0]} - {window_str[1]}" if window_str else ""

        print(f"\n  {day}, {date_str}{hours_label}")
        print(f"  {'─' * 95}")
        print(f"  {'Time':<24} {'Employee':<22} {'Role':<10} {'Sling Position':<22} {'Type':<8} {'Hours':>5}")
        print(f"  {'─' * 24} {'─' * 22} {'─' * 10} {'─' * 22} {'─' * 8} {'─' * 5}")

        for s in sorted(shifts, key=lambda x: (x["start_hour"], x["start_min"],
                                                x["position"] != "Lead")):
            time_range = f"{s['start_time']} - {s['end_time']}"
            print(f"  {time_range:<24} {s['employee']:<22} {s['position']:<10} "
                  f"{s['sling_position']:<22} {s.get('shift_type', ''):<8} {s['shift_hours']:>5.1f}")

    # Summary
    print(f"\n  {'═' * 95}")
    print(f"  WEEKLY SUMMARY")
    print(f"  {'─' * 50}")

    emp_hours = defaultdict(float)
    emp_lead = defaultdict(int)
    emp_cashier = defaultdict(int)
    emp_days = defaultdict(int)
    for s in schedule:
        emp_hours[s["employee"]] += s["shift_hours"]
        emp_days[s["employee"]] += 1
        if s["position"] == "Lead":
            emp_lead[s["employee"]] += 1
        else:
            emp_cashier[s["employee"]] += 1

    print(f"\n  {'Employee':<22} {'Hours':>6} {'Days':>5} {'Lead':>5} {'Cash':>5}")
    print(f"  {'─' * 22} {'─' * 6} {'─' * 5} {'─' * 5} {'─' * 5}")
    for name in sorted(emp_hours.keys()):
        print(f"  {name:<22} {emp_hours[name]:>6.1f} {emp_days[name]:>5} "
              f"{emp_lead[name]:>5} {emp_cashier[name]:>5}")

    total_shifts = len(schedule)
    total_hours = sum(s["shift_hours"] for s in schedule)
    total_leads = sum(1 for s in schedule if s["position"] == "Lead")
    total_cashiers = sum(1 for s in schedule if s["position"] == "Cashier")
    print(f"\n  Total: {total_shifts} shifts, {total_hours:.1f} hours "
          f"({total_leads} lead, {total_cashiers} cashier)")
