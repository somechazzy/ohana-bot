import asyncio
import discord

from components.music_components.on_startup_music_component import MusicOnRestartComponent
from globals_ import shared_memory
from globals_.clients import discord_client, reminder_service, worker_manager_service
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from utils.helpers import load_level_requirement_models, load_mal_usernames, \
    load_al_usernames, load_guilds_prefs, load_guilds_xp, load_commands_permissions, \
    load_guilds_with_disabled_players_refresh_button, load_music_streams


async def perform_on_launch_tasks():
    if hasattr(perform_on_launch_tasks, 'already_run'):  # function attributes are fun
        return
    perform_on_launch_tasks.already_run = True

    load_commands_permissions()

    from slashes import blueprint
    await blueprint.add_cogs()

    await load_guilds_prefs()

    load_level_requirement_models()
    await load_mal_usernames()
    await load_al_usernames()
    await load_guilds_xp()
    await GuildPrefsComponent().refresh_guilds_info()
    asyncio.get_event_loop().create_task(reminder_service.restore_reminders())

    asyncio.get_event_loop().create_task(MusicOnRestartComponent().perform_on_startup_tasks())
    await load_guilds_with_disabled_players_refresh_button()
    load_music_streams()

    await worker_manager_service.register_workers()
    asyncio.get_event_loop().create_task(worker_manager_service.run())

    shared_memory.queues['youtube_download_queue'] = asyncio.Queue()

    await discord_client.change_presence(activity=discord.Game(f'housewife | /help'))
