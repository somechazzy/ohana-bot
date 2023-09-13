import traceback

from globals_.constants import BotLogLevel
from utils.exceptions import MyAnimeListParseException, AnilistParseException
from models.anilist_list import AnilistList
from models.anilist_profile import AnilistProfile
from models.mal_list import MALAnimeListItem, MALMangaListItem
from services.third_party.anilist import AnilistService
from services.third_party.myanimelist import MyAnimeListService
from slashes.base_slashes import BaseSlashes
from utils.web_parsers.mal_profile_parser import parse_mal_profile


class UserSlashes(BaseSlashes):

    def __init__(self, interaction):
        super().__init__(interaction=interaction)
        self.mal_service = MyAnimeListService()
        self.anilist_service = AnilistService()
        self.loading_emoji = '⌛'

    async def preprocess_and_validate(self, **kwargs):
        if not await super().preprocess_and_validate(**kwargs):
            return False
        return True

    async def get_mal_profile_info(self, username):
        profile_content = await self.mal_service.get_profile_webpage(username=username)

        try:
            profile_info = parse_mal_profile(username=username, profile_content=profile_content)
        except Exception as e:
            self.error_logger.log(f"Failed at parsing MAL profile for {username}. "
                                  f"Error: {e}\ntraceback: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR, log_to_discord=True)
            raise MyAnimeListParseException(e)

        if profile_info['parsings_warnings']:
            self.error_logger.log(f"Parsing warnings for {username}'s MAL profile: {profile_info['parsings_warnings']}",
                                  level=BotLogLevel.WARNING, log_to_discord=True)

        return profile_info

    async def get_mal_lists(self, username):
        anime_dict_list = await self.mal_service.get_anime_list(username=username)
        manga_dict_list = await self.mal_service.get_manga_list(username=username)

        try:
            anime_list = [MALAnimeListItem.from_dict(dict_item) for dict_item in anime_dict_list]
            manga_list = [MALMangaListItem.from_dict(dict_item) for dict_item in manga_dict_list]
        except Exception as e:
            self.error_logger.log(f"Failed at parsing MAL lists for {username}. "
                                  f"Error: {e}\ntraceback: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR, log_to_discord=True)
            raise MyAnimeListParseException(e)

        return anime_list, manga_list

    async def get_anilist_profile_info(self, username):
        profile_json = await self.anilist_service.get_profile(username=username)

        try:
            anilist_profile = AnilistProfile(profile_json)
        except Exception as e:
            self.error_logger.log(f"Failed at parsing Anilist profile for {username}. "
                                  f"Error: {e}\ntraceback: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR, log_to_discord=True)
            raise AnilistParseException(e)

        return anilist_profile

    async def get_anilist_lists(self, username):
        anime_list_raw = await self.anilist_service.get_anime_list(username=username)
        manga_list_raw = await self.anilist_service.get_manga_list(username=username)

        try:
            anime_list_container = AnilistList.from_dict(anime_list_raw)
            manga_list_container = AnilistList.from_dict(manga_list_raw)
            anime_score_format = anime_list_container.data.media_list_collection.user.media_list_options.score_format
            manga_scoring_system = manga_list_container.data.media_list_collection.user.media_list_options.score_format
            anime_list = self._order_and_combine_anilist_list(anime_list_container)
            manga_list = self._order_and_combine_anilist_list(manga_list_container)
        except Exception as e:
            self.error_logger.log(f"Failed at parsing Anilist lists for {username}. "
                                  f"Error: {e}\ntraceback: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR, log_to_discord=True)
            raise AnilistParseException(e)

        return anime_list, manga_list, anime_score_format, manga_scoring_system

    @staticmethod
    def _order_and_combine_anilist_list(list_object):
        if not list_object:
            return []
        lists = list_object.data.media_list_collection.lists
        planning_list = []
        current_list = []
        completed_list = []
        dropped_list = []
        paused_list = []
        repeating_list = []
        else_list = []
        for list_ in lists:
            if isinstance(list_.entries[0].status, type(None)):
                else_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "PLANNING":
                planning_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "CURRENT":
                current_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "COMPLETED":
                completed_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "DROPPED":
                dropped_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "PAUSED":
                paused_list.extend(list_.entries)
            elif str(list_.entries[0].status.name) == "REPEATING":
                repeating_list.extend(list_.entries)
            else:
                else_list.extend(list_.entries)

        master_list = []
        for list_ in [current_list, repeating_list, completed_list, planning_list, paused_list, dropped_list,
                      else_list]:
            master_list.extend(list_)
        return master_list

    async def get_anime_by_name(self, anime_query):
        search_result_raw = await self.mal_service.get_anime_search_results(query=anime_query)
        entries = []
        for result in search_result_raw:
            title = result['name']
            url = result['url']
            anime_type = result['payload']['media_type']
            eps = result['payload']['aired']
            score = result['payload']['score']
            anime_id = result['id']
            entry = {
                "title": title,
                "url": url,
                "type": anime_type,
                "eps": eps,
                "score": score,
                "id": anime_id
            }
            entries.append(entry)
        search_result = {
            "thumbnail": search_result_raw[0]['image_url'],
            "entries": entries
        }

        first_anime_info = await self.mal_service.get_anime_info(anime_id=entries[0]['id'])

        return first_anime_info, search_result

    async def get_manga_by_name(self, manga_query):
        search_result_raw = await self.mal_service.get_manga_search_results(query=manga_query)
        entries = []
        for result in search_result_raw:
            title = result['name']
            url = result['url']
            manga_type = result['payload']['media_type']
            volumes = result['payload']['published'].replace(" ??", "")
            score = result['payload']['score']
            manga_id = result['id']
            entry = {
                "title": title,
                "url": url,
                "type": manga_type,
                "volumes": volumes,
                "score": score,
                "id": manga_id
            }
            entries.append(entry)
        search_result = {
            "thumbnail": search_result_raw[0]['image_url'],
            "entries": entries
        }

        first_anime_info = await self.mal_service.get_manga_info(manga_id=entries[0]['id'])

        return first_anime_info, search_result
