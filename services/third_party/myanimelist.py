import urllib.parse
from auth import auth
from globals_.constants import CachingType, BotLogLevel
from services.third_party.base import ThirdPartyService
from utils.exceptions import MyAnimeListNotFoundException, MyAnimeListInternalErrorException, MyAnimeListException
from internal.requests_manager import request


class MyAnimeListService(ThirdPartyService):
    ANIME_INFO_URL = "https://api.myanimelist.net/v2/anime/{id}" + "?fields=id,title,main_picture,alternative_titles," \
                                                                   "start_date,end_date,synopsis,mean,rank," \
                                                                   "num_scoring_users,genres,media_type,status," \
                                                                   "num_episodes,start_season,source,studios"
    MANGA_INFO_URL = "https://api.myanimelist.net/v2/manga/{id}" + "?fields=id,title,main_picture,alternative_titles," \
                                                                   "start_date,end_date,synopsis,mean,rank," \
                                                                   "num_scoring_users,genres,media_type,status," \
                                                                   "num_chapters,authors{{first_name,last_name}}"

    ANIME_SEARCH_URL = "https://myanimelist.net/search/prefix.json?type=anime&keyword={query}&v=1"
    MANGA_SEARCH_URL = "https://myanimelist.net/search/prefix.json?type=manga&keyword={query}&v=1"

    ANIME_LIST_URL = "https://myanimelist.net/animelist/{username}/load.json?status=7&offset={offset}"
    MANGA_LIST_URL = "https://myanimelist.net/mangalist/{username}/load.json?status=7&offset={offset}"

    PROFILE_WEBPAGE_URL = "https://myanimelist.net/profile/{username}"

    def __init__(self):
        super().__init__()
        self._client_id = auth.MYANIMELIST_CLIENT_ID
        self._headers = {
            "X-MAL-CLIENT-ID": self._client_id,
        }

    async def _handle_response(self, response, return_attr='json', raise_for_400=True):
        if response.status == 400:
            if raise_for_400:
                raise MyAnimeListException("Bad request")
            else:
                return None
        if response.status == 404:
            raise MyAnimeListNotFoundException("Not found")
        elif response.status >= 500:
            raise MyAnimeListInternalErrorException("MyAnimeList is down")
        elif response.status != 200:
            self.error_logger.log(f"Received {response.status} while requesting {response.url}\n "
                                  f"Response: {response.content}",
                                  level=BotLogLevel.ERROR)
            raise MyAnimeListException("Something went wrong")

        return getattr(response, return_attr)

    async def get_anime_info(self, anime_id):
        url = self.ANIME_INFO_URL.format(id=anime_id)
        response = await request(method="get", url=url, type_of_request=CachingType.MAL_INFO_ANIME,
                                 headers=self._headers)
        return await self._handle_response(response)

    async def get_manga_info(self, manga_id):
        url = self.MANGA_INFO_URL.format(id=manga_id)
        response = await request(method="get", url=url, type_of_request=CachingType.MAL_INFO_MANGA,
                                 headers=self._headers)
        return await self._handle_response(response)

    async def get_anime_search_results(self, query):
        url = self.ANIME_SEARCH_URL.format(query=urllib.parse.quote(query.replace('/', ' ')))
        response = await request(method="get", url=url, type_of_request=CachingType.MAL_SEARCH_ANIME)
        results = await self._handle_response(response)
        return results['categories'][0]['items']

    async def get_manga_search_results(self, query):
        url = self.MANGA_SEARCH_URL.format(query=urllib.parse.quote(query.replace('/', ' ')))
        response = await request(method="get", url=url, type_of_request=CachingType.MAL_SEARCH_MANGA)
        results = await self._handle_response(response)
        return results['categories'][0]['items']

    async def get_anime_list(self, username):
        anime_list = []
        offset = 0
        while True:
            url = self.ANIME_LIST_URL.format(username=urllib.parse.quote(username.replace('/', ' ')),
                                             offset=offset)
            response = await request(method="get", url=url, type_of_request=CachingType.MAL_LIST_ANIME)
            results = await self._handle_response(response, raise_for_400=False)
            if response.status != 200 or not results:
                break
            anime_list.extend(results)
            if len(results) < 300:
                break
            offset += 300
        return anime_list

    async def get_manga_list(self, username):
        manga_list = []
        offset = 0
        while True:
            url = self.MANGA_LIST_URL.format(username=urllib.parse.quote(username.replace('/', ' ')),
                                             offset=offset)
            response = await request(method="get", url=url, type_of_request=CachingType.MAL_LIST_MANGA)
            results = await self._handle_response(response, raise_for_400=False)
            if response.status != 200 or not results:
                break
            manga_list.extend(results)
            if len(results) < 300:
                break
            offset += 300
        return manga_list

    async def get_profile_webpage(self, username):
        url = self.PROFILE_WEBPAGE_URL.format(username=username)
        response = await request(method="get", url=url, type_of_request=CachingType.MAL_PROFILE)
        return await self._handle_response(response, return_attr='content')
