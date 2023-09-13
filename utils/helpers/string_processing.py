import re

from globals_.constants import MerriamDictionaryResponseType, MusicTrackSource
from urllib.parse import urlparse


def get_id_from_text(text):
    text = re.sub(" +", " ", text).strip()
    expected_ids = re.findall('[0-9]+', text)
    for id_ in expected_ids:
        if len(id_) > 15:
            return int(id_)
    return None


def get_id_from_text_if_exists_otherwise_get_author_id(text, author):
    if not text:
        return author.id, False
    expected_ids = re.findall('[0-9]+', text)
    if not expected_ids:
        return author.id, False
    expected_id = expected_ids[0]
    if len(expected_id) > 15:
        return int(expected_id), True
    return author.id, False


def get_ids_from_text(text):
    text = re.sub(" +", " ", text)
    arguments = text.split(" ")
    ids = []
    for argument in arguments:
        expected_id = re.sub('[^0-9]+', '', argument)
        if len(expected_id) > 15:
            ids.append(int(expected_id))
    return ids


def get_duration_in_minutes_from_text(text: str):
    text = re.sub(" +", " ", text.strip())
    minutes = 0
    duration_matches = re.findall("([0-9]+[wW] ?)?([0-9]+[dD] ?)?([0-9]+[hH] ?)?([0-9]+[mM] ?)?", text)
    if len(duration_matches) > 0:
        duration_tuple = duration_matches[0]
        weeks = 0
        days = 0
        hours = 0
        minutes = 0
        if len(duration_tuple[0]) > 0:
            weeks = int(str(duration_tuple[0]).replace("w", "").replace("W", ""))
        if len(duration_tuple[1]) > 0:
            days = int(str(duration_tuple[1]).replace("d", "").replace("D", ""))
        if len(duration_tuple[2]) > 0:
            hours = int(str(duration_tuple[2]).replace("h", "").replace("H", ""))
        if len(duration_tuple[3]) > 0:
            minutes = int(str(duration_tuple[3]).replace("m", "").replace("M", ""))
        days += (weeks * 7)
        hours += (days * 24)
        minutes += (hours * 60)

    return minutes


def get_auto_response_command_parameters(text: str):
    delete = False
    match_type = "full"
    trigger = None
    response = None

    lowered_text = text.lower()
    options = re.findall("-[a-z]+", lowered_text)
    for option in options:
        option: str = option.replace('-', '')
        if option.startswith('d'):
            delete = True
        elif option.startswith('f'):
            match_type = "full"
        elif option.startswith('s'):
            match_type = "startswith"
        elif option.startswith('p'):
            match_type = "partial"

    trigger_and_response = re.findall("[\"'][^'\"]*[\"']", text)
    if len(trigger_and_response) < 2:
        return trigger, response, delete, match_type
    trigger = trigger_and_response[0].lower().strip()
    response = trigger_and_response[1].strip()

    return trigger[1:len(trigger)-1], response[1:len(response)-1], delete, match_type


def get_merriam_response_type(response_json):
    # what in the fuck
    if not response_json:
        return MerriamDictionaryResponseType.OTHER
    elif len(re.findall("^\\[({.+\\}*,?)+\\]$", str(response_json))) > 0:
        return MerriamDictionaryResponseType.SUCCESS
    elif len(re.findall("^\\[([\'\"].+[\'\"],?)*\\]$", str(response_json))) > 0:
        return MerriamDictionaryResponseType.NOT_FOUND
    else:
        return MerriamDictionaryResponseType.OTHER


def get_presentable_merriam_definition_data(response_json):
    response_type = get_merriam_response_type(response_json)
    data = []

    if response_type == MerriamDictionaryResponseType.SUCCESS:
        for i, definition in enumerate(response_json):
            data_element = {
                "pos": definition.get("fl", "Unknown part of speech"),
                "definitions": definition.get("shortdef", ["No short definition available", ])
            }
            data.append(data_element)
    elif response_type == MerriamDictionaryResponseType.NOT_FOUND:
        data_element = {
            "suggestions": response_json
        }
        data.append(data_element)
    elif response_json:
        data_element = {
            "error": "There was an error. This could be due to reaching our allowed daily quota."
        }
        data.append(data_element)

    return data, response_type


