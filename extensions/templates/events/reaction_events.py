"""
Templates for custom extensions handling reaction-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnReactionAddEventHandler(_BaseEventHandler):
    """
    Base template for on-reaction-add event handlers.

    Attributes:
        reaction (discord.Reaction): The reaction that triggered the event.
        member (discord.Member): The member who added the reaction.
    """
    def __init__(self, reaction: discord.Reaction, member: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.reaction: discord.Reaction = reaction
        self.member: discord.Member = member


class BaseOnReactionRemoveEventHandler(_BaseEventHandler):
    """
    Base template for on-reaction-remove event handlers.

    Attributes:
        reaction (discord.Reaction): The reaction that was removed.
        member (discord.Member): The member who removed the reaction.
    """
    def __init__(self, reaction: discord.Reaction, member: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.reaction: discord.Reaction = reaction
        self.member: discord.Member = member


class BaseOnReactionClearEventHandler(_BaseEventHandler):
    """
    Base template for on-reaction-clear event handlers.

    Attributes:
        message (discord.Message): The message from which reactions were cleared.
        reactions (list[discord.Reaction]): List of reactions that were cleared.
    """
    def __init__(self, message: discord.Message, reactions: list[discord.Reaction], **kwargs):
        super().__init__(**kwargs)
        self.message: discord.Message = message
        self.reactions: list[discord.Reaction] = reactions


class BaseOnReactionClearEmojiEventHandler(_BaseEventHandler):
    """
    Base template for on-reaction-clear-emoji event handlers.

    Attributes:
        reaction (discord.Reaction): The reaction that was cleared.
    """
    def __init__(self, reaction: discord.Reaction, **kwargs):
        super().__init__(**kwargs)
        self.reaction: discord.Reaction = reaction


class BaseOnRawReactionAddEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-reaction-add event handlers.

    Attributes:
        payload (discord.RawReactionActionEvent): The raw reaction action event payload.
    """
    def __init__(self, payload: discord.RawReactionActionEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawReactionActionEvent = payload


class BaseOnRawReactionRemoveEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-reaction-remove event handlers.

    Attributes:
        payload (discord.RawReactionActionEvent): The raw reaction action event payload.
    """
    def __init__(self, payload: discord.RawReactionActionEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawReactionActionEvent = payload


class BaseOnRawReactionClearEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-reaction-clear event handlers.

    Attributes:
        payload (discord.RawReactionActionEvent): The raw reaction action event payload.
    """
    def __init__(self, payload: discord.RawReactionActionEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawReactionActionEvent = payload


class BaseOnRawReactionClearEmojiEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-reaction-clear-emoji event handlers.

    Attributes:
        payload (discord.RawReactionActionEvent): The raw reaction action event payload.
    """
    def __init__(self, payload: discord.RawReactionActionEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawReactionActionEvent = payload
