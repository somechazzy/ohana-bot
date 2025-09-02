from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from models.guild_settings_models import GuildMusicSettings
from repositories.guild_settings_repositories.guild_music_settings_repo import GuildMusicSettingsRepo

NOT_SET = NOT_SET_()


class GuildMusicSettingsComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_guild_music_settings(self,
                                          guild_id: int,
                                          guild_settings_id: int) -> GuildMusicSettings:
        """
        Create a new guild music settings entry.
        Args:
            guild_id (int): The ID of the guild to create settings for.
            guild_settings_id (int): The GuildSettings ID related to the guild.

        Returns:
            GuildMusicSettings: The created GuildMusicSettings object.
        """
        self.logger.debug(f"Creating music settings for guild_id: {guild_id}")
        guild_music_settings_repo = GuildMusicSettingsRepo(session=get_session())
        return await guild_music_settings_repo.create_guild_music_settings(
            guild_settings_id=guild_settings_id
        )

    async def update_guild_music_settings(self,
                                          guild_id: int,
                                          guild_settings_id: int,
                                          music_channel_id: int | NOT_SET_ = NOT_SET,
                                          music_header_message_id: int | NOT_SET_ = NOT_SET,
                                          music_player_message_id: int | NOT_SET_ = NOT_SET):
        """
        Update the music channel settings for a guild.
        Args:
            guild_id (int): The ID of the guild to update settings for.
            guild_settings_id (int): The GuildSettings ID related.
            music_channel_id (int | NOT_SET_): The ID of the music channel to set.
            music_header_message_id (int | NOT_SET_): The ID of the music header message to set.
            music_player_message_id (int | NOT_SET_): The ID of the music player message to set.
        """
        self.logger.debug(f"Updating music settings for guild_id: {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_music_settings_repo = GuildMusicSettingsRepo(session=get_session())

        update_data = {}
        if music_channel_id is not NOT_SET:
            update_data['music_channel_id'] = music_channel_id
            guild_settings.music_channel_id = music_channel_id
        if music_header_message_id is not NOT_SET:
            update_data['music_header_message_id'] = music_header_message_id
            guild_settings.music_header_message_id = music_header_message_id
        if music_player_message_id is not NOT_SET:
            update_data['music_player_message_id'] = music_player_message_id
            guild_settings.music_player_message_id = music_player_message_id

        if not await guild_music_settings_repo.get_guild_music_settings(
            guild_settings_id=guild_settings_id
        ):
            await guild_music_settings_repo.create_guild_music_settings(
                guild_settings_id=guild_settings_id,
                music_channel_id=music_channel_id if music_channel_id is not NOT_SET else None,
                music_header_message_id=music_header_message_id if music_header_message_id is not NOT_SET else None,
                music_player_message_id=music_player_message_id if music_player_message_id is not NOT_SET else None
            )
        else:
            await guild_music_settings_repo.update_guild_music_settings(
                guild_settings_id=guild_settings_id,
                **update_data
            )
