from globals_ import clients
from globals_.settings import settings
from services.third_party.discord import DiscordClient
from events import *

"""
First run checks to make sure you've set up everything correctly.
Feel free to delete the import and the first_run_checks file once you've run the bot once successfully.
"""
import first_run_checks
first_run_checks.perform_checks()
"""
"""

print(f"## RUNNING IN {settings.ENVIRONMENT.upper()} ENVIRONMENT ##")

clients.firebase_client.initialize_fb()


@clients.discord_client.event
async def on_ready():
    InfoLogger("main").log("######### Started logging #########", level=BotLogLevel.BOT_INFO)
    from internal.on_launch import perform_on_launch_tasks
    await perform_on_launch_tasks()
    InfoLogger("main").log("Bot is up and running (on-ready event).", level=constants.BotLogLevel.BOT_INFO)


DiscordClient.run_client()
