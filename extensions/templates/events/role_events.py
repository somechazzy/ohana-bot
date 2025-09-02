"""
Templates for custom extensions handling role-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnGuildRoleCreateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-role-create event handlers.

    Attributes:
        role (discord.Role): The role that triggered the event.
    """
    def __init__(self, role: discord.Role, **kwargs):
        super().__init__(**kwargs)
        self.role: discord.Role = role


class BaseOnGuildRoleDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-role-delete event handlers.

    Attributes:
        role (discord.Role): The role that triggered the event.
    """
    def __init__(self, role: discord.Role, **kwargs):
        super().__init__(**kwargs)
        self.role: discord.Role = role


class BaseOnGuildRoleUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-role-update event handlers.

    Attributes:
        before (discord.Role): The role before the update.
        after (discord.Role): The role after the update.
    """
    def __init__(self, before: discord.Role, after: discord.Role, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.Role = before
        self.after: discord.Role = after
