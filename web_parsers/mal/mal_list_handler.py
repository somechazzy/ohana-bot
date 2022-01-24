import json
from internal.web_handler import request
from globals_ import constants
from models.mal_list import MALAnimeListItem, MALMangaListItem


async def request_list(username, anime_or_manga='anime'):
    full_list = []
    offset = 0
    while True:
        response = await request("get", f"https://myanimelist.net/{anime_or_manga}list/"
                                        f"{username}/load.json?status=7&offset={offset}",
                                 constants.CachingType.MAL_LIST_ANIME if anime_or_manga == "anime"
                                 else constants.CachingType.MAL_INFO_MANGA)
        if response.status != 200:
            break
        list_ = json.loads(response.content)
        full_list.extend(list_)
        if len(list_) < 300:
            break
        offset += 300

    return full_list


async def get_anime_list(username):
    return await request_list(username, 'anime')


async def get_manga_list(username):
    return await request_list(username, 'manga')


def mal_anime_list_item_from_dict(s) -> MALAnimeListItem:
    return MALAnimeListItem.from_dict(s)


async def get_mal_anime_list_for_user(username):
    dict_list = await get_anime_list(username)
    return [mal_anime_list_item_from_dict(dict_item) for dict_item in dict_list]


async def get_mal_user_stats_for_anime(username, anime_id):
    dict_list = await get_anime_list(username)
    for anime_dict in dict_list:
        if anime_dict['anime_id'] == anime_id:
            return mal_anime_list_item_from_dict(anime_dict)
    return None


def mal_manga_list_item_from_dict(s) -> MALMangaListItem:
    return MALMangaListItem.from_dict(s)


async def get_mal_manga_list_for_user(username):
    dict_list = await get_manga_list(username)
    return [mal_manga_list_item_from_dict(dict_item) for dict_item in dict_list]


async def get_mal_user_stats_for_manga(username, manga_id):
    dict_list = await get_manga_list(username)
    for manga_dict in dict_list:
        if manga_dict['manga_id'] == manga_id:
            return mal_manga_list_item_from_dict(manga_dict)
    return None
