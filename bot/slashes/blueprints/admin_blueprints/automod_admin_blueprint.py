"""
Automod admin slash command blueprints. All commands here are prefixed with `/manage`.
"""
import discord
from discord import app_commands
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.admin_slashes.automod_admin_slashes import AutomodAdminSlashes
from strings.commands_strings import AdminSlashCommandsStrings


class AutomodAdminBlueprints(Cog):
    ROLE_PERSISTENCE = app_commands.command(name="role-persistence",
                                            description=AdminSlashCommandsStrings.ROLE_PERSISTENCE_DESCRIPTION,
                                            extras={"group": CommandGroup.ROLE_MANAGEMENT,
                                                    "aliases": ["manage rolepersistence"]})
    ROLEPERSISTENCE = app_commands.command(name="rolepersistence",
                                           description=AdminSlashCommandsStrings.ROLE_PERSISTENCE_DESCRIPTION,
                                           extras={"is_alias": True,
                                                   "alias_for": "manage role-persistence",
                                                   "group": CommandGroup.ROLE_MANAGEMENT})
    AUTOROLES = app_commands.command(name="autoroles",
                                     description=AdminSlashCommandsStrings.AUTOROLES_DESCRIPTION,
                                     extras={"group": CommandGroup.ROLE_MANAGEMENT})
    AUTO_RESPONSES = app_commands.command(name="auto-responses",
                                          description=AdminSlashCommandsStrings.AUTO_RESPONSES_DESCRIPTION,
                                          extras={"group": CommandGroup.AUTOMOD,
                                                  "listing_priority": 10,
                                                  "aliases": ["manage autoresponses"]})
    AUTORESPONSES = app_commands.command(name="autoresponses",
                                         description=AdminSlashCommandsStrings.AUTO_RESPONSES_DESCRIPTION,
                                         extras={"is_alias": True,
                                                 "alias_for": "manage auto-responses",
                                                 "group": CommandGroup.AUTOMOD,
                                                 "listing_priority": 10})
    GALLERY_CHANNELS = app_commands.command(name="gallery-channels",
                                            description=AdminSlashCommandsStrings.GALLERY_CHANNELS_DESCRIPTION,
                                            extras={"group": CommandGroup.CHANNEL_MANAGEMENT})
    LIMITED_MESSAGES_CHANNELS = app_commands.command(
        name="limited-messages-channels",
        description=AdminSlashCommandsStrings.LIMITED_MESSAGES_CHANNELS_DESCRIPTION,
        extras={"group": CommandGroup.CHANNEL_MANAGEMENT}
    )

    @ROLE_PERSISTENCE
    @app_commands.guild_only()
    async def role_persistence(self, interaction: discord.Interaction, enable: bool):
        """Automatically reassign roles to members who leave and rejoin

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        enable: bool
            Whether to enable role persistence
        """

        await AutomodAdminSlashes(interaction=interaction).role_persistence(enable=enable)

    @ROLEPERSISTENCE
    @app_commands.guild_only()
    async def rolepersistence(self, interaction: discord.Interaction, enable: bool):
        """Automatically reassign roles to members who leave and rejoin

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        enable: bool
            Whether to enable role persistence
        """

        await AutomodAdminSlashes(interaction=interaction).role_persistence(enable=enable)

    @AUTOROLES
    @app_commands.guild_only()
    async def autoroles(self, interaction: discord.Interaction):
        """Manage autoroles for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await AutomodAdminSlashes(interaction=interaction).autoroles()

    @AUTO_RESPONSES
    @app_commands.guild_only()
    async def auto_responses(self, interaction: discord.Interaction):
        """Manage auto-responses for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await AutomodAdminSlashes(interaction=interaction).auto_responses()

    @AUTORESPONSES
    @app_commands.guild_only()
    async def autoresponses(self, interaction: discord.Interaction):
        """Manage auto-responses for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await AutomodAdminSlashes(interaction=interaction).auto_responses()

    @GALLERY_CHANNELS
    @app_commands.guild_only()
    async def gallery_channels(self, interaction: discord.Interaction):
        """Manage gallery channels for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await AutomodAdminSlashes(interaction=interaction).gallery_channels()

    @LIMITED_MESSAGES_CHANNELS
    @app_commands.guild_only()
    async def limited_messages_channels(self, interaction: discord.Interaction):
        """Manage limited-messages channels for this server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await AutomodAdminSlashes(interaction=interaction).limited_messages_channels()
