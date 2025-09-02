"""
General admin slash command blueprints. All commands here are prefixed with `/manage`.
"""
import discord
from discord import app_commands
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.admin_slashes.general_admin_slashes import GeneralAdminSlashes
from strings.commands_strings import AdminSlashCommandsStrings


class GeneralAdminBlueprints(Cog):
    LOGGING_CHANNEL = app_commands.command(name="logging-channel",
                                           description=AdminSlashCommandsStrings.LOGGING_CHANNEL_DESCRIPTION,
                                           extras={"group": CommandGroup.GENERAL_MANAGEMENT})

    SETTINGS = app_commands.command(name="settings",
                                    description=AdminSlashCommandsStrings.GENERAL_SETTINGS_DESCRIPTION,
                                    extras={"group": CommandGroup.GENERAL_MANAGEMENT,
                                            "listing_priority": 1})

    @LOGGING_CHANNEL
    @app_commands.guild_only()
    async def logging_channel(self, interaction: discord.Interaction):
        """Set/unset the logging channel for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await GeneralAdminSlashes(interaction=interaction).logging_channel()

    @SETTINGS
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def settings(self, interaction: discord.Interaction, make_visible: bool = False):
        """View a summary and manage all the settings for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        make_visible: bool
            Whether to make the message visible to everyone
        """

        await GeneralAdminSlashes(interaction=interaction).settings(make_visible=make_visible)
