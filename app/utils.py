"""Utilities for working with dates and calendar"""

import calendar
from datetime import date, timedelta
from typing import List, Tuple

WEEK_DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HABIT_COLORS = [
    "#3b82f6",  # Bright blue
    "#10b981",  # Vibrant green
    "#8b5cf6",  # Rich purple
    "#f59e0b",  # Energetic orange
    "#ef4444",  # Bold red
    "#06b6d4",  # Bright cyan
    "#ec4899",  # Vibrant pink
    "#f97316",  # Warm orange-red
]

MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def get_week_days() -> List[str]:
    """Returns list of dates for current week (starting from Monday)"""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


def get_week_day_names() -> List[str]:
    """Returns week day names"""
    return WEEK_DAY_NAMES.copy()


def get_calendar_data(year: int, month: int) -> Tuple[List[List[int]], str]:
    """Returns calendar data for specified year and month"""
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    return cal, month_name


def get_period_dates(period: str) -> List[date]:
    """Returns list of dates for specified period"""
    today = date.today()

    if period == "7days":
        start_date = today - timedelta(days=6)
        return [start_date + timedelta(days=i) for i in range(7)]
    elif period == "30days":
        start_date = today - timedelta(days=29)
        return [start_date + timedelta(days=i) for i in range(30)]
    elif period == "week":
        start_of_week = today - timedelta(days=today.weekday())
        return [start_of_week + timedelta(days=i) for i in range(7)]
    elif period == "month":
        start_of_month = today.replace(day=1)
        next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        dates = []
        current = start_of_month
        while current < next_month:
            dates.append(current)
            current += timedelta(days=1)
        return dates
    else:
        return [today - timedelta(days=i) for i in range(6, -1, -1)]


def format_date_for_display(d: date) -> str:
    """Formats date for display (e.g., '15 Jan')"""
    return f"{d.day} {MONTH_NAMES[d.month]}"


def get_habit_color(habit_index: int) -> str:
    """Returns color for habit by index"""
    return HABIT_COLORS[habit_index % len(HABIT_COLORS)]
