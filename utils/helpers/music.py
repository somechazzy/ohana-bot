import asyncio
import json
import os
from datetime import datetime
from math import ceil

import discord

from globals_ import shared_memory
from globals_.clients import firebase_client, discord_client
from .string_manipulation import build_path
from .views_factory import get_player_message_views
from pathlib import Path


async def backup_music_services():
    music_services = shared_memory.guild_music_services
    gms = {}
    for guild_id, guild_music_service in music_services.items():
        if not guild_music_service.voice_client or not guild_music_service.voice_client.is_connected():
            continue
        gms[guild_id] = guild_music_service.export_gms_to_dict()

    gms_backup = json.dumps(gms)
    await firebase_client.set_gms(gms_backup)
    return len(gms)


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


async def reset_music_player_message(guild):
    from utils.embed_factory import make_initial_player_message_embed
    guild_prefs = shared_memory.guilds_prefs[guild.id]
    if not guild_prefs.music_player_message:
        return
    player_embed = make_initial_player_message_embed(guild)
    player_views = get_player_message_views()
    try:
        message = discord_client\
            .get_channel(guild_prefs.music_channel)\
            .get_partial_message(guild_prefs.music_player_message)
        await message.edit(embed=player_embed, view=player_views)
    except (discord.NotFound, discord.Forbidden):
        return
    except Exception as e:
        print(f"Couldn't reset music player message for guild {guild.id} "
              f"in channel {guild_prefs.music_channel} "
              f"for message {guild_prefs.music_player_message}. \n{e}")
