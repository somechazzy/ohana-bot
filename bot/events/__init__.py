"""
This module is responsible for registering all event handlers for the bot simply by importing them.
"""


def register_event_handlers():
    from bot.events import (
        bot_events,
        channel_events,
        guild_events,
        interaction_events,
        member_events,
        message_events,
        reaction_events,
        voice_events
    )
