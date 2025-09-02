"""
Base class for third party services for which this layout applies.
"""
import json
from datetime import timedelta, datetime

import aiohttp
import requests
from requests.structures import CaseInsensitiveDict

import cache
from common.app_logger import AppLogger
from common.http_session import get_async_http_session, get_sync_http_session
from constants import CachingPolicyPresetName, CACHING_POLICY_PRESET


class ThirdPartyService:
    BASE_URL = None
    LOG_REQUESTS = True

    class Endpoint:
        # to be overridden by child classes
        pass

    def __init__(self, *args, **kwargs):
        self.logger = AppLogger(component=self.__class__.__name__)

    def __new__(cls, *args, **kwargs):
        if cls is ThirdPartyService:
            raise TypeError("ThirdPartyService class cannot be instantiated.")
        return super().__new__(cls)

    async def _request(self,
                       method: str,
                       url: str,
                       json_: dict | None = None,
                       headers: dict | None = None,
                       params: dict | None = None,
                       data: dict | None = None,
                       caching_policy: int = CachingPolicyPresetName.NO_CACHE) -> 'StandardResponse':
        if not (standard_response := self._get_cached_response(
            method=method, url=url, json_=json_, headers=headers, params=params, data=data
        )):
            if self.LOG_REQUESTS:
                self.logger.debug(f"Making `{method}` request to `{url}` with "
                                  f"body: {json_}, "
                                  f"headers: {headers}, "
                                  f"params: {params},"
                                  f"and data: {data}.")
            session = await get_async_http_session(name=self.__class__.__name__)
            async with session.request(method=method, url=url, json=json_,
                                       headers=headers, params=params, data=data) as response:
                standard_response = await StandardResponse.from_aiohttp_response(response)
            self._handle_caching(standard_response=standard_response, caching_policy=caching_policy,
                                 data=data, method=method, url=url, json_=json_,
                                 headers=headers, params=params)
        else:
            if self.LOG_REQUESTS:
                self.logger.debug(f"Using cached response for `{method}` request to `{url}` with "
                                  f"body: {json_}, "
                                  f"headers: {headers}, "
                                  f"and params: {params}.")
        return standard_response

    def _sync_request(self,
                      method: str,
                      url: str,
                      json_: dict | None = None,
                      headers: dict | None = None,
                      params: dict | None = None,
                      data: dict | None = None,
                      caching_policy: int = CachingPolicyPresetName.NO_CACHE) -> 'StandardResponse':
        if not (standard_response := self._get_cached_response(
            method=method, url=url, json_=json_, headers=headers, params=params, data=data
        )):
            if self.LOG_REQUESTS:
                self.logger.debug(f"Making `{method}` request to `{url}` with "
                                  f"body: {json_}, "
                                  f"headers: {headers}, "
                                  f"params: {params},"
                                  f"and data: {data}.")
            session = get_sync_http_session(name=self.__class__.__name__)
            with session.request(method=method, url=url, json=json_,
                                 headers=headers, params=params, data=data) as response:
                standard_response = StandardResponse.from_requests_response(response)
            self._handle_caching(standard_response=standard_response, caching_policy=caching_policy,
                                 data=data, method=method, url=url, json_=json_, headers=headers, params=params)
        else:
            if self.LOG_REQUESTS:
                self.logger.debug(f"Using cached response for `{method}` request to `{url}` with "
                                  f"body: {json_}, "
                                  f"headers: {headers}, "
                                  f"and params: {params}.")
        return standard_response

    # noinspection PyMethodMayBeStatic
    def _get_cached_response(self,
                             method: str,
                             url: str,
                             json_: dict | None = None,
                             headers: dict | None = None,
                             params: dict | None = None,
                             data: dict | None = None) -> 'StandardResponse | None':
        cache_key = f"{method}|{url}|{json_}|{headers}|{params}|{data}"
        cached_response = cache.CACHED_WEB_RESPONSES.get(cache_key)
        if cached_response and cached_response.cache_expiry < datetime.now():
            return None
        return cached_response

    # noinspection PyMethodMayBeStatic
    def _handle_caching(self,
                        standard_response: 'StandardResponse',
                        caching_policy: int,
                        data: dict | None,
                        method: str,
                        url: str,
                        json_: dict | None,
                        headers: dict | None,
                        params: dict | None) -> None:
        if caching_policy == CachingPolicyPresetName.NO_CACHE or standard_response.status_code >= 400:
            return
        cache_key = f"{method}|{url}|{json_}|{headers}|{params}|{data}"
        standard_response.cache_expiry = datetime.now() + timedelta(seconds=CACHING_POLICY_PRESET[caching_policy])
        cache.CACHED_WEB_RESPONSES[cache_key] = standard_response


class StandardResponse:
    def __init__(self,
                 original_response: aiohttp.ClientResponse | requests.Response,
                 status: int,
                 url: str,
                 json_: dict | None = None,
                 text: str | None = None,
                 headers: CaseInsensitiveDict | None = None):
        self.original_response: aiohttp.ClientResponse | requests.Response = original_response
        self.status: int = status
        self.status_code: int = status  # alias
        self.url: str = url
        self.json: dict | None = json_
        self.text: str | None = text
        self.content: str | None = text  # alias?
        self.headers: CaseInsensitiveDict = headers
        self.cache_expiry: datetime | None = ...  # to be set when caching is applied

    @staticmethod
    async def from_aiohttp_response(response: aiohttp.ClientResponse) -> 'StandardResponse':
        try:
            text = await response.text()
        except Exception:
            text = None
        try:
            json_ = await response.json()
        except Exception:
            try:
                json_ = json.loads(text)
            except Exception:
                json_ = None
        return StandardResponse(original_response=response, status=response.status, url=str(response.url),
                                json_=json_, text=text, headers=response.headers)

    @staticmethod
    def from_requests_response(response: requests.Response) -> 'StandardResponse':
        try:
            json_ = response.json()
        except Exception:
            json_ = None
        return StandardResponse(original_response=response, status=response.status_code, url=response.url,
                                json_=json_, text=response.text, headers=response.headers)
