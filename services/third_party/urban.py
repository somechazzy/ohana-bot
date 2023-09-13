import urllib.parse

from auth import auth
from globals_.constants import CachingType
from internal.requests_manager import request
from services.third_party.base import ThirdPartyService


class UrbanDictionaryService(ThirdPartyService):
    DEFINE_URL = "https://mashape-community-urban-dictionary.p.rapidapi.com/define?term={term}"

    def __init__(self):
        super().__init__()
        self._headers = {
            'x-rapidapi-key': auth.RAPID_API_KEY,
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
        }

    async def _handle_response(self, response):
        if response.status != 200:
            self.error_logger.log(f"Received {response.status} while requesting {response.url}\n "
                                  f"Response: {response.content}")
            raise Exception

        return response.json

    async def get_definitions(self, term):
        if not auth.RAPID_API_KEY:
            raise NotImplementedError("Urban Dictionary API key not set.")
        url = self.DEFINE_URL.format(term=urllib.parse.quote(term.replace("/", " ")))
        response = await request(method="get", url=url, type_of_request=CachingType.URBAN_DICTIONARY,
                                 headers=self._headers)
        return (await self._handle_response(response))['list']
