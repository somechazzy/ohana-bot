from typing import Iterable

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, load_only, contains_eager

from models.guild_settings_models import GuildSettings, GuildRoleMenu, GuildXPSettings
from repositories import BaseRepo


class GuildSettingsRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_settings(self,
                                    guild_id: int,
                                    guild_name: str,
                                    currently_in_guild: bool = True,
                                    role_persistence_enabled: bool = False,
                                    logging_channel_id: int = None) -> GuildSettings:
        """
        Create settings for a guild.
        """
        new_settings = GuildSettings(
            guild_id=guild_id,
            guild_name=guild_name,
            currently_in_guild=currently_in_guild,
            role_persistence_enabled=role_persistence_enabled,
            logging_channel_id=logging_channel_id,
            channels_settings=[],
            autoroles=[],
            auto_responses=[],
            role_menus=[],
            music_settings=None,
            xp_settings=None,
            user_xps=[]
        )
        self._session.add(new_settings)
        await self._session.flush()
        return new_settings

    async def get_guild_settings(self,
                                 guild_id: int,
                                 load_all_relations: bool = False,
                                 only: Iterable | None = None) -> GuildSettings | None:
        """
        Retrieve guild settings by guild ID.
        """
        query = select(GuildSettings).where(GuildSettings.guild_id == guild_id)
        if load_all_relations:
            query = query.options(
                joinedload(GuildSettings.channels_settings),
                joinedload(GuildSettings.autoroles),
                joinedload(GuildSettings.auto_responses),
                joinedload(GuildSettings.role_menus).joinedload(GuildRoleMenu.restricted_roles),
                joinedload(GuildSettings.music_settings),
                joinedload(GuildSettings.xp_settings).joinedload(GuildXPSettings.level_roles),
                joinedload(GuildSettings.xp_settings).joinedload(GuildXPSettings.ignored_channels),
                joinedload(GuildSettings.xp_settings).joinedload(GuildXPSettings.ignored_roles),
            )
        if only:
            query = query.options(load_only(*only))
        return (await self._session.execute(query)).unique().scalar_one_or_none()

    async def update_guild_settings(self, guild_settings_id: int, **update_data) -> None:
        """
        Update guild settings for a specific guild.
        """
        await self._session.execute(
            update(GuildSettings).where(GuildSettings.id == guild_settings_id).values(**update_data)
        )
        await self._session.flush()

    async def get_necessary_data_for_guild_user_xp_decay(self) -> list[GuildSettings]:
        """
        Retrieves guild settings with data loaded specifically for user XP decay purposes.
        Loads:
        GuildSettings
        -- id
        -- guild_id
        -- currently_in_guild
        -- xp_settings
            -- xp_decay_enabled
            -- xp_decay_grace_period_days
        Conditions:
        -- GuildSettings.currently_in_guild is True
        -- GuildSettings.xp_settings.xp_decay_enabled is True
        """
        query = select(GuildSettings).\
            join(GuildXPSettings, GuildSettings.id == GuildXPSettings.guild_settings_id) \
            .options(contains_eager(GuildSettings.xp_settings)
                     .options(load_only(GuildXPSettings.xp_decay_enabled,
                                        GuildXPSettings.xp_decay_grace_period_days))) \
            .where(GuildSettings.currently_in_guild.is_(True)) \
            .where(GuildXPSettings.xp_decay_enabled.is_(True)) \
            .options(load_only(GuildSettings.id, GuildSettings.guild_id, GuildSettings.currently_in_guild))

        return (await self._session.execute(query)).scalars().all()
