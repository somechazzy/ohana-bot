"""
Moderation bot actions with exception handling and logging.
"""
import asyncio
import datetime
from types import coroutine

import discord

from bot.utils.bot_actions.basic_actions import send_message, add_roles
from bot.utils.embed_factory.general_embeds import get_info_embed
from bot.utils.guild_logger import GuildLogger, GuildLogEventField
from bot.utils.helpers.client_helpers import force_fetch_member
from bot.utils.helpers.moderation_helpers import assert_hierarchy
from common.app_logger import AppLogger
from common.exceptions import UserInputException
from constants import GuildLogEvent, AppLogCategory
from utils.helpers.text_manipulation_helpers import get_human_readable_time
from common.exceptions import ModerationHierarchyError

logger = AppLogger(component=__name__)


async def mute_member(member: discord.Member, duration_in_minutes: int, actor: discord.Member,
                      reason: str | None):
    """
    Mute a member in a guild for a specified duration.
    Args:
        member (discord.Member | discord.User): The member to mute.
        duration_in_minutes (int): Duration of the mute in minutes.
        actor (discord.Member): The moderator performing the mute action.
        reason (str | None): Reason for the mute action.
    Raises:
        UserInputException: If the member is not found in the guild.
        ModerationHierarchyError: If the actor or bot does not have permission to mute the target member.
    """
    if isinstance(member, discord.User):
        member = await force_fetch_member(user_id=member.id, guild=actor.guild)
    assert_hierarchy(actor=actor, target=member)
    await member.timeout(datetime.timedelta(minutes=duration_in_minutes),
                         reason=reason or "Not provided" + f" - Moderator: {actor}")

    await GuildLogger(guild=member.guild).log_event(
        event=GuildLogEvent.MUTED_MEMBER,
        actor=actor,
        member=member,
        reason=reason or "No reason provided",
        fields=[GuildLogEventField("Duration", get_human_readable_time(duration_in_minutes)),
                GuildLogEventField("Moderator", actor.mention)]
    )
    logger.info(f"Muted {member} in guild {member.guild} for {duration_in_minutes} minutes.",
                extras={"member_id": member.id, "guild_id": member.guild.id, "moderator_id": actor.id},
                category=AppLogCategory.BOT_GENERAL)


async def unmute_member(member: discord.Member, actor: discord.Member, reason: str | None):
    """
    Unmute a member in a guild.
    Args:
        member (discord.Member | discord.User): The member to unmute.
        actor (discord.Member): The moderator performing the unmute action.
        reason (str | None): Reason for the unmute action.
    Raises:
        UserInputException: If the member is not found in the guild.
        ModerationHierarchyError: If the actor or bot does not have permission to unmute the target member.
    """
    if isinstance(member, discord.User):
        member = await force_fetch_member(user_id=member.id, guild=actor.guild)
    assert_hierarchy(actor=actor, target=member)
    await member.timeout(None, reason=reason or "Not provided" + f" - Moderator: {actor}")

    await GuildLogger(guild=member.guild).log_event(
        event=GuildLogEvent.UNMUTED_MEMBER,
        actor=actor,
        member=member,
        reason=reason or "No reason provided",
        fields=[GuildLogEventField("Moderator", actor.mention)]
    )
    logger.info(f"Unmuted {member} in guild {member.guild}.",
                extras={"member_id": member.id, "guild_id": member.guild.id, "moderator_id": actor.id},
                category=AppLogCategory.BOT_GENERAL)


async def kick_member(member: discord.Member, actor: discord.Member, reason: str | None):
    """
    Kick a member from a guild.
    Args:
        member (discord.Member | discord.User): The member to kick.
        actor (discord.Member): The moderator performing the kick action.
        reason (str | None): Reason for the kick action.
    Raises:
        UserInputException: If the member is not found in the guild.
        ModerationHierarchyError: If the actor or bot does not have permission to kick the target member.
    """
    if isinstance(member, discord.User):
        member = await force_fetch_member(user_id=member.id, guild=actor.guild)
    assert_hierarchy(actor=actor, target=member)
    await send_message(channel=member,
                       content=f"You have been kicked from {member.guild.name}. Reason: {reason}",
                       raise_on_error=False)
    await member.kick(reason=reason or "Not provided" + f" - Moderator: {actor}")

    await GuildLogger(guild=member.guild).log_event(
        event=GuildLogEvent.KICKED_MEMBER,
        actor=actor,
        member=member,
        reason=reason or "No reason provided",
        fields=[GuildLogEventField("Moderator", actor.mention)]
    )
    logger.info(f"Kicked {member} from guild {member.guild}.",
                extras={"member_id": member.id, "guild_id": member.guild.id, "moderator_id": actor.id},
                category=AppLogCategory.BOT_GENERAL)


