"""
This module contains event handlers for channel-related events.
"""
from bot.utils.decorators import extensible_event
from clients import discord_client


@discord_client.event
@extensible_event(group='channel')
async def on_guild_channel_create(*_):
    pass


@discord_client.event
@extensible_event(group='channel')
async def on_guild_channel_delete(*_):
    pass


@discord_client.event
@extensible_event(group='channel')
async def on_guild_channel_update(*_):
    pass


@discord_client.event
@extensible_event(group='channel')
async def on_guild_channel_pins_update(*_):
    pass


@discord_client.event
@extensible_event(group='channel')
async def on_typing(*_):
    pass


@discord_client.event
@extensible_event(group='channel')
async def on_raw_typing(*_):
    pass
