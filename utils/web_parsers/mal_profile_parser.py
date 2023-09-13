import urllib.parse

from bs4 import BeautifulSoup
import re


def parse_mal_profile(username, profile_content):
    soup = BeautifulSoup(profile_content, features="lxml")

    warnings = []

    profile_avatar = ""
    try:
        profile_avatar_selection = soup.select(".user-image")
        if profile_avatar_selection:
            profile_avatar = profile_avatar_selection[0].contents[1].attrs['data-src']
    except Exception as e:
        warnings.append(f"Failed at retrieving profile avatar for {username}. Error: {e}")

    profile_banner = ""
    try:
        profile_banner_selection = soup.select(".l-mainvisual img")
        if profile_banner_selection:
            profile_banner = profile_banner_selection[0].attrs['src']
    except Exception as e:
        warnings.append(f"Failed at retrieving profile banner for {username}. Error: {e}")

    anime_days, anime_avg_score = "?", "?"
    try:
        anime_days_and_avg_score_selection = soup.select(".anime .fw-b")
        anime_days, anime_avg_score = get_days_and_avg_score(anime_days_and_avg_score_selection)  # anime days and score
    except Exception as e:
        warnings.append(f"Failed at retrieving anime days and score for {username}. Error: {e}")

    manga_days, manga_avg_score = "?", "?"
    try:
        manga_days_and_avg_score_selection = soup.select(".manga .fw-b")
        manga_days, manga_avg_score = get_days_and_avg_score(manga_days_and_avg_score_selection)  # manga days and score
    except Exception as e:
        warnings.append(f"Failed at retrieving manga days and score for {username}. Error: {e}")

    anime_watching, anime_completed = "?", "?"
    try:
        anime_total_stats_selection = soup.select(".anime .stats-status")
        anime_watching, anime_completed = get_total_stats(anime_total_stats_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving anime watching and complete count for {username}. Error: {e}")
    manga_reading, manga_completed = "?", "?"
    try:
        manga_total_stats_selection = soup.select(".manga .stats-status")
        manga_reading, manga_completed = get_total_stats(manga_total_stats_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving manga reading and complete count for {username}. Error: {e}")

    anime_entries, anime_rewatched, anime_episodes = "?", "?", "?"
    try:
        anime_stats_selection = soup.select(".anime .stats-data")  # anime entries, rewatched and episodes
        anime_entries, anime_rewatched, anime_episodes = get_general_stats(anime_stats_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving anime general stats for {username}. Error: {e}")

    manga_entries, manga_reread, manga_chapters = "?", "?", "?"
    try:
        manga_stats_selection = soup.select(".manga .stats-data")  # manga entries, rewatched and episodes
        manga_entries, manga_reread, manga_chapters = get_general_stats(manga_stats_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving manga general stats for {username}. Error: {e}")

    user_info = {}
    try:
        user_info_selection = soup.select(".mb4 .clearfix")  # 5 user-related info
        user_info = get_user_info(user_info_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving user info for {username}. Error: {e}")
    # this should be all there is to the main profile page, make reactions to display favorites, lists

    anime_fav_list = []
    try:
        anime_fav_selection = str(soup.select("#anime_favorites"))
        anime_fav_list = get_fav(anime_fav_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving anime fav list for {username}. Error: {e}")

    manga_fav_list = []
    try:
        manga_fav_selection = str(soup.select("#manga_favorites"))
        manga_fav_list = get_fav(manga_fav_selection)
    except Exception as e:
        warnings.append(f"Failed at retrieving manga fav list for {username}. Error: {e}")

    characters_fav_list = []
    try:
        characters_fav_selection = str(soup.select("#character_favorites"))
        characters_fav_list = get_fav(characters_fav_selection, type_="character")
    except Exception as e:
        warnings.append(f"Failed at retrieving character fav list for {username}. Error: {e}")

    people_fav_list = []
    try:
        people_fav_selection = str(soup.select("#person_favorites"))
        people_fav_list = get_fav(people_fav_selection, type_="people")
    except Exception as e:
        warnings.append(f"Failed at retrieving people fav list for {username}. Error: {e}")

    company_fav_list = []
    try:
        company_fav_selection = str(soup.select("#company_favorites"))
        company_fav_list = get_fav(company_fav_selection, type_="anime/producer")
    except Exception as e:
        warnings.append(f"Failed at retrieving company fav list for {username}. Error: {e}")

    profile_info = {
        "username": username,
        "profile_avatar": profile_avatar,
        "profile_banner": profile_banner,
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
        "anime_fav_list": anime_fav_list,
        "manga_fav_list": manga_fav_list,
        "characters_fav_list": characters_fav_list,
        "people_fav_list": people_fav_list,
        "company_fav_list": company_fav_list,
        "user_info": user_info,
        "parsings_warnings": warnings,
        "status_code": 200
    }

    return profile_info


def get_days_and_avg_score(selection):
    days = selection[0].contents[1]  # days
    avg_score = selection[1].contents[3].contents[0]  # avg score
    return days, avg_score


def get_total_stats(selection):
    return selection[0].contents[0].contents[1].contents[0], selection[0].contents[1].contents[1].contents[0]


def get_general_stats(selection):
    # entries
    # reconsumed
    # amount
    return selection[0].contents[0].contents[1].contents[0], \
        selection[0].contents[1].contents[1].contents[0], \
        selection[0].contents[2].contents[1].contents[0]


def get_user_info(selection):
    user_info = {}
    for subselection in selection:
        user_info[subselection.contents[0].contents[0]] = subselection.contents[1].contents[0]
    return user_info


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
            "url": urls[i] if len(urls) > i else f"https://myanimelist.net/search/all?q={urllib.parse.quote(titles[i])}"
        }
        fav_list.append(fav)
    return fav_list
