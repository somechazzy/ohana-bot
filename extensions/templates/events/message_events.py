"""
Templates for custom extensions handling message-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnMessageEventHandler(_BaseEventHandler):
    """
    Base template for on-message event handlers.

    Attributes:
        message (discord.Message): The message that triggered the event.
    """
    _event_group = "message"
    _event_name = "on_message"

    def __init__(self, message: discord.Message, **kwargs):
        super().__init__(**kwargs)
        self.message: discord.Message = message


class BaseOnMessageEditEventHandler(_BaseEventHandler):
    """
    Base template for on-message-edit event handlers.

    Attributes:
        before (discord.Message): The message before it was edited.
        after (discord.Message): The message after it was edited.
    """
    _event_group = "message"
    _event_name = "on_message_edit"

    def __init__(self, before: discord.Message, after: discord.Message, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.Message = before
        self.after: discord.Message = after


class BaseOnMessageDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-message-delete event handlers.

    Attributes:
        message (discord.Message): The message that was deleted.
    """
    _event_group = "message"
    _event_name = "on_message_delete"

    def __init__(self, message: discord.Message, **kwargs):
        super().__init__(**kwargs)
        self.message: discord.Message = message


class BaseOnBulkMessageDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-bulk-message-delete event handlers.

    Attributes:
        messages (list[discord.Message]): The list of messages that were deleted.
    """
    _event_group = "message"
    _event_name = "on_bulk_message_delete"

    def __init__(self, messages: list[discord.Message], **kwargs):
        super().__init__(**kwargs)
        self.messages: list[discord.Message] = messages


class BaseOnRawMessageEditEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-message-edit event handlers.

    Attributes:
        payload (discord.RawMessageUpdateEvent): The raw message update event payload.
    """
    _event_group = "message"
    _event_name = "on_raw_message_edit"

    def __init__(self, payload: discord.RawMessageUpdateEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawMessageUpdateEvent = payload


class BaseOnRawMessageDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-message-delete event handlers.

    Attributes:
        payload (discord.RawMessageDeleteEvent): The raw message delete event payload.
    """
    _event_group = "message"
    _event_name = "on_raw_message_delete"

    def __init__(self, payload: discord.RawMessageDeleteEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawMessageDeleteEvent = payload


class BaseOnRawBulkMessageDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-bulk-message-delete event handlers.

    Attributes:
        payload (discord.RawBulkMessageDeleteEvent): The raw bulk message delete event payload.
    """
    _event_group = "message"
    _event_name = "on_raw_bulk_message_delete"

    def __init__(self, payload: discord.RawBulkMessageDeleteEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawBulkMessageDeleteEvent = payload
