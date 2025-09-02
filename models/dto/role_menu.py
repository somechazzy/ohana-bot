import discord

from constants import RoleMenuDefaults


class RoleMenuSettings:
    def __init__(self, name: str, description: str, roles: list['RoleMenuRole'],
                 embed_color: hex, thumbnail_url: str | None = None,
                 image_url: str | None = None, footer_note: str | None = None):
        self.name: str = name
        self.description: str = description
        self.roles: list['RoleMenuRole'] = roles
        self.embed_color: hex = embed_color
        self.thumbnail_url: str | None = thumbnail_url
        self.image_url: str | None = image_url
        self.footer_note: str | None = footer_note

    @classmethod
    def with_defaults(cls):
        return cls(
            name=RoleMenuDefaults.NAME,
            description=RoleMenuDefaults.DESCRIPTION,
            roles=[],
            embed_color=RoleMenuDefaults.EMBED_COLOUR,
            thumbnail_url=None,
            image_url=None,
            footer_note=None
        )

    def add_role(self, role_id: int, alias: str,
                 emoji: discord.Emoji | discord.PartialEmoji | None,
                 rank: int | None = None):
        if rank is None:
            rank = (max(role.rank for role in self.roles) + 1) if self.roles else 1
        self.roles.append(RoleMenuRole(role_id=role_id, alias=alias, rank=rank, emoji=emoji))
        self.refresh_role_ranks()

    def remove_role(self, role_id):
        self.roles = [role for role in self.roles if role.role_id != role_id]
        self.refresh_role_ranks()

    def refresh_role_ranks(self):
        self.roles.sort()
        for index, role in enumerate(self.roles):
            role.rank = index + 1


class RoleMenuRole:
    def __init__(self, role_id: int, alias: str, rank: int, emoji: discord.Emoji | discord.PartialEmoji | None = None):
        self.role_id: int = role_id
        self.alias: str = alias
        self.rank: int = rank
        self.emoji: discord.Emoji | discord.PartialEmoji | None = emoji

    def __lt__(self, other: 'RoleMenuRole'):
        return self.rank < other.rank

    def __gt__(self, other: 'RoleMenuRole'):
        return self.rank > other.rank
