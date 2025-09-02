"""
XP admin slash command blueprints. All commands here are prefixed with `/manage xp`.
"""
import discord
from discord import app_commands
from discord.ext.commands import GroupCog

from constants import CommandGroup
from bot.slashes.admin_slashes.xp_admin_slashes import XPAdminSlashes
from strings.commands_strings import AdminSlashCommandsStrings


class XPAdminBlueprints(GroupCog):
    xp_group = app_commands.Group(name="xp",
                                  description=AdminSlashCommandsStrings.XP_GROUP_DESCRIPTION,
                                  extras={"group": CommandGroup.XP_MANAGEMENT})

    SETTINGS = xp_group.command(name="settings",
                                description=AdminSlashCommandsStrings.XP_SETTINGS_DESCRIPTION,
                                extras={"group": CommandGroup.XP_MANAGEMENT,
                                        "listing_priority": 2})

    TRANSFER = xp_group.command(name="transfer",
                                description=AdminSlashCommandsStrings.XP_TRANSFER_DESCRIPTION,
                                extras={"group": CommandGroup.XP_MANAGEMENT,
                                        "listing_priority": 3})

    @SETTINGS
    @app_commands.guild_only()
    async def settings(self, interaction: discord.Interaction):
        """Manage XP and levels settings for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await XPAdminSlashes(interaction=interaction).settings()

    @TRANSFER
    @app_commands.guild_only()
    async def transfer(self, interaction: discord.Interaction):
        """Award, remove, or transfer XP from/to users

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await XPAdminSlashes(interaction=interaction).transfer()
