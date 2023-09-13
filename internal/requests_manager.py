import json
from datetime import datetime
from typing import Union

import aiohttp
from globals_.shared_memory import cached_pages
from globals_.constants import CachingType


class Response:

    def __init__(self):
        self.status: int = -1
        self.json: Union[dict, None] = None
        self.content: Union[str, None] = str()
        self.original_response: aiohttp.ClientResponse = ...
        self.url: str = ...

    def __str__(self):
        return f"Status: {self.status}\n" \
               f"Content: {self.content}\n" \
               f"Json: {self.json}"

    async def instantiate_from_aiohttp_response(self, response, type_of_request, url_key, no_caching=False):
        self.original_response = response
        self.url = response.url
        self.status = response.status
        self.content = await response.content.read()
        try:
            self.content = self.content.decode("utf-8")
        except Exception:
            pass
        if self.status == 200:
            if response.content_type == 'application/json':
                self.json = await response.json()
                if not self.json:
                    try:
                        self.json = json.loads(self.content)
                    except Exception:
                        pass
        if self.status in range(200, 299) and not no_caching:
            page_dict = {
                "timestamp": int(datetime.utcnow().timestamp()),
                "url": self.url,
                "type": type_of_request,
                "response": self
            }
            cached_pages[url_key] = page_dict
        return self


async def request(method, url, type_of_request=CachingType.NO_CACHE,
                  json_=None, headers=None, params=None, data=None) -> Response:
    url_key = url
    if json_ is not None:
        url_key += str(json_)
    elif params is not None:
        url_key += str(params)
    if url_key in cached_pages:
        return cached_pages.get(url_key).get("response")

    method = method.upper()
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=json_, headers=headers, params=params, data=data) as response:
            return await Response().instantiate_from_aiohttp_response(
                response=response,
                type_of_request=type_of_request,
                no_caching=type_of_request == CachingType.NO_CACHE,
                url_key=url_key
            )
