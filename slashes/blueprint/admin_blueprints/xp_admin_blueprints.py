from discord import Interaction, app_commands
from discord.ext.commands import GroupCog

from globals_.constants import XPTransferAction, XPTransferActionTarget
from slashes.admin_slashes.xp_admin_slashes import XPAdminSlashes


class XPAdminBlueprints(GroupCog):
    xp_group = app_commands.Group(name="xp",
                                  description="XP and levels system settings")

    SETTINGS = xp_group.command(name="settings",
                                description="Manage XP and levels settings for this server")

    OVERVIEW = xp_group.command(name="overview",
                                description="View a summary of all XP and levels settings for this server")

    TRANSFER = xp_group.command(name="transfer",
                                description="Award or remove XP from users")

    @SETTINGS
    @app_commands.guild_only()
    async def settings(self, inter: Interaction):
        """Manage XP and levels settings for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await XPAdminSlashes(interaction=inter).settings()

    @OVERVIEW
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def overview(self, inter: Interaction, make_visible: bool = False):
        """View a summary of all XP and levels settings for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        make_visible: bool
            Whether to make the message visible to everyone
        """

        await XPAdminSlashes(interaction=inter).overview(make_visible=make_visible)

    @TRANSFER
    @app_commands.guild_only()
    async def transfer(self, inter: Interaction, action: XPTransferAction, target: XPTransferActionTarget):
        """Award or remove XP from users

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        action:
            XP action to perform
        target:
            Target of the action
        """

        await XPAdminSlashes(interaction=inter).transfer(action=action, target=target)
