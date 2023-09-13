from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Cog

from slashes.user_slashes.xp_user_slashes import XPUserSlashes


class XPUserBlueprints(Cog):
    LEVEL = app_commands.command(name="level",
                                 description="Get your current level and rank - or someone else's")
    RANK = app_commands.command(name="rank",
                                description="Get your current level and rank - or someone else's (alias for /level)",
                                extras={"is_alias": True, "alias_for": "level"})
    LEADERBOARD = app_commands.command(name="leaderboard",
                                       description="Get the server leaderboard")
    LB = app_commands.command(name="lb",
                              description="Get the server leaderboard (alias for /leaderboard)",
                              extras={"is_alias": True, "alias_for": "leaderboard"})
    LEVEL_ROLES = app_commands.command(name="level-roles",
                                       description="Show what level roles the server offers")

    @LEVEL
    @app_commands.guild_only()
    async def level(self, inter, member: Union[discord.Member, discord.User] = None):
        """Get your current level and rank - or someone else's

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: discord.Member
            Member to get the level of
        """

        await XPUserSlashes(interaction=inter).level(member=member)

    @RANK
    @app_commands.guild_only()
    async def rank(self, inter, member: Union[discord.Member, discord.User] = None):
        """Get your current level and rank - or someone else's

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: discord.Member
            Member to get the level of
        """

        await XPUserSlashes(interaction=inter).level(member=member)

    @LEADERBOARD
    @app_commands.guild_only()
    @app_commands.rename(jump_to_page="jump-to-page")
    @app_commands.rename(make_visible="make-visible")
    async def leaderboard(self, inter, jump_to_page: int = 1, make_visible: bool = True):
        """Get the server leaderboard

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        jump_to_page: int
            Jump to a specific page
        make_visible: bool
            Make the leaderboard visible to everyone
        """

        await XPUserSlashes(interaction=inter).leaderboard(jump_to_page=jump_to_page, make_visible=make_visible)

    @LB
    @app_commands.guild_only()
    @app_commands.rename(jump_to_page="jump-to-page")
    @app_commands.rename(make_visible="make-visible")
    async def lb(self, inter, jump_to_page: int = 1, make_visible: bool = True):
        """Get the server leaderboard

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        jump_to_page: int
            Jump to a specific page
        make_visible: bool
            Make the leaderboard visible to everyone
        """

        await XPUserSlashes(interaction=inter).leaderboard(jump_to_page=jump_to_page, make_visible=make_visible)

    @LEVEL_ROLES
    @app_commands.guild_only()
    async def level_roles(self, inter):
        """Show what level roles the server offers

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await XPUserSlashes(interaction=inter).level_roles()
