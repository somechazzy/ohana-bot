"""
This module is responsible for creating and running the API service.
Any new views are expected to be added to the `views` list.
"""
from types import coroutine

import aiohttp_cors
from aiohttp import web

from api.views.base_view import BaseAPIView
from api.views.v1.cache_view import InvalidateGuildCacheView
from api.views.v1.emojis_view import EmojisSyncView
from api.views.v1.healthcheck_view import HealthcheckView
from api.views.v1.commands_view import CommandsView, CommandsSyncView
from common.app_logger import AppLogger
from common.db import session_context, get_session, execute_post_commit_actions, execute_post_rollback_actions
from common.exceptions import APIException, APIUnauthorizedException, UserReadableException
from settings import API_SERVICE_PORT, API_AUTH_TOKEN
from constants import AppLogCategory
from utils.helpers.api_helpers import api_response
from utils.helpers.context_helpers import set_context_id, reset_context_id


class APIService:
    _instance: 'APIService' = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.app = web.Application(middlewares=[self.request_middleware])
        self.runner = None
        self.site = None
        self.port = API_SERVICE_PORT
        self.cors = None
        self.logger = AppLogger(self.__class__.__name__)

    async def start(self):
        """
        Starts the API service by setting up the application, registering routes, and starting the web server.
        To be called once on startup.
        Returns:
            None
        """
        self._register_routes()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await self.site.start()
        self.logger.info(f"API service started on port {self.port}", log_to_discord=True)

    def _register_routes(self):
        """
        Registers the API views with the application and sets up CORS for them.
        Returns:
            None
        """
        self.cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        for view in views:
            self._register_view(view, path=rf"/api/{view.API_VERSION.strip('/')}/{view.route.lstrip('/')}")

    def _register_view(self, view_class: type(web.View), path: str):
        """
        Registers a view class with the application and sets up CORS for it.
        Args:
            view_class (type[web.View]): The view class to register.
            path (str): The URL path for the view.

        Returns:
            None
        """
        self.cors.add(self.app.router.add_view(path, view_class))

    @web.middleware
    async def request_middleware(self, request: web.Request, handler: coroutine) -> web.Response:
        """
        Middleware to handle requests, set context ID, log necessary information and catch API exceptions.
        Args:
            request (web.Request): The incoming request object.
            handler (coroutine): The handler function to process the request.

        Returns:
            web.Response: The response object.
        """
        token = set_context_id()
        response_status_code = 500
        error = None
        async with session_context():
            try:
                if handler.AUTH_REQUIRED:
                    if request.headers.get('Authorization') != API_AUTH_TOKEN:
                        raise APIUnauthorizedException("Unauthorized access")
                handler = handler(request)  # noqa
                if request.can_read_body:
                    handler.request_body = await request.json()
                method = getattr(handler, request.method.lower(), None)
                if not method:
                    return api_response(body="Method Not Allowed", status=405)
                response = await method()
                response_status_code = response.status
                return response
            except Exception as e:
                await get_session().rollback()
                await execute_post_rollback_actions()
                if isinstance(e, APIException):
                    return api_response(body=e.response_body(), status=e.status)
                elif isinstance(e, UserReadableException):
                    return api_response(body={"error": e.user_message}, status=400)
                error = e
                return api_response(body="Internal error occurred", status=500)
            finally:
                await get_session().commit()
                await execute_post_commit_actions()
                self.logger.info(f"{request.method} {request.url} -> status {response_status_code}",
                                 category=AppLogCategory.API_REQUEST_RECEIVED,
                                 extras={
                                     "method": request.method,
                                     "url": str(request.url),
                                     "headers": dict(request.headers),
                                     "query_params": dict(request.query),
                                     "body": await request.text() if request.can_read_body else None,
                                     "response": {
                                         "status_code": response_status_code,
                                         "error": str(error) if error else None,
                                     },
                                     "remote": request.remote,
                                 })
                reset_context_id(token)


views = [
    HealthcheckView,
    CommandsView,
    CommandsSyncView,
    EmojisSyncView,
    InvalidateGuildCacheView
]
