from datetime import UTC, datetime, timedelta
from typing import Any

from common.db import get_session, add_post_rollback_action
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components import BaseGuildUserXPComponent
import cache
from models.dto.cachables import CachedGuildXP
from repositories.guild_settings_repositories.guild_settings_repository import GuildSettingsRepo
from repositories.guild_settings_repositories.guild_user_xp_repo import GuildUserXPRepo


class GuildUserXPComponent(BaseGuildUserXPComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def fetch_guild_xp(self, guild_id: int, force_refresh_cache: bool = False):
        """
        Fetches the XP data for all users in a guild and caches it.
        Args:
            guild_id (int): The ID of the guild to fetch XP data for.
            force_refresh_cache (bool): If True and the guild is already cached with pending updates,
                the cache will be refreshed. Otherwise, an error is raised.
        """
        self.logger.debug(f"Fetching XP data for guild {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if cache.CACHED_GUILD_XP.get(guild_id) \
                and not cache.CACHED_GUILD_XP[guild_id].is_synced \
                and not force_refresh_cache:
            raise ValueError(f"Guild {guild_id} already cached with pending updates, yet a fetch was requested.")
        guild_user_xp_records = await GuildUserXPRepo(session=get_session()).get_all_for_guild(
            guild_settings_id=guild_settings.guild_settings_id
        )
        cache.CACHED_GUILD_XP[guild_id] = CachedGuildXP.from_orm_objects(
            guild_id=guild_id,
            guild_settings_id=guild_settings.guild_settings_id,
            guild_user_xps=guild_user_xp_records
        )

    async def get_guild_xp(self, guild_id: int) -> CachedGuildXP:
        """
        Returns the cached XP data for a guild. If not found then the data is fetched and cached.
        Args:
            guild_id (int): The ID of the guild to get XP data for.
        Returns:
            CachedGuildXP: The cached XP data for the guild.
        """
        if guild_id not in cache.CACHED_GUILD_XP:
            await self.fetch_guild_xp(guild_id)
        return cache.CACHED_GUILD_XP[guild_id]

    async def sync_up_guild_user_xp(self) -> None:
        """
        Syncs up all the cached guild user XP data to the database.
        """
        self.logger.debug(f"Syncing up XP data.")
        upsert_data: dict[tuple[int, int], dict[str, Any]] = {}
        guild_ids = list(cache.CACHED_GUILD_XP.keys())
        for guild_id in guild_ids:
            cached_guild_xp = cache.CACHED_GUILD_XP[guild_id]
            for member_xp in cached_guild_xp.get_unsynced_xps():
                upsert_data[(cached_guild_xp.guild_settings_id, member_xp.user_id)] = {
                    "user_username": member_xp.user_username,
                    "xp": member_xp.xp,
                    "level": member_xp.level,
                    "message_count": member_xp.message_count,
                    "latest_gain_time": member_xp.latest_gain_time,
                    "latest_level_up_message_time": member_xp.latest_level_up_message_time,
                    "decayed_xp": member_xp.decayed_xp,
                    "latest_decay_time": member_xp.latest_decay_time,
                    "latest_message_time": member_xp.latest_message_time,
                }
                member_xp.is_synced = True
                add_post_rollback_action(member_xp.set_sync_status, is_synced=False)
            cached_guild_xp.is_synced = True

        if upsert_data:
            await GuildUserXPRepo(session=get_session()).bulk_upsert_guild_user_xp(upsert_data)

    async def fetch_guild_xp_for_decay_eligible_guilds(self):
        """
        Fetches the XP data for all guilds that are eligible for decay and have members pending decay.
        """
        self.logger.debug("Fetching XP data for guilds eligible for decay.")
        guild_settings_with_decay_enabled = await GuildSettingsRepo(session=get_session()).\
            get_necessary_data_for_guild_user_xp_decay()
        guild_settings_id_guild_id_map = {
            guild_settings.id: guild_settings.guild_id
            for guild_settings in guild_settings_with_decay_enabled
        }

        guild_settings_ids_to_decay_cutoff_datetime_pairs = []
        for guild_settings in guild_settings_with_decay_enabled:
            if guild_settings.guild_id in cache.CACHED_GUILD_XP:
                continue
            if guild_settings.xp_settings.xp_decay_enabled:
                grace_days = guild_settings.xp_settings.xp_decay_grace_period_days
                cutoff_datetime = datetime.now(UTC) - timedelta(days=grace_days)
                guild_settings_ids_to_decay_cutoff_datetime_pairs.append((guild_settings.id, cutoff_datetime))
        guild_settings_ids = await GuildUserXPRepo(session=get_session()).\
            get_guild_settings_ids_with_decay_eligible_members(
                guild_settings_id_last_message_time_pairs=guild_settings_ids_to_decay_cutoff_datetime_pairs
            )

        guild_user_xps = await GuildUserXPRepo(session=get_session()).get_all_for_guilds(
            guild_settings_ids=guild_settings_ids
        )
        guild_settings_id_guild_user_xps_map = {}
        for guild_user_xp in guild_user_xps:
            guild_settings_id = guild_user_xp.guild_settings_id
            if guild_settings_id not in guild_settings_id_guild_user_xps_map:
                guild_settings_id_guild_user_xps_map[guild_settings_id] = []
            guild_settings_id_guild_user_xps_map[guild_settings_id].append(guild_user_xp)
        for guild_settings_id, guild_user_xps in guild_settings_id_guild_user_xps_map.items():
            guild_id = guild_settings_id_guild_id_map[guild_settings_id]
            cache.CACHED_GUILD_XP[guild_id] = CachedGuildXP.from_orm_objects(
                guild_id=guild_id,
                guild_settings_id=guild_settings_id,
                guild_user_xps=guild_user_xps
            )