def get_curly_bracketed_parameters_from_text(text: str):
    return re.findall("[{][^{}]+[}]", text)


def process_music_play_arguments(text):
    """
    Returns either url_details if a url is found, or a search term, or an error text.
    :param text: user input
    :return: url_details (dict), search_term (str), error_message (str)
    """
    first_param = text.split(' ')[0]
    if not first_param.startswith("https://"):
        for netloc_sw in ['www.', 'youtube.com', 'youtu.be', 'open.spotify', 'spotify']:
            if first_param.lower().startswith(netloc_sw):
                first_param = 'https://' + first_param
                break
    url_object = urlparse(first_param)
    if url_object.netloc:
        if url_object.netloc.lower() in ['youtu.be', 'www.youtu.be', 'youtube.com', 'www.youtube.com']:
            if url_object.path.lower() not in ['/watch', '/playlist']\
                    and url_object.netloc.lower() not in ['youtu.be', 'www.youtu.be']:
                return None, None, "Invalid link."
            if url_object.netloc.lower() in ['youtu.be', 'www.youtu.be']:
                youtube_id = url_object.path[1:]
                youtube_type = 'video'
            else:
                youtube_id, youtube_type = get_id_and_type_from_url_query(url_object.query)
                if not youtube_id:
                    return None, None, "Invalid link."
            url = f"https://www.youtube.com/{'watch?v=' if youtube_type == 'video' else 'playlist?list='}{youtube_id}"
            url_details = {
                "source": MusicTrackSource.YOUTUBE,
                "url": url,
                'is_playlist': youtube_type == 'playlist'
            }
            return url_details, None, None
        elif url_object.netloc.lower() in ['spotify.com', 'www.spotify.com', 'open.spotify.com']:
            if url_object.path and url_object.path.lower().startswith('/track/') and len(url_object.path) > 7:
                spotify_id = url_object.path[7:].split('/')[0]
                spotify_type = 'track'
            elif url_object.path and url_object.path.lower().startswith('/playlist/') and len(url_object.path) > 10:
                spotify_id = url_object.path[10:].split('/')[0]
                spotify_type = 'playlist'
            elif url_object.path and url_object.path.lower().startswith('/album/') and len(url_object.path) > 7:
                spotify_id = url_object.path[7:].split('/')[0]
                spotify_type = 'album'
            else:
                return None, None, "Invalid Spotify link."
            url = f"https://open.spotify.com/{spotify_type}/{spotify_id}"
            url_details = {
                "source": MusicTrackSource.SPOTIFY,
                "url": url,
                "id": spotify_id,
                'is_playlist': spotify_type in ['playlist', 'album'],
                'is_album': spotify_type == 'album'
            }
            return url_details, None, None
        else:
            return None, None, "Only Youtube and Spotify links are supported for now."
    return None, text, None


def get_id_and_type_from_url_query(query):
    parameters = query.split('/')[0].split('&')
    for parameter in parameters:
        if parameter.lower().startswith('list'):
            return parameter[5:], 'playlist'
        elif parameter.lower().startswith('v'):
            return parameter[2:], 'video'
    return None, None


def get_seconds_for_seek_command(text):
    if not re.fullmatch("(([0-9]?[0-9][:.])?([0-5]?[0-9][:.])?)?[0-5]?[0-9]", text):
        return None
    values = re.split("[.:]", text)
    hours = minutes = 0
    if len(values) == 3:
        hours = int(values[0])
        minutes = int(values[1])
        seconds = int(values[2])
    elif len(values) == 2:
        minutes = int(values[0])
        seconds = int(values[1])
    else:
        seconds = int(values[0])
    return hours * 3600 + minutes * 60 + seconds


def get_displayable_date(year, month, day):
    date = ""
    if year:
        date += str(year)
        if month:
            date += f"-{month}"
            if day:
                date += f"-{day}"
    return date or 'N/A'
