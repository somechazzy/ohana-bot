import asyncio
import gc
import time
import traceback
from actions import send_dm, edit_message
from globals_ import variables
from globals_.clients import firebase_client, discord_client
from globals_.constants import DEFAULT_PREFIX, BotLogType, cache_timeout_minutes, \
    CACHE_CLEANUP_FREQUENCY_SECONDS
from globals_.variables import cached_pages
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import import_command_list, import_level_requirement_models, import_mal_usernames, import_al_usernames, \
    import_guilds_prefs, import_guilds_xp, convert_minutes_to_time_string, restore_music_services, \
    fill_youtube_cache_with_restored_queues, reset_music_players
from internal.bot_logging import log
import disnake as discord

from web_parsers.music import youtube_parser
from xp import xp_tasks


async def perform_on_launch_tasks():
    if variables.performed_on_launch_tasks:
        return
    variables.performed_on_launch_tasks = True

    import_command_list()
    import_level_requirement_models()
    await import_mal_usernames()
    await import_al_usernames()
    await import_guilds_prefs()
    await import_guilds_xp()
    await GuildPrefsComponent().refresh_guilds_info()

    await discord_client.\
        change_presence(activity=discord.Game(f'{DEFAULT_PREFIX}help'))

    asyncio.get_event_loop().create_task(handle_interrupted_timers())
    asyncio.get_event_loop().create_task(cache_cleanup())
    asyncio.get_event_loop().create_task(handle_music_on_launch())

    asyncio.get_event_loop().create_task(xp_tasks.periodic_guilds_xp_sync())
    asyncio.get_event_loop().create_task(xp_tasks.queue_members_for_xp_decay())
    asyncio.get_event_loop().create_task(xp_tasks.initiate_periodic_xp_decay())
    asyncio.get_event_loop().create_task(youtube_parser.start_download_queue_worker())


async def handle_interrupted_timers():
    asyncio.get_event_loop().create_task(handle_interrupted_countdowns())
    asyncio.get_event_loop().create_task(handle_interrupted_reminders())


async def handle_interrupted_countdowns():
    countdowns = await firebase_client.get_all_countdowns()
    try:
        _ = countdowns[0]
    except:
        return
    await log(f"Recovered {len(countdowns.val())} countdowns.", level=BotLogType.BOT_INFO)
    for countdown in countdowns:
        asyncio.get_event_loop().create_task(handle_recovered_countdown(cd_key=countdown.key(), cd_val=countdown.val()))


async def handle_interrupted_reminders():
    reminders = await firebase_client.get_all_reminders()
    try:
        _ = reminders[0]
    except:
        return
    await log(f"Recovered {len(reminders.val())} reminders.", level=BotLogType.BOT_INFO)
    for reminder in reminders:
        reminder_dict = reminder.val()
        db_key = reminder.key()
        time_of_duration_end_seconds = reminder_dict.get("time_of_duration_end_seconds")
        reason = reminder_dict.get("reason")
        user_id = reminder_dict.get("user_id")

        asyncio.get_event_loop().create_task(handle_recovered_reminder(time_of_duration_end_seconds, reason,
                                                                       user_id, db_key))


