"""
Templates for custom extensions handling guild-related events.
"""
from collections.abc import Sequence

import discord

from . import _BaseEventHandler


class BaseOnGuildJoinEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-join event handlers.

    Attributes:
        guild (discord.Guild): The guild that triggered the event.
    """
    def __init__(self, guild: discord.Guild, **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild


class BaseOnGuildRemoveEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-remove event handlers.

    Attributes:
        guild (discord.Guild): The guild that triggered the event.
    """
    def __init__(self, guild: discord.Guild, **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild


class BaseOnGuildUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-update event handlers.

    Attributes:
        before (discord.Guild): The guild object before the update.
        after (discord.Guild): The guild object after the update.
    """
    def __init__(self, before: discord.Guild, after: discord.Guild, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.Guild = before
        self.after: discord.Guild = after


class BaseOnGuildEmojisUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-emojis-update event handlers.

    Attributes:
        guild (discord.Guild): The guild that triggered the event.
        before (Sequence[discord.Emoji]): The emojis before the update.
        after (Sequence[discord.Emoji]): The emojis after the update.
    """
    def __init__(self,
                 guild: discord.Guild,
                 before: Sequence[discord.Emoji],
                 after: Sequence[discord.Emoji],
                 **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild
        self.before: Sequence[discord.Emoji] = before
        self.after: Sequence[discord.Emoji] = after


class BaseOnGuildStickersUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-guild-stickers-update event handlers.

    Attributes:
        guild (discord.Guild): The guild that triggered the event.
        before (Sequence[discord.Sticker]): The stickers before the update.
        after (Sequence[discord.Sticker]): The stickers after the update.
    """
    def __init__(self,
                 guild: discord.Guild,
                 before: Sequence[discord.Sticker],
                 after: Sequence[discord.Sticker],
                 **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild
        self.before: Sequence[discord.Sticker] = before
        self.after: Sequence[discord.Sticker] = after


class BaseOnAuditLogEntryCreateEventHandler(_BaseEventHandler):
    """
    Base template for on-audit-log-entry-create event handlers.

    Attributes:
        entry (discord.AuditLogEntry): The audit log entry that was created.
    """
    def __init__(self, entry: discord.AuditLogEntry, **kwargs):
        super().__init__(**kwargs)
        self.entry: discord.AuditLogEntry = entry


class BaseOnInviteCreateEventHandler(_BaseEventHandler):
    """
    Base template for on-invite-create event handlers.

    Attributes:
        invite (discord.Invite): The invite that was created.
    """
    def __init__(self, invite: discord.Invite, **kwargs):
        super().__init__(**kwargs)
        self.invite: discord.Invite = invite


class BaseOnInviteDeleteEventHandler(_BaseEventHandler):
    """
    Base template for on-invite-delete event handlers.

    Attributes:
        invite (discord.Invite): The invite that was deleted.
    """
    def __init__(self, invite: discord.Invite, **kwargs):
        super().__init__(**kwargs)
        self.invite: discord.Invite = invite
