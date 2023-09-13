import copy
from math import floor

from globals_ import constants
from globals_.constants import XPSettingsKey, OSType
from globals_.settings import settings


def convert_minutes_to_time_string(minutes: int):
    days = int(minutes / (60 * 24))
    hours = int(minutes / 60) % 24
    minutes = minutes % 60
    days_string = f"{days} days" if days > 1 else f"{days} day" if days == 1 else ""
    hours_string = f"{hours} hours" if hours > 1 else f"{hours} hour" if hours == 1 else ""
    minutes_string = f"{minutes} minutes" if minutes > 1 else f"{minutes} minute" if minutes == 1 else ""
    if days and hours and minutes:
        time_string = f"{days_string}, {hours_string} and {minutes_string}"
    elif days and hours:
        time_string = f"{days_string} and {hours_string}"
    elif hours and minutes:
        time_string = f"{hours_string} and {minutes_string}"
    elif days and minutes:
        time_string = f"{days_string} and {minutes_string}"
    elif days:
        time_string = f"{days_string}"
    elif hours:
        time_string = f"{hours_string}"
    elif minutes:
        time_string = f"{minutes_string}"
    else:
        time_string = "unknown time"

    return time_string


def shorten_text_if_above_x_characters(text: str, limit):
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def get_encrypted_string(text: str):
    for symbol in constants.ENCRYPTED_CHARACTERS.keys():
        text = text.replace(symbol, constants.ENCRYPTED_CHARACTERS[symbol])
    return text


def get_decrypted_string(text: str):
    for symbol in constants.ENCRYPTED_CHARACTERS.keys():
        text = text.replace(constants.ENCRYPTED_CHARACTERS[symbol], symbol)
    return text


def encrypt_guild_prefs_keys(guild_prefs):
    keys_ar = []
    new_dicts_ar = {}
    for key in guild_prefs.auto_responses.keys():
        new_key = get_encrypted_string(key)
        new_dicts_ar[new_key] = copy.deepcopy(guild_prefs.auto_responses[key])
        keys_ar.append(key)
    for key in keys_ar:
        guild_prefs.auto_responses.pop(key)
    for key in new_dicts_ar.keys():
        guild_prefs.auto_responses[key] = new_dicts_ar[key]

    return guild_prefs


def stringify_xp_settings_values(xp_settings: dict):
    xp_settings[XPSettingsKey.LEVELUP_CHANNEL] = str(xp_settings[XPSettingsKey.LEVELUP_CHANNEL])

    str_ignored_channels = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_CHANNELS]]
    xp_settings[XPSettingsKey.IGNORED_CHANNELS] = str_ignored_channels

    str_ignored_roles = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_ROLES]]
    xp_settings[XPSettingsKey.IGNORED_ROLES] = str_ignored_roles

    for key, value in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
        xp_settings[XPSettingsKey.LEVEL_ROLES][key] = str(value)

    return xp_settings


def data_size_human_format(num):  # stackoverflow.com/a/45846841
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
        if magnitude == 4:
            break
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def build_path(relative_path_params: [], append_main_path=True):
    # whatever the fuck this function has become
    if settings.os_type == OSType.WINDOWS:
        relative_path = '\\' + '\\'.join(relative_path_params)
    else:
        relative_path = '/' if (append_main_path and not settings.main_path.endswith('/')) else ''
        relative_path += '/'.join(relative_path_params)
    path = (settings.main_path + relative_path) if append_main_path else relative_path
    if path.startswith("\\C:\\"):
        path = path.replace("\\C:\\", "C:\\", 1)
    return path


def convert_seconds_to_numeric_time(seconds):
    remaining_seconds = seconds
    hours = str(floor(remaining_seconds / 3600))
    remaining_seconds = remaining_seconds % 3600
    minutes = str(floor(remaining_seconds / 60))
    remaining_seconds = remaining_seconds % 60
    numeric_time = ''
    if hours != '0':
        if len(hours) == 1:
            hours = f"0{hours}"
        numeric_time += f'{hours}:'
    if minutes != '0':
        if len(minutes) == 1:
            minutes = f"0{minutes}"
        numeric_time += f'{minutes}:'
    else:
        numeric_time += '00:'
    remaining_seconds = str(remaining_seconds)
    if len(remaining_seconds) == 1:
        remaining_seconds = f"0{remaining_seconds}"
    numeric_time += f'{remaining_seconds}'
    return numeric_time


def get_lyrics_pages(lyrics):
    lyrics_lines = lyrics.split("\n")
    lyrics_pages = []
    lyrics_page = ""
    for lyrics_line in lyrics_lines:
        lyrics_page_with_new_line = lyrics_page + f"{lyrics_line}\n"
        if len(lyrics_page_with_new_line) < 4000:
            lyrics_page = lyrics_page_with_new_line
        else:
            lyrics_pages.append(lyrics_page.strip())
            lyrics_page = f"{lyrics_line}\n"
    lyrics_page = lyrics_page.replace("EmbedCopy", "").replace("URLCopy", "").replace("EmbedShare", "").strip()
    while lyrics_page[-1].isdigit():
        lyrics_page = lyrics_page[:-1]
    lyrics_pages.append(lyrics_page.strip())

    return lyrics_pages


def get_progress_bar_from_percentage(percentage):
    # https://i.redd.it/97p4ob5aebj51.png
    p = '█'
    u = '░'
    played_squares = round(percentage * 20)
    unplayed_squares = 20 - played_squares
    return p * played_squares + u * unplayed_squares
