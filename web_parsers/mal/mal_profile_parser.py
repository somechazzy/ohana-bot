from urllib.parse import quote

from internal.web_handler import request
from bs4 import BeautifulSoup
import re
from globals_ import constants
from internal.bot_logging import log


async def get_mal_profile(username):
    username = quote(username, safe='')
    url = f"https://myanimelist.net/profile/{username}"
    response = await request("get", url, constants.CachingType.MAL_PROFILE)
    if response.status != 200:
        return {"status_code": response.status}
    soup = BeautifulSoup(response.content, features="lxml")

    profile_avatar = ""
    try:
        profile_avatar_selection = str(soup.select(".user-image"))
        profile_avatar = re.findall("https[^\"]+", profile_avatar_selection)[0]
    except Exception as e:
        await log(f"Failed at retrieving profile avatar for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    anime_days, anime_avg_score = "?", "?"
    try:
        anime_days_and_avg_score_selection = soup.select(".anime .fw-b")
        anime_days, anime_avg_score = get_days_and_avg_score(anime_days_and_avg_score_selection)  # anime days and score
    except Exception as e:
        await log(f"Failed at retrieving anime days and score for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    manga_days, manga_avg_score = "?", "?"
    try:
        manga_days_and_avg_score_selection = soup.select(".manga .fw-b")
        manga_days, manga_avg_score = get_days_and_avg_score(manga_days_and_avg_score_selection)  # manga days and score
    except Exception as e:
        await log(f"Failed at retrieving manga days and score for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    anime_watching, anime_completed = "?", "?"
    try:
        anime_total_stats_selection = str(soup.select(".anime .stats-status"))
        anime_watching, anime_completed = get_total_stats(anime_total_stats_selection)
    except Exception as e:
        await log(f"Failed at retrieving anime watching and complete count for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    manga_reading, manga_completed = "?", "?"
    try:
        manga_total_stats_selection = str(soup.select(".manga .stats-status"))
        manga_reading, manga_completed = get_total_stats(manga_total_stats_selection)
    except Exception as e:
        await log(f"Failed at retrieving manga reading and complete count for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    anime_entries, anime_rewatched, anime_episodes = "?", "?", "?"
    try:
        anime_stats_selection = str(soup.select(".anime .stats-data"))  # anime entries, rewatched and episodes
        anime_entries, anime_rewatched, anime_episodes = get_general_stats(anime_stats_selection)
    except Exception as e:
        await log(f"Failed at retrieving anime general stats for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    manga_entries, manga_reread, manga_chapters = "?", "?", "?"
    try:
        manga_stats_selection = str(soup.select(".manga .stats-data"))  # manga entries, rewatched and episodes
        manga_entries, manga_reread, manga_chapters = get_general_stats(manga_stats_selection)
    except Exception as e:
        await log(f"Failed at retrieving manga general stats for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)

    last_online, gender, birthday, location, joined = "?", "?", "?", "?", "?"
    try:
        user_info_selection = str(soup.select(".mb4 .clearfix"))  # 5 user-related info
        last_online, gender, birthday, location, joined = get_user_info(user_info_selection)
    except Exception as e:
        await log(f"Failed at retrieving user info for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_discord=False)
    # this should be all there is to the main profile page, make reactions to display favorites, lists

    anime_fav_list = []
    try:
        anime_fav_selection = str(soup.select("#anime_favorites"))
        anime_fav_list = get_fav(anime_fav_selection)
    except Exception as e:
        await log(f"Failed at retrieving anime fav list for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_db=False, log_to_discord=False)

    manga_fav_list = []
    try:
        manga_fav_selection = str(soup.select("#manga_favorites"))
        manga_fav_list = get_fav(manga_fav_selection)
    except Exception as e:
        await log(f"Failed at retrieving manga fav list for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_db=False, log_to_discord=False)

    characters_fav_list = []
    try:
        characters_fav_selection = str(soup.select("#character_favorites"))
        characters_fav_list = get_fav(characters_fav_selection, type_="character")
    except Exception as e:
        await log(f"Failed at retrieving character fav list for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_db=False, log_to_discord=False)

    people_fav_list = []
    try:
        people_fav_selection = str(soup.select("#person_favorites"))
        people_fav_list = get_fav(people_fav_selection, type_="people")
    except Exception as e:
        await log(f"Failed at retrieving people fav list for {username}. Error: {e}",
                  level=constants.BotLogType.BOT_WARNING_IGNORE, log_to_db=False, log_to_discord=False)

    profile_info = {
        "username": username,
        "profile_avatar": profile_avatar,
        "anime_days": anime_days,
        "anime_avg_score": anime_avg_score,
        "manga_days": manga_days,
        "manga_avg_score": manga_avg_score,
        "anime_watching": anime_watching,
        "anime_completed": anime_completed,
        "manga_reading": manga_reading,
        "manga_completed": manga_completed,
        "anime_entries": anime_entries,
        "anime_rewatched": anime_rewatched,
        "anime_episodes": anime_episodes,
        "manga_entries": manga_entries,
        "manga_reread": manga_reread,
        "manga_chapters": manga_chapters,
        "last_online": last_online,
        "gender": gender,
        "birthday": birthday,
        "location": location,
        "joined": joined,
        "anime_fav_list": anime_fav_list,
        "manga_fav_list": manga_fav_list,
        "characters_fav_list": characters_fav_list,
        "people_fav_list": people_fav_list,
        "status_code": 200
    }

    return profile_info


def get_days_and_avg_score(selection):
    days_selection = str(selection[0])
    avg_score_selection = str(selection[1])
    days = re.sub("<[^>]*>", "", days_selection).replace("Days:", "").strip()  # days
    avg_score = re.sub("<[^>]*>", "", avg_score_selection).replace("Mean Score:", "").strip()  # avg score
    return days, avg_score


def get_total_stats(selection):
    total_stats_alloyed = re.split("<[^>]*>", selection)
    total_stats = [s for s in total_stats_alloyed if (s != '' and s != ']' and s != '[')]
    return total_stats[1], total_stats[3]


def get_general_stats(selection):
    stats_alloyed = re.split("<[^>]*>", selection)
    stats = [s for s in stats_alloyed if (s != '' and s != ']' and s != '[')]
    entries = stats[1]  # entries
    redone = stats[3]  # redone
    amount = stats[5]  # amount
    return entries, redone, amount


def get_user_info(selection):
    user_info_alloyed = re.split("<[^>]*>", selection)
    user_info = [s for s in user_info_alloyed if (s != '' and s != ']' and s != '[' and s.strip() != ',')]
    last_online, gender, birthday, location, joined = 'Unavailable', 'Unavailable', 'Unavailable', \
                                                      'Unavailable', 'Unavailable'
    for i in range(0, len(user_info)):
        if user_info[i] == "Last Online":
            last_online = user_info[i + 1]
        elif user_info[i] == "Gender":
            gender = user_info[i + 1]
        elif user_info[i] == "Birthday":
            birthday = user_info[i + 1]
        elif user_info[i] == "Location":
            location = user_info[i + 1]
        elif user_info[i] == "Joined":
            joined = user_info[i + 1]

    return last_online, gender, birthday, location, joined


def get_fav(selection, type_='anime_manga'):
    titles_alloyed = re.split("<[^>]*>", selection)
    titles = ([s for s in titles_alloyed if (s.strip() not in ['', ']', '[', ',', '\n'])])[::2]
    if type_ == 'anime_manga':
        urls = [url for url in re.findall("https[^\"]+", selection) if 'cdn.' not in url]
    else:
        urls = [f"https://myanimelist.net{url}" for url in re.findall(f"/{type_}/[^\"]+", selection)]
    fav_list = []
    for i in range(0, len(titles)):
        fav = {
            "title": titles[i],
            "url": urls[i] if len(urls) > i else f"https://myanimelist.net/search/all?q={quote(titles[i])}"
        }
        fav_list.append(fav)
    return fav_list
