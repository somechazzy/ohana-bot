from typing import Iterable

import discord
from discord.abc import Snowflake
from discord.types.embed import EmbedField

from bot.utils.bot_actions.basic_actions import send_message
from bot.utils.embed_factory.log_embeds import get_guild_log_embed
from clients import discord_client
from common.app_logger import AppLogger
from common.decorators import suppress_and_log
from constants import GuildLogEvent, Colour


class GuildLogger:
    """
    A class to handle logging for guild-related events to the guild's logging channel.
    """
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.logger = AppLogger(component=self.__class__.__name__)

    @suppress_and_log()
    async def log_event(self,
                        event: str,  # GuildLogEvent
                        event_message: str | None = None,
                        reason: str | None = None,
                        actor: discord.Member | None = None,
                        member: discord.Member | discord.User | Snowflake | None = None,
                        channel: discord.TextChannel | None = None,
                        roles: list[discord.Role] | None = None,
                        roles_deltas: tuple[Iterable[discord.Role], Iterable[discord.Role]] | None = None,
                        message: discord.Message | None = None,
                        fields: list['GuildLogEventField'] | None = None) -> None:
        """
        Logs an event to the guild's log channel.
        Args:
            event (str): event type, one of GuildLogEvent values
            event_message (str | None): a message describing the event (usually for GENERAL and SETTING_CHANGE).
            reason (str | None): reason for the action if done by the bot or a moderator.
            actor (discord.Member | None): The member who triggered the event, if any.
            member (discord.Member | discord.User | None): The member affected by the event, if any.
            channel (discord.TextChannel | None): The channel related to the event occurred, if applicable.
            roles (list[discord.Role] | None): The roles involved in the event, if any.
            roles_deltas (tuple(Iterable[discord.Role], Iterable[discord.Role]) | None):
                A tuple of role lists, first containing added roles and second containing removed roles.
                This is primarily meant for the EDITED_ROLES event.
            message (discord.Message | None): The message related to the event, if applicable.
            fields (list[GuildLogEventField] | None): Additional fields to include in the log message.
        Returns:
            None
        """
        from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
        logging_channel_id = (await GuildSettingsComponent().
                              get_guild_settings(guild_id=self.guild.id)).logging_channel_id
        if not logging_channel_id:
            return
        logging_channel = discord_client.get_partial_messageable(logging_channel_id,
                                                                 guild_id=self.guild.id,
                                                                 type=discord.ChannelType.text)
        fields = fields or []
        if reason:
            fields.append(GuildLogEventField(name="Reason", value=reason))

        match event:
            case GuildLogEvent.GENERAL:
                author = member or self.guild.me
                embed_color = Colour.NEUTRAL
                debug_info = f"User ID: {member.id}" if member else None
            case GuildLogEvent.SETTING_CHANGE:
                author = actor or self.guild.me
                embed_color = Colour.NOTICE_ME
                debug_info = f"User ID: {actor.id}" if actor else None
            case GuildLogEvent.ASSIGNED_ROLES:
                author = member
                embed_color = Colour.NOTICE_ME
                debug_info = f"User ID: {member.id}" if member else None
                event_message = (f"{member.mention} was added to the role(s): "
                                 f"{', '.join(role.mention for role in roles)}")
            case GuildLogEvent.UNASSIGNED_ROLES:
                author = member
                embed_color = Colour.NOTICE_ME
                debug_info = f"User ID: {member.id}" if member else None
                event_message = (f"{member.mention} was removed from the role(s): "
                                 f"{', '.join(role.mention for role in roles)}")
            case GuildLogEvent.EDITED_ROLES:
                author = actor or self.guild.me
                embed_color = Colour.NOTICE_ME
                debug_info = f"User ID: {actor.id}" if actor else None
                event_message = f"• {member.mention} was given the following role(s): \n" \
                                f"{', '.join(role.mention for role in roles_deltas[0]) or 'none'}\n" \
                                f"• and removed from the following role(s): \n" \
                                f"{', '.join(role.mention for role in roles_deltas[1]) or 'none'}"
            case GuildLogEvent.MUTED_MEMBER:
                author = actor or self.guild.me
                embed_color = Colour.UNFORTUNATE
                debug_info = f"User ID: {member.id}"
                event_message = f"{member.mention} was muted by {author.mention}."
            case GuildLogEvent.UNMUTED_MEMBER:
                author = actor or self.guild.me
                embed_color = Colour.SUCCESS
                debug_info = f"User ID: {member.id}"
                event_message = f"{member.mention} was unmuted by {author.mention}."
            case GuildLogEvent.KICKED_MEMBER:
                author = member
                embed_color = Colour.WARNING
                debug_info = f"User ID: {member.id}"
                event_message = f"{member.mention} was kicked from the server by {actor.mention}."
            case GuildLogEvent.BANNED_MEMBER:
                author = member
                embed_color = Colour.ERROR
                debug_info = f"User ID: {member.id}"
                event_message = f"{member.mention} was banned from the server by {actor.mention}."
            case GuildLogEvent.UNBANNED_MEMBER:
                author = actor
                embed_color = Colour.SUCCESS
                debug_info = f"User ID: {member.id}"
                event_message = f"{member.id} was unbanned from the server by {actor.mention}."
            case GuildLogEvent.CREATED_ROLE:
                author = actor or self.guild.me
                embed_color = Colour.SUCCESS
                debug_info = f"Role ID: {roles[0].id}"
                event_message = f"Role {roles[0].mention} was created by {author.mention}."
            case GuildLogEvent.CREATED_CHANNEL:
                author = actor or self.guild.me
                embed_color = Colour.SUCCESS
                debug_info = f"Channel ID: {channel.id}"
                event_message = f"Channel {channel.mention} was created by {author.mention}."
            case GuildLogEvent.DELETED_MESSAGE:
                author = message.author
                embed_color = Colour.WARNING
                debug_info = f"Message ID: {message.id}"
                event_message = f"Message by {author.mention} in {message.channel.mention} was deleted."
            case GuildLogEvent.SENT_MESSAGE:
                author = message.author
                embed_color = Colour.NEUTRAL
                debug_info = f"Message ID: {message.id}"
                event_message = f"Message by {author.mention} in {message.channel.mention} was sent."
            case GuildLogEvent.PERM_ERROR | GuildLogEvent.ACTION_ERROR:
                author = self.guild.me
                embed_color = Colour.ERROR
                debug_info = None
            case _:
                if event.startswith("CUSTOM_"):
                    event = event.removeprefix("CUSTOM_")
                    author = member or actor or self.guild.me
                    embed_color = Colour.NEUTRAL
                    debug_info = f"ID: {author.id}" if author else None
                else:
                    self.logger.error(f"Unhandled event type: {event} in guild logger, locals: {locals()}")
                    return

        try:
            await send_message(
                channel=logging_channel,
                embed=get_guild_log_embed(guild=self.guild,
                                          author=author,
                                          event=event,
                                          event_message=event_message,
                                          footer_text=debug_info,
                                          color=embed_color,
                                          event_fields=fields)
            )
        except Exception as e:
            self.logger.warning(f"Failed to log event {event} in guild {self.guild.id}: {e}",
                                extras={"guild_id": self.guild.id})
            return


class GuildLogEventField:  # small DTO for constructing log messages
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def as_embed_field(self):
        return EmbedField(name=self.name, value=self.value, inline=False)
