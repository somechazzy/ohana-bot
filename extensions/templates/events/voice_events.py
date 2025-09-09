"""
Templates for custom extensions handling voice-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnVoiceStateUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-voice-state-update event handlers.

    Attributes:
        member (discord.Member): The member that triggered the event.
        before (discord.VoiceState): The voice state before the update.
        after (discord.VoiceState): The voice state after the update.
    """
    _event_group = "voice"
    _event_name = "on_voice_state_update"

    def __init__(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, **kwargs):
        super().__init__(**kwargs)
        self.member = member
        self.before = before
        self.after = after


class BaseOnVoiceChannelEffectEventHandler(_BaseEventHandler):
    """
    Base template for on-voice-channel-effect event handlers.

    Attributes:
        effect (discord.VoiceChannelEffect): The voice channel effect that triggered the event.
    """
    _event_group = "voice"
    _event_name = "on_voice_channel_effect"

    def __init__(self, effect: discord.VoiceChannelEffect, **kwargs):
        super().__init__(**kwargs)
        self.effect = effect
