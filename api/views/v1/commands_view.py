from api.views.base_view import APIViewV1
from bot.utils.helpers.client_helpers import sync_commands_on_discord
from common.exceptions import APIBadRequestException
from utils.helpers.api_helpers import api_response
from components.commands_component import CommandsComponent
from constants import CommandQueryType


class CommandsView(APIViewV1):
    route = '/commands'

    async def get(self):
        """
        Get a list of all available commands and their details.
        Parameters:
            - category (optional): Category of commands to filter by. One of 'ALL', 'USER' or 'ADMIN'. Default is 'ALL'.
        """
        category = CommandQueryType.ALL
        if self.request.query and 'category' in self.request.query:
            category = (self.request.query.get('category', '') or '').upper()
            if category not in CommandQueryType.as_list():
                raise APIBadRequestException(message=f'Invalid category. Must be one of {CommandQueryType.as_list()}')

        return api_response({'commands': CommandsComponent().get_commands_info(category)})


class CommandsSyncView(APIViewV1):
    route = '/commands/sync'
    AUTH_REQUIRED = True

    async def post(self):
        """
        Sync commands with Discord.
        Parameters:
            - guild_id (optional): Guild ID to sync commands to. If not provided, commands will be synced globally.
        """
        await sync_commands_on_discord(guild_id=self.request_body.get('guild_id', None))
        return api_response({'message': 'Commands synced successfully'})
