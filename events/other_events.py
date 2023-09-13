import sys
import traceback
from globals_.clients import discord_client
from internal.bot_logger import ErrorLogger
from globals_ import constants

client = discord_client


@client.event
async def on_error(event, *args, **kwargs):
    error_text = f"event= {event}\n" \
                 f"args= {args}\n" \
                 f"kwargs= {kwargs}\n" \
                 f"exception_info= {sys.exc_info()}\n" \
                 f"traceback=\n {traceback.format_exc()}"

    ErrorLogger().log(error_text, level=constants.BotLogLevel.ERROR)
