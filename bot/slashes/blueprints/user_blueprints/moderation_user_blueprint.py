"""
Blueprint for moderation user slash commands. All commands here expect the user to have elevated guild permissions.
"""
import discord
from discord import app_commands
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.user_slashes.moderation_user_slashes import ModerationUserSlashes
from strings.commands_strings import UserSlashCommandsStrings


class ModerationUserBlueprint(Cog):
    MUTE = app_commands.command(name="mute",
                                description=UserSlashCommandsStrings.MUTE_DESCRIPTION,
                                extras={"group": CommandGroup.MODERATION,
                                        "listing_priority": 2})
    UNMUTE = app_commands.command(name="unmute",
                                  description=UserSlashCommandsStrings.UNMUTE_DESCRIPTION,
                                  extras={"group": CommandGroup.MODERATION,
                                          "listing_priority": 3})
    KICK = app_commands.command(name="kick",
                                description=UserSlashCommandsStrings.KICK_DESCRIPTION,
                                extras={"group": CommandGroup.MODERATION,
                                        "listing_priority": 1})
    BAN = app_commands.command(name="ban",
                               description=UserSlashCommandsStrings.BAN_DESCRIPTION,
                               extras={"group": CommandGroup.MODERATION,
                                       "listing_priority": 4})
    UNBAN = app_commands.command(name="unban",
                                 description=UserSlashCommandsStrings.UNBAN_DESCRIPTION,
                                 extras={"group": CommandGroup.MODERATION,
                                         "listing_priority": 5})

    @MUTE
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def mute(self,
                   interaction: discord.Interaction,
                   member: discord.Member | discord.User,
                   duration: str = "10m",
                   reason: str = None):
        """Mute a member

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        member: discord.Member | discord.User
            Member to mute (you can enter a user ID)
        duration: str
            Mute duration (ex: 10m, 1h, 1d, 1w - default: 10m)
        reason: str
            Reason for muting the member
        """

        await ModerationUserSlashes(interaction=interaction).mute(member=member, duration=duration, reason=reason)

    @UNMUTE
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def unmute(self,
                     interaction: discord.Interaction,
                     member: discord.Member | discord.User,
                     reason: str = None):
        """Unmute a member

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        member: discord.Member | discord.User
            Member to unmute (you can enter a user ID)
        reason: str
        """

        await ModerationUserSlashes(interaction=interaction).unmute(member=member, reason=reason)

    @KICK
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self,
                   interaction: discord.Interaction,
                   member: discord.Member | discord.User,
                   reason: str = None):
        """Kick a member

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        member: discord.Member | discord.User
            Member to kick (you can enter a user ID)
        reason: str
            Reason for kicking the member
        """

        await ModerationUserSlashes(interaction=interaction).kick(member=member, reason=reason)

    @BAN
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self,
                  interaction: discord.Interaction,
                  member: discord.Member | discord.User,
                  delete_in_hours: int = 0,
                  reason: str = None):
        """Ban a member

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        member: discord.Member | discord.User
            Member to ban (you can enter a user ID)
        delete_in_hours: int
            Delete messages the member sent over the last X hours (0 = no deletion, max: 168)
        reason: str
            Reason for banning the member
        """
        await ModerationUserSlashes(interaction=interaction).ban(member=member,
                                                                 delete_in_hours=delete_in_hours,
                                                                 reason=reason)

    @UNBAN
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(self,
                    interaction: discord.Interaction,
                    user: discord.Member | discord.User,
                    reason: str = None):
        """Unban a member

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        user: discord.User
            user to unban (you can enter a user ID)
        reason: str
            Reason for unbanning the member
        """

        await ModerationUserSlashes(interaction=interaction).unban(user=user, reason=reason)
