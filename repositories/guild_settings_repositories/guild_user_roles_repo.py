from sqlalchemy import update, select, delete
from sqlalchemy.dialects.mysql import insert

from models.guild_settings_models import GuildUserRoles
from repositories import BaseRepo


class GuildUserRolesRepo(BaseRepo):

    async def upsert_guild_user_roles(self,
                                      guild_settings_id: int,
                                      user_id: int,
                                      role_ids: list[int]):
        """
        Create or update GuildUserRoles entry for a specific guild member.
        """
        stmt = insert(GuildUserRoles).values(
            guild_settings_id=guild_settings_id,
            user_id=user_id,
            role_ids=role_ids,
        ).on_duplicate_key_update(
            role_ids=role_ids,
        )
        await self._session.execute(stmt)
        await self._session.flush()

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
