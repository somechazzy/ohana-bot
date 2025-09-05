from api.views.base_view import APIViewV1
from utils.helpers.api_helpers import api_response


class HealthcheckView(APIViewV1):
    route = '/healthcheck'
    LOG_REQUEST = False

    async def get(self):
        """
        API service healthcheck.
        """
        return api_response(body={"status": "ok"})

    async def head(self):
        """
        API service healthcheck (HEAD).
        """
        return api_response(body=None, status=200)
