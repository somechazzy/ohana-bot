from common.exceptions import ExternalServiceException
from settings import RAPID_API_KEY
from constants import CachingPolicyPresetName
from strings.integrations_strings import GeneralIntegrationStrings
from services import ThirdPartyService, StandardResponse


class UrbanDictionaryService(ThirdPartyService):
    API_BASE_URL = "https://mashape-community-urban-dictionary.p.rapidapi.com"

    class Endpoint:
        DEFINE = "/define?term={term}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_key = RAPID_API_KEY

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
                       headers: dict | None = None,
                       **kwargs) -> StandardResponse:
        headers = headers or {}
        headers |= {
            'x-rapidapi-key': self._api_key,
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
        }
        return await super()._request(method=method, headers=headers, **kwargs)

    async def get_definitions(self, term: str) -> list[dict]:
        url = self.API_BASE_URL + self.Endpoint.DEFINE.format(term=term)
        response = await self._request("GET", url=url, caching_policy=CachingPolicyPresetName.URBAN_DEFINITION)
        return self._process_response(response)['list']