async def ban_member(member: discord.Member, actor: discord.Member, delete_in_hours: int, reason: str):
    """
    Ban a member from a guild, optionally deleting their messages from the past specified hours.
    Args:
        member (discord.Member | discord.User): The member to ban.
        actor (discord.Member): The moderator performing the ban action.
        delete_in_hours (int): Number of hours of messages to delete (0-168).
        reason (str): Reason for the ban action.
    Raises:
        ModerationHierarchyError: If the actor or bot does not have permission to ban the target member.
    """
    ban_as_user = False
    if isinstance(member, discord.User):
        try:
            member = await actor.guild.fetch_member(member.id)
        except discord.NotFound:
            ban_as_user = True

    if not ban_as_user:
        assert_hierarchy(actor=actor, target=member)
        await send_message(channel=member,
                           content=f"You have been banned from {member.guild.name}. Reason: {reason}")
        await member.ban(reason=reason or "Not provided" + f" - Moderator: {actor}",
                         delete_message_seconds=delete_in_hours * 3600)
    else:
        try:
            await actor.guild.ban(user=member, reason=reason or "Not provided" + f" - Moderator: {actor}")
        except Exception as e:
            raise ModerationHierarchyError(f"Failed to ban user: {e} "
                                           f"- this is likely due to the user not being in the server.")

    await GuildLogger(guild=actor.guild).log_event(
        event=GuildLogEvent.BANNED_MEMBER,
        actor=actor,
        member=member,
        reason=reason or "No reason provided",
        fields=[GuildLogEventField("Moderator", actor.mention)]
    )
    logger.info(f"Banned {member} in guild {member.guild} with message deletion for {delete_in_hours} hours.",
                extras={"member_id": member.id, "guild_id": member.guild.id, "moderator_id": actor.id},
                category=AppLogCategory.BOT_GENERAL)


async def unban_member(user: discord.User, actor: discord.Member, reason: str = "Not provided"):
    """
    Unban a user from a guild by their user ID.
    Args:
        user (discord.User): The user to unban.
        actor (discord.Member): The moderator performing the unban action.
        reason (str): Reason for the unban action.
    Raises:
        UserInputException: If the unban action fails.
    """
    try:
        await actor.guild.unban(user, reason=reason or "Not provided" + f" - Moderator: {actor}")
    except Exception as e:
        raise UserInputException(f"Failed to unban user: {e}")

    await GuildLogger(guild=actor.guild).log_event(
        event=GuildLogEvent.UNBANNED_MEMBER,
        actor=actor,
        member=user,
        reason=reason or "No reason provided",
        fields=[GuildLogEventField("Moderator", actor.mention)]
    )
    logger.info(f"Unbanned user {user} in guild {actor.guild}.",
                extras={"user_id": user.id, "guild_id": actor.guild.id, "moderator_id": actor.id},
                category=AppLogCategory.BOT_GENERAL)


async def scan_for_messages_and_assign_role(channel: discord.TextChannel,
                                            role: discord.Role,
                                            update_callback: coroutine):
    """
    Scan the recent message history of a channel, collect unique members who have sent messages,
    and assign them a specified role.
    This is used for initializing a "limited-messages" channel where members can send a message only once.
    The function processes up to the last 300 messages in the channel, assigns the role to
    each unique member found, and provides updates via the provided callback.
    Args:
        channel (discord.TextChannel): The channel to scan for messages.
        role (discord.Role): The role to assign to members who have sent messages.
        update_callback (coroutine): A coroutine function to call with status updates.
    """
    success_count = 0
    failed_count = 0
    members: set[discord.Member] = set()
    async for message in channel.history(limit=300):
        if message.author.bot:
            continue
        members.add(message.author)

    try:
        await update_callback(embed=get_info_embed(f"Found {len(members)} members to assign the role to."))
    except:
        pass

    for member in members:
        try:
            await add_roles(member, roles=[role], reason=f"Assigned for limited-messages in #{channel.name}.",
                            raise_without_logging=True, log_event_to_guild=False)
            success_count += 1
        except:
            failed_count += 1
        await asyncio.sleep(1)

    try:
        await update_callback(embed=get_info_embed(
            f"Role assignment completed: {success_count} members updated, {failed_count} failed.\n"
            f"Feel free to setup role permissions in {channel.mention} to prevent its members from messaging there - "
            f"or let me do the hard work and auto-delete their messages on the go."
        ))
    except:
        pass

    await GuildLogger(guild=channel.guild).log_event(
        event=GuildLogEvent.SETTING_CHANGE,
        event_message=f"Assigned {role.mention} to **{success_count} members**.\n"
                      + (f"Assignment failed for **{failed_count} members** "
                         f"(hierarchy or permission issues most likely)." if failed_count else ""),
        reason=f"Initializing {channel.mention} as a limited-messages channel."
    )
    logger.info(f"Assigned {role} to {success_count} members, {failed_count} failed in guild {channel.guild}"
                f" while initializing limited-messages channel {channel}.",
                extras={"role_id": role.id, "guild_id": channel.guild.id, "channel_id": channel.id},
                category=AppLogCategory.BOT_GENERAL)
