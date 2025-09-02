"""
Logtail service for logging
"""
from common.exceptions import ExternalServiceException
from services import ThirdPartyService, StandardResponse


class LogtailService(ThirdPartyService):
    BASE_URL = "https://in.logs.betterstack.com"
    LOG_REQUESTS = False

    def __init__(self, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

    async def log(self, log_records: list) -> StandardResponse:
        url = f"{self.BASE_URL}"
        response = await self._request(method="POST", url=url, json_=log_records)
        self._process_response(response)
        return response

    async def _request(self,
                       method: str,
                       headers: dict | None = None,
                       **kwargs) -> StandardResponse:
        headers = headers or {}
        headers["Authorization"] = f"Bearer {self.token}"
        if method in ["POST", "PUT"]:
            headers["Content-Type"] = "application/json"
        return await super()._request(method=method, headers=headers, **kwargs)

    # noinspection PyMethodMayBeStatic
    def _process_response(self, response: StandardResponse) -> list[dict] | StandardResponse:
        if response.status not in range(200, 300):
            raise ExternalServiceException(
                message=f"Received {response.status} while calling Logtail API.\n",
                debugging_info={
                    "response": response.text,
                    "url": response.url
                },
                status_code=response.status
            )
        return response
