import cache
from api.views.base_view import APIViewV1
from utils.helpers.api_helpers import api_response


class InvalidateGuildCacheView(APIViewV1):
    AUTH_REQUIRED = True
    route = '/invalidate_guild_cache'

    async def post(self):
        """
        Invalidate the guild settings and XP caches.
        Parameters:
            - guild_id (optional): The ID of the guild to invalidate. If not provided, all guilds will be invalidated.
        """
        guild_id = self.request_body.get('guild_id')
        if guild_id:
            cache.CACHED_GUILD_SETTINGS.pop(guild_id, None)
            cache.CACHED_GUILD_XP.pop(guild_id, None)
        else:
            cache.CACHED_GUILD_SETTINGS.clear()
            cache.CACHED_GUILD_XP.clear()
        return api_response({'message': 'Guild settings and XP caches invalidated successfully'})
