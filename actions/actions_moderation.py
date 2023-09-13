import datetime
import discord
from actions.actions_basic import send_message
from globals_.constants import GuildLogType
from utils.helpers import convert_minutes_to_time_string
from internal.guild_logging import log_to_server
from utils.exceptions import ModerationHierarchyError


async def mute_member(member: discord.Member, duration_in_minutes: int, actor: discord.Member,
                      reason: str = "Not provided"):
    if isinstance(member, discord.User):
        try:
            member = await actor.guild.fetch_member(member.id)
        except discord.NotFound:
            raise ModerationHierarchyError("Member not found in this server")
    assert_hierarchy(actor=actor, target=member)
    await member.timeout(datetime.timedelta(minutes=duration_in_minutes),
                         reason=reason or "Not provided" + f" - Moderator: {actor}")

    log_fields = ["Reason", "Duration", "Moderator"]
    log_values = [reason or "Not provided", convert_minutes_to_time_string(duration_in_minutes), actor.mention]
    await log_to_server(guild=member.guild,
                        event_type=GuildLogType.MUTED_MEMBER,
                        member=member,
                        fields=log_fields,
                        values=log_values)


async def unmute_member(member: discord.Member, actor: discord.Member, reason: str = "Not provided"):
    if isinstance(member, discord.User):
        try:
            member = await actor.guild.fetch_member(member.id)
        except discord.NotFound:
            raise ModerationHierarchyError("Member not found in this server")
    assert_hierarchy(actor=actor, target=member)
    await member.timeout(None, reason=reason or "Not provided" + f" - Moderator: {actor}")

    log_fields = ["Reason", "Moderator"]
    log_values = [reason or "Not provided", actor.mention]
    await log_to_server(guild=member.guild,
                        event_type=GuildLogType.UNMUTED_MEMBER,
                        member=member,
                        fields=log_fields,
                        values=log_values)


async def kick_member(member: discord.Member, actor: discord.Member, reason: str = "Not provided"):
    if isinstance(member, discord.User):
        try:
            member = await actor.guild.fetch_member(member.id)
        except discord.NotFound:
            raise ModerationHierarchyError("Member not found in this server")
    assert_hierarchy(actor=actor, target=member)
    try:
        await send_message(f"You have been kicked from {member.guild.name}. Reason: {reason}", channel=member)
    except Exception:
        pass
    await member.kick(reason=reason or "Not provided" + f" - Moderator: {actor}")

    log_fields = ["Reason", "Moderator"]
    log_values = [reason or "Not provided", actor.mention]
    await log_to_server(guild=actor.guild,
                        event_type=GuildLogType.UNMUTED_MEMBER,
                        member=member,
                        fields=log_fields,
                        values=log_values)


async def ban_member(member: discord.Member, actor: discord.Member, delete_hours: int, reason: str = "Not provided"):
    if isinstance(member, discord.User):
        try:
            member = await actor.guild.fetch_member(member.id)
        except discord.NotFound:
            raise ModerationHierarchyError("Member not found in this server")
    assert_hierarchy(actor=actor, target=member)
    try:
        await send_message(f"You have been banned from {member.guild.name}. Reason: {reason}", channel=member)
    except Exception:
        pass
    await member.ban(reason=reason or "Not provided" + f" - Moderator: {actor}",
                     delete_message_seconds=delete_hours * 3600)

    log_fields = ["Reason", "Moderator"]
    log_values = [reason or "Not provided", actor.mention]
    await log_to_server(guild=actor.guild,
                        event_type=GuildLogType.BANNED_MEMBER,
                        member=member,
                        fields=log_fields,
                        values=log_values)


async def unban_member(user: discord.User, actor: discord.Member, reason: str = "Not provided"):
    try:
        await actor.guild.unban(user, reason=reason or "Not provided" + f" - Moderator: {actor}")
    except discord.NotFound:
        raise ModerationHierarchyError("User does not seem to be banned.")

    log_fields = ["Reason", "Moderator"]
    log_values = [reason or "Not provided", actor.mention]
    await log_to_server(guild=actor.guild,
                        event_type=GuildLogType.UNBANNED_MEMBER,
                        member=user,
                        fields=log_fields,
                        values=log_values)


def assert_hierarchy(actor, target):
    if not actor_can_moderate_target_member(actor, target):
        raise ModerationHierarchyError("You do not have the necessary permission or role hierarchy order to do this.")
    if not bot_can_moderate_target_member(target):
        raise ModerationHierarchyError("I do not have the necessary permission or role hierarchy order to do this.")


def bot_can_moderate_target_member(target):
    if target == target.guild.owner:
        return False
    return target.guild.me.roles[-1] > target.roles[-1]


def actor_can_moderate_target_member(actor, target):
    if not actor:
        return True
    if target == target.guild.owner:
        return False
    if actor == actor.guild.owner:
        return True
    return actor.roles[-1] > target.roles[-1]
