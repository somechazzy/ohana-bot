from auth import auth
from discord.ext import commands
import discord
from globals_.constants import BOT_OWNER_ID


class DiscordClient:
    client = None

    @staticmethod
    def get_client() -> commands.Bot:
        if DiscordClient.client is None:
            intents = discord.Intents.all()
            intents.presences = False
            DiscordClient.client = commands.Bot(intents=intents,
                                                command_prefix='.',
                                                sync_commands_debug=True,
                                                owner_id=BOT_OWNER_ID)
        return DiscordClient.client

    @staticmethod
    def run_client():
        DiscordClient.get_client().run(token=auth.BOT_TOKEN)
