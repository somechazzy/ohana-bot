"""
This module contains event handlers for reaction-related events.
"""
from bot.utils.decorators import extensible_event
from clients import discord_client


@discord_client.event
@extensible_event(group='reaction')
async def on_reaction_add(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_reaction_remove(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_reaction_clear(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_reaction_clear_emoji(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_raw_reaction_add(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_raw_reaction_remove(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_raw_reaction_clear(*_):
    pass


@discord_client.event
@extensible_event(group='reaction')
async def on_raw_reaction_clear_emoji(*_):
    pass
