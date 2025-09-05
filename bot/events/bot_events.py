"""
This module contains general event handlers related to the bot's lifecycle.
"""
import sys

from api.api_service import APIService
from bot import register_cogs
from clients import discord_client, emojis, worker_manager_service
from components.guild_user_xp_components.xp_model_component import XPModelComponent
from components.music_component import MusicComponent
from constants import ChunkGuildsSetting, AppLogCategory
from settings import ENABLE_API_SERVICE, SYNC_COMMANDS_ON_STARTUP, SYNC_EMOJIS_ON_STARTUP, CHUNK_GUILDS_SETTING
from system.checks import verify_slashes_decorators
from utils.helpers.context_helpers import create_isolated_task
from ..utils.decorators import extensible_event
from ..utils.helpers.application_emojis_helper import sync_up_application_emojis
from ..utils.helpers.client_helpers import lazy_chunk_guilds, sync_commands_on_discord

from common.app_logger import AppLogger
logger: AppLogger = AppLogger('bot_events')


@discord_client.event
@extensible_event(group='bot')
async def on_connect():
    """
    This event is triggered when the bot connects to Discord.
    """
    if getattr(on_connect, 'already_run', False):
        return
    on_connect.already_run = True

    if ENABLE_API_SERVICE:
        create_isolated_task(APIService().start())
    verify_slashes_decorators()


@discord_client.event
@extensible_event(group='bot')
async def on_ready():
    """
    This event is triggered when the bot is fully ready, and is meant to perform start-up tasks such as populating the
    in-memory cache, adding command cogs, registering workers, etc.
    """
    if getattr(on_ready, 'already_run', False):
        return
    on_ready.already_run = True
    logger.info("Performing on-ready event tasks.", category=AppLogCategory.BOT_GENERAL)

    await XPModelComponent().load_xp_model()
    await MusicComponent().load_radio_streams()
    await register_cogs()
    if SYNC_EMOJIS_ON_STARTUP:
        await sync_up_application_emojis(refetch_and_set=False)
    emojis.set_emojis(await discord_client.fetch_application_emojis())

    await worker_manager_service.register_workers()
    create_isolated_task(worker_manager_service.run())

    if CHUNK_GUILDS_SETTING == ChunkGuildsSetting.LAZY:
        create_isolated_task(lazy_chunk_guilds())

    if SYNC_COMMANDS_ON_STARTUP:
        await sync_commands_on_discord()

    logger.info("Bot is up and running (on-ready event).", category=AppLogCategory.BOT_GENERAL)


@discord_client.event
@extensible_event(group='bot')
async def on_error(event, *args, **kwargs):
    """
    This event is triggered when an error occurs within an event handler and isn't explicitly caught.
    """
    logger.error(f"Error occurred while handling event {event} with args {args} and kwargs {kwargs}.\n"
                 f"Exception info: {sys.exc_info()}", category=AppLogCategory.BOT_GENERAL)
