from datetime import datetime
from auto_moderation.auto_moderator import assign_autoroles
from auto_moderation.role_management import reinstate_roles_for, save_roles_for
from internal.bot_logging import log_to_server
from globals_.clients import discord_client
from globals_ import constants
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
import disnake as discord


@discord_client.event
async def on_member_join(member):
    # leave as True to send member join messages to servers' logs channels
    # honestly there's no need for this but I'm just leaving the code for whoever wants to use it
    if True:
        await log_to_server(member.guild, constants.GuildLogType.MEMBER_JOINED, member=member,
                            fields=["Account Info"],
                            values=[f"**Created:** {member.created_at.date()} {member.created_at.time().hour}:"
                                    f"{member.created_at.time().minute} GMT"])
    if "MEMBER_VERIFICATION_GATE_ENABLED" not in member.guild.features or not member.pending:
        reinstated = False
        if (await GuildPrefsComponent().get_guild_prefs(member.guild)).role_persistence_enabled:
            reinstated = await reinstate_roles_for(member)
        if not member.bot and not reinstated:
            await assign_autoroles(member)


@discord_client.event
async def on_member_remove(member):
    if (await GuildPrefsComponent().get_guild_prefs(member.guild)).role_persistence_enabled:
        await save_roles_for(member)
    # leave as True to send member leave messages to servers' logs channels
    if True:
        await log_to_server(member.guild, constants.GuildLogType.MEMBER_LEFT, member=member,
                            fields=["Member Info"],
                            values=[f"**Joined:** <t:{int(datetime.timestamp(member.joined_at))}:f>"])


@discord_client.event
async def on_member_update(member_before: discord.Member, member_after):
    if "MEMBER_VERIFICATION_GATE_ENABLED" in member_before.guild.features:
        if member_before.pending and not member_after.pending:
            reinstated = False
            if (await GuildPrefsComponent().get_guild_prefs(member_after.guild)).role_persistence_enabled:
                reinstated = await reinstate_roles_for(member_after)
            if not member_after.bot and not reinstated:
                await assign_autoroles(member_after, wait=0)
