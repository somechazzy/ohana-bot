import discord
from discord.ext import commands
import logging

from constants import ChunkGuildsSetting
from settings import DISCORD_BOT_TOKEN, BOT_OWNER_ID, CHUNK_GUILDS_SETTING


class DiscordService:
    """
    Singleton class to manage the Discord bot client.
    """
    _client = None

    @classmethod
    def get_client(cls) -> commands.Bot:
        if cls._client is None:
            intents = discord.Intents.all()
            intents.presences = False
            cls._client = commands.Bot(intents=intents,
                                       chunk_guilds_at_startup=CHUNK_GUILDS_SETTING == ChunkGuildsSetting.AT_STARTUP,
                                       command_prefix='/',
                                       owner_id=BOT_OWNER_ID)
        return cls._client

    @classmethod
    def run_client(cls):
        from common.app_logger import DpyLoggingHandler
        cls.get_client().run(token=DISCORD_BOT_TOKEN, log_handler=DpyLoggingHandler(),
                             log_formatter=logging.Formatter("%(name)s: %(message)s"))

