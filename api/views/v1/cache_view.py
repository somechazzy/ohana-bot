import cache
from api.views.base_view import APIViewV1
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from utils.helpers.api_helpers import api_response


class InvalidateGuildCacheView(APIViewV1):
    AUTH_REQUIRED = True
    ROUTE = '/guild_cache/invalidate'

    async def post(self):
        """
        Invalidate the guild settings and XP caches.
        Parameters:
            - guild_id: The ID of the guild to invalidate. If not provided, all guilds will be invalidated.
        """
        guild_id = self.request_body.get('guild_id')
        if guild_id:
            guild_id = int(guild_id)
            refresh_in_place = self.request_body.get('refresh_in_place', False)
            if refresh_in_place:
                await GuildSettingsComponent().fetch_guild_settings(guild_id=guild_id, create_if_not_exists=True)
                await GuildUserXPComponent().fetch_guild_xp(guild_id=guild_id, force_refresh_cache=True)
            else:
                cache.CACHED_GUILD_SETTINGS.pop(guild_id, None)
                cache.CACHED_GUILD_XP.pop(guild_id, None)
        else:
            cache.CACHED_GUILD_SETTINGS.clear()
            cache.CACHED_GUILD_XP.clear()
        return api_response({'message': 'Guild settings and XP caches invalidated successfully'})
