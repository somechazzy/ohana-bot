import codecs
import re

from constants import OFFENSIVE_WORDS_LIST


def clean_text_with_html_tags(html_text: str) -> str:
    """
    Cleans the input HTML text by removing HTML tags and unnecessary whitespace.

    Args:
        html_text (str): The input HTML text to be cleaned.

    Returns:
        str: The cleaned text without HTML tags and extra whitespace.
    """
    return re.sub(re.compile('<.*?>'), '', html_text)


def extract_emojis_from_discord_message(message: str) -> list[tuple[bool, str, int]]:
    """
    Extracts emojis from a Discord message.

    Args:
        message (str): The input message containing emojis.

    Returns:
        list[tuple[bool, str, int]]: A list of tuples where each tuple contains:
            - bool: indicating if the emoji is animated or not.
            - str: emoji name.
            - int: emoji ID.
    """
    emojis = re.findall(r'<(a)?:([^:]+):([0-9]+)>', message)
    return [(bool(a), name, int(id_)) for a, name, id_ in emojis]


def get_time_in_minutes_from_user_text(text: str) -> int:
    """
    Extracts a duration in minutes from the given text.

    Args:
        text (str): The input text containing a duration.

    Returns:
        int: The duration in minutes, or 0 if no valid duration is found.
    """
    total_minutes = 0
    duration_matches = re.findall(r"([0-9]+(?:\.[0-9]+)?[wW] ?)?([0-9]+(?:\.[0-9]+)?[dD] ?)"
                                  r"?([0-9]+(?:\.[0-9]+)?[hH] ?)?([0-9]+(?:\.[0-9]+)?[mM] ?)?", text)

    for duration_tuple in duration_matches:
        weeks, days, hours, minutes = 0, 0, 0, 0
        if len(duration_tuple[0]) > 0:
            weeks = float(str(duration_tuple[0]).replace("w", "").replace("W", ""))
        if len(duration_tuple[1]) > 0:
            days = float(str(duration_tuple[1]).replace("d", "").replace("D", ""))
        if len(duration_tuple[2]) > 0:
            hours = float(str(duration_tuple[2]).replace("h", "").replace("H", ""))
        if len(duration_tuple[3]) > 0:
            minutes = float(str(duration_tuple[3]).replace("m", "").replace("M", ""))
        total_minutes += (weeks * 7 * 24 * 60) + (days * 24 * 60) + (hours * 60) + minutes

    return int(total_minutes)


def text_contains_offensive_words(text: str) -> bool:
    """
    Checks if the given text contains any offensive words.
    Args:
        text (str): The input text to check for offensive words.

    Returns:
        bool: True if the text contains offensive words, False otherwise.
    """
    word_list = codecs.decode(OFFENSIVE_WORDS_LIST.encode('utf-8'), 'base64').decode('utf-8').split(',')
    text = text.lower()
    for word in word_list:
        if word.lower() in text:
            return True
    return False


def get_mal_username_from_url(username: str) -> str:
    """
    Extracts the MyAnimeList username from a given URL or returns the username if it's already in the correct format.
    Args:
        username (str): The input string which can be a URL or a username.

    Returns:
        str: The extracted username or the original string if no URL pattern is matched.
    """
    match = re.search(r"(?:https?://)?(?:www\.)?myanimelist\.net/profile/([a-zA-Z0-9_-]+)", username)
    if match:
        return match.group(1)
    return username


def get_anilist_username_from_url(username: str) -> str:
    """
    Extracts the AniList username from a given URL or returns the username if it's already in the correct format.
    Args:
        username (str): The input string which can be a URL or a username.

    Returns:
        str: The extracted username or the original string if no URL pattern is matched.
    """
    match = re.search(r"(?:https?://)?(?:www\.)?anilist\.co/user/([a-zA-Z0-9_-]+)", username)
    if match:
        return match.group(1)
    return username
