import re
from datetime import datetime, timedelta, UTC

import pytz

from constants import REMINDER_YEAR_DAY_FORMAT


def from_timestamp(utc_timestamp: int | float, timezone: str | None = None) -> datetime:
    """
    Convert a UTC timestamp to a timezone-aware datetime object.
    Args:
        utc_timestamp: The UTC timestamp to convert.
        timezone: The timezone string (e.g., 'America/New_York'). If None, UTC is used.
    Returns:
        datetime: A timezone-aware datetime object.
    """
    if timezone:
        return datetime.fromtimestamp(utc_timestamp, pytz.timezone(timezone))
    return datetime.fromtimestamp(utc_timestamp, UTC)


def get_next_year_day(year_day: str, from_datetime: datetime) -> datetime:
    """
    Get the next occurrence of a specific month-day (%B %d) from a given datetime.
    If the specified day does not exist in the next year (e.g., February 29 on a non-leap year),
    it will adjust to the closest valid date (e.g., February 28).
    Args:
        year_day (str): The month-day in "%B %d" format.
        from_datetime (datetime): The starting datetime to calculate from.
    Returns:
        datetime: The next occurrence of the specified month-day.
    """
    next_year = from_datetime.year + 1
    year_day_datetime = datetime.strptime(year_day, REMINDER_YEAR_DAY_FORMAT)
    day = year_day_datetime.day
    month = year_day_datetime.month

    new_datetime = None
    while not new_datetime:
        assert 1 <= day <= 31, 'breaking the infinite loop'
        try:
            new_datetime = from_datetime.replace(year=next_year,
                                                 month=month,
                                                 day=day)
        except ValueError:
            day -= 1

    return new_datetime


def get_next_weekday(weekday: int, from_datetime: datetime) -> datetime:
    """
    Get the next occurrence of a specific weekday from a given datetime.
    Args:
        weekday: The target weekday as an integer (0=Monday, 6=Sunday).
        from_datetime: The starting datetime to calculate from.
    Returns:
        datetime: The next occurrence of the specified weekday.
    """
    days_ahead = weekday - from_datetime.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return from_datetime + timedelta(days=days_ahead)


def get_next_month_day(month_day: int, from_datetime: datetime) -> datetime:
    """
    Get the next occurrence of a specific day of the month from a given datetime.
    If the specified day does not exist in the next month (e.g., February 30),
    it will adjust to the closest valid date (e.g., February 28 or 29).
    Args:
        month_day (int): The target day of the month (1-31).
        from_datetime (datetime): The starting datetime to calculate from.
    Returns:
        datetime: The next occurrence of the specified day of the month.
    """
    next_year = from_datetime.year
    next_month = from_datetime.month
    if month_day <= from_datetime.day:
        next_month += 1
        if next_month == 13:
            next_month = 1
            next_year += 1

    new_datetime = None
    while not new_datetime:
        assert 1 <= month_day <= 31, 'breaking the infinite loop'
        try:
            new_datetime = from_datetime.replace(year=next_year, month=next_month, day=month_day)
        except ValueError:
            month_day -= 1

    return new_datetime


def parse_mal_user_entry_date(date_str: str) -> datetime | None:
    """
    Parse MAL's user entry date string in "MM-DD-YY" format, handling 00" for month/day.
    Args:
        date_str (str): The date string to parse.
    Returns:
        datetime | None: The parsed datetime object, or None if invalid.
    """
    if not date_str:
        return None
    if not re.match(r"^\d{2}-\d{2}-\d{2}$", date_str):
        return None
    month, day, year = date_str.split("-")
    if day == "00":
        day = "01"
    if month == "00":
        month = "01"
    try:
        return datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%y")
    except ValueError:
        return None


def parse_fuzzy_anilist_date_into_str(date: dict[str, int]) -> str | None:
    """
    Parse a fuzzy date dictionary from Anilist into a human-readable string.
    Args:
        date (dict[str, int]): The fuzzy date dictionary with possible keys "year", "month", "day".
    Returns:
        str | None: The formatted date string, or None if year is missing.
    """
    if not date or not date.get("year"):
        return None

    result = f"{date.get("year")}"
    month = datetime.strptime(str(date["month"]), "%m") if date.get("month") else None
    if month:
        month_str = month.strftime("%b")
        if date.get("day"):
            month_str = f"{month_str} {date["day"]}"
        result = f"{month_str}, {result}"

    return result.strip()
