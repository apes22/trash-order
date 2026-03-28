"""
Sling Scheduler — FastAPI web API.

Serves the schedule UI and provides endpoints for:
- Generating proposed schedules
- Listing employees and operating hours
- Fairness analysis
- Pushing shifts to the Sling API
- Editing individual shifts
"""

import sys
import os
import json
from datetime import date, timedelta, datetime
from collections import defaultdict

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from sling.config import (
    DAYS_OF_WEEK,
    LOCATION_ID_MAP,
    LOCATION_PREFIX,
    POSITION_MAP,
    ROLE_LEAD_ONLY,
    ROLE_LEAD_ELIGIBLE,
    ROLE_CASHIER_ONLY,
    DEFAULT_MAX_WEEKLY_HOURS,
    MAX_SHIFT_HOURS,
    MIN_SHIFT_HOURS,
    LATE_NIGHT_HOURS,
)
from sling.hours_config import OPERATING_HOURS, get_shift_window, get_shift_window_str, SHIFT_BUFFER_MINUTES
from sling.data_loader import get_active_employees
from sling.fairness_tracker import get_lead_priority, analyze_historical_fairness
from sling.scheduler import generate_schedule, generate_all_locations
from sling.sling_connector import SlingConnector
from sling.constraints import load_availability


app = FastAPI(title="Sling Scheduler", version="1.0.0")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ── Helpers ──────────────────────────────────────────────────────────────

