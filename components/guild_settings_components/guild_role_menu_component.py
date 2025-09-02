from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import RoleMenuMode, RoleMenuType
from models.guild_settings_models import GuildRoleMenu
from repositories.guild_settings_repositories.guild_role_menu_repo import GuildRoleMenuRepo

NOT_SET = NOT_SET_()


class GuildRoleMenuComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_role_menu(self,
                               guild_id: int,
                               channel_id: int,
                               message_id: int,
                               menu_type: str = RoleMenuType.SELECT,
                               menu_mode: str = RoleMenuMode.SINGLE) -> GuildRoleMenu:
        """
        Creates record for a new role menu in the guild.
        Args:
            guild_id (int): The ID of the guild.
            channel_id (int): The ID of the channel where the role menu will be used.
            message_id (int): The ID of the message that contains the role menu.
            menu_type (str): The type of the role menu - RoleMenuType
            menu_mode (str): The mode of the role menu - RoleMenuMode

        Returns:
            GuildRoleMenu: The created GuildRoleMenu instance.
        """
        self.logger.debug(f"Creating role menu for guild {guild_id} in channel {channel_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_role_menu_repo = GuildRoleMenuRepo(session=get_session())
        role_menu = await guild_role_menu_repo.create_guild_role_menu(
            guild_settings_id=guild_settings.guild_settings_id,
            channel_id=channel_id,
            message_id=message_id,
            menu_type=menu_type,
            menu_mode=menu_mode
        )
        guild_settings.add_role_menu(guild_role_menu_id=role_menu.id,
                                     channel_id=channel_id,
                                     message_id=message_id,
                                     menu_type=menu_type,
                                     menu_mode=menu_mode)
        return role_menu

    async def update_role_menu(self,
                               guild_id: int,
                               guild_role_menu_id: int,
                               menu_type: str | NOT_SET_ = NOT_SET,
                               menu_mode: str | NOT_SET_ = NOT_SET,
                               role_restriction_description: str | NOT_SET_ = NOT_SET) -> None:
        """
        Update an existing role menu in the guild.
        Args:
            guild_id (int): The ID of the guild related.
            guild_role_menu_id (int): The ID of the role menu to update.
            menu_type (str | NOT_SET_): The new type of the role menu - RoleMenuType.
            menu_mode (str | NOT_SET_): The new mode of the role menu - RoleMenuMode.
            role_restriction_description (str | NOT_SET_): The new description for role restrictions, if applicable.
        """
        self.logger.debug(f"Updating role menu with ID {guild_role_menu_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        role_menu = guild_settings.get_role_menu(guild_role_menu_id=guild_role_menu_id)
        update_data = {}
        if menu_type is not NOT_SET:
            update_data['menu_type'] = menu_type
            role_menu.menu_type = menu_type
        if menu_mode is not NOT_SET:
            update_data['menu_mode'] = menu_mode
            role_menu.menu_mode = menu_mode
        if role_restriction_description is not NOT_SET:
            update_data['role_restriction_description'] = role_restriction_description
            role_menu.role_restriction_description = role_restriction_description

        guild_role_menu_repo = GuildRoleMenuRepo(session=get_session())
        await guild_role_menu_repo.update_guild_role_menu(guild_role_menu_id=guild_role_menu_id, **update_data)

    async def update_role_menu_restricted_role(self,
                                               guild_id: int,
                                               guild_role_menu_id: int,
                                               role_ids: list[int]) -> None:
        """
        Update the restricted roles for a role menu.
        Args:
            guild_id (int): The ID of the guild.
            guild_role_menu_id (int): The ID of the role menu to update.
            role_ids (list[int]): List of role IDs to set as restricted for the role menu.
        """
        self.logger.debug(f"Updating restricted roles for role menu {guild_role_menu_id} in guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        role_menu = guild_settings.get_role_menu(guild_role_menu_id=guild_role_menu_id)
        removed_role_ids = set(role_menu.restricted_role_ids) - set(role_ids)
        added_role_ids = set(role_ids) - set(role_menu.restricted_role_ids)

        guild_role_menu_repo = GuildRoleMenuRepo(session=get_session())
        for role_id in added_role_ids:
            await guild_role_menu_repo.add_restricted_role(guild_role_menu_id=guild_role_menu_id, role_id=role_id)
        for role_id in removed_role_ids:
            await guild_role_menu_repo.remove_restricted_role(guild_role_menu_id=guild_role_menu_id, role_id=role_id)
        role_menu.restricted_role_ids = set(role_ids)
