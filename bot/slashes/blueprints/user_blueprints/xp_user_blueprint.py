"""
Blueprint for XP user slash commands.
"""
import discord
from discord import app_commands
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.user_slashes.xp_user_slashes import XPUserSlashes
from strings.commands_strings import UserSlashCommandsStrings


class XPUserBlueprint(Cog):
    LEVEL = app_commands.command(name="level",
                                 description=UserSlashCommandsStrings.LEVEL_DESCRIPTION,
                                 extras={"group": CommandGroup.XP,
                                         "listing_priority": 1,
                                         "aliases": ["rank"]})
    RANK = app_commands.command(name="rank",
                                description=UserSlashCommandsStrings.LEVEL_DESCRIPTION,
                                extras={"is_alias": True,
                                        "alias_for": "level",
                                        "group": CommandGroup.XP})
    LEADERBOARD = app_commands.command(name='leaderboard',
                                       description=UserSlashCommandsStrings.LEADERBOARD_DESCRIPTION,
                                       extras={"group": CommandGroup.XP,
                                               "listing_priority": 2,
                                               "aliases": ["lb"]})
    LB = app_commands.command(name="lb",
                              description=UserSlashCommandsStrings.LEADERBOARD_DESCRIPTION,
                              extras={"is_alias": True,
                                      "alias_for": "leaderboard",
                                      "group": CommandGroup.XP})
    LEVEL_ROLES = app_commands.command(name="level-roles",
                                       description=UserSlashCommandsStrings.LEVEL_ROLES_DESCRIPTION,
                                       extras={"group": CommandGroup.XP,
                                               "listing_priority": 3,
                                               "aliases": ["levelroles"]})
    LEVELROLES = app_commands.command(name="levelroles",
                                      description=UserSlashCommandsStrings.LEVEL_ROLES_DESCRIPTION,
                                      extras={"is_alias": True,
                                              "alias_for": "level-roles",
                                              "group": CommandGroup.XP,
                                              "listing_priority": 3})

    @LEVEL
    @app_commands.guild_only()
    async def level(self,
                    interaction: discord.Interaction,
                    member: discord.Member | discord.User = None):
        """Get your current level and rank - or someone else's

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        member: discord.Member
            Member to get the level of
        """

        await XPUserSlashes(interaction=interaction).level(member=member)

    @RANK
    @app_commands.guild_only()
    async def rank(self,
                   interaction: discord.Interaction,
                   member: discord.Member | discord.User = None):
        """Get your current level and rank - or someone else's (alias for /level)

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        member: discord.Member
            Member to get the level of
        """
        await XPUserSlashes(interaction=interaction).level(member=member)

    @LEADERBOARD
    @app_commands.guild_only()
    @app_commands.rename(jump_to_page="jump-to-page")
    @app_commands.rename(show_decays="show-decays")
    @app_commands.rename(make_visible="make-visible")
    async def leaderboard(self,
                          interaction: discord.Interaction,
                          jump_to_page: int = 1,
                          show_decays: bool = False,
                          make_visible: bool = True):
        """Get the server XP leaderboard

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        jump_to_page: int
            Page to jump to in the leaderboard
        show_decays: bool
            Whether to show decayed XP of each member
        make_visible: bool
            Whether to make the leaderboard visible to everyone or not
        """
        await XPUserSlashes(interaction=interaction).leaderboard(jump_to_page=jump_to_page,
                                                                 show_decays=show_decays,
                                                                 make_visible=make_visible)

    @LB
    @app_commands.guild_only()
    @app_commands.rename(jump_to_page="jump-to-page")
    @app_commands.rename(show_decays="show-decays")
    @app_commands.rename(make_visible="make-visible")
    async def lb(self,
                 interaction: discord.Interaction,
                 jump_to_page: int = 1,
                 show_decays: bool = False,
                 make_visible: bool = True):
        """Get the server XP leaderboard (alias for /leaderboard)

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        jump_to_page: int
            Page to jump to in the leaderboard
        show_decays: bool
            Whether to show decayed XP of each member
        make_visible: bool
            Whether to make the leaderboard visible to everyone or not
        """
        await XPUserSlashes(interaction=interaction).leaderboard(jump_to_page=jump_to_page,
                                                                 show_decays=show_decays,
                                                                 make_visible=make_visible)

    @LEVEL_ROLES
    @app_commands.guild_only()
    async def level_roles(self, interaction: discord.Interaction):
        """Show what level roles the server offers

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        """
        await XPUserSlashes(interaction=interaction).level_roles()

    @LEVELROLES
    @app_commands.guild_only()
    async def levelroles(self, interaction: discord.Interaction):
        """Show what level roles the server offers

        Parameters
        -----------
        interaction: Interaction
            Interaction to handle
        """
        await XPUserSlashes(interaction=interaction).level_roles()
