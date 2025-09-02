from sqlalchemy import update, delete

from constants import RoleMenuDefaults
from models.guild_settings_models import GuildRoleMenu, GuildRoleMenuRestrictedRole
from repositories import BaseRepo


class GuildRoleMenuRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_role_menu(self,
                                     guild_settings_id: int,
                                     channel_id: int,
                                     message_id: int,
                                     menu_type: str = RoleMenuDefaults.MENU_TYPE,
                                     menu_mode: str = RoleMenuDefaults.MENU_MODE,
                                     role_restriction_description: str | None = None) -> GuildRoleMenu:
        """
        Create a new GuildRoleMenu entry in the database.
        """
        role_menu = GuildRoleMenu(
            guild_settings_id=guild_settings_id,
            channel_id=channel_id,
            message_id=message_id,
            menu_type=menu_type,
            menu_mode=menu_mode,
            role_restriction_description=role_restriction_description,
            restricted_roles=[]
        )
        self._session.add(role_menu)
        await self._session.flush()
        return role_menu

    async def update_guild_role_menu(self,
                                     guild_role_menu_id: int,
                                     **update_data):
        """
        Update an existing GuildRoleMenu entry.
        """
        await self._session.execute(
            update(GuildRoleMenu).where(
                GuildRoleMenu.id == guild_role_menu_id
            ).values(**update_data)
        )

    async def delete_guild_role_menu(self,
                                     guild_role_menu_id: int):
        """
        Delete a GuildRoleMenu entry by its ID.
        """
        await self._session.execute(
            delete(GuildRoleMenu).where(
                GuildRoleMenu.id == guild_role_menu_id
            )
        )

    # noinspection PyTypeChecker
    async def add_restricted_role(self,
                                  guild_role_menu_id: int,
                                  role_id: int):
        """
        Add a restricted role to a GuildRoleMenu.
        """
        restricted_role = GuildRoleMenuRestrictedRole(
            guild_role_menu_id=guild_role_menu_id,
            role_id=role_id
        )
        self._session.add(restricted_role)
        await self._session.flush()
        return restricted_role

    async def remove_restricted_role(self,
                                     guild_role_menu_id: int,
                                     role_id: int):
        """
        Remove a restricted role from a GuildRoleMenu.
        """
        await self._session.execute(
            delete(GuildRoleMenuRestrictedRole).where(
                GuildRoleMenuRestrictedRole.guild_role_menu_id == guild_role_menu_id,
                GuildRoleMenuRestrictedRole.role_id == role_id
            )
        )
