import json
import os
import traceback
from datetime import datetime
from pathlib import Path

from globals_ import variables
from globals_.clients import firebase_client, discord_client
from globals_.constants import BotLogType
from helpers import build_path


async def backup_music_services():
    music_services = variables.guild_music_services
    gms = {}
    for guild_id, guild_music_service in music_services.items():
        if not guild_music_service.voice_client or not guild_music_service.voice_client.is_connected():
            continue
        gms[guild_id] = guild_music_service.export_gms_to_dict()

    gms_backup = json.dumps(gms)
    await firebase_client.set_gms(gms_backup)


async def restore_music_services():
    from services.music_service import GuildMusicService
    from internal.bot_logging import log
    gms_string = (await firebase_client.get_gms()).val()
    if not gms_string:
        gms_string = "{}"
    gms_dicts = json.loads(gms_string)
    gms_to_play = []
    gms_to_pause = []
    for guild_id, gms_dict in gms_dicts.items():
        guild_id = int(guild_id)
        guild_music_service = GuildMusicService(guild_id, 0, None, None)
        guild_music_service.import_gms_from_dict(gms_dict=gms_dict)
        was_paused = gms_dict['was_paused']
        if _guild_music_service_playable(guild_music_service):
            if was_paused:
                gms_to_pause.append(guild_music_service)
            else:
                gms_to_play.append(guild_music_service)
            variables.guild_music_services[guild_id] = guild_music_service
    await firebase_client.reset_gms()
    if gms_dicts:
        await log(message=f"Restored {len(gms_dicts)} music services: "
                          f"{len(gms_to_play)} playing, {len(gms_to_pause)} paused.", level=BotLogType.BOT_INFO)
    return gms_to_play, gms_to_pause


def _guild_music_service_playable(guild_music_service):
    guild = discord_client.get_guild(guild_music_service.guild_id)
    return guild_music_service.queue \
        and guild_music_service.voice_client and \
        guild.me in guild.get_channel(guild_music_service.voice_channel_id).members


def fill_youtube_cache_with_restored_queues():
    music_services = variables.guild_music_services.values()
    queue = []
    for music_service in music_services:
        queue.extend(music_service.queue)
    for queued_track in queue:
        url = queued_track['url']
        title = queued_track['title']
        thumbnail_url = queued_track['thumbnail_url']
        tiny_thumbnail_url = queued_track['tiny_thumbnail_url']
        duration = queued_track['duration']
        audio_url = queued_track['audio_url']
        audio_expiry = queued_track['audio_expiry']
        song_details = queued_track['song_details']
        if url in variables.cached_youtube_info:
            _, _, _, _, _, existing_audio_expiry, _ = variables.cached_youtube_info[url]
            if existing_audio_expiry > audio_expiry:
                continue
        if datetime.utcnow() > datetime.fromtimestamp(audio_expiry):
            continue
        variables.cached_youtube_info[url] =\
            title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details


async def reset_music_players():
    from embed_factory import make_initial_player_message_embed
    from internal.bot_logging import log
    for guild_prefs in variables.guilds_prefs.values():
        try:
            music_channel = discord_client.get_channel(guild_prefs.music_channel)
            if music_channel and guild_prefs.guild_id not in variables.guild_music_services:
                player_message = music_channel.get_partial_message(guild_prefs.music_player_message)
                if player_message:
                    embed = make_initial_player_message_embed(guild=music_channel.guild)
                    await player_message.edit(embed=embed)
        except Exception as e:
            await log(f"Failed at resetting music player for guild {guild_prefs.guild_id}:"
                      f" {e}\n{traceback.format_exc()}", level=BotLogType.BOT_ERROR, guild_id=guild_prefs.guild_id)


async def add_track_to_guild_music_history(track, guild_id):
    history_directory_path = build_path(["media", "music", "history"])
    guild_history_path = build_path(["media", "music", "history", f"{guild_id}.json"])
    Path(history_directory_path).mkdir(parents=True, exist_ok=True)
    history = {}
    if os.path.isfile(guild_history_path):
        with open(guild_history_path, 'r') as file:
            history = json.load(file)
    youtube_id = track['url'].split('=')[1]
    if youtube_id in history:
        history.pop(youtube_id)
    history[youtube_id] = {
        "title": track['title'],
        "url": track['url'],
        "duration_text": track['duration_text'],
        "timestamp": int(datetime.utcnow().timestamp())
    }
    with open(guild_history_path, 'w') as file:
        json.dump(dict(list(history.items())[-50:]), file)
