"""
Templates for custom extensions handling channel-related events.
"""
import datetime

import discord

from . import _BaseEventHandler


class BaseOnGuildChannelCreateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-channel-create event handlers.

    Attributes:
        channel (discord.abc.GuildChannel): The channel that triggered the event.
    """
    def __init__(self, channel: discord.abc.GuildChannel, **kwargs):
        super().__init__(**kwargs)
        self.channel: discord.abc.GuildChannel = channel


class BaseOnGuildChannelDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-channel-delete event handlers.

    Attributes:
        channel (discord.abc.GuildChannel): The channel that triggered the event.
    """
    def __init__(self, channel: discord.abc.GuildChannel, **kwargs):
        super().__init__(**kwargs)
        self.channel: discord.abc.GuildChannel = channel


class BaseOnGuildChannelUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-channel-update event handlers.

    Attributes:
        before (discord.abc.GuildChannel): The channel before the update.
        after (discord.abc.GuildChannel): The channel after the update.
    """
    def __init__(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.abc.GuildChannel = before
        self.after: discord.abc.GuildChannel = after


class BaseOnGuildChannelPinsUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-channel-pins-update event handlers.

    Attributes:
        channel (discord.abc.GuildChannel | discord.Thread): The channel that triggered the event.
        last_pin (datetime.datetime): The timestamp of the last pin update.
    """
    def __init__(self,
                 channel: discord.abc.GuildChannel | discord.Thread,
                 last_pin: datetime.datetime | None,
                 **kwargs):
        super().__init__(**kwargs)
        self.channel: discord.abc.GuildChannel | discord.Thread = channel
        self.last_pin = last_pin


class BaseOnTypingEventHandler(_BaseEventHandler):
    """
    Base template for on-typing event handlers.

    Attributes:
        channel (discord.abc.GuildChannel): The channel where the typing event occurred.
        member (discord.User | discord.Member): The member who triggered the typing event.
        when (datetime.datetime): The timestamp of the typing event.
    """
    def __init__(self,
                 channel: discord.abc.GuildChannel,
                 member: discord.Member,
                 when: datetime.datetime,
                 **kwargs):
        super().__init__(**kwargs)
        self.channel: discord.abc.GuildChannel = channel
        self.member: discord.Member = member
        self.when: datetime.datetime = when


class BaseOnRawTypingEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-typing event handlers.

    Attributes:
        payload (discord.RawTypingEvent): The raw typing event payload.
    """
    def __init__(self, payload: discord.RawTypingEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawTypingEvent = payload
