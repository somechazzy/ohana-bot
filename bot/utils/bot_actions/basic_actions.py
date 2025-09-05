"""
Basic discord bot actions with exception handling and logging.
"""
import discord

from common.app_logger import AppLogger
from constants import GuildLogEvent, AppLogCategory

logger = AppLogger(component=__name__)


async def send_message(
    channel: discord.abc.Messageable,
    content: str | None = None,
    embed: discord.Embed | None = None,
    file: discord.File | None = None,
    view: discord.ui.View | None = None,
    reply_to: discord.Message | None = None,
    delete_after: float | None = None,
    raise_on_error: bool = True,
    log_action: bool = False
):
    """
    Wrapper for sending messages to a Discord channel or user. Use cases include exception handling and logging
    Args:
        channel (discord.abc.Messageable): The channel or user to send the message to.
        content (str | None): The content of the message. Defaults to None.
        embed (discord.Embed | None): The embed to send. Defaults to None.
        file (discord.File | None): The file to send. Defaults to None.
        view (discord.ui.View | None): The view to send. Defaults to None.
        reply_to (discord.Message | None): The message to reply to. Defaults to None.
        delete_after (float | None): The time in seconds to delete the message after sending. Defaults to None.
        raise_on_error (bool): Whether to raise an exception on error. Defaults to True.
        log_action (bool): Whether to log the action. Defaults to False.
    Raises:
        discord.Forbidden: If the bot does not have the necessary permissions and raise_on_error is True.
        Exception: If any other exception occurs and raise_on_error is True.
    """
    if isinstance(channel, (discord.User, discord.Member)):
        try:
            channel = channel.dm_channel or await channel.create_dm()  # type: ignore
        except discord.Forbidden as e:
            if raise_on_error:
                raise e
            if log_action:
                logger.info(f"Failed to create DM channel with {channel}. Locals: {locals()}",
                            extras={'guild_id': channel.guild.id, 'user_id': channel.id},
                            category=AppLogCategory.BOT_GENERAL)
            return
    guild_id = channel.guild.id if getattr(channel, 'guild', None) else None
    try:
        await channel.send(
            content=content,
            embed=embed,
            file=file,
            view=view,
            reference=reply_to,
            delete_after=delete_after
        )
    except Exception as e:
        if raise_on_error:
            raise e
        if log_action:
            logger.info(f"Failed to send message to {channel}: {e}. Locals: {locals()}",
                        extras={'guild_id': guild_id, 'channel_id': channel.id},
                        category=AppLogCategory.BOT_GENERAL)
            return
    if log_action:
        logger.info(f"Sent message to #{channel}.",
                    extras={'guild_id': guild_id, 'channel_id': channel.id},
                    category=AppLogCategory.BOT_MESSAGE_SENT)


async def delete_message(message: discord.Message, reason: str = "Not specified.") -> bool:
    """
    Wrapper for deleting a message in Discord. Use cases include exception handling and logging
    Args:
        message (discord.Message): The message to delete.
        reason (str | None): The reason for deleting the message. Defaults to "Not specified".
    Returns:
        bool: True if the message was deleted successfully, False otherwise.
    """
    from bot.utils.guild_logger import GuildLogger
    from bot.utils.guild_logger import GuildLogEventField
    try:
        await message.delete()
    except Exception as e:
        if isinstance(e, discord.Forbidden):
            failure_reason = "no permissions to delete the message."
        else:
            failure_reason = f"internal error."
        await GuildLogger(guild=message.guild).log_event(event=GuildLogEvent.ACTION_ERROR,
                                                         event_message=f"Failed to delete [message]({message.jump_url})"
                                                                       f" due to: {failure_reason}.\n"
                                                                       f"Original deletion reason: {reason}")
        return False

    await GuildLogger(guild=message.guild).log_event(event=GuildLogEvent.DELETED_MESSAGE,
                                                     message=message,
                                                     reason=reason,
                                                     fields=[
                                                         GuildLogEventField(name="Content",
                                                                            value=message.content[:1024] or "None")
                                                     ])
    logger.info(f"Deleted message {message.id} in guild {message.guild.name}. Reason: {reason}.",
                extras={'guild_id': message.guild.id, 'user_id': message.author.id, 'message_id': message.id},
                category=AppLogCategory.BOT_MESSAGE_DELETED)
    return True


async def add_roles(member: discord.Member, roles: list[discord.Role], reason: str = "Not specified.",
                    raise_without_logging: bool = False, log_event_to_guild: bool = True) -> bool:
    """
    Wrapper for adding a role to a member in Discord. Use cases include exception handling and logging
    Args:
        member (discord.Member): The member to add the role to.
        roles (list[discord.Role]): The roles to add to the member.
        reason (str | None): The reason for adding the role. Defaults to "Not specified".
        raise_without_logging (bool): Whether to raise instead of logging on error. Defaults to False.
        log_event_to_guild (bool): Whether to log the event to the guild. Defaults to True.
    Returns:
        bool: True if the role was added successfully, False otherwise.
    Raises:
        discord.Forbidden: If the bot does not have the necessary permissions and raise_without_logging is True.
        Exception: If any other exception occurs and raise_without_logging is True.
    """
    from bot.utils.guild_logger import GuildLogger
    try:
        await member.add_roles(*roles, reason=reason)
    except Exception as e:
        if raise_without_logging:
            raise e
        if isinstance(e, discord.Forbidden):
            failure_reason = "no permissions to add the roles."
        else:
            logger.warning(f"Failed to add roles {', '.join(str(role.id) for role in roles)} to "
                           f"{member.display_name} in guild {member.guild.name} due to: {e}. Locals: {locals()}",
                           extras={'guild_id': member.guild.id, 'user_id': member.id,
                                   'role_ids': [role.id for role in roles]},
                           category=AppLogCategory.BOT_GENERAL)
            failure_reason = f"internal error."
        if log_event_to_guild:
            await GuildLogger(guild=member.guild).log_event(
                event=GuildLogEvent.ACTION_ERROR,
                event_message=f"Failed to add roles ({', '.join(role.mention for role in roles)}) to "
                              f"{member.mention} due to: {failure_reason}.\n"
                              f"Original addition reason: {reason}"
            )
        return False

    if log_event_to_guild:
        await GuildLogger(guild=member.guild).log_event(event=GuildLogEvent.ASSIGNED_ROLES,
                                                        member=member,
                                                        roles=roles,
                                                        reason=reason)
    logger.info(f"Added {len(roles)} roles to {member.display_name} in guild {member.guild.name}",
                extras={'guild_id': member.guild.id, 'user_id': member.id, 'role_ids': [role.id for role in roles]},
                category=AppLogCategory.BOT_GENERAL)
    return True
