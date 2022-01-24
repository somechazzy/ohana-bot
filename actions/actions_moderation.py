import disnake as discord
import helpers
from actions.actions_basic import send_dm, send_embed
from internal.bot_logging import log, log_to_server
from globals_ import constants


async def mute_member(member: discord.Member, guild: discord.Guild, time_in_minutes, send_on_channel=False,
                      channel=None, reason="Not provided", moderator=None):
    if not guild.me.guild_permissions.moderate_members or not helpers.bot_can_moderate_target_member(member):
        if send_on_channel and channel is not None:
            await send_embed(f"I do not have the necessary permission or role"
                             f" hierarchy position to mute/timeout this person.",
                             channel, emoji='❌', color=0xFF522D)
        return
    if guild.me.top_role <= member.top_role:
        if send_on_channel and channel is not None:
            await send_embed(f"The user is on equal level or higher than my highest role.",
                             channel, emoji='❌', color=0xFF522D)
        return
    time_string = helpers.convert_minutes_to_time_string(time_in_minutes)
    await member.timeout(duration=time_in_minutes * 60.0, reason=reason)
    if send_on_channel and channel is not None:
        await send_embed(f"{member} is now on timeout for {time_string}.", channel, emoji='✅', color=0x0AAC00)
        await log(f"User {member} with ID \"{member.id}\" timed-out for {time_in_minutes} minutes. Reason:"
                  f" \"{reason}\". Guild: {guild.name}",
                  level=constants.BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False,
                  guild_id=member.guild.id)

        fields = ["Moderator"] if moderator is not None else []
        values = [str(moderator)] if moderator is not None else []
        await log_to_server(member.guild, constants.GuildLogType.MUTED_MEMBER, member=member,
                            fields=["Reason", "Duration"] + fields,
                            values=[reason, time_string] + values)


async def unmute_member(member, guild, send_on_channel=False, channel=None, reason="None", moderator=None):
    if not guild.me.guild_permissions.moderate_members or not helpers.bot_can_moderate_target_member(member):
        if send_on_channel and channel is not None:
            await send_embed(f"I do not have the necessary permission or role"
                             f" hierarchy position to unmute/un-timeout this person.",
                             channel, emoji='❌', color=0xFF522D)
        return
    if guild.me.top_role <= member.top_role:
        if send_on_channel and channel is not None:
            await send_embed(f"The user is on equal level or higher than my highest role.",
                             channel, emoji='❌', color=0xFF522D)
        return
    await member.timeout(duration=None, reason=reason)
    if send_on_channel and channel is not None:
        await send_embed(f"{member}'s timeout has been lifted.", channel, emoji='✅', color=0x0AAC00)
    await log(f"User {member} with ID \"{str(member.id)}\" has been un-timed-out. Reason:"
              f" \"{reason}\". Guild: {guild.name}",
              level=constants.BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False, guild_id=member.guild.id)
    fields = ["Moderator"] if moderator is not None else []
    values = [str(moderator)] if moderator is not None else []
    await log_to_server(member.guild, constants.GuildLogType.UNMUTED_MEMBER,
                        member=member, fields=fields, values=values)


async def kick_member(member, guild, dm_user=True, reason="not provided", moderator=None):
    if not guild.me.guild_permissions.kick_members or not helpers.bot_can_moderate_target_member(member):
        return
    if dm_user:
        try:
            await send_dm(f"You have been kicked from {guild.name}. Reason: {reason}", member)
        except:
            pass
    try:
        await member.kick(reason=reason)
        fields = ["Moderator"] if moderator is not None else []
        values = [str(moderator)] if moderator is not None else []
        await log_to_server(member.guild, constants.GuildLogType.KICKED_MEMBER, member=member,
                            fields=["Reason"] + fields,
                            values=[reason] + values)
    except:
        pass
    await log(f"User {member} with ID \"{str(member.id)}\" has been kicked. Reason: \"{reason}\". Guild: {guild.name}",
              level=constants.BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False, guild_id=member.guild.id)


async def ban_member(member, guild, delete_messages=False, dm_user=True, reason="not provided", moderator=None):
    if not guild.me.guild_permissions.ban_members or not helpers.bot_can_moderate_target_member(member):
        return
    if dm_user:
        try:
            await send_dm(f"You have been banned from {guild.name}. Reason: {reason}", member)
        except:
            pass
    try:
        await member.ban(reason=reason, delete_message_days=(1 if delete_messages else 0))
        fields = ["Moderator"] if moderator is not None else []
        values = [str(moderator)] if moderator is not None else []
        await log_to_server(member.guild, constants.GuildLogType.BANNED_MEMBER, member=member,
                            fields=["Reason"] + fields,
                            values=[reason] + values)
        await log(f"User {member} with ID \"{str(member.id)}\" has been banned."
                  f" Reason: \"{reason}\". Guild: {guild.name}",
                  level=constants.BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False,
                  guild_id=guild.id)
    except:
        pass
