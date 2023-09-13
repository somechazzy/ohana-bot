import discord

from actions import mute_member, unmute_member, kick_member, ban_member, unban_member
from utils.embed_factory import quick_embed
from globals_.constants import Colour
from utils.helpers import get_duration_in_minutes_from_text, convert_minutes_to_time_string
from utils.exceptions import ModerationHierarchyError
from utils.decorators import slash_command
from slashes.user_slashes.base_user_slashes import UserSlashes


class ModerationUserSlashes(UserSlashes):

    @slash_command
    async def mute(self, member: discord.Member, duration: str = "10m", reason: str = None):
        """
        /mute
        Mute a member
        """

        if not await self.preprocess_and_validate():
            return

        duration_in_minutes = get_duration_in_minutes_from_text(duration)
        if not duration_in_minutes:
            await self.interaction.response.send_message(embed=quick_embed("Invalid duration. Example: \n"
                                                                           "• **1d 12h** means 1 day and 12 hours\n"
                                                                           "• **1h 30m** means 1 hour and 30 minutes",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return
        if duration_in_minutes > 28 * 24 * 60:
            await self.interaction.response.send_message(embed=quick_embed("Maximum duration is 28 days",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.defer(thinking=True)

        try:
            await mute_member(member=member, duration_in_minutes=duration_in_minutes, reason=reason, actor=self.member)
        except ModerationHierarchyError as e:
            await self.interaction.followup.send(embed=quick_embed(str(e),
                                                                   emoji='',
                                                                   color=Colour.ERROR,
                                                                   bold=False),
                                                 ephemeral=True)

        await self.interaction.followup.send(
            embed=quick_embed(f"{member.mention} has been muted for "
                              f"{convert_minutes_to_time_string(duration_in_minutes)}",
                              emoji='',
                              color=Colour.SUCCESS,
                              bold=False),
            ephemeral=self.send_as_ephemeral())

    @slash_command
    async def unmute(self, member: discord.Member, reason: str = None):
        """
        /unmute
        Unmute a member
        """

        if not await self.preprocess_and_validate():
            return

        if not member.timed_out_until:
            await self.interaction.response.send_message(embed=quick_embed(f"{member.mention} is not muted",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.defer(thinking=True)

        try:
            await unmute_member(member=member, reason=reason, actor=self.member)
        except ModerationHierarchyError as e:
            await self.interaction.followup.send(embed=quick_embed(str(e),
                                                                   emoji='',
                                                                   color=Colour.ERROR,
                                                                   bold=False),
                                                 ephemeral=True)
            return

        await self.interaction.followup.send(embed=quick_embed(f"{member.mention} has been unmuted",
                                                               emoji='',
                                                               color=Colour.SUCCESS,
                                                               bold=False),
                                             ephemeral=self.send_as_ephemeral())

    @slash_command
    async def kick(self, member: discord.Member, reason: str = None):
        """
        /kick
        Kick a member
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.defer(thinking=True)

        try:
            await kick_member(member=member, reason=reason, actor=self.member)
        except ModerationHierarchyError as e:
            await self.interaction.followup.send(embed=quick_embed(str(e),
                                                                   emoji='',
                                                                   color=Colour.ERROR,
                                                                   bold=False),
                                                 ephemeral=True)
            return

        await self.interaction.followup.send(embed=quick_embed(f"{member.mention} has been kicked",
                                                               emoji='',
                                                               color=Colour.SUCCESS,
                                                               bold=False),
                                             ephemeral=self.send_as_ephemeral())

    @slash_command
    async def ban(self, member: discord.Member, delete_hours: int = 0, reason: str = None):
        """
        /ban
        Ban a member
        """

        if not await self.preprocess_and_validate():
            return

        delete_hours = 7 * 24 if delete_hours > 7 * 24 else delete_hours

        await self.interaction.response.defer(thinking=True)

        try:
            await ban_member(member=member, delete_hours=delete_hours, reason=reason, actor=self.member)
        except ModerationHierarchyError as e:
            await self.interaction.followup.send(embed=quick_embed(str(e),
                                                                   emoji='',
                                                                   color=Colour.ERROR,
                                                                   bold=False),
                                                 ephemeral=True)
            return

        await self.interaction.followup.send(embed=quick_embed(f"{member.mention} has been banned",
                                                               emoji='',
                                                               color=Colour.SUCCESS,
                                                               bold=False),
                                             ephemeral=self.send_as_ephemeral())

    @slash_command
    async def unban(self, user: discord.User, reason: str = None):
        """
        /unban
        Unban a member
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.defer(thinking=True)

        try:
            await unban_member(user=user, reason=reason, actor=self.member)
        except ModerationHierarchyError as e:
            await self.interaction.followup.send(embed=quick_embed(str(e),
                                                                   emoji='',
                                                                   color=Colour.ERROR,
                                                                   bold=False),
                                                 ephemeral=True)
            return

        await self.interaction.followup.send(embed=quick_embed(f"{user.mention} has been unbanned",
                                                               emoji='',
                                                               color=Colour.SUCCESS,
                                                               bold=False),
                                             ephemeral=self.send_as_ephemeral())
