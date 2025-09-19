import re

from common.exceptions import ExternalServiceException
from settings import MERRIAM_API_KEY
from constants import CachingPolicyPresetName
from strings.integrations_strings import GeneralIntegrationStrings
from services import ThirdPartyService, StandardResponse


class MerriamWebsterService(ThirdPartyService):
    API_BASE_URL = "https://dictionaryapi.com/api/v3"

    class Endpoint:
        DEFINE = "/references/collegiate/json/{term}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_key = MERRIAM_API_KEY

    # noinspection PyMethodMayBeStatic
    def _process_response(self, response: StandardResponse) -> dict | list[dict]:
        if response.status != 200:
            raise ExternalServiceException("Non-200 unhandled status code",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "status": response.status,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=GeneralIntegrationStrings.CONNECTION_ERROR_MESSAGE,
                                           alert_worthy=True)

        return response.json

    async def _request(self,
                       method: str,
                       params: dict | None = None,
                       **kwargs) -> StandardResponse:
        params = params or {}
        params |= {
            "key": self._api_key,
        }
        return await super()._request(method=method, params=params, **kwargs)

    async def get_definitions(self, term: str) -> list[dict | str]:
        url = self.API_BASE_URL + self.Endpoint.DEFINE.format(term=re.sub(r"[^a-zA-Z0-9\s]", "", term).strip().lower())
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.MERRIAM_DEFINITION)
        return self._process_response(response)
