from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from models.guild_settings_models import GuildUserRoles
from repositories.guild_settings_repositories.guild_user_roles_repo import GuildUserRolesRepo

NOT_SET = NOT_SET_()


class GuildUserRolesComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def bulk_create_guild_user_roles(self,
                                           guild_id: int,
                                           user_id_role_ids_map: dict[int, list[int]],
                                           delete_existing_guild_user_roles: bool = False) -> None:
        """
        Create in bulk GuildUserRole objects for the specified guild.
        Args:
            guild_id (int): The ID of the guild to create settings for.
            user_id_role_ids_map (dict[int, list[int]]): A mapping of user IDs to lists of role IDs.
            delete_existing_guild_user_roles (bool): True - existing user roles for the guild will be deleted first.
        """
        self.logger.debug(f"Creating guild user roles for guild {guild_id} "
                          f"for {len(user_id_role_ids_map)} users.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_user_roles_data = [
            {
                "guild_settings_id": guild_settings.guild_settings_id,
                "user_id": user_id,
                "role_ids": role_ids
            } for user_id, role_ids in user_id_role_ids_map.items()
        ]
        guild_user_roles_repo = GuildUserRolesRepo(session=get_session())
        if delete_existing_guild_user_roles:
            await guild_user_roles_repo.delete_guild_user_roles_for_guild(
                guild_settings_id=guild_settings.guild_settings_id
            )
        await guild_user_roles_repo.bulk_create_guild_user_roles(data=guild_user_roles_data)

    async def get_guild_user_roles_for_user(self, guild_id: int, user_id: int) -> GuildUserRoles | None:
        """
        Get the roles for a specific user in a guild.
        Args:
            guild_id (int): The ID of the guild.
            user_id (int): The ID of the user.
        Returns:
            GuildUserRoles: The GuildUserRoles object for the user, or None if not found.
        """
        self.logger.debug(f"Fetching roles for user {user_id} in guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_user_roles_repo = GuildUserRolesRepo(session=get_session())
        return await guild_user_roles_repo.get_guild_user_roles(
            guild_settings_id=guild_settings.guild_settings_id,
            user_id=user_id
        )

    async def set_guild_user_roles(self, guild_id: int, user_id: int, role_ids: list[int]) -> None:
        """
        Create a GuildUserRoles object for a specific user in a guild or update existing roles.
        Args:
            guild_id (int): The ID of the guild.
            user_id (int): The ID of the user.
            role_ids (list[int]): The list of role IDs to set for the user.
        """
        self.logger.debug(f"Creating guild user roles for user {user_id} in guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_user_roles_repo = GuildUserRolesRepo(session=get_session())
        if not await guild_user_roles_repo.get_guild_user_roles(
            guild_settings_id=guild_settings.guild_settings_id,
            user_id=user_id
        ):
            await guild_user_roles_repo.create_guild_user_roles(
                guild_settings_id=guild_settings.guild_settings_id,
                user_id=user_id,
                role_ids=role_ids
            )
        else:
            await guild_user_roles_repo.update_guild_user_roles(
                guild_settings_id=guild_settings.guild_settings_id,
                user_id=user_id,
                role_ids=role_ids
            )
