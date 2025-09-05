"""
Blueprint for general user slash commands that don't belong to a particular category.
"""
import discord
from discord import app_commands
from discord.app_commands import allowed_installs, allowed_contexts
from discord.ext.commands import Cog

from constants import CommandGroup, CommandCategory
from bot.slashes.user_slashes.general_user_slashes import GeneralUserSlashes
from strings.commands_strings import UserSlashCommandsStrings


class GeneralUserBlueprint(Cog):
    USER_SETTINGS = app_commands.command(name="user-settings",
                                         description=UserSlashCommandsStrings.USER_SETTINGS_DESCRIPTION,
                                         extras={"group": CommandGroup.GENERAL,
                                                 "listing_priority": 1,
                                                 "aliases": ["usersettings"]})
    USERSETTINGS = app_commands.command(name="usersettings",
                                        description=UserSlashCommandsStrings.USER_SETTINGS_DESCRIPTION,
                                        extras={"is_alias": True,
                                                "alias_for": "user-settings",
                                                "group": CommandGroup.GENERAL,
                                                "listing_priority": 1})
    FEEDBACK = app_commands.command(name="feedback",
                                    description=UserSlashCommandsStrings.FEEDBACK_DESCRIPTION,
                                    extras={"unlisted": True,
                                            "group": CommandGroup.GENERAL})
    HELP = app_commands.command(name="help",
                                description=UserSlashCommandsStrings.HELP_DESCRIPTION,
                                extras={"unlisted": True,
                                        "group": CommandGroup.GENERAL})
    MUSIC_FIX = app_commands.command(name="music-fix",
                                     description=UserSlashCommandsStrings.MUSIC_FIX_DESCRIPTION,
                                     extras={"group": CommandGroup.GENERAL,
                                             "listing_priority": 2,
                                             "aliases": ["musicfix"]})
    MUSICFIX = app_commands.command(name="musicfix",
                                    description=UserSlashCommandsStrings.MUSIC_FIX_DESCRIPTION,
                                    extras={"is_alias": True,
                                            "alias_for": "music-fix",
                                            "group": CommandGroup.GENERAL,
                                            "listing_priority": 2})

    @USER_SETTINGS
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def user_settings(self, interaction: discord.Interaction):
        """Manage your settings on Ohana

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await GeneralUserSlashes(interaction=interaction).manage_user_settings()

    @USERSETTINGS
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def usersettings(self, interaction: discord.Interaction):
        """Manage your settings on Ohana

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await GeneralUserSlashes(interaction=interaction).manage_user_settings()

    @FEEDBACK
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def feedback(self, interaction: discord.Interaction, feedback: str):
        """Send feedback to the bot owner

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        feedback: str
            Feedback to send
        """

        await GeneralUserSlashes(interaction=interaction).feedback(feedback=feedback)

    @HELP
    @app_commands.rename(make_visible="make-visible")
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def help(self, 
                   interaction: discord.Interaction, 
                   menu: CommandCategory.values_as_enum() = None,
                   make_visible: bool = False):
        """Show the help menu

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        menu: CommandCategory.values_as_enum()
           Jump to a specific menu
        make_visible: bool
            Make the menu visible to everyone (can be spammy...)
        """
        await GeneralUserSlashes(interaction=interaction).help(menu=menu, make_visible=make_visible)

    @MUSIC_FIX
    @allowed_installs(users=False, guilds=True)
    @allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def music_fix(self, interaction: discord.Interaction):
        """Fix Ohana player/radio by force resetting everything.

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """
        await GeneralUserSlashes(interaction=interaction).music_fix()

    @MUSICFIX
    @allowed_installs(users=False, guilds=True)
    @allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def musicfix(self, interaction: discord.Interaction):
        """Fix Ohana player/radio by force resetting everything.

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """
        await GeneralUserSlashes(interaction=interaction).music_fix()
