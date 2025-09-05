"""
_APIView class is a base class for all API views.
Versioned API views should inherit from it. Any new API view should inherit from a versioned API view.
"""
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_cors import CorsViewMixin

from utils.helpers.api_helpers import api_response


class BaseAPIView(CorsViewMixin, web.View):
    API_VERSION = None
    route = None
    AUTH_REQUIRED = False
    LOG_REQUEST = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_body: dict = {}

    def __new__(cls, *args, **kwargs):
        if cls is BaseAPIView:
            raise TypeError("_APIView class cannot be instantiated.")
        return super().__new__(cls)

    async def head(self, *args, **kwargs):
        pass

    async def get(self, *args, **kwargs):
        pass

    async def post(self, *args, **kwargs):
        pass

    async def put(self, *args, **kwargs):
        pass

    async def patch(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass

    @property
    def request(self) -> Request:  # overridden to fix type hinting
        return self._request


class APIViewV1(BaseAPIView):
    API_VERSION = 'v1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is APIViewV1:
            raise TypeError("APIViewV1 class cannot be instantiated.")
        return super().__new__(cls)

    async def head(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)

    async def get(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)

    async def post(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)

    async def put(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)

    async def patch(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)

    async def delete(self, *args, **kwargs):
        return api_response({"message": "Method not allowed"}, status=405)
