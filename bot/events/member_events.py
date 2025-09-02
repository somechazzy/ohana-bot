"""
This module contains event handlers for member-related events.
"""
import discord

from bot.utils.decorators import extensible_event
from bot.utils.bot_actions.automod_actions import apply_persistent_roles_to_member, assign_autoroles_to_member
from clients import discord_client
from common.decorators import require_db_session
from components.guild_settings_components.guild_user_roles_component import GuildUserRolesComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import GUILD_FEATURE_MEMBER_VERIFICATION_GATE_ENABLED


@discord_client.event
@require_db_session
@extensible_event(group='member')
async def on_member_join(member: discord.Member):
    """
    Event handler for when a member joins a guild.
    Args:
        member (discord.Member): The member who joined.
    """
    if member.id == discord_client.user.id:
        return
    if GUILD_FEATURE_MEMBER_VERIFICATION_GATE_ENABLED not in member.guild.features or not member.pending:
        guild_settings = await GuildSettingsComponent().get_guild_settings(member.guild.id)
        previous_roles_reinstated = False
        if guild_settings.role_persistence_enabled:
            previous_roles_reinstated = await apply_persistent_roles_to_member(member)
        if not member.bot and not previous_roles_reinstated and guild_settings.autoroles_ids:
            await assign_autoroles_to_member(member)


@discord_client.event
@require_db_session
@extensible_event(group='member')
async def on_member_remove(member: discord.Member):
    """
    Event handler for when a member leaves a guild.
    Args:
        member: discord.Member: The member who left.
    """
    if member.id == discord_client.user.id:
        return
    await GuildUserRolesComponent().set_guild_user_roles(guild_id=member.guild.id, user_id=member.id,
                                                         role_ids=[role.id for role in member.roles
                                                                   if role.id != member.guild.id])


@discord_client.event
@require_db_session
@extensible_event(group='member')
async def on_member_update(member_before: discord.Member, member_after: discord.Member):
    """
    Event handler for when a member is updated.
    Args:
        member_before (discord.Member): The member before the update.
        member_after (discord.Member): The member after the update.
    """
    if member_before.id == discord_client.user.id:
        return
    if {role.id for role in member_before.roles} != {role.id for role in member_after.roles}:
        await GuildUserRolesComponent().set_guild_user_roles(guild_id=member_after.guild.id,
                                                             user_id=member_after.id,
                                                             role_ids=[role.id for role in member_after.roles])
        if GUILD_FEATURE_MEMBER_VERIFICATION_GATE_ENABLED in member_before.guild.features:
            guild_settings = await GuildSettingsComponent().get_guild_settings(member_after.guild.id)
            if member_before.pending and not member_after.pending:
                previous_roles_reinstated = False
                if guild_settings.role_persistence_enabled:
                    previous_roles_reinstated = await apply_persistent_roles_to_member(member_after)
                if not member_after.bot and not previous_roles_reinstated and guild_settings.autoroles_ids:
                    await assign_autoroles_to_member(member_after)


@discord_client.event
@extensible_event(group='member')
async def on_raw_member_remove(*_):
    pass


@discord_client.event
@extensible_event(group='member')
async def on_user_update(*_):
    pass


@discord_client.event
@extensible_event(group='member')
async def on_member_ban(*_):
    pass


@discord_client.event
@extensible_event(group='member')
async def on_member_unban(*_):
    pass


@discord_client.event
@extensible_event(group='member')
async def on_presence_update(*_):
    pass


@discord_client.event
@extensible_event(group='member')
async def on_raw_presence_update(*_):
    pass
