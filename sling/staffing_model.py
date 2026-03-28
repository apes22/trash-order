"""
Staffing model: correlates historical sales with historical staffing
to build a staffing curve and predict future needs.

Late-night transactions (12am-3am) are folded into the evening shift
rather than treated as separate staffing needs.
"""

import math
from collections import defaultdict
from datetime import datetime, timedelta, date

from sling.config import (
    DAYS_OF_WEEK,
    LEAD_POSITIONS,
    CASHIER_POSITIONS,
    SCHEDULABLE_POSITIONS,
    DEFAULT_TRANSACTIONS_PER_STAFF,
    LOCATION_FULL_NAMES,
    LATE_NIGHT_HOURS,
    DEFAULT_OPEN_HOUR,
)
from sling.data_loader import load_shifts, load_hourly_summary, normalize_location


def _parse_shift_hours(shift):
    """Parse a shift's start and end into datetime objects + location."""
    dtstart = shift.get("dtstart_raw", "")
    dtend = shift.get("dtend_raw", "")
    if not dtstart or not dtend:
        return None

    try:
        dt_start = datetime.fromisoformat(dtstart)
        dt_end = datetime.fromisoformat(dtend)
    except (ValueError, TypeError):
        return None

    loc = normalize_location(shift.get("location_name", ""))
    return (dt_start, dt_end, loc)


def build_historical_staffing():
    """Build historical staff-on-floor per location/day/hour.

    Only counts operating hours (skips late-night 0-3am).

    Returns:
        dict: {location: {day_of_week: {hour: [count_per_date]}}}
    """
    shifts = load_shifts()

    date_hour_staff = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for shift in shifts:
        pos = shift.get("position_name", "")
        if pos not in SCHEDULABLE_POSITIONS:
            continue

        parsed = _parse_shift_hours(shift)
        if not parsed:
            continue

        dt_start, dt_end, loc = parsed
        shift_date = shift.get("shift_date", "")

        current = dt_start.replace(minute=0, second=0, microsecond=0)
        while current < dt_end:
            # Skip late-night hours
            if current.hour not in LATE_NIGHT_HOURS:
                date_hour_staff[loc][shift_date][current.hour] += 1
            current += timedelta(hours=1)

    # Aggregate by day-of-week
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for loc, dates in date_hour_staff.items():
        for date_str, hours in dates.items():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                dow = dt.strftime("%A")
            except ValueError:
                continue
            for hour, count in hours.items():
                result[loc][dow][hour].append(count)

    return result


def build_historical_transactions():
    """Build average transactions per location/day-of-week/hour.

    Late-night transactions (0-3am) are excluded from the model since
    they represent closing activity, not separate staffing needs.

    Returns:
        dict: {location: {day_of_week: {hour: avg_transactions}}}
    """
    hourly_data = load_hourly_summary()

    result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for loc, dates in hourly_data.items():
        for date_str, hours in dates.items():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                dow = dt.strftime("%A")
            except ValueError:
                continue

            for hour_str, count in hours.items():
                hour = int(hour_str)
                # Skip late-night hours
                if hour in LATE_NIGHT_HOURS:
                    continue
                result[loc][dow][hour].append(count)

    # Convert lists to averages
    averages = {}
    for loc, days in result.items():
        averages[loc] = {}
        for dow, hours in days.items():
            averages[loc][dow] = {}
            for hour, counts in hours.items():
                averages[loc][dow][hour] = sum(counts) / len(counts)

    return averages


def build_staffing_ratios():
    """Compute historical transactions-per-staff ratio.

    Returns:
        dict: {location: {day_of_week: {hour: {
            "avg_transactions": float,
            "avg_staff": float,
            "ratio": float
        }}}}
    """
    txn_data = build_historical_transactions()
    staff_data = build_historical_staffing()

    ratios = {}
    for loc in set(list(txn_data.keys()) + list(staff_data.keys())):
        ratios[loc] = {}
        txn_days = txn_data.get(loc, {})
        staff_days = staff_data.get(loc, {})

        for dow in DAYS_OF_WEEK:
            ratios[loc][dow] = {}
            txn_hours = txn_days.get(dow, {})
            staff_hours = staff_days.get(dow, {})

            all_hours = set(list(txn_hours.keys()) + list(staff_hours.keys()))
            for hour in sorted(all_hours):
                # Skip late-night
                if hour in LATE_NIGHT_HOURS:
                    continue

                avg_txn = txn_hours.get(hour, 0)
                staff_counts = staff_hours.get(hour, [])
                avg_staff = sum(staff_counts) / len(staff_counts) if staff_counts else 0

                ratio = avg_txn / avg_staff if avg_staff > 0 else DEFAULT_TRANSACTIONS_PER_STAFF

                ratios[loc][dow][hour] = {
                    "avg_transactions": round(avg_txn, 1),
                    "avg_staff": round(avg_staff, 1),
                    "ratio": round(ratio, 1),
                }

    return ratios


def generate_staffing_needs(location, target_week_start):
    """Generate recommended staffing for a target week.

    Uses historical averages to predict transaction volume, then applies
    the historical transactions-per-staff ratio to recommend headcount.
    Only schedules during operating hours (no late-night splits).

    Args:
        location: Short location name ("Bentonville" or "Rogers")
        target_week_start: date or str of the Monday starting the week

    Returns:
        dict: {day_name: {hour: {
            "predicted_transactions": int,
            "recommended_staff": int,
            "recommended_leads": int,
        }}}
    """
    if isinstance(target_week_start, str):
        target_week_start = datetime.strptime(target_week_start, "%Y-%m-%d").date()

    txn_data = build_historical_transactions()
    ratios = build_staffing_ratios()

    loc_txn = txn_data.get(location, {})
    loc_ratios = ratios.get(location, {})

    result = {}
    for day_offset, dow in enumerate(DAYS_OF_WEEK):
        day_txn = loc_txn.get(dow, {})
        day_ratios = loc_ratios.get(dow, {})

        result[dow] = {}
        for hour in sorted(set(list(day_txn.keys()) + list(day_ratios.keys()))):
            # Skip late-night hours
            if hour in LATE_NIGHT_HOURS:
                continue

            predicted_txn = day_txn.get(hour, 0)
            ratio_info = day_ratios.get(hour, {})
            hist_ratio = ratio_info.get("ratio", DEFAULT_TRANSACTIONS_PER_STAFF)

            if predicted_txn > 0:
                raw_staff = predicted_txn / hist_ratio
                recommended_staff = max(1, round(raw_staff))
            else:
                recommended_staff = 0

            # Always exactly 1 lead per staffed hour
            recommended_leads = 1 if recommended_staff > 0 else 0

            result[dow][hour] = {
                "predicted_transactions": round(predicted_txn),
                "recommended_staff": recommended_staff,
                "recommended_leads": recommended_leads,
            }

    return result
