import os
import sys
import auth
import asyncio
from globals_ import clients, constants, variables
from internal.clients import DiscordClient, SpotifyClient, GeniusClient

variables.os_type = constants.OSType.LINUX if sys.platform.lower() == 'linux' else \
    constants.OSType.WINDOWS if sys.platform.lower() == 'win32' else constants.OSType.OTHER
variables.main_path = os.path.dirname(__file__)

clients.firebase_client.initialize_fb()
clients.spotify_client = SpotifyClient(client_id=auth.SPOTIFY_CLIENT_ID, client_secret=auth.SPOTIFY_CLIENT_SECRET)
asyncio.get_event_loop().create_task(clients.spotify_client.perform_auth())
clients.genius_client = GeniusClient()


@clients.discord_client.event
async def on_ready():
    from internal.on_launch import perform_on_launch_tasks
    from internal.bot_logging import log
    await perform_on_launch_tasks()
    await log("Bot is up and running (on-ready event).", level=constants.BotLogType.BOT_INFO)


from events import *
DiscordClient.run_client()
