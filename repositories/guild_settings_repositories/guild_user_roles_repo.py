from sqlalchemy import update, select, delete

from models.guild_settings_models import GuildUserRoles
from repositories import BaseRepo


class GuildUserRolesRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_user_roles(self,
                                      guild_settings_id: int,
                                      user_id: int,
                                      role_ids: list) -> GuildUserRoles:
        """
        Create a new GuildUserRoles entry.
        """
        guild_user_roles = GuildUserRoles(
            guild_settings_id=guild_settings_id,
            user_id=user_id,
            role_ids=role_ids
        )
        self._session.add(guild_user_roles)
        await self._session.flush()
        return guild_user_roles

    async def update_guild_user_roles(self,
                                      guild_settings_id: int,
                                      user_id: int,
                                      role_ids: list[int]):
        """
        Update the role IDs for a specific guild member.
        """
        await self._session.execute(
            update(GuildUserRoles).where(
                GuildUserRoles.guild_settings_id == guild_settings_id,
                GuildUserRoles.user_id == user_id
            ).values(role_ids=role_ids)
        )

    async def get_guild_user_roles(self, guild_settings_id: int, user_id: int) -> GuildUserRoles | None:
        """
        Get the GuildUserRoles entry for a specific user in a guild.
        """
        result = await self._session.execute(
            select(GuildUserRoles).where(
                GuildUserRoles.guild_settings_id == guild_settings_id,
                GuildUserRoles.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def delete_guild_user_roles_for_guild(self, guild_settings_id: int) -> None:
        """
        Delete all GuildUserRoles entries for a specific guild.
        """
        await self._session.execute(
            delete(GuildUserRoles).where(
                GuildUserRoles.guild_settings_id == guild_settings_id
            )
        )
        await self._session.flush()

    async def bulk_create_guild_user_roles(self, data: list[dict]) -> None:
        """
        Bulk create GuildUserRoles entries.
        """
        await self._session.run_sync(
            lambda sync_session: sync_session.bulk_insert_mappings(GuildUserRoles, data)
        )
        await self._session.flush()
