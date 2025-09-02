"""
Music admin slash command blueprints. All commands here are prefixed with `/manage`.
"""
import discord
from discord import app_commands
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.admin_slashes.music_admin_slashes import MusicAdminSlashes
from strings.commands_strings import AdminSlashCommandsStrings


class MusicAdminBlueprints(Cog):
    MUSIC_CREATE_CHANNEL = app_commands.command(name="music-create-channel",
                                                description=AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_DESCRIPTION,
                                                extras={"group": CommandGroup.MUSIC,
                                                        "listing_priority": 1})

    @MUSIC_CREATE_CHANNEL
    @app_commands.guild_only()
    async def music_create_channel(self, interaction: discord.Interaction):
        """Create the #ohana-player channel

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await MusicAdminSlashes(interaction=interaction).music_create_channel()
