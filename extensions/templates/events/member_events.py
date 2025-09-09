"""
Templates for custom extensions handling member-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnMemberJoinEventHandler(_BaseEventHandler):
    """
    Base template for on-member-join event handlers.

    Attributes:
        member (discord.Member): The member that triggered the event.
    """
    _event_group = "member"
    _event_name = "on_member_join"

    def __init__(self, member: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.member: discord.Member = member


class BaseOnMemberRemoveEventHandler(_BaseEventHandler):
    """
    Base template for on-member-remove event handlers.

    Attributes:
        member (discord.Member): The member that triggered the event.
    """
    _event_group = "member"
    _event_name = "on_member_remove"

    def __init__(self, member: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.member: discord.Member = member


class BaseOnRawMemberRemoveEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-member-remove event handlers.

    Attributes:
        payload: discord.RawMemberRemoveEvent: The payload that triggered the event.
    """
    _event_group = "member"
    _event_name = "on_raw_member_remove"

    def __init__(self, payload: discord.RawMemberRemoveEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawMemberRemoveEvent = payload


class BaseOnMemberUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-member-update event handlers.

    Attributes:
        before (discord.Member): The member state before the update.
        after (discord.Member): The member state after the update.
    """
    _event_group = "member"
    _event_name = "on_member_update"

    def __init__(self, before: discord.Member, after: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.Member = before
        self.after: discord.Member = after


class BaseOnUserUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-user-update event handlers.

    Attributes:
        before (discord.User): The user state before the update.
        after (discord.User): The user state after the update.
    """
    _event_group = "member"
    _event_name = "on_user_update"

    def __init__(self, before: discord.User, after: discord.User, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.User = before
        self.after: discord.User = after


class BaseOnMemberBanEventHandler(_BaseEventHandler):
    """
    Base template for on-member-ban event handlers.

    Attributes:
        guild (discord.Guild): The guild where the ban occurred.
        user (discord.Member | discord.User): The user that was banned.
    """
    _event_group = "member"
    _event_name = "on_member_ban"

    def __init__(self, guild: discord.Guild, user: discord.Member | discord.User, **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild
        self.user: discord.Member | discord.User = user


class BaseOnMemberUnbanEventHandler(_BaseEventHandler):
    """
    Base template for on-member-unban event handlers.

    Attributes:
        guild (discord.Guild): The guild where the unban occurred.
        user (discord.User): The user that was unbanned.
    """
    _event_group = "member"
    _event_name = "on_member_unban"

    def __init__(self, guild: discord.Guild, user: discord.User, **kwargs):
        super().__init__(**kwargs)
        self.guild: discord.Guild = guild
        self.user: discord.User = user


class BaseOnPresenceUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-presence-update event handlers.

    Attributes:
        before (discord.Member): The member before the update.
        after (discord.Member): The member after the update.
    """
    _event_group = "member"
    _event_name = "on_presence_update"

    def __init__(self, before: discord.Member, after: discord.Member, **kwargs):
        super().__init__(**kwargs)
        self.before: discord.Member = before
        self.after: discord.Member = after


class BaseOnRawPresenceUpdateEventHandler(_BaseEventHandler):
    """
    Base template for on-raw-presence-update event handlers.

    Attributes:
        payload (discord.RawPresenceUpdateEvent): The payload that triggered the event.
    """
    _event_group = "member"
    _event_name = "on_raw_presence_update"

    def __init__(self, payload: discord.RawPresenceUpdateEvent, **kwargs):
        super().__init__(**kwargs)
        self.payload: discord.RawPresenceUpdateEvent = payload
