from sqlalchemy import select, update

from models.guild_settings_models import GuildMusicSettings, GuildSettings
from repositories import BaseRepo


class GuildMusicSettingsRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_music_settings(self,
                                          guild_settings_id: int,
                                          music_channel_id: int | None = None,
                                          music_header_message_id: int | None = None,
                                          music_player_message_id: int | None = None) -> GuildMusicSettings:
        """
        Create music settings for a guild.
        """
        settings = GuildMusicSettings(
            guild_settings_id=guild_settings_id,
            music_channel_id=music_channel_id,
            music_header_message_id=music_header_message_id,
            music_player_message_id=music_player_message_id
        )
        self._session.add(settings)
        await self._session.flush()
        return settings

    async def get_guild_music_settings(self,
                                       guild_id: int | None = None,
                                       guild_settings_id: int | None = None) -> GuildMusicSettings | None:
        """
        Retrieve guild music settings. Must provide either guild_id or guild_settings_id.
        """
        if guild_id is None and guild_settings_id is None:
            raise ValueError("Either guild_id or guild_settings_id must be provided.")
        if guild_id:
            return await self._session.execute(
                select(GuildMusicSettings)
                .join(GuildMusicSettings.guild_settings)
                .where(GuildSettings.guild_id == guild_id)
            ).scalar_one_or_none()
        return (await self._session.execute(
            select(GuildMusicSettings).where(GuildMusicSettings.guild_settings_id == guild_settings_id)
        )).scalar_one_or_none()

    async def update_guild_music_settings(self, guild_settings_id: int, **update_data) -> None:
        """
        Update music settings for a specific guild.
        """
        await self._session.execute(
            update(GuildMusicSettings)
            .where(GuildMusicSettings.guild_settings_id == guild_settings_id)
            .values(**update_data)
        )
        await self._session.flush()
