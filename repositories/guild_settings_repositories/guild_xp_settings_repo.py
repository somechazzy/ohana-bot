from sqlalchemy import select, update, delete

from models.guild_settings_models import GuildXPSettings, GuildSettings, GuildXPLevelRole, \
    GuildXPIgnoredRole, GuildXPIgnoredChannel
from repositories import BaseRepo


class GuildXPSettingsRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_xp_settings(self, guild_settings_id: int, **attributes) -> GuildXPSettings:
        """
        Create XP settings for a guild.
        """
        settings = GuildXPSettings(
            guild_settings_id=guild_settings_id,
            **attributes,
            level_roles=[],
            ignored_roles=[],
            ignored_channels=[]
        )
        self._session.add(settings)
        await self._session.flush()
        return settings

    async def get_guild_xp_settings(self,
                                    guild_id: int | None = None,
                                    guild_settings_id: int | None = None) -> GuildXPSettings | None:
        """
        Retrieve guild XP settings. Must provide either guild_id or guild_settings_id.
        """
        if guild_id is None and guild_settings_id is None:
            raise ValueError("Either guild_id or guild_settings_id must be provided.")
        if guild_id:
            return (await self._session.execute(
                select(GuildXPSettings).join(GuildXPSettings.guild_settings).where(GuildSettings.guild_id == guild_id)
            )).unique().scalar_one_or_none()
        return (await self._session.execute(
            select(GuildXPSettings).where(GuildXPSettings.guild_settings_id == guild_settings_id)
        )).unique().scalar_one_or_none()

    async def update_guild_xp_settings(self,
                                       guild_xp_settings_id: int | None = None,
                                       guild_xp_settings: GuildXPSettings | None = None, **kwargs) -> None:
        """
        Update XP settings for a specific guild. Must provide either guild_xp_settings_id or guild_xp_settings.
        """
        if guild_xp_settings_id:
            await self._session.execute(
                update(GuildXPSettings).where(GuildXPSettings.id == guild_xp_settings_id).values(**kwargs)
            )
            await self._session.flush()
        elif guild_xp_settings:
            for key, value in kwargs.items():
                setattr(guild_xp_settings, key, value)
            self._session.add(guild_xp_settings)
            await self._session.flush()
        else:
            raise ValueError("Either guild_xp_settings_id or guild_xp_settings must be provided.")

    # noinspection PyTypeChecker
    async def add_xp_level_role(self, guild_xp_settings_id: int, role_id: int, level: int,):
        """
        Add a role to the XP level roles.
        """
        level_role = GuildXPLevelRole(
            guild_xp_settings_id=guild_xp_settings_id,
            role_id=role_id,
            level=level
        )
        self._session.add(level_role)
        await self._session.flush()
        return level_role

    async def update_level_role(self, role_id: int, level: int):
        """
        Update an existing XP level role by role_id.
        """
        await self._session.execute(
            update(GuildXPLevelRole).where(GuildXPLevelRole.role_id == role_id)
            .values(level=level)
        )
        await self._session.flush()

    async def remove_xp_level_role(self, role_id: int, level: int):
        """
        Remove a role from the XP level roles.
        """
        await self._session.execute(
            delete(GuildXPLevelRole).where(GuildXPLevelRole.role_id == role_id, GuildXPLevelRole.level == level)
        )
        await self._session.flush()

    # noinspection PyTypeChecker
    async def add_xp_ignored_role(self, guild_xp_settings_id: int, role_id: int):
        """
        Add a role to the XP ignored roles.
        """
        ignored_role = GuildXPIgnoredRole(
            guild_xp_settings_id=guild_xp_settings_id,
            role_id=role_id
        )
        self._session.add(ignored_role)
        await self._session.flush()
        return ignored_role

    async def remove_xp_ignored_role(self, role_id: int):
        """
        Remove a role from the XP ignored roles.
        """
        await self._session.execute(
            delete(GuildXPIgnoredRole).where(GuildXPIgnoredRole.role_id == role_id)
        )
        await self._session.flush()

    # noinspection PyTypeChecker
    async def add_xp_ignored_channel(self, guild_xp_settings_id: int, channel_id: int):
        """
        Add a channel to the XP ignored channels.
        """
        ignored_channel = GuildXPIgnoredChannel(
            guild_xp_settings_id=guild_xp_settings_id,
            channel_id=channel_id
        )
        self._session.add(ignored_channel)
        await self._session.flush()
        return ignored_channel

    async def remove_xp_ignored_channel(self, channel_id: int):
        """
        Remove a channel from the XP ignored channels.
        """
        await self._session.execute(
            delete(GuildXPIgnoredChannel).where(GuildXPIgnoredChannel.channel_id == channel_id)
        )
        await self._session.flush()
