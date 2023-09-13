import discord

from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from internal.bot_logger import InfoLogger, ErrorLogger
from globals_.constants import BotLogLevel


class BaseInteractionsHandler:
    def __init__(self, source_interaction):
        if self.__class__ == BaseInteractionsHandler:
            raise NotImplementedError("BaseInteractionsHandler is an abstract class and cannot be instantiated")
        self.source_interaction: discord.Interaction = source_interaction
        self.guild_prefs_component = GuildPrefsComponent()
        self.info_logger = InfoLogger(component=self.__class__.__name__)
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def on_timeout(self):
        self.info_logger.log(f"View timeout not handled. Handler class: {self.__class__.__name__}",
                             level=BotLogLevel.MINOR_WARNING, log_to_discord=True)


class NumberedListInteractions:

    async def handle_selection(self, interaction: discord.Interaction):
        raise NotImplemented

    async def handle_cancel(self, interaction: discord.Interaction):
        raise NotImplemented


class NavigationInteractions:

    async def handle_next(self, interaction: discord.Interaction):
        raise NotImplemented

    async def handle_previous(self, interaction: discord.Interaction):
        raise NotImplemented

    async def handle_cancel(self, interaction: discord.Interaction):
        raise NotImplemented

    async def handle_go_back(self, interaction: discord.Interaction):
        raise NotImplemented
