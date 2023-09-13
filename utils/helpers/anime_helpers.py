import traceback

from globals_.constants import BotLogLevel, MAL_ANIME_STATUS_MAPPING, MAL_MANGA_STATUS_MAPPING
from internal.bot_logger import ErrorLogger
from utils.helpers.username_manager import get_mal_username, get_anilist_username
from utils.helpers.string_processing import get_displayable_date
from utils.exceptions import MyAnimeListException, AnilistNotFoundException, AnilistException
from services.third_party.anilist import AnilistService
from services.third_party.myanimelist import MyAnimeListService

error_logger = ErrorLogger("anime_helpers")


async def get_user_stats_for_anime(user_id, anime_id):
    mal_username = get_mal_username(user_id=user_id)
    anilist_username = get_anilist_username(user_id=user_id)

    user_stats = {}
    try:
        if mal_username:
            user_stats['username'] = mal_username
            user_anime_list = await MyAnimeListService().get_anime_list(username=mal_username)
            anime = None
            for user_anime in user_anime_list:
                if user_anime['anime_id'] == anime_id:
                    anime = user_anime
                    break
            if not anime:
                user_stats['status'] = ''
                return user_stats
            user_stats['status'] = MAL_ANIME_STATUS_MAPPING.get(str(anime['status']), "N/A") or "N/A"
            user_stats['score'] = anime['score'] or "N/A"
            user_stats['progress'] = anime['num_watched_episodes'] or 0
            user_stats['start_and_finish_dates'] = (anime['start_date_string'] or "N/A") \
                + " - " + (anime['finish_date_string'] or "N/A")
            user_stats['start_and_finish_dates'] += f" ({anime['days_string'] or 0} days)"
            user_stats['scoring_system'] = "POINT_10_DECIMAL"
        elif anilist_username:
            user_stats['username'] = anilist_username
            anilist_anime_data = await AnilistService().get_anime_by_mal_id(mal_id=anime_id)
            anilist_anime_id = anilist_anime_data.get('data', {}).get('Media', {}).get('id', None)
            if not anilist_anime_id:
                return user_stats
            try:
                user_anime_stats = await AnilistService().get_user_stats_for_anime(anilist_id=anilist_anime_id,
                                                                                   username=anilist_username)
            except AnilistNotFoundException:
                user_stats['status'] = ''
                return user_stats
            anime = user_anime_stats['data']['MediaList']
            user_stats['status'] = anime['status'].capitalize() if anime['status'] else "N/A"
            if user_stats['status'] == "Current":
                user_stats['status'] = "Watching"
            user_stats['score'] = anime['score'] or "N/A"
            user_stats['progress'] = anime['progress'] or 0
            user_stats['scoring_system'] = anime['user']['mediaListOptions']['scoreFormat']
            user_stats['start_and_finish_dates'] = \
                get_displayable_date(anime['startedAt']['year'],
                                     anime['startedAt']['month'],
                                     anime['startedAt']['day']) + " - " + \
                get_displayable_date(anime['completedAt']['year'],
                                     anime['completedAt']['month'],
                                     anime['completedAt']['day'])
            user_stats['rewatch_count'] = anime['repeat']

    except (MyAnimeListException, AnilistException):
        pass
    except Exception as e:
        error_logger.log(message=f"Error while getting user stats for anime\n"
                                 f"Anime ID: {anime_id}\n"
                                 f"Usernames: MAL: {mal_username}, Anilist: {anilist_username}\n"
                                 f"Error: {e}: {traceback.format_exc()}",
                                 level=BotLogLevel.MINOR_WARNING,
                                 log_to_discord=True)
        pass

    return user_stats


async def get_user_stats_for_manga(user_id, manga_id):
    # need to rewrite this mess
    mal_username = get_mal_username(user_id=user_id)
    anilist_username = get_anilist_username(user_id=user_id)

    user_stats = {}
    try:
        if mal_username:
            user_stats['username'] = mal_username
            user_manga_list = await MyAnimeListService().get_manga_list(username=mal_username)
            manga = None
            for user_manga in user_manga_list:
                if user_manga['manga_id'] == manga_id:
                    manga = user_manga
                    break
            if not manga:
                user_stats['status'] = ''
                return user_stats
            user_stats['status'] = MAL_MANGA_STATUS_MAPPING.get(str(manga['status']), "N/A") or "N/A"
            user_stats['score'] = manga['score'] or "N/A"
            user_stats['progress'] = manga['num_read_chapters'] or 0
            user_stats['start_and_finish_dates'] = (manga['start_date_string'] or "N/A") \
                + " - " + (manga['finish_date_string'] or "N/A")
            user_stats['scoring_system'] = "POINT_10_DECIMAL"
        elif anilist_username:
            user_stats['username'] = anilist_username
            anilist_manga_data = await AnilistService().get_manga_by_mal_id(mal_id=manga_id)
            anilist_manga_id = anilist_manga_data.get('data', {}).get('Media', {}).get('id', None)
            if not anilist_manga_id:
                user_stats['status'] = ''
                return user_stats
            try:
                user_manga_stats = await AnilistService().get_user_stats_for_manga(anilist_id=anilist_manga_id,
                                                                                   username=anilist_username)
            except AnilistNotFoundException:
                user_stats['status'] = ''
                return user_stats
            manga = user_manga_stats['data']['MediaList']
            user_stats['status'] = manga['status'].capitalize() if manga['status'] else "N/A"
            if user_stats['status'] == "Current":
                user_stats['status'] = "Reading"
            user_stats['score'] = manga['score'] or "N/A"
            user_stats['progress'] = manga['progress'] or 0
            user_stats['scoring_system'] = manga['user']['mediaListOptions']['scoreFormat']
            user_stats['start_and_finish_dates'] = \
                get_displayable_date(manga['startedAt']['year'],
                                     manga['startedAt']['month'],
                                     manga['startedAt']['day']) + " - " + \
                get_displayable_date(manga['completedAt']['year'],
                                     manga['completedAt']['month'],
                                     manga['completedAt']['day'])
            user_stats['reread_count'] = manga['repeat']

    except (MyAnimeListException, AnilistException):
        pass
    except Exception as e:
        error_logger.log(message=f"Error while getting user stats for manga\n"
                                 f"Manga ID: {manga_id}\n"
                                 f"Usernames: MAL: {mal_username}, Anilist: {anilist_username}"
                                 f"Error: {e}: {traceback.format_exc()}",
                         level=BotLogLevel.MINOR_WARNING,
                         log_to_discord=True)
        pass

    return user_stats
