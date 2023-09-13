from datetime import datetime
from auto_moderation.role_management import reinstate_roles_for, save_roles_for, assign_autoroles
from globals_.constants import SUPPORT_SERVER_ID, \
    GuildLogType
from internal.guild_logging import log_to_server
from globals_.clients import discord_client
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
import discord

client = discord_client


@client.event
async def on_member_join(member):
    if member.guild.id in [SUPPORT_SERVER_ID]:
        await log_to_server(member.guild, GuildLogType.MEMBER_JOINED, member=member,
                            fields=["Account Info"],
                            values=[f"**Created:** {member.created_at.date()} {member.created_at.time().hour}:"
                                    f"{member.created_at.time().minute} GMT"])
    if "MEMBER_VERIFICATION_GATE_ENABLED" not in member.guild.features or not member.pending:
        reinstated = False
        if (await GuildPrefsComponent().get_guild_prefs(member.guild)).role_persistence_enabled:
            reinstated = await reinstate_roles_for(member)
        if not member.bot and not reinstated:
            await assign_autoroles(member)


@client.event
async def on_member_remove(member):
    if (await GuildPrefsComponent().get_guild_prefs(member.guild)).role_persistence_enabled:
        await save_roles_for(member)
    if member.guild.id in [SUPPORT_SERVER_ID]:
        await log_to_server(member.guild, GuildLogType.MEMBER_LEFT, member=member,
                            fields=["Member Info"],
                            values=[f"**Joined:** <t:{int(datetime.timestamp(member.joined_at))}:f>"])


@client.event
async def on_member_update(member_before: discord.Member, member_after):
    if "MEMBER_VERIFICATION_GATE_ENABLED" in member_before.guild.features:
        if member_before.pending and not member_after.pending:
            reinstated = False
            if (await GuildPrefsComponent().get_guild_prefs(member_after.guild)).role_persistence_enabled:
                reinstated = await reinstate_roles_for(member_after)
            if not member_after.bot and not reinstated:
                await assign_autoroles(member_after, wait=0)
