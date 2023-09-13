import urllib.parse

from auth import auth
from globals_.constants import CachingType
from internal.bot_logger import ErrorLogger
from internal.requests_manager import request


class MerriamDictionaryService:
    DEFINE_URL = "https://dictionaryapi.com/api/v3/references/collegiate/json/{term}?key={auth_key}"

    def __init__(self):
        self.auth_key = auth.MERRIAM_API_KEY
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def _handle_response(self, response):
        if response.status != 200:
            self.error_logger.log(f"Received {response.status} while requesting {response.url}\n "
                                  f"Response: {response.content}")
            raise Exception

        return response.json

    async def get_definitions(self, term):
        if not auth.RAPID_API_KEY:
            raise NotImplementedError("Merriam Dictionary API key not set.")
        url = self.DEFINE_URL.format(term=urllib.parse.quote(term.replace("/", " ")), auth_key=self.auth_key)
        response = await request(method="get", url=url, type_of_request=CachingType.MERRIAM_DICTIONARY)
        return await self._handle_response(response)
