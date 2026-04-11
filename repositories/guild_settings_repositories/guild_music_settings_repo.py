from sqlalchemy import update
from sqlalchemy.dialects.mysql import insert

from models.guild_settings_models import GuildMusicSettings
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

    async def upsert_guild_music_settings(self,
                                          guild_settings_id: int,
                                          **update_data):
        """
        Create or update GuildMusicSettings entry for a specific guild.
        """
        stmt = insert(GuildMusicSettings).values(
            guild_settings_id=guild_settings_id,
            **update_data
        ).on_duplicate_key_update(
            **update_data
        )
        await self._session.execute(stmt)
        await self._session.flush()