async def handle_recovered_countdown(cd_key, cd_val):
    ids = cd_key.strip().split("_")
    params = cd_val.split("|")
    channel_id, message_id = ids[:2]
    reason = params[0].strip()
    requested_by_name = params[1].strip()
    requested_by_avatar = params[2].strip()
    time_of_countdown_end_seconds = int(params[3].strip())
    time_remaining_initial = params[4].strip()
    channel = discord_client.get_channel(int(channel_id))
    if not channel:
        return
    sent_message = channel.get_partial_message(int(message_id))
    sent_message_id = sent_message.id

    time_of_countdown_end_string = time.strftime("%H:%M, %d/%m/%Y", time.
                                                 localtime(time_of_countdown_end_seconds))

    def make_countdown_embed(description_, reason_, author_, author_avatar_, _, cd_up_=False, cd_duration_=None):
        bot_avatar = discord_client.user.avatar.with_size(32).url
        embed_ = discord.Embed(colour=discord.Colour(0x2d6d46),
                               description=description_)
        embed_.set_thumbnail(url=f"https://i.pinimg.com/564x/e6/f6/ef/e6f6efb2d160cb0d487098077bdb967f.jpg")
        embed_.set_author(name=f"Countdown for: {reason_}",
                          icon_url=bot_avatar)
        embed_.set_footer(text=f"Requested by {author_}" +
                               (f"| {cd_duration_} elapsed." if cd_up_ and cd_duration_ is not None else " "),
                          icon_url=author_avatar_ or discord.embeds.EmptyEmbed)
        return embed_

    while True:
        current_time_seconds = int(time.time()) + time.altzone
        time_remaining_seconds = time_of_countdown_end_seconds - current_time_seconds
        if time_remaining_seconds < 60:
            if time_remaining_seconds < 0:
                break
            description = f"‎‎‎\n‎‎‎ ⏳ **{time_remaining_seconds} seconds to go.**\n‎‎‎"
            embed = make_countdown_embed(description, reason, requested_by_name,
                                         requested_by_avatar, time_of_countdown_end_string)
            sent_message = sent_message.channel.get_partial_message(sent_message_id)
            await edit_message(sent_message, content=None, embed=embed)
            await asyncio.sleep(time_remaining_seconds)
        else:
            time_remaining_minutes = int(time_remaining_seconds / 60)
            time_remaining_string = convert_minutes_to_time_string(time_remaining_minutes)
            description = f"‎‎‎\n‎‎‎ ⏳ **{time_remaining_string} to go.**\n‎‎‎"
            embed = make_countdown_embed(description, reason, requested_by_name,
                                         requested_by_avatar, time_of_countdown_end_string)
            sent_message = sent_message.channel.get_partial_message(sent_message_id)
            await edit_message(sent_message, content=None, embed=embed, log_enable=False)
            await asyncio.sleep(30)
    description = f"‎‎‎\n‎‎‎ ⏳ Countdown is up.\n‎‎‎"
    embed = make_countdown_embed(description, reason, requested_by_name, requested_by_avatar,
                                 time_of_countdown_end_string, cd_up_=True, cd_duration_=time_remaining_initial)
    sent_message = sent_message.channel.get_partial_message(sent_message_id)
    await edit_message(sent_message, content=None, embed=embed)
    await firebase_client.remove_countdown(sent_message)


async def handle_recovered_reminder(time_of_duration_end_seconds, reason, user_id, db_key):
    user = discord_client.get_user(int(user_id))
    if not user:
        await log(f"Could not retrieve user with ID {user_id} for reminder during reminders recovery.",
                  level=BotLogType.BOT_WARNING_IGNORE)
        await firebase_client.remove_reminder(db_key)
        return

    current_time_seconds = int(time.time()) + time.altzone
    if current_time_seconds >= time_of_duration_end_seconds:
        time_late_string = convert_minutes_to_time_string(int((current_time_seconds - time_of_duration_end_seconds)/60))
        await send_dm(f"⏱ Belated Reminder: {reason}\nI was offline "
                      f"{time_late_string} ago so I missed the reminder. Sorry!",
                      user=user, log_to_discord=False)
        await firebase_client.remove_reminder(db_key)
        return

    seconds_left = time_of_duration_end_seconds - current_time_seconds
    await asyncio.sleep(seconds_left if seconds_left > 2 else 1)
    await send_dm(f"⏱ Reminder: {reason}", user, log_to_discord=False)
    await firebase_client.remove_reminder(db_key)


async def cache_cleanup():
    tracker = 0
    while True:
        current_time = int(time.time())
        to_remove = []
        for cached_page in cached_pages:
            cache_timestamp = cached_pages.get(cached_page).get("timestamp")
            cache_timeout = cache_timeout_minutes.get(cached_pages.get(cached_page).get("type")) * 60
            if current_time - cache_timestamp > cache_timeout:
                to_remove.append(cached_page)
        for item in to_remove:
            cached_pages.pop(item)
        gc.collect()
        tracker += 1
        if tracker % 10 == 0:
            variables.users_notified_of_rate_limit.clear()
            variables.user_ar_trigger.clear()
            variables.user_command_use.clear()
        if tracker % 360 == 0:
            variables.cached_youtube_info = {}
            variables.cached_youtube_search_results = {}

        await asyncio.sleep(CACHE_CLEANUP_FREQUENCY_SECONDS)


async def handle_music_on_launch():
    await asyncio.sleep(1)
    for guild in discord_client.guilds:
        if guild.me.voice and guild.me.voice.channel:
            try:
                await guild.me.voice.channel.connect()
            except Exception as e:
                await log(f"Error while reconnecting to VC after restarting music bot: {e}.\n{traceback.format_exc()}",
                          level=BotLogType.BOT_ERROR, guild_id=guild.id)
                pass
    gms_to_play, gms_to_pause = await restore_music_services()
    fill_youtube_cache_with_restored_queues()
    for gms in gms_to_play:
        asyncio.get_event_loop().create_task(gms.start_worker())
    for gms in gms_to_pause:
        asyncio.get_event_loop().create_task(gms.start_worker(pause_immediately=True))
    await reset_music_players()
