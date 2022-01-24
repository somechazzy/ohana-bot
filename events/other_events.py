import sys
import traceback
from globals_.clients import discord_client
from internal.bot_logging import log
from globals_ import constants


@discord_client.event
async def on_error(event, *args, **kwargs):
    args_text = "\n".join(args)
    kwargs_text = "\n".join(kwargs)
    error_text = f'''
event= {event}
args= {args_text.strip()}
kwargs= {kwargs_text.strip()}
exception_info= {sys.exc_info()}
traceback=\n {traceback.format_exc()}
    '''
    await log(error_text, level=constants.BotLogType.BOT_ERROR, ping_me=True)
