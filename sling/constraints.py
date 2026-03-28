"""
Scheduling constraints.

Pluggable constraint system. Each constraint is a simple check that
returns True if the assignment is allowed, False if not.

Add new constraints here as needed — the scheduler checks all of them
before making any assignment.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
AVAILABILITY_FILE = os.path.join(DATA_DIR, "employee_availability.json")


def check_max_weekly_hours(employee_name, shift_hours, weekly_hours, max_hours=30):
    """Employee can't exceed max weekly hours."""
    return weekly_hours.get(employee_name, 0) + shift_hours <= max_hours


def check_one_shift_per_day(employee_name, day, daily_assignments):
    """Employee can only work one shift per day."""
    return day not in daily_assignments.get(employee_name, set())


def check_max_shift_duration(shift_hours, max_duration=8):
    """Shift can't exceed max duration in hours."""
    return shift_hours <= max_duration


def check_min_shift_duration(shift_hours, min_duration=3):
    """Shift must be at least min duration in hours."""
    return shift_hours >= min_duration


def check_no_cross_location_conflict(employee_name, day, location, cross_location_assignments):
    """Employee can't be at two locations on the same day.

    cross_location_assignments tracks {employee_name: {day: location}}.
    If they're already assigned to a different location this day, block it.
    """
    assigned = cross_location_assignments.get(employee_name, {})
    if day in assigned and assigned[day] != location:
        return False
    return True


def check_availability(employee_name, day, start_hour=None, end_hour=None):
    """Check if employee is available on this day/time.

    Reads from employee_availability.json. If no availability is set
    for an employee, they're assumed available (open availability).

    Availability format in JSON:
    {
        "Employee Name": {
            "available_days": ["Monday", "Tuesday", ...],
            "available_hours": {"start": 11, "end": 22},
            "time_off_dates": ["2026-04-01", ...],
            "notes": "Can't work Sundays"
        }
    }
    """
    avail = load_availability()
    if not avail or employee_name not in avail:
        return True  # No restrictions set = fully available

    emp_avail = avail[employee_name]

    # Check available days
    if "available_days" in emp_avail and emp_avail["available_days"]:
        if day not in emp_avail["available_days"]:
            return False

    # Check available hours
    if "available_hours" in emp_avail and start_hour is not None:
        avail_start = emp_avail["available_hours"].get("start", 0)
        avail_end = emp_avail["available_hours"].get("end", 24)
        if start_hour < avail_start or (end_hour and end_hour > avail_end):
            return False

    return True


def check_time_off(employee_name, date_str):
    """Check if employee has time off on a specific date.

    Reads from employee_availability.json time_off_dates field.
    """
    avail = load_availability()
    if not avail or employee_name not in avail:
        return True  # No time off set

    emp_avail = avail[employee_name]
    time_off = emp_avail.get("time_off_dates", [])
    if date_str in time_off:
        return False

    return True


def load_availability():
    """Load employee availability from JSON file."""
    if not os.path.exists(AVAILABILITY_FILE):
        return {}
    with open(AVAILABILITY_FILE) as f:
        return json.load(f)


def save_availability(data):
    """Save employee availability to JSON file."""
    os.makedirs(os.path.dirname(AVAILABILITY_FILE), exist_ok=True)
    with open(AVAILABILITY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def can_assign(employee_name, day, shift_hours, weekly_hours, daily_assignments,
               max_weekly_hours=30, max_shift_hours=8,
               location=None, cross_location_assignments=None,
               start_hour=None, end_hour=None, date_str=None):
    """Run all constraints. Returns True if employee can be assigned.

    This is the single entry point the scheduler uses.
    """
    if not check_max_weekly_hours(employee_name, shift_hours, weekly_hours, max_weekly_hours):
        return False
    if not check_one_shift_per_day(employee_name, day, daily_assignments):
        return False
    if not check_max_shift_duration(shift_hours, max_shift_hours):
        return False
    if location and cross_location_assignments is not None:
        if not check_no_cross_location_conflict(employee_name, day, location,
                                                 cross_location_assignments):
            return False
    if not check_availability(employee_name, day, start_hour, end_hour):
        return False
    if date_str and not check_time_off(employee_name, date_str):
        return False
    return True