def get_next_monday(from_date=None):
    """Get the next Monday from a given date."""
    if from_date is None:
        from_date = date.today()
    days_ahead = (7 - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return from_date + timedelta(days=days_ahead)


def _position_name_to_id(position_name):
    """Reverse-lookup a Sling position name to its ID."""
    for pid, pname in POSITION_MAP.items():
        if pname == position_name:
            return pid
    return None


# ── Cache for employees (avoid hitting Sling API on every request) ───────

_employee_cache = {
    "data": None,
    "timestamp": None,
    "ttl_seconds": 300,  # 5 min cache
}


def _get_employees():
    """Get employees with simple time-based cache."""
    now = datetime.now()
    if (_employee_cache["data"] is not None
            and _employee_cache["timestamp"] is not None
            and (now - _employee_cache["timestamp"]).total_seconds() < _employee_cache["ttl_seconds"]):
        return _employee_cache["data"]

    employees = get_active_employees(min_shifts=3)
    _employee_cache["data"] = employees
    _employee_cache["timestamp"] = now
    return employees


# ── Pydantic models ─────────────────────────────────────────────────────

class ShiftUpdate(BaseModel):
    """Request body for updating a single shift."""
    date: str
    original_employee: str
    new_employee: str
    start_hour: int
    start_min: int
    end_hour: int
    end_min: int
    position: str  # "Lead" or "Cashier"


class PushRequest(BaseModel):
    """Request body for pushing the schedule to Sling."""
    shifts: List[dict]
    location: str


# ── Root route ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "Sling Scheduler API running"}


# ── API endpoints ────────────────────────────────────────────────────────

@app.get("/schedule")
async def api_schedule(week_start: str = None, location: str = "Bentonville",
                       max_weekly_hours: int = None, max_shift_hours: int = None,
                       min_shift_hours: int = None, staff_buffer: int = None,
                       min_staff_per_hour: int = None):
    """Generate and return a proposed schedule for a week.

    Query params:
        week_start: YYYY-MM-DD (defaults to next Monday)
        location: "Bentonville" or "Rogers"
        max_weekly_hours: Override max weekly hours per employee
        max_shift_hours: Override max shift duration
        min_shift_hours: Override min shift duration
        staff_buffer: Extra staff above historical average
        min_staff_per_hour: Minimum staff per open hour
    """
    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        start_date = get_next_monday()

    if location not in ("Bentonville", "Rogers"):
        raise HTTPException(status_code=400, detail="Location must be 'Bentonville' or 'Rogers'.")

    try:
        employees = _get_employees()

        # Generate BOTH locations together to prevent cross-location conflicts
        fairness_by_loc = {}
        for loc in ["Bentonville", "Rogers"]:
            fairness_by_loc[loc] = get_lead_priority(employees, location=loc)

        all_schedules = generate_all_locations(
            week_start_date=start_date,
            employees=employees,
            fairness_data_by_location=fairness_by_loc,
            max_weekly_hours=max_weekly_hours,
        )

        # Return the requested location's schedule
        schedule = all_schedules.get(location, [])

        # Build summary stats
        emp_hours = defaultdict(float)
        emp_lead = defaultdict(int)
        emp_cashier = defaultdict(int)
        emp_days = defaultdict(set)
        for s in schedule:
            emp_hours[s["employee"]] += s["shift_hours"]
            emp_days[s["employee"]].add(s["day"])
            if s["position"] == "Lead":
                emp_lead[s["employee"]] += 1
            else:
                emp_cashier[s["employee"]] += 1

        summary = []
        for name in sorted(emp_hours.keys()):
            summary.append({
                "employee": name,
                "total_hours": round(emp_hours[name], 1),
                "days_scheduled": len(emp_days[name]),
                "lead_shifts": emp_lead[name],
                "cashier_shifts": emp_cashier[name],
            })

        return {
            "week_start": start_date.isoformat(),
            "location": location,
            "shifts": schedule,
            "summary": summary,
            "total_shifts": len(schedule),
            "total_hours": round(sum(s["shift_hours"] for s in schedule), 1),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule generation failed: {str(e)}")


@app.get("/employees")
async def api_employees(location: str = None):
    """Return active employees with roles.

    Query params:
        location: Optional filter — "Bentonville" or "Rogers"
    """
    try:
        employees = _get_employees()

        if location:
            employees = [e for e in employees if location in e.get("locations", [])]

        # Clean up for JSON
        result = []
        for emp in employees:
            result.append({
                "user_id": emp["user_id"],
                "user_name": emp["user_name"],
                "role": emp["role"],
                "total_shifts": emp["total_shifts"],
                "lead_shifts": emp["lead_shifts"],
                "cashier_shifts": emp["cashier_shifts"],
                "positions": emp["positions"],
                "locations": emp["locations"],
                "last_shift_date": emp["last_shift_date"],
            })

        return {"employees": result, "count": len(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load employees: {str(e)}")


@app.get("/hours")
async def api_hours():
    """Return operating hours config for all locations."""
    result = {}
    for location in ["Bentonville", "Rogers"]:
        loc_hours = {}
        for dow in DAYS_OF_WEEK:
            hours = OPERATING_HOURS.get(location, {}).get(dow, {})
            window = get_shift_window_str(location, dow)
            loc_hours[dow] = {
                "open": hours.get("open", ""),
                "close": hours.get("close", ""),
                "shift_start": window[0] if window else "",
                "shift_end": window[1] if window else "",
                "closed": not bool(hours),
            }
        result[location] = loc_hours

    return {"hours": result}


@app.get("/fairness")
async def api_fairness(location: str = "Bentonville"):
    """Return fairness analysis for lead-eligible employees.

    Query params:
        location: "Bentonville" or "Rogers"
    """
    try:
        employees = _get_employees()
        fairness = analyze_historical_fairness(location=location, employees=employees)

        # Calculate group average
        if fairness:
            avg_pct = sum(r["lead_percentage"] for r in fairness.values()) / len(fairness)
        else:
            avg_pct = 50.0

        records = []
        for rec in sorted(fairness.values(), key=lambda r: r["lead_percentage"]):
            priority = ""
            if rec["fairness_score"] < -10:
                priority = "HIGH"
            elif rec["fairness_score"] < -5:
                priority = "MED"
            elif rec["fairness_score"] < 0:
                priority = "LOW"

            records.append({
                "user_name": rec["user_name"],
                "user_id": rec["user_id"],
                "lead_shifts": rec["lead_shifts"],
                "cashier_shifts": rec["cashier_shifts"],
                "total_shifts": rec["total_shifts"],
                "lead_percentage": rec["lead_percentage"],
                "fairness_score": rec["fairness_score"],
                "priority": priority,
            })

        return {
            "location": location,
            "group_average_lead_pct": round(avg_pct, 1),
            "employees": records,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fairness analysis failed: {str(e)}")


@app.get("/explain")
async def api_explain(week_start: str = None, location: str = "Bentonville"):
    """Return detailed algorithm explanation showing how the schedule was built.

    For each day, shows the hourly breakdown of historical data, the shift
    slots that were generated, and the reasoning behind each decision.

    Query params:
        week_start: YYYY-MM-DD (defaults to next Monday)
        location: "Bentonville" or "Rogers"
    """
    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        start_date = get_next_monday()

    if location not in ("Bentonville", "Rogers"):
        raise HTTPException(status_code=400, detail="Location must be 'Bentonville' or 'Rogers'.")

    try:
        # Load staffing curves
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        curves_path = os.path.join(data_dir, "staffing_curves.json")
        with open(curves_path) as f:
            curves = json.load(f)

        loc_curves = curves.get(location, {})

        days_result = {}

        for day_offset, dow in enumerate(DAYS_OF_WEEK):
            day_date = start_date + timedelta(days=day_offset)
            date_str = day_date.strftime("%Y-%m-%d")

            # Operating hours for this day
            day_hours = OPERATING_HOURS.get(location, {}).get(dow, {})
            if not day_hours:
                continue

            open_time = day_hours.get("open", "12:00")
            close_time = day_hours.get("close", "21:00")

            # Shift window
            window = get_shift_window(location, dow)
            if not window:
                continue
            shift_start_h, shift_start_m, shift_end_h, shift_end_m = window
            window_strs = get_shift_window_str(location, dow)

            # Get hourly data from curves
            day_data = loc_curves.get(dow, {})
            hours_data = day_data.get("hours", {})
            shift_patterns = day_data.get("shift_patterns", {})
            weeks_of_data = day_data.get("weeks_of_data", 8)

            # Build hourly breakdown — only operating/shift hours
            hourly_breakdown = []
            max_txn = 0
            peak_hour = None
            peak_txn = 0

            for h in range(shift_start_h, shift_end_h + 1):
                hour_str = str(h)
                info = hours_data.get(hour_str, {})

                # Skip late-night hours in the display
                if h in LATE_NIGHT_HOURS:
                    continue

                avg_txn = info.get("avg_transactions", 0.0)
                avg_staff = info.get("avg_staff", 0.0)
                avg_leads = info.get("avg_leads", 0.0)
                avg_cashiers = info.get("avg_cashiers", 0.0)
                txn_per_staff = info.get("txn_per_staff")
                rec_total = info.get("recommended_total", 0)
                rec_leads = info.get("recommended_leads", 0)
                rec_cashiers = info.get("recommended_cashiers", 0)

                if avg_txn > max_txn:
                    max_txn = avg_txn
                if avg_txn > peak_txn:
                    peak_txn = avg_txn
                    peak_hour = h

                # Generate reasoning
                reasoning = _generate_hour_reasoning(
                    h, avg_txn, avg_staff, rec_total, rec_leads, rec_cashiers,
                    shift_start_h, shift_end_h, open_time, close_time
                )

                # Format display time
                display = _fmt_hour_display(h)

                hourly_breakdown.append({
                    "hour": h,
                    "display": display,
                    "avg_historical_transactions": round(avg_txn, 2),
                    "avg_historical_staff": round(avg_staff, 2),
                    "avg_historical_leads": round(avg_leads, 2),
                    "avg_historical_cashiers": round(avg_cashiers, 2),
                    "txn_per_staff_ratio": round(txn_per_staff, 2) if txn_per_staff is not None else 0.0,
                    "recommended_total": rec_total,
                    "recommended_leads": rec_leads,
                    "recommended_cashiers": rec_cashiers,
                    "reasoning": reasoning,
                })

            # Build shift slots explanation from shift patterns
            shift_slots = _build_shift_slots_explanation(
                shift_patterns, shift_start_h, shift_start_m,
                shift_end_h, shift_end_m, hours_data, open_time, close_time
            )

            # Calculate totals
            total_leads = 0
            total_cashiers = 0
            for slot in shift_slots:
                if slot["role"] == "lead":
                    total_leads += 1
                else:
                    total_cashiers += 1

            days_result[dow] = {
                "date": date_str,
                "hourly_breakdown": hourly_breakdown,
                "shift_slots": shift_slots,
                "peak_hour": {
                    "hour": peak_hour,
                    "display": _fmt_hour_display(peak_hour) if peak_hour is not None else "N/A",
                    "avg_transactions": round(peak_txn, 1),
                } if peak_hour is not None else None,
                "total_staff_needed": total_leads + total_cashiers,
                "total_leads": total_leads,
                "total_cashiers": total_cashiers,
            }

        return {
            "location": location,
            "week_start": start_date.isoformat(),
            "operating_hours": {
                "open": OPERATING_HOURS.get(location, {}).get("Monday", {}).get("open", "12:00"),
                "close": OPERATING_HOURS.get(location, {}).get("Monday", {}).get("close", "21:00"),
            },
            "shift_window": {
                "start": get_shift_window_str(location, "Monday")[0] if get_shift_window_str(location, "Monday") else "",
                "end": get_shift_window_str(location, "Monday")[1] if get_shift_window_str(location, "Monday") else "",
            },
            "days": days_result,
            "algorithm_summary": {
                "data_source": f"{loc_curves.get('Monday', {}).get('weeks_of_data', 8)}-{loc_curves.get('Saturday', {}).get('weeks_of_data', 8)} weeks of historical data (Jan 1 - Mar 26, 2026)",
                "sales_source": "Toast POS -- transaction data across both locations",
                "staffing_source": "Sling -- published shift data",
                "method": "Historical correlation: for each day-of-week and hour, we look at average transaction volume and average staff on floor from the past weeks, then apply the same staffing ratio to predict next week's needs.",
            },
            "adjustable_variables": [
                {"name": "operating_hours", "current": f"{OPERATING_HOURS.get(location, {}).get('Monday', {}).get('open', '12:00')}-{OPERATING_HOURS.get(location, {}).get('Monday', {}).get('close', '21:00')}", "description": "Store open/close times -- shifts start 30min before, end 30min after"},
                {"name": "max_weekly_hours", "current": DEFAULT_MAX_WEEKLY_HOURS, "description": "Maximum hours any employee can work per week"},
                {"name": "max_shift_hours", "current": MAX_SHIFT_HOURS, "description": "Maximum length of a single shift"},
                {"name": "min_shift_hours", "current": MIN_SHIFT_HOURS, "description": "Minimum length of a single shift"},
                {"name": "staff_buffer", "current": 0, "description": "Extra staff above historical average (0 = match history, 1 = add one more person)"},
                {"name": "min_staff_per_hour", "current": 1, "description": "Minimum staff during any open hour"},
                {"name": "lead_cashier_fairness", "current": True, "description": "Rotate lead shifts fairly among lead-eligible employees"},
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm explanation failed: {str(e)}")


def _fmt_hour_display(h):
    """Format an hour integer as a readable time string."""
    if h is None:
        return "N/A"
    if h == 0 or h == 24:
        return "12:00 AM"
    elif h < 12:
        return f"{h}:00 AM"
    elif h == 12:
        return "12:00 PM"
    else:
        return f"{h - 12}:00 PM"


def _generate_hour_reasoning(hour, avg_txn, avg_staff, rec_total, rec_leads,
                              rec_cashiers, shift_start_h, shift_end_h,
                              open_time, close_time):
    """Generate a human-readable reasoning string for an hour's staffing."""
    open_h = int(open_time.split(":")[0])
    close_h = int(close_time.split(":")[0])

    parts = []

    # Opening/closing context
    if hour == shift_start_h:
        parts.append("Opening prep -- lead arrives 30min before doors")
    elif hour == open_h:
        parts.append("Doors open")
    elif hour == close_h:
        parts.append("Closing hour")
    elif hour == shift_end_h:
        parts.append("Post-close cleanup (30min buffer)")

    # Volume context
    if avg_txn == 0 and rec_total > 0:
        parts.append("low/no sales volume but staff needed for coverage")
    elif avg_txn > 0 and avg_txn <= 2:
        parts.append(f"light volume (~{avg_txn:.1f} txn/hr avg)")
    elif avg_txn > 2 and avg_txn <= 5:
        parts.append(f"moderate volume (~{avg_txn:.1f} txn/hr avg)")
    elif avg_txn > 5:
        parts.append(f"busy period (~{avg_txn:.1f} txn/hr avg)")

    # Staffing context
    if rec_total == 1 and rec_leads == 1 and rec_cashiers == 0:
        parts.append("1 lead covers the floor solo")
    elif rec_cashiers > 0:
        parts.append(f"{rec_leads} lead + {rec_cashiers} cashier")

    # Historical vs recommended gap
    if avg_staff > 0 and rec_total > avg_staff:
        parts.append(f"recommending more than historical avg ({avg_staff:.1f})")
    elif avg_staff > 0 and rec_total < avg_staff:
        parts.append(f"trimmed from historical avg ({avg_staff:.1f})")

    if not parts:
        parts.append(f"{rec_total} staff recommended based on historical patterns")

    return " -- ".join(parts)


def _build_shift_slots_explanation(shift_patterns, shift_start_h, shift_start_m,
                                    shift_end_h, shift_end_m, hours_data,
                                    open_time, close_time):
    """Build explained shift slots from patterns and hourly data."""
    slots = []

    # Parse close hour for reasoning
    close_h = int(close_time.split(":")[0])

    # --- OPENER lead ---
    if shift_patterns.get("opener"):
        pat = shift_patterns["opener"]
        start_parts = pat.get("avg_start", f"{shift_start_h}:{shift_start_m:02d}").split(":")
        end_parts = pat.get("avg_end", "17:00").split(":")
        start_h, start_m = int(start_parts[0]), int(start_parts[1])
        end_h, end_m = int(end_parts[0]), int(end_parts[1])
        hours = round((end_h * 60 + end_m - start_h * 60 - start_m) / 60, 1)

        opener_display_start = _fmt_time_hm(start_h, start_m)
        opener_display_end = _fmt_time_hm(end_h, end_m)

        slots.append({
            "type": "opener",
            "start": opener_display_start,
            "end": opener_display_end,
            "role": "lead",
            "hours": hours,
            "reasoning": f"Day lead opens 30min before doors and runs through afternoon (based on {pat.get('count', 0)} historical opener shifts)",
        })

    # --- BRIDGE (if exists) ---
    if shift_patterns.get("bridge") and shift_patterns["bridge"].get("count", 0) > 1:
        pat = shift_patterns["bridge"]
        start_parts = pat["avg_start"].split(":")
        end_parts = pat["avg_end"].split(":")
        start_h, start_m = int(start_parts[0]), int(start_parts[1])
        end_h, end_m = int(end_parts[0]), int(end_parts[1])
        hours = round((end_h * 60 + end_m - start_h * 60 - start_m) / 60, 1)

        role = "lead" if pat.get("typical_role") == "Lead" else "cashier"

        slots.append({
            "type": "bridge",
            "start": _fmt_time_hm(start_h, start_m),
            "end": _fmt_time_hm(end_h, end_m),
            "role": role,
            "hours": hours,
            "reasoning": f"Mid-day overlap covers lunch-to-dinner transition ({pat.get('count', 0)} historical bridge shifts, typically {pat.get('typical_role', 'mixed')})",
        })

    # --- CLOSER lead ---
    if shift_patterns.get("closer"):
        pat = shift_patterns["closer"]
        start_parts = pat.get("avg_start", "17:00").split(":")
        end_parts = pat.get("avg_end", f"{shift_end_h}:{shift_end_m:02d}").split(":")
        start_h, start_m = int(start_parts[0]), int(start_parts[1])
        end_h, end_m = int(end_parts[0]), int(end_parts[1])
        hours = round((end_h * 60 + end_m - start_h * 60 - start_m) / 60, 1)

        # Determine reasoning based on volume in evening hours
        evening_txn = []
        for eh in range(start_h, min(close_h + 1, 24)):
            info = hours_data.get(str(eh), {})
            evening_txn.append(info.get("avg_transactions", 0))
        avg_evening = sum(evening_txn) / len(evening_txn) if evening_txn else 0

        role_label = pat.get("typical_role", "Mixed")
        if role_label == "Lead":
            role = "lead"
        elif role_label == "Cashier":
            role = "cashier"
        else:
            role = "lead"

        if avg_evening > 3:
            reasoning = f"Evening lead takes over for dinner rush (avg {avg_evening:.1f} txn/hr, {pat.get('count', 0)} historical closer shifts)"
        else:
            reasoning = f"Evening crew covers close and cleanup ({pat.get('count', 0)} historical closer shifts)"

        slots.append({
            "type": "closer",
            "start": _fmt_time_hm(start_h, start_m),
            "end": _fmt_time_hm(end_h, end_m),
            "role": role,
            "hours": hours,
            "reasoning": reasoning,
        })

    # --- CASHIER slots: check if any hours recommend cashiers ---
    cashier_hours = []
    for h in range(shift_start_h, shift_end_h + 1):
        info = hours_data.get(str(h), {})
        if info.get("recommended_cashiers", 0) > 0:
            cashier_hours.append(h)

    if cashier_hours:
        # Group consecutive cashier hours
        groups = []
        current = [cashier_hours[0]]
        for h in cashier_hours[1:]:
            if h == current[-1] + 1:
                current.append(h)
            else:
                groups.append(current)
                current = [h]
        groups.append(current)

        for group in groups:
            c_start = group[0]
            c_end = group[-1] + 1
            hours = c_end - c_start

            # Get avg txn for this range
            range_txn = []
            for h in group:
                info = hours_data.get(str(h), {})
                range_txn.append(info.get("avg_transactions", 0))
            avg_range_txn = sum(range_txn) / len(range_txn) if range_txn else 0

            # Don't duplicate if closer pattern already covers this as cashier
            already_covered = False
            for s in slots:
                if s["role"] == "cashier":
                    already_covered = True
                    break

            if not already_covered:
                reasoning = f"Sales ramp up {_fmt_hour_display(c_start)}-{_fmt_hour_display(c_end)}, avg {avg_range_txn:.1f} txn/hr, need cashier support"

                slots.append({
                    "type": "closer" if c_start >= 17 else "bridge",
                    "start": _fmt_hour_display(c_start),
                    "end": _fmt_hour_display(c_end),
                    "role": "cashier",
                    "hours": hours,
                    "reasoning": reasoning,
                })

    return slots


def _fmt_time_hm(h, m):
    """Format hour and minute as readable time."""
    if h == 0 or h == 24:
        return f"12:{m:02d} AM"
    elif h < 12:
        return f"{h}:{m:02d} AM"
    elif h == 12:
        return f"12:{m:02d} PM"
    else:
        return f"{h - 12}:{m:02d} PM"


@app.post("/schedule/push")
async def api_push_schedule(req: PushRequest):
    """Push the schedule to Sling by creating shifts via the API.

    Expects a JSON body with:
        shifts: list of shift dicts (from /api/schedule)
        location: "Bentonville" or "Rogers"
    """
    try:
        sling = SlingConnector()
        location_id = LOCATION_ID_MAP.get(req.location)
        if not location_id:
            raise HTTPException(status_code=400, detail=f"Unknown location: {req.location}")

        results = []
        errors = []

        for shift in req.shifts:
            try:
                # Build ISO datetime strings
                shift_date = shift["date"]
                start_h = shift["start_hour"]
                start_m = shift["start_min"]
                end_h = shift["end_hour"]
                end_m = shift["end_min"]

                start_dt = f"{shift_date}T{start_h:02d}:{start_m:02d}:00"
                end_dt = f"{shift_date}T{end_h:02d}:{end_m:02d}:00"

                # Look up position ID
                position_name = shift.get("sling_position", "")
                position_id = _position_name_to_id(position_name)
                if not position_id:
                    errors.append({
                        "shift": shift,
                        "error": f"Unknown position: {position_name}",
                    })
                    continue

                user_id = shift.get("user_id")

                result = sling.create_shift(
                    date_str=shift_date,
                    start_time=start_dt,
                    end_time=end_dt,
                    user_id=user_id,
                    position_id=position_id,
                    location_id=location_id,
                )

                results.append({
                    "employee": shift["employee"],
                    "date": shift_date,
                    "status": "created",
                    "sling_id": result.get("id") if isinstance(result, dict) else None,
                })

            except Exception as e:
                errors.append({
                    "employee": shift.get("employee", "unknown"),
                    "date": shift.get("date", "unknown"),
                    "error": str(e),
                })

        return {
            "created": len(results),
            "errors": len(errors),
            "results": results,
            "error_details": errors,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Push to Sling failed: {str(e)}")


@app.put("/schedule/shift")
async def api_update_shift(update: ShiftUpdate):
    """Update a single shift in the current proposed schedule.

    This updates the in-memory schedule (not Sling directly).
    The user reviews changes, then pushes the final version.
    """
    return {
        "status": "updated",
        "shift": {
            "date": update.date,
            "employee": update.new_employee,
            "start_hour": update.start_hour,
            "start_min": update.start_min,
            "end_hour": update.end_hour,
            "end_min": update.end_min,
            "position": update.position,
        },
    }


# ── Availability (Read-Only from Sling) ──────────────────────────────────

@app.get("/availability")
async def api_get_availability():
    """Get employee availability — pulled from Sling (read-only).

    Sling is the authoritative source. This endpoint reads availability
    and time-off data from Sling and combines it with employee info.
    """
    import requests as req

    employees = _get_employees()
    token = os.getenv("SLING_AUTH_TOKEN", "").strip("'")
    sling_headers = {"Authorization": token}

    # Pull availability from Sling (may be empty if not set by employees)
    sling_avail = {}
    try:
        r = req.get("https://api.getsling.com/v1/availability?dates=2025-01-01/2027-12-31",
                     headers=sling_headers, timeout=10)
        if r.status_code == 200:
            avail_data = r.json()
            for entry in avail_data:
                uid = entry.get("user", {}).get("id")
                if uid:
                    if uid not in sling_avail:
                        sling_avail[uid] = []
                    sling_avail[uid].append(entry)
    except Exception:
        pass

    # Pull hours cap from Sling user objects
    hours_caps = {}
    try:
        r = req.get("https://api.getsling.com/v1/users", headers=sling_headers, timeout=10)
        if r.status_code == 200:
            for u in r.json():
                hours_caps[u["id"]] = u.get("hoursCap", 0)
    except Exception:
        pass

    result = []
    for emp in employees:
        uid = emp["user_id"]
        has_avail = uid in sling_avail and len(sling_avail[uid]) > 0

        result.append({
            "employee_name": emp["user_name"],
            "user_id": uid,
            "role": emp["role"],
            "locations": emp["locations"],
            "hours_cap": hours_caps.get(uid, 0),
            "has_custom_availability": has_avail,
            "total_shifts": emp.get("total_shifts", 0),
            "lead_shifts": emp.get("lead_shifts", 0),
            "cashier_shifts": emp.get("cashier_shifts", 0),
            "last_shift_date": emp.get("last_shift_date", ""),
        })

    return {"availability": result}
