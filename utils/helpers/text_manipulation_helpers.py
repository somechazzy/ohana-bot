from datetime import datetime, UTC

from constants import DAY_OF_WEEK_NUMBER_NAME_MAP


def shorten_text(text: str, max_length: int) -> str:
    """
    Shorten text to a maximum length, adding ellipsis if truncated.
    Args:
        text (str): The text to shorten.
        max_length (int): The maximum allowed length of the text.
    Returns:
        str: The shortened text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..." if max_length > 3 else "..."


def get_human_readable_app_log_category(category: str) -> str:
    """
    Convert app log category to a human-readable format.
    Args:
        category (str): The app log category string.
    Returns:
        str: The human-readable app log category.
    """
    category = category.replace("_", " ") \
        .replace("BOT ", "BOT - ") \
        .replace("APP ", "APP - ")
    return category.title()


def get_human_readable_number(number: int) -> str:
    """
    Convert a number to a human-readable format with commas.
    Args:
        number (int): The number to convert.
    Returns:
        str: The human-readable number.
    """
    return f"{number:,}" if number else "0"


def get_discord_emoji_string(emoji_name: str, emoji_id: int, is_animated: bool) -> str:
    """
    Return a formatted Discord emoji string.
    Args:
        emoji_name (str): The name of the emoji.
        emoji_id (int): The ID of the emoji.
        is_animated (bool): Whether the emoji is animated.
    Returns:
        str: The formatted Discord emoji string.
    """
    return f"<{'a' if is_animated else ''}:{emoji_name}:{emoji_id}>"


def get_human_readable_time(minutes: int | float) -> str:
    """
    Convert time in minutes to a human-readable format.
    Args:
        minutes (int | float): The time in minutes.
    Returns:
        str: The human-readable time string.
    """
    days = int(minutes // (60 * 24))
    hours = int((minutes % (60 * 24)) // 60)
    minutes = int(minutes % 60)
    days_str = f"{days} day{'s' if days != 1 else ''}" if days > 0 else ""
    hours_str = f"{hours} hour{'s' if hours != 1 else ''}" if hours > 0 else ""
    minutes_str = f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else ""
    parts = [part for part in [days_str, hours_str, minutes_str] if part]
    if not parts:
        return "0 minutes"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return " and ".join(parts)
    else:
        return ", ".join(parts[:-1]) + " and " + parts[-1]


def get_days_of_week_from_numbers(days: list[int]) -> list[str]:
    """
    Convert a list of day numbers to their corresponding names.
    Args:
        days (list[int]): List of day numbers (0=Monday, 6=Sunday).
    Returns:
        list[str]: List of day names.
    """
    days_of_week = []
    for day in sorted(days):
        if day not in DAY_OF_WEEK_NUMBER_NAME_MAP:
            continue
        days_of_week.append(DAY_OF_WEEK_NUMBER_NAME_MAP[day])
    return days_of_week


def get_numbers_with_suffix(numbers: list[int]) -> list[str]:
    """
    Convert a list of numbers to their human-readable format with ordinal suffixes.
    Args:
        numbers (list[int]): List of numbers.
    Returns:
        list[str]: List of numbers with ordinal suffixes.
    """
    numbers_with_suffix = []
    for number in numbers:
        if number % 10 == 1 and number != 11:
            suffix = "st"
        elif number % 10 == 2 and number != 12:
            suffix = "nd"
        elif number % 10 == 3 and number != 13:
            suffix = "rd"
        else:
            suffix = "th"
        numbers_with_suffix.append(f"{number}{suffix}")
    return numbers_with_suffix


def get_progress_bar_from_percentage(percentage: float) -> str:
    """
    Generate a progress bar string from a percentage.
    Args:
        percentage (float): The progress percentage (0.0 to 1.0).
    Returns:
        str: The progress bar string.
    """
    # https://i.redd.it/97p4ob5aebj51.png
    played_squares = round(percentage * 20)
    unplayed_squares = 20 - played_squares
    return '█' * played_squares + '░' * unplayed_squares


def convert_seconds_to_numeric_time(seconds: int) -> str:
    """
    Convert seconds to a numeric time format (HH:MM:SS) or (MM:SS) if less than an hour.
    Args:
        seconds (int): The time in seconds. Must be less than 24 hours (86400 seconds).
    Returns:
        str: The numeric time string.
    """
    dt = datetime.fromtimestamp(seconds, tz=UTC)
    if dt.hour >= 1:
        return dt.strftime("%H:%M:%S")
    else:
        return dt.strftime("%M:%S")


def get_shortened_human_readable_number(number: int):  # stackoverflow.com/a/45846841
    """
    Convert a number to a shortened human-readable format (e.g., 1.2K, 3.4M).
    Args:
        number (int): The number to convert.
    Returns:
        str: The shortened human-readable number.
    """
    num = float('{:.3g}'.format(number))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
        if magnitude == 4:
            break
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
