from datetime import datetime


class XPAction:

    def __init__(self, guild_id: int, member_id: int, username: str, xp_offset: int = 0, reset: bool = False):
        self.guild_id: int = guild_id
        self.member_id: int = member_id
        self.username: str = username
        self.xp_offset: int = xp_offset
        self.reset: bool = reset

    def __str__(self):
        return f"XPAction(guild_id={self.guild_id}, member_id={self.member_id}, xp_offset={self.xp_offset})"


class XPDecayItem:
    def __init__(self, guild_id: int, member_id: int, username: str, next_decay: datetime):
        self.guild_id: int = guild_id
        self.member_id: int = member_id
        self.username: str = username
        self.next_decay: datetime = next_decay

    def __lt__(self, other):
        return self.next_decay < other.next_decay

    def __gt__(self, other):
        return self.next_decay > other.next_decay

    def __str__(self):
        return f"XPDecayItem(guild_id={self.guild_id}, member_id={self.member_id}, next_decay={self.next_decay})"
