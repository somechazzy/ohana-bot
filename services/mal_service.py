import urllib.parse
from typing import Any

from settings import MYANIMELIST_CLIENT_ID
from constants import CachingPolicyPresetName
from common.exceptions import ExternalServiceException
from strings.integrations_strings import MALStrings
from services import ThirdPartyService, StandardResponse


class MyAnimeListService(ThirdPartyService):
    API_BASE_URL = "https://api.myanimelist.net/v2"
    WEBSITE_BASE_URL = "https://myanimelist.net"

    class Endpoint:
        ANIME_INFO = "/anime/{id}?fields=id,title,main_picture,alternative_titles," \
                      "start_date,end_date,synopsis,mean,rank,average_episode_duration," \
                      "num_scoring_users,genres,media_type,status,num_episodes," \
                      "start_season,source,studios,num_list_users"
        MANGA_INFO = "/manga/{id}?fields=id,title,main_picture,alternative_titles,mean,rank," \
                     "start_date,end_date,synopsis,num_scoring_users,genres,num_chapters," \
                     "num_volumes,media_type,status,authors{{first_name,last_name}},num_list_users"

        ANIME_SEARCH = "/search/prefix.json?type=anime&keyword={query}&v=1"
        MANGA_SEARCH = "/search/prefix.json?type=manga&keyword={query}&v=1"

        ANIME_LIST = "/animelist/{username}/load.json?status=7&offset={offset}"
        MANGA_LIST = "/mangalist/{username}/load.json?status=7&offset={offset}"

        PROFILE_WEBPAGE = "/profile/{username}"

    def __init__(self):
        super().__init__()
        self._client_id = MYANIMELIST_CLIENT_ID

    # noinspection PyMethodMayBeStatic
    def _process_response(self, response: StandardResponse, return_attr: str = 'json', raise_for_404: bool = True,
                          raise_for_400: bool = True, default: Any = None):
        if response.status == 400:
            if raise_for_400:
                raise ExternalServiceException("Bad request",
                                               status_code=response.status,
                                               debugging_info={
                                                   "url": response.url,
                                                   "content": response.content,
                                                   "headers": response.headers
                                               },
                                               user_message=MALStrings.CONNECTION_ERROR_MESSAGE,
                                               alert_worthy=True)
            else:
                return default
        if response.status == 404:
            if raise_for_404:
                raise ExternalServiceException("Not found",
                                               status_code=response.status,
                                               debugging_info={
                                                   "url": response.url,
                                                   "status": response.status,
                                                   "content": response.content,
                                                   "headers": response.headers
                                               },
                                               user_message=MALStrings.NOT_FOUND_MESSAGE)
            else:
                return default
        elif response.status >= 500:
            raise ExternalServiceException("MAL is down",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "status": response.status,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=MALStrings.SERVICE_DOWN_MESSAGE)
        elif response.status != 200:
            raise ExternalServiceException("Non-200 unhandled status code",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "status": response.status,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=MALStrings.CONNECTION_ERROR_MESSAGE,
                                           alert_worthy=True)

        return getattr(response, return_attr)

    async def _request(self,
                       method: str,
                       headers: dict | None = None,
                       add_client_id: bool = True,
                       **kwargs) -> StandardResponse:
        if add_client_id:
            headers = headers or {}
            headers["X-MAL-CLIENT-ID"] = self._client_id
        if method in ["POST", "PUT"]:
            headers["Content-Type"] = "application/json"
        return await super()._request(method=method, headers=headers, **kwargs)

    async def get_anime_info(self, anime_id: int) -> dict:
        url = self.API_BASE_URL + self.Endpoint.ANIME_INFO.format(id=anime_id)
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MAL_INFO)
        return self._process_response(response)

    async def get_manga_info(self, manga_id: int) -> dict:
        url = self.API_BASE_URL + self.Endpoint.MANGA_INFO.format(id=manga_id)
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MAL_INFO)
        return self._process_response(response)

    async def get_anime_search_results(self, query: str) -> list:
        url = (self.WEBSITE_BASE_URL +
               self.Endpoint.ANIME_SEARCH.format(query=urllib.parse.quote(query.replace('/', ' '))))
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MAL_SEARCH)
        return self._process_response(response)['categories'][0]['items']

    async def get_manga_search_results(self, query: str) -> list:
        url = (self.WEBSITE_BASE_URL +
               self.Endpoint.MANGA_SEARCH.format(query=urllib.parse.quote(query.replace('/', ' '))))
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MAL_SEARCH)
        return self._process_response(response)['categories'][0]['items']

    async def get_anime_list(self, username: str, offset: int = 0) -> list[dict]:
        url = (self.WEBSITE_BASE_URL +
               self.Endpoint.ANIME_LIST.format(username=urllib.parse.quote(username.replace('/', ' ')),
                                               offset=offset))
        response = await self._request("GET", url=url,
                                       caching_policy=CachingPolicyPresetName.MAL_LIST,
                                       add_client_id=False)
        return self._process_response(response, raise_for_404=False, raise_for_400=False, default=[])

    async def get_manga_list(self, username: str, offset: int = 0) -> list[dict]:
        url = (self.WEBSITE_BASE_URL +
               self.Endpoint.MANGA_LIST.format(username=urllib.parse.quote(username.replace('/', ' ')),
                                               offset=offset))
        response = await self._request("GET", url=url,
                                       caching_policy=CachingPolicyPresetName.MAL_LIST,
                                       add_client_id=False)
        return self._process_response(response, raise_for_404=False, raise_for_400=False, default=[])

    async def get_profile_webpage(self, username: str) -> str:
        url = self.WEBSITE_BASE_URL + self.Endpoint.PROFILE_WEBPAGE.format(username=username)
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MAL_PROFILE)
        return self._process_response(response, return_attr='content')
