import time
import aiohttp

from globals_.constants import CachingType
from globals_ import variables

"""
This file is a hot mess - but it works. Improve it if you want to!
"""


class WebResponse:

    def __init__(self):
        self.status = 200
        self.json = None
        self.content = ""
        self.text = ""


async def request(method, url: str, type_of_request: CachingType, json=None, headers=None, params=None, data=None,
                  ignore_status_for_caching=False, no_caching=False):
    url_key = url
    if json is not None:
        url_key += str(json)
    elif params is not None:
        url_key += str(params)
    if url_key in variables.cached_pages:
        return variables.cached_pages.get(url_key).get("response")
    else:
        method = method.upper()
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=json, headers=headers, params=params, data=data) as response:
                web_response = WebResponse()
                web_response.status = response.status
                web_response.content = await response.content.read()
                try:
                    web_response.content = web_response.content.decode("utf-8")
                except:
                    pass
                if web_response.status == 200:
                    try:
                        web_response.text = await response.text()
                    except UnicodeDecodeError:
                        from internal.bot_logging import log
                        if type_of_request not in [CachingType.DISCORD_AVATAR, ]:
                            await log(f"'UnicodeDecodeError' while getting response text for {type_of_request}.\n"
                                      f"URL={url}\n"
                                      f"JSON={json}\n"
                                      f"Headers={headers}\n"
                                      f"Params={params}")
                    except:
                        raise
                    if response.content_type == 'application/json':
                        web_response.json = await response.json()
                if (web_response.status in range(200, 299) or ignore_status_for_caching) and not no_caching:
                    page_dict = {
                        "timestamp": int(time.time()),
                        "url": url,
                        "type": type_of_request,
                        "response": web_response
                    }
                    variables.cached_pages[url_key] = page_dict
                return web_response
