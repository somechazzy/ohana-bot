import discord

from globals_ import shared_memory
from models.guild import GuildPrefs
from user_interactions.base_interactions_handler import BaseInteractionsHandler


class UserInteractionsHandler(BaseInteractionsHandler):

    def __init__(self, source_interaction):
        super().__init__(source_interaction=source_interaction)
        if self.__class__ == UserInteractionsHandler:
            raise NotImplementedError("UserInteractionsHandler is an abstract class and cannot be instantiated")
        self.guild = source_interaction.guild or None
        self.guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(self.guild.id) if self.guild else None
        self.user = source_interaction.user
        self.member = self.guild.get_member(self.source_interaction.user.id) if self.guild else None
        self.is_dm = not self.guild

    async def on_timeout(self):
        try:
            await self.source_interaction.edit_original_response(view=None)
        except discord.NotFound:
            pass
