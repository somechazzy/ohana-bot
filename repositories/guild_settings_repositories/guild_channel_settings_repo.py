from sqlalchemy import update, select

from models.guild_settings_models import GuildChannelSettings
from repositories import BaseRepo


class GuildChannelSettingsRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_channel_settings(self,
                                            guild_settings_id: int,
                                            channel_id: int,
                                            is_gallery_channel: bool,
                                            message_limiting_role_id: int) -> GuildChannelSettings:
        """
        Create a new GuildChannelSettings entry for a guild.
        """
        channel_settings = GuildChannelSettings(
            guild_settings_id=guild_settings_id,
            channel_id=channel_id,
            is_gallery_channel=is_gallery_channel,
            message_limiting_role_id=message_limiting_role_id
        )
        self._session.add(channel_settings)
        await self._session.flush()
        return channel_settings

    async def update_guild_channel_settings(self,
                                            guild_settings_id: int,
                                            channel_id: int,
                                            **update_data):
        """
        Update an existing GuildChannelSettings entry.
        """
        await self._session.execute(
            update(GuildChannelSettings).where(
                GuildChannelSettings.guild_settings_id == guild_settings_id,
                GuildChannelSettings.channel_id == channel_id
            ).values(**update_data)
        )

    async def get_guild_channel_settings(self,
                                         guild_settings_id: int,
                                         channel_id: int) -> GuildChannelSettings | None:
        """
        Retrieve GuildChannelSettings for a specific guild and channel.
        """

        query = select(GuildChannelSettings).where(GuildChannelSettings.guild_settings_id == guild_settings_id,
                                                   GuildChannelSettings.channel_id == channel_id)
        return (await self._session.execute(query)).unique().scalar_one_or_none()
