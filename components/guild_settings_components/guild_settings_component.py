from datetime import datetime, UTC

import cache
from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from constants import GuildEventType
from models.dto.cachables import CachedGuildSettings
from models.guild_settings_models import GuildSettings
from repositories.guild_settings_repositories.guild_settings_repository import GuildSettingsRepo

NOT_SET = NOT_SET_()


class GuildSettingsComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_initial_guild_settings(self,
                                            guild_id: int,
                                            guild_name: str,
                                            joined_at: datetime,
                                            guild_data: dict) -> GuildSettings:
        """
        Creates initial guild settings. This includes GuildSettings, a join event
        in GuildEvent, and default XP settings in GuildXPSettings, and default music settings in GuildMusicSettings.
        Args:
            guild_id (int): The ID of the guild.
            guild_name (str): The name of the guild.
            joined_at (datetime): The date and time when the bot joined the guild.
            guild_data (dict): Additional data about the guild to store in the event metadata.

        Returns:
            GuildSettings: The initial settings for the new guild.
        """
        self.logger.debug(f"Creating initial guild settings for guild ID: {guild_id}, Name: {guild_name}")

        from components.guild_settings_components.guild_event_component import GuildEventComponent
        from components.guild_settings_components.guild_music_settings_component import GuildMusicSettingsComponent
        from components.guild_settings_components.guild_xp_settings_component import GuildXPSettingsComponent
        guild_settings = await GuildSettingsRepo(session=get_session()).create_guild_settings(
            guild_id=guild_id,
            guild_name=guild_name,
            currently_in_guild=True,
        )
        await GuildEventComponent().create_guild_event(guild_id=guild_id,
                                                       guild_settings_id=guild_settings.id,
                                                       event=GuildEventType.JOIN,
                                                       event_time=joined_at,
                                                       event_metadata=guild_data)
        guild_settings.music_settings = await GuildMusicSettingsComponent().create_guild_music_settings(
            guild_id=guild_id,
            guild_settings_id=guild_settings.id
        )
        guild_settings.xp_settings = await GuildXPSettingsComponent().create_guild_xp_settings(
            guild_id=guild_id,
            guild_settings_id=guild_settings.id
        )
        self.logger.info(f"Initial guild settings created for guild ID: {guild_name} ({guild_id})",
                         extras={"guild_id": guild_id})
        return guild_settings

    async def get_guild_settings(self, guild_id: int, force_fetch: bool = False) -> CachedGuildSettings | None:
        """
        Gets guild settings for guild ID.
        If settings are cached, it returns the cached version unless force_fetch is True.
        Args:
            guild_id (int): The ID of the guild to fetch settings for.
            force_fetch (bool): If True, it will force a fresh fetch from the database. Use with care.

        Returns:
            GuildSettings: The settings for the specified guild ID.
        """
        if not cache.CACHED_GUILD_SETTINGS.get(guild_id) or force_fetch:
            await self.fetch_guild_settings(guild_id, create_if_not_exists=True)
        return cache.CACHED_GUILD_SETTINGS.get(guild_id)

    async def fetch_guild_settings(self, guild_id: int, create_if_not_exists: bool = False) -> GuildSettings | None:
        """
        Fetches guild settings for a given guild ID from the database and caches it.
        Args:
            guild_id (int): The ID of the guild to fetch settings for.
            create_if_not_exists (bool): If True, creates initial settings if not found.
        Returns:
            GuildSettings | None: Guild settings object if found, otherwise None.
        """
        self.logger.debug(f"Fetching guild settings for guild ID: {guild_id}")
        guild_settings_repo = GuildSettingsRepo(session=get_session())
        guild_settings = await guild_settings_repo.get_guild_settings(guild_id=guild_id,
                                                                      load_all_relations=True)
        if not guild_settings:
            if create_if_not_exists:
                self.logger.warning(f"No guild settings found for guild ID: {guild_id}. "
                                    f"Creating blindly without name or joined_at.",
                                    extras={"guild_id": guild_id})
                guild_settings = await self.create_initial_guild_settings(
                    guild_id=guild_id,
                    guild_name=f"Guild [{guild_id}]",
                    joined_at=datetime.now(UTC),
                    guild_data={"record_creation_note": "Created blindly without name or joined_at."}
                )
            else:
                return None
        else:
            from components.guild_settings_components.guild_music_settings_component import GuildMusicSettingsComponent
            from components.guild_settings_components.guild_xp_settings_component import GuildXPSettingsComponent
            if not guild_settings.music_settings:
                self.logger.warning(f"Guild settings for guild ID {guild_id} do not have music settings. "
                                    f"Creating default music settings.",
                                    extras={"guild_id": guild_id})
                guild_settings.music_settings = \
                    await GuildMusicSettingsComponent().create_guild_music_settings(guild_id=guild_id,
                                                                                    guild_settings_id=guild_settings.id)
            if not guild_settings.xp_settings:
                self.logger.warning(f"Guild settings for guild ID {guild_id} do not have XP settings. "
                                    f"Creating default XP settings.",
                                    extras={"guild_id": guild_id})
                guild_settings.xp_settings = \
                    await GuildXPSettingsComponent().create_guild_xp_settings(guild_id=guild_id,
                                                                              guild_settings_id=guild_settings.id)
        self._handle_caching(guild_settings=guild_settings)
        return guild_settings

    async def update_guild_settings(self,
                                    guild_id: int,
                                    role_persistence_enabled: bool | NOT_SET_ = NOT_SET,
                                    logging_channel_id: int | None | NOT_SET_ = NOT_SET,
                                    currently_in_guild: bool | NOT_SET_ = NOT_SET,
                                    guild_name: str | NOT_SET_ = NOT_SET) -> None:
        """
        Updates guild settings for a given guild ID.
        Args:
            guild_id (int): The ID of the guild to update.
            role_persistence_enabled (int | NOT_SET_): Whether role persistence is enabled.
            logging_channel_id (int | NOT_SET_): The ID of the logging channel.
            currently_in_guild (bool | NOT_SET_): Whether the bot is currently in the guild.
            guild_name (str | NOT_SET_): The name of the guild.
        """
        self.logger.debug(f"Updating guild settings for guild ID: {guild_id}")
        guild_settings = await self.get_guild_settings(guild_id=guild_id)
        guild_settings_repo = GuildSettingsRepo(session=get_session())
        update_data = {}
        if role_persistence_enabled is not NOT_SET:
            update_data['role_persistence_enabled'] = role_persistence_enabled
            guild_settings.role_persistence_enabled = role_persistence_enabled
        if logging_channel_id is not NOT_SET:
            update_data['logging_channel_id'] = logging_channel_id
            guild_settings.logging_channel_id = logging_channel_id
        if currently_in_guild is not NOT_SET:
            update_data['currently_in_guild'] = currently_in_guild
        if guild_name is not NOT_SET:
            update_data['guild_name'] = guild_name
        await guild_settings_repo.update_guild_settings(guild_settings_id=guild_settings.guild_settings_id,
                                                        **update_data)

    @staticmethod
    def _handle_caching(guild_settings: GuildSettings):
        """
        Handles caching of specific guild settings.
        Args:
            guild_settings (GuildSettings): The guild settings to cache.
        """
        cache.CACHED_GUILD_SETTINGS[guild_settings.guild_id] = CachedGuildSettings.from_orm_object(guild_settings)
