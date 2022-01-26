import copy
import random
import re
from math import floor
from globals_ import variables
from globals_.constants import XPSettingsKey, OSType, UWUFY_FACES, ENCRYPTED_CHARACTERS


def convert_minutes_to_time_string(minutes: int):
    days = int(minutes / (60 * 24))
    hours = int(minutes / 60) % 24
    minutes = minutes % 60
    days_string = f"{days} day{'s' if days > 1 else ''}"
    hours_string = f"{hours} hour{'s' if hours > 1 else ''}"
    minutes_string = f"{minutes} minute{'s' if minutes > 1 else ''}"
    time_string = f"{days_string}, {hours_string} and {minutes_string}"
    time_string = time_string.replace("0 day,", "")\
        .replace("0 hour and", "")\
        .replace(", 0 hour", "")\
        .replace("and 0 minute", "")\
        .strip()
    if not time_string:
        time_string = "unknown time"
    # if days and hours and minutes:
    #     time_string = f"{days_string}, {hours_string} and {minutes_string}"
    # elif days and hours:
    #     time_string = f"{days_string} and {hours_string}"
    # elif hours and minutes:
    #     time_string = f"{hours_string} and {minutes_string}"
    # elif days and minutes:
    #     time_string = f"{days_string} and {minutes_string}"
    # elif days:
    #     time_string = f"{days_string}"
    # elif hours:
    #     time_string = f"{hours_string}"
    # elif minutes:
    #     time_string = f"{minutes_string}"
    # else:
    #     time_string = "unknown time"

    return time_string


# idk why this function is like this or when i wrote it, and i dont wanna know
def get_uwufied_text(src: str):
    """
    Uwufies a text, I guess. Rewritten from a Stackoverflow answer from a different language.
    :param (str) src:
    :return: str
    """
    output_text = ""
    previous_char = ""
    for current_char in src:
        if current_char == 'L' or current_char == 'R':
            output_text += 'W'
        elif current_char == 'l' or current_char == 'r':
            output_text += 'w'
        elif current_char == 'O' and (previous_char == 'N' or previous_char == 'n'):
            output_text += 'YO'
        elif current_char == 'o' and (previous_char == 'N' or previous_char == 'n'):
            output_text += 'yo'
        else:
            output_text += current_char
        previous_char = current_char

    output_text = re.sub("[ ]+", " ", output_text.strip())
    words_list = output_text.split(" ")
    num_of_words = len(words_list)
    uwufy_faces = UWUFY_FACES.copy()
    random.shuffle(uwufy_faces)
    uwu_face_index = 0
    output_text_with_faces = output_text

    for i in range(1, num_of_words, 5):
        if i == 1:
            while uwufy_faces[uwu_face_index % len(uwufy_faces)] in ['uwu', 'UwU']:
                uwu_face_index += 1
        part_to_replace = f"{words_list[i - 1]} {words_list[i]}"
        replacement = f"{words_list[i - 1]} {uwufy_faces[uwu_face_index % len(uwufy_faces)]} {words_list[i]}"
        output_text_with_faces = output_text_with_faces.replace(part_to_replace, replacement, 1)
        uwu_face_index += 1
    if (output_text_with_faces.endswith(words_list[num_of_words - 1])) or num_of_words == 1:
        output_text_with_faces += f" {uwufy_faces[uwu_face_index % len(uwufy_faces)]} "

    return output_text_with_faces


def make_message_send_log_string(message, embed, embed_feedback_message):
    if embed_feedback_message:
        message = str(embed.description)
    elif not embed_feedback_message and not message:
        message = str(embed.title) if embed.title else str(embed.author) \
            if embed.author else str(embed.description) \
            if embed.description else "None"
    return message


def shorten_text_if_above_x_characters(text: str, limit):
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def get_encrypted_string(text: str):
    """
    Encrypts a string in a roundabout way to avoid using special characters for Firebase Database keys
    :param (str) text:
    :return: str
    """
    for symbol in ENCRYPTED_CHARACTERS.keys():
        text = text.replace(symbol, ENCRYPTED_CHARACTERS[symbol])
    return text


def get_decrypted_string(text: str):
    for symbol in ENCRYPTED_CHARACTERS.keys():
        text = text.replace(ENCRYPTED_CHARACTERS[symbol], symbol)
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

    keys_bw = []
    new_dicts_bw = {}
    for key in guild_prefs.banned_words.keys():
        new_key = get_encrypted_string(key)
        new_dicts_bw[new_key] = copy.deepcopy(guild_prefs.banned_words[key])
        keys_bw.append(key)
    for key in keys_bw:
        guild_prefs.banned_words.pop(key)
    for key in new_dicts_bw.keys():
        guild_prefs.banned_words[key] = new_dicts_bw[key]

    return guild_prefs


def stringify_xp_settings_values(xp_settings: dict):
    """
    Stringifies non-strings like discord IDs since they get shortened in integer format on Firebase DB
    :param (dict) xp_settings:
    :return: dict
    """
    xp_settings[XPSettingsKey.LEVELUP_CHANNEL] = str(xp_settings[XPSettingsKey.LEVELUP_CHANNEL])

    str_ignored_channels = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_CHANNELS]]
    xp_settings[XPSettingsKey.IGNORED_CHANNELS] = str_ignored_channels

    str_ignored_roles = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_ROLES]]
    xp_settings[XPSettingsKey.IGNORED_ROLES] = str_ignored_roles

    for key, value in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
        xp_settings[XPSettingsKey.LEVEL_ROLES][key] = str(value)

    return xp_settings


def human_format(num):  # stackoverflow.com/a/45846841
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def build_path(relative_path_params: []):
    if variables.os_type == OSType.WINDOWS:
        relative_path = '\\' + '\\'.join(relative_path_params)
    else:
        relative_path = '/' if variables.main_path != '/' else ''
        relative_path += '/'.join(relative_path_params)
    return variables.main_path + relative_path


# could be written better but i had no time
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
    played_blocks = round(percentage * 20)
    unplayed_blocks = 20 - played_blocks
    return p * played_blocks + u * unplayed_blocks
