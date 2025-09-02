from common.exceptions import ExternalServiceException
from constants import CachingPolicyPresetName
from strings.integrations_strings import GeneralIntegrationStrings
from services import ThirdPartyService, StandardResponse


class RadioStreamStatusService(ThirdPartyService):

    def __init__(self, api_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_url = api_url

    # noinspection PyMethodMayBeStatic
    def _process_response(self, response: StandardResponse) -> dict | list[dict] | str:
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

        return response.json or response.text

    async def get_stream_status_data(self, method: str, data: dict | None) -> dict | list | str:
        response = await self._request(method=method,
                                       url=self._api_url,
                                       data=data,
                                       caching_policy=CachingPolicyPresetName.NO_CACHE)
        return self._process_response(response)
