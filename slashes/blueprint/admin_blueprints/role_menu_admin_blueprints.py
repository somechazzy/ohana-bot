from discord import Interaction, app_commands
from discord.ext.commands import GroupCog

from slashes.admin_slashes.role_menu_admin_slashes import RoleMenuAdminSlashes


class RoleMenuAdminBlueprints(GroupCog):
    playlist_group = app_commands.Group(name="role-menu",
                                        description="Create and edit role menus",
                                        extras={"unlisted": True})

    ROLE_MENU_CREATE = playlist_group.command(name="create",
                                              description="Create a new role menu")

    ROLE_MENU_EDIT = playlist_group.command(name="edit",
                                            description="Edit an existing role menu (also use to remove deleted roles)")

    @ROLE_MENU_CREATE
    @app_commands.guild_only()
    async def role_menu_create(self, inter: Interaction):
        """Create a new role menu

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await RoleMenuAdminSlashes(interaction=inter).role_menu_create()

    @ROLE_MENU_EDIT
    @app_commands.guild_only()
    @app_commands.rename(message_id="role-menu-message-id")
    async def role_menu_edit(self, inter: Interaction, message_id: str):
        """Edit an existing role menu (also use to remove deleted roles)

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        message_id: str
            ID of the role menu message
        """

        await RoleMenuAdminSlashes(interaction=inter).role_menu_edit(message_id=message_id)
