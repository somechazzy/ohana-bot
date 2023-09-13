from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Cog

from slashes.user_slashes.moderation_user_slashes import ModerationUserSlashes


class ModerationUserBlueprints(Cog):
    MUTE = app_commands.command(name="mute",
                                description="Mute a member")
    UNMUTE = app_commands.command(name="unmute",
                                  description="Unmute a member")
    KICK = app_commands.command(name="kick",
                                description="Kick a member")
    BAN = app_commands.command(name="ban",
                               description="Ban a member")
    UNBAN = app_commands.command(name="unban",
                                 description="Unban a member")

    @MUTE
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def mute(self, inter, member: Union[discord.Member, discord.User], duration: str = "10m",
                   reason: str = None):
        """Mute a member

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: Union[discord.Member, discord.User]
            Member to mute (you can enter a user ID)
        duration: str
            Mute duration (ex: 10m, 1h, 1d, 1w - default: 10m)
        reason: str
            Reason for muting the member
        """

        await ModerationUserSlashes(interaction=inter).mute(member=member, duration=duration, reason=reason)

    @UNMUTE
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def unmute(self, inter, member: Union[discord.Member, discord.User], reason: str = None):
        """Unmute a member

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: Union[discord.Member, discord.User]
            Member to unmute (you can enter a user ID)
        reason: str
        """

        await ModerationUserSlashes(interaction=inter).unmute(member=member, reason=reason)

    @KICK
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, inter, member: Union[discord.Member, discord.User], reason: str = None):
        """Kick a member

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: Union[discord.Member, discord.User]
            Member to kick (you can enter a user ID)
        reason: str
            Reason for kicking the member
        """

        await ModerationUserSlashes(interaction=inter).kick(member=member, reason=reason)

    @BAN
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self, inter, member: Union[discord.Member, discord.User], delete_hours: int = 0, reason: str = None):
        """Ban a member

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        member: Union[discord.Member, discord.User]
            Member to ban (you can enter a user ID)
        delete_hours: int
            Delete messages the member sent over the last X hours (0 = no deletion, max: 168)
        reason: str
            Reason for banning the member
        """
        await ModerationUserSlashes(interaction=inter).ban(member=member, delete_hours=delete_hours, reason=reason)

    @UNBAN
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self, inter, user: Union[discord.Member, discord.User], reason: str = None):
        """Unban a member

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user: discord.User
            user to unban (you can enter a user ID)
        reason: str
            Reason for unbanning the member
        """

        await ModerationUserSlashes(interaction=inter).unban(user=user, reason=reason)
