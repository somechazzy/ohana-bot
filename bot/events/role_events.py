"""
This module contains event handlers for role-related events.
"""
from bot.utils.decorators import extensible_event
from clients import discord_client


@discord_client.event
@extensible_event(group='role')
async def on_guild_role_create(*_):
    pass


@discord_client.event
@extensible_event(group='role')
async def on_guild_role_delete(*_):
    pass


@discord_client.event
@extensible_event(group='role')
async def on_guild_role_update(*_):
    pass
