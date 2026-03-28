"""
Operating hours configuration.

Hardcoded for now based on historical shift data.
Will be replaced with Google Business Profile API pull once approved.

Hours are the POSTED operating hours. Shifts start 30 min before
and end 30 min after these times.
"""

# Operating hours per location per day of week
# Format: {"open": "HH:MM", "close": "HH:MM"} or None if closed
# Close times after midnight use 24+ notation (e.g., "01:00" for 1am)
OPERATING_HOURS = {
    "Bentonville": {
        "Monday":    {"open": "12:00", "close": "21:00"},
        "Tuesday":   {"open": "12:00", "close": "21:00"},
        "Wednesday": {"open": "12:00", "close": "21:00"},
        "Thursday":  {"open": "12:00", "close": "21:00"},
        "Friday":    {"open": "12:00", "close": "22:00"},
        "Saturday":  {"open": "12:00", "close": "22:00"},
        "Sunday":    {"open": "12:00", "close": "21:00"},
    },
    "Rogers": {
        "Monday":    {"open": "12:00", "close": "21:00"},
        "Tuesday":   {"open": "12:00", "close": "21:00"},
        "Wednesday": {"open": "12:00", "close": "21:00"},
        "Thursday":  {"open": "12:00", "close": "21:00"},
        "Friday":    {"open": "12:00", "close": "22:00"},
        "Saturday":  {"open": "12:00", "close": "22:00"},
        "Sunday":    {"open": "12:00", "close": "21:00"},
    },
}

# Shift buffer: how many minutes before open / after close
SHIFT_BUFFER_MINUTES = 30


def get_shift_window(location, day_of_week):
    """Get the shift start and end times for a location/day.

    Returns times with the 30-minute buffer applied.

    Args:
        location: "Bentonville" or "Rogers"
        day_of_week: "Monday", "Tuesday", etc.

    Returns:
        tuple: (shift_start_hour, shift_start_min, shift_end_hour, shift_end_min)
               or None if closed that day.
    """
    loc_hours = OPERATING_HOURS.get(location, {})
    day_hours = loc_hours.get(day_of_week)

    if not day_hours:
        return None

    # Parse open time
    open_parts = day_hours["open"].split(":")
    open_h, open_m = int(open_parts[0]), int(open_parts[1])

    # Parse close time
    close_parts = day_hours["close"].split(":")
    close_h, close_m = int(close_parts[0]), int(close_parts[1])

    # Apply buffer: start 30 min before open
    start_total_min = open_h * 60 + open_m - SHIFT_BUFFER_MINUTES
    shift_start_h = start_total_min // 60
    shift_start_m = start_total_min % 60

    # Apply buffer: end 30 min after close
    end_total_min = close_h * 60 + close_m + SHIFT_BUFFER_MINUTES
    shift_end_h = end_total_min // 60
    shift_end_m = end_total_min % 60

    return (shift_start_h, shift_start_m, shift_end_h, shift_end_m)


def get_shift_window_str(location, day_of_week):
    """Get shift window as readable strings.

    Returns:
        tuple: (start_str, end_str) like ("11:30 AM", "10:00 PM") or None
    """
    window = get_shift_window(location, day_of_week)
    if not window:
        return None

    start_h, start_m, end_h, end_m = window

    def fmt(h, m):
        if h == 0:
            return f"12:{m:02d} AM"
        elif h < 12:
            return f"{h}:{m:02d} AM"
        elif h == 12:
            return f"12:{m:02d} PM"
        elif h < 24:
            return f"{h - 12}:{m:02d} PM"
        else:
            return f"{h - 24}:{m:02d} AM"

    return (fmt(start_h, start_m), fmt(end_h, end_m))
