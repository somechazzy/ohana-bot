import asyncio
import json
import traceback
from datetime import datetime

import discord

from components.music_components.base_music_component import MusicComponent
from globals_ import shared_memory
from globals_.clients import discord_client, firebase_client
from globals_.constants import BotLogLevel, MusicServiceMode, DEFAULT_PLAYER_MESSAGE_CONTENT
from globals_.settings import settings
from services.background.music_service import GuildMusicService
from utils.helpers import get_player_message_views
from utils.embed_factory import make_initial_player_message_embed


class MusicOnRestartComponent(MusicComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def perform_on_startup_tasks(self):
        await self.reconnect_to_voice_channels()

        gms_to_play, gms_to_pause = await self.restore_music_services()
        for gms in gms_to_play:
            if gms.service_mode == MusicServiceMode.RADIO:
                asyncio.get_event_loop().create_task(gms.start_radio())
            else:
                asyncio.get_event_loop().create_task(gms.start_worker())
        for gms in gms_to_pause:
            asyncio.get_event_loop().create_task(gms.start_worker(pause_immediately=True))

        self.fill_youtube_cache_with_restored_queues()

        await self.reset_music_players()

    async def reconnect_to_voice_channels(self):
        await asyncio.sleep(1)
        reconnected_count = 0
        for guild in discord_client.guilds:
            if guild.me.voice and guild.me.voice.channel:
                try:
                    await guild.me.voice.channel.connect()
                    reconnected_count += 1
                except Exception as e:
                    self.error_logger.log(f"Error while reconnecting to VC after restarting music bot:"
                                          f" {e}.\n{traceback.format_exc()}")
        if reconnected_count:
            self.info_logger.log(f"Reconnected to {reconnected_count} voice channels after restarting music bot.",
                                 level=BotLogLevel.BOT_INFO)

    async def restore_music_services(self):
        gms_string = (await firebase_client.get_gms()).val()
        if not gms_string:
            gms_string = "{}"
        gms_dicts = json.loads(gms_string)
        gms_to_play = []
        gms_to_pause = []
        for guild_id, gms_dict in gms_dicts.items():
            guild_id = int(guild_id)
            if not gms_dict.get('service_mode'):
                gms_dict['service_mode'] = MusicServiceMode.PLAYER
            guild_music_service = GuildMusicService(guild_id, int(gms_dict['voice_channel_id']), None, None)
            guild_music_service.import_gms_from_dict(gms_dict=gms_dict, )
            was_paused = gms_dict['was_paused'] if gms_dict['service_mode'] != MusicServiceMode.RADIO else False
            current_timestamp = int(datetime.utcnow().timestamp())
            attempt_reconnect = current_timestamp - gms_dict.get('export_timestamp', current_timestamp) < 180
            if await self._guild_music_service_playable(guild_music_service, attempt_reconnect=attempt_reconnect):
                if was_paused:
                    gms_to_pause.append(guild_music_service)
                else:
                    gms_to_play.append(guild_music_service)
                shared_memory.guild_music_services[guild_id] = guild_music_service
        await firebase_client.reset_gms()
        if gms_dicts:
            self.info_logger.log(f"Restored {len(gms_dicts)} music services: "
                                 f"{len(gms_to_play)} playing, {len(gms_to_pause)} paused.",
                                 level=BotLogLevel.BOT_INFO)
        return gms_to_play, gms_to_pause

    async def _guild_music_service_playable(self, guild_music_service, attempt_reconnect=False):
        async def attempt_reconnection():
            try:
                guild_music_service.voice_client = \
                    await discord_client.get_channel(guild_music_service.voice_channel_id).connect()
            except discord.ClientException as e:
                if "already connected" in str(e).lower():
                    await guild.voice_client.disconnect(force=True)
                    guild_music_service.voice_client = \
                        await discord_client.get_channel(guild_music_service.voice_channel_id).connect()
                else:
                    self.error_logger.log(f"Error while reconnecting to VC, {e}")
            except Exception as e:
                self.error_logger.log(f"Error while reconnecting to VC, {e}")

        guild = discord_client.get_guild(guild_music_service.guild_id)
        if guild_music_service.service_mode == MusicServiceMode.PLAYER:
            if guild_music_service.queue and not guild_music_service.voice_client and attempt_reconnect:
                await attempt_reconnection()
            return guild_music_service.queue \
                and guild_music_service.voice_client and \
                guild.me in guild.get_channel(guild_music_service.voice_channel_id).members
        elif guild_music_service.service_mode == MusicServiceMode.RADIO:
            if guild_music_service.radio_stream and not guild_music_service.voice_client:
                await attempt_reconnection()
            return guild_music_service.radio_stream and guild_music_service.voice_client \
                and guild.me in guild.get_channel(guild_music_service.voice_channel_id).members

    @staticmethod
    def fill_youtube_cache_with_restored_queues():
        music_services = shared_memory.guild_music_services.values()
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
            if url in shared_memory.cached_youtube_info:
                _, _, _, _, _, existing_audio_expiry, _ = shared_memory.cached_youtube_info[url]
                if existing_audio_expiry > audio_expiry:
                    continue
            if datetime.utcnow() > datetime.fromtimestamp(audio_expiry):
                continue
            shared_memory.cached_youtube_info[url] = \
                title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details

    async def reset_music_players(self):
        for guild_prefs in shared_memory.guilds_prefs.values():
            try:
                music_channel = discord_client.get_channel(guild_prefs.music_channel)
                if music_channel and guild_prefs.guild_id not in shared_memory.guild_music_services:
                    player_message = music_channel.get_partial_message(guild_prefs.music_player_message)
                    if player_message:
                        content = DEFAULT_PLAYER_MESSAGE_CONTENT
                        embed = make_initial_player_message_embed(guild=music_channel.guild)
                        views = get_player_message_views()
                        await player_message.edit(content=content, embed=embed, view=views)
            except Exception as e:
                self.error_logger.log(f"Failed at resetting music player for guild {guild_prefs.guild_id}: {e}",
                                      guild_id=guild_prefs.guild_id,
                                      level=BotLogLevel.MINOR_WARNING, log_to_discord=False)
