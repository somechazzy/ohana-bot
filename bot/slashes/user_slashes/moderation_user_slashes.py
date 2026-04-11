from datetime import datetime, UTC, timedelta

import discord

from bot.slashes.user_slashes import UserSlashes
from bot.utils.embed_factory.general_embeds import get_success_embed
from bot.utils.bot_actions.moderation_actions import mute_member, unmute_member, kick_member, ban_member, unban_member

from bot.utils.decorators import slash_command
from common.exceptions import UserInputException
from constants import DiscordTimestamp
from strings.commands_strings import UserSlashCommandsStrings
from utils.helpers.text_parsing_helpers import get_future_time_from_user_text


class ModerationUserSlashes(UserSlashes):

    @slash_command(guild_only=True,
                   bot_permissions=["moderate_members"],
                   user_permissions=["moderate_members"])
    async def mute(self, member: discord.Member, duration: str, reason: str | None):
        """
        /mute
        Mute a member
        """
        target_time = get_future_time_from_user_text(duration)
        if not target_time:
            raise UserInputException(UserSlashCommandsStrings.INVALID_DURATION_ERROR_MESSAGE)
        if target_time > datetime.now(UTC) + timedelta(weeks=4):
            raise UserInputException(UserSlashCommandsStrings.MUTE_DURATION_INVALID_ERROR_MESSAGE)

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        await mute_member(member=member,
                          mute_expiry=target_time,
                          actor=self.member,
                          reason=reason)

        await self.interaction.followup.send(
            embed=get_success_embed(UserSlashCommandsStrings.MUTE_SUCCESS_FEEDBACK.format(
                member=member.mention,
                date_and_time=DiscordTimestamp.LONG_DATE_TIME.format(timestamp=int(target_time.timestamp())),
                relative_time=DiscordTimestamp.RELATIVE_TIME.format(timestamp=int(target_time.timestamp()))
            )),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command(guild_only=True,
                   bot_permissions=["moderate_members"],
                   user_permissions=["moderate_members"])
    async def unmute(self, member: discord.Member, reason: str | None):
        """
        /unmute
        Unmute a member
        """
        if not member.is_timed_out():
            raise UserInputException(
                UserSlashCommandsStrings.UNMUTE_NON_MUTED_ERROR_MESSAGE.format(member=member.mention)
            )

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        await unmute_member(member=member, actor=self.member, reason=reason)

        await self.interaction.followup.send(
            embed=get_success_embed(UserSlashCommandsStrings.UNMUTE_SUCCESS_FEEDBACK.format(member=member.mention)),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command(guild_only=True,
                   bot_permissions=["kick_members"],
                   user_permissions=["kick_members"])
    async def kick(self, member: discord.Member, reason: str | None):
        """
        /kick
        Kick a member from the server
        """
        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        await kick_member(member=member, actor=self.member, reason=reason)

        await self.interaction.followup.send(
            embed=get_success_embed(UserSlashCommandsStrings.KICK_SUCCESS_FEEDBACK.format(member=member.mention)),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command(guild_only=True,
                   bot_permissions=["ban_members"],
                   user_permissions=["ban_members"])
    async def ban(self, member: discord.Member, delete_in_hours: int | None, reason: str | None):
        """
        /ban
        Ban a member from the server
        """
        if delete_in_hours and delete_in_hours < 0 or delete_in_hours > 24:
            raise UserInputException(UserSlashCommandsStrings.BAN_DELETE_DURATION_INVALID_ERROR_MESSAGE)

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        await ban_member(member=member, actor=self.member, delete_in_hours=delete_in_hours or 0, reason=reason)

        await self.interaction.followup.send(
            embed=get_success_embed(UserSlashCommandsStrings.BAN_SUCCESS_FEEDBACK.format(member=member.mention)),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command(guild_only=True,
                   bot_permissions=["ban_members"],
                   user_permissions=["ban_members"])
    async def unban(self, user: discord.User, reason: str | None):
        """
        /unban
        Unban a user from the server
        """

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        await unban_member(user=user, actor=self.member, reason=reason)

        await self.interaction.followup.send(
            embed=get_success_embed(UserSlashCommandsStrings.UNBAN_SUCCESS_FEEDBACK.format(user=user.display_name,
                                                                                           user_id=user.id)),
            ephemeral=self.send_as_ephemeral()
        )
