"""
Role menu admin slash command blueprints. All commands here are prefixed with `/manage role-menu`.
"""
import discord
from discord import app_commands
from discord.ext.commands import GroupCog

from constants import CommandGroup
from bot.slashes.admin_slashes.role_menu_admin_slashes import RoleMenuAdminSlashes
from strings.commands_strings import AdminSlashCommandsStrings


class RoleMenuAdminBlueprints(GroupCog):
    role_menu_group = app_commands.Group(name="role-menu",
                                         description=AdminSlashCommandsStrings.ROLE_MENU_CREATE_DESCRIPTION,
                                         extras={"unlisted": True,
                                                 "group": CommandGroup.ROLE_MENU_MANAGEMENT})

    ROLE_MENU_CREATE = role_menu_group.command(name="create",
                                               description=AdminSlashCommandsStrings.ROLE_MENU_CREATE_DESCRIPTION,
                                               extras={"group": CommandGroup.ROLE_MENU_MANAGEMENT,
                                                       "listing_priority": 1,
                                                       "aliases": ["manage rolemenu create"]})

    ROLE_MENU_EDIT = role_menu_group.command(name="edit",
                                             description=AdminSlashCommandsStrings.ROLE_MENU_EDIT_DESCRIPTION,
                                             extras={"group": CommandGroup.ROLE_MENU_MANAGEMENT,
                                                     "listing_priority": 2,
                                                     "aliases": ["manage rolemenu edit"]})

    rolemenu_group = app_commands.Group(name="rolemenu",
                                        description=AdminSlashCommandsStrings.ROLE_MENU_CREATE_DESCRIPTION,
                                        extras={"unlisted": True,
                                                "group": CommandGroup.ROLE_MENU_MANAGEMENT})
    ROLEMENU_CREATE = rolemenu_group.command(name="create",
                                             description=AdminSlashCommandsStrings.ROLE_MENU_CREATE_DESCRIPTION,
                                             extras={"is_alias": True,
                                                     "alias_for": "manage role-menu create",
                                                     "group": CommandGroup.ROLE_MENU_MANAGEMENT})
    ROLEMENU_EDIT = rolemenu_group.command(name="edit",
                                           description=AdminSlashCommandsStrings.ROLE_MENU_EDIT_DESCRIPTION,
                                           extras={"is_alias": True,
                                                   "alias_for": "manage role-menu edit",
                                                   "group": CommandGroup.ROLE_MENU_MANAGEMENT})

    @ROLE_MENU_CREATE
    @app_commands.guild_only()
    async def role_menu_create(self, interaction: discord.Interaction):
        """Create a new role menu

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await RoleMenuAdminSlashes(interaction=interaction).role_menu_create()

    @ROLE_MENU_EDIT
    @app_commands.guild_only()
    @app_commands.rename(message_id="role-menu-message-id")
    async def role_menu_edit(self, interaction: discord.Interaction, message_id: str):
        """Edit an existing role menu (also use to remove deleted roles)

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        message_id: str
            ID of the role menu message
        """

        await RoleMenuAdminSlashes(interaction=interaction).role_menu_edit(message_id=message_id)

    @ROLEMENU_CREATE
    @app_commands.guild_only()
    async def rolemenu_create(self, interaction: discord.Interaction):
        """Create a new role menu

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await RoleMenuAdminSlashes(interaction=interaction).role_menu_create()

    @ROLEMENU_EDIT
    @app_commands.guild_only()
    @app_commands.rename(message_id="role-menu-message-id")
    async def rolemenu_edit(self, interaction: discord.Interaction, message_id: str):
        """Edit an existing role menu (also use to remove deleted roles)

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        message_id: str
            ID of the role menu message
        """

        await RoleMenuAdminSlashes(interaction=interaction).role_menu_edit(message_id=message_id)
