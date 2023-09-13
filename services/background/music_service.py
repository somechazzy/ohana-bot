import asyncio
import os
import random
import traceback
from copy import deepcopy
from math import ceil
from typing import Union

import discord
from discord import ClientException, NotFound

from actions import send_embed
from components.music_components.youtube_music_component import YoutubeMusicComponent
from globals_.clients import discord_client
from internal.bot_logger import InfoLogger, ErrorLogger
from globals_ import shared_memory
from models.music_stream import MusicStream
from utils.helpers import convert_seconds_to_numeric_time, build_path, add_track_to_guild_music_history, \
    get_player_message_views, get_radio_message_views
from globals_.constants import MusicVCState, MusicVCLoopMode, next_music_vc_loop_mode, MusicServiceMode, \
    DEFAULT_PLAYER_MESSAGE_CONTENT, DEFAULT_RADIO_MESSAGE_CONTENT
from utils.embed_factory import make_player_message_embed, make_radio_message_embed
from datetime import datetime, timedelta


class GuildMusicService:

    def __init__(self, guild_id, voice_channel_id, voice_client, text_channel):
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.voice_client = voice_client
        self.text_channel, self.music_channel, self.player_message_id =\
            self.get_channels_and_player_info(guild_id, text_channel)
        self.queue = list()
        self.state = MusicVCState.DISCONNECTED
        self.loop_mode = MusicVCLoopMode.NONE
        self.currently_played_track_index = 0
        self.current_track_progress = 0
        self.player_page = 1
        self._BASE_FFMPEG_OPTIONS = {'before_options': '-reconnect 1 ',
                                     'options': '-vn -ss 0'}
        self._adjust_indices = False
        self._last_refresh_time = datetime.utcnow().timestamp() - 3
        self.youtube_music_component = YoutubeMusicComponent()
        self.info_logger = InfoLogger(component='MusicService')
        self.error_logger = ErrorLogger(component='MusicService')

        self.radio_stream: Union[MusicStream, None] = None
        self.service_mode = MusicServiceMode.PLAYER

    async def start_worker(self, pause_immediately=False):
        await self.change_service_mode(service_mode=MusicServiceMode.PLAYER)
        self._adjust_indices = False
        guild = discord_client.get_guild(self.guild_id)
        voice_channel = discord_client.get_channel(self.voice_channel_id)
        try:
            if not guild.me.voice or not guild.me.voice.channel or \
                    guild.me.voice.channel.id != self.voice_channel_id or not self.voice_client:
                self.voice_client = guild.voice_client or await voice_channel.connect()
        except discord.ClientException as e:
            if "already connected" in str(e).lower():
                await guild.voice_client.disconnect(force=True)
                self.voice_client = await voice_channel.connect()
            else:
                raise e
        while self.queue and self.voice_client and self.voice_client.is_connected():
            self.current_track_progress = 0
            self.state = MusicVCState.PLAYING
            if self._adjust_indices:
                self._adjust_currently_played_track_index()
            else:
                self._adjust_indices = True
            if not self.queue:
                break
            track = await self._get_current_track()
            audio_source = await self._get_audio_source(track.get('audio_url'), seek_to_second=track.get('seek_to'))
            try:
                self.voice_client.play(source=audio_source)
            except ClientException as e:
                if "already playing" in str(e).lower():
                    return
                elif "not connected" in str(e).lower():
                    await voice_channel.connect()
                    self.voice_client.play(source=audio_source)
                else:
                    self.error_logger.log(f"Error while playing audio (.play() call): {e}\n{traceback.format_exc()}")
            if pause_immediately:
                await self.pause_playback()
                pause_immediately = False
            if track['seek_to']:
                self.current_track_progress = track['seek_to']
            track['seek_to'] = 0 if track['reset_seek'] else track['seek_to']
            track['reset_seek'] = False
            asyncio.get_event_loop().create_task(add_track_to_guild_music_history(self.current_track, self.guild_id))
            asyncio.get_event_loop().create_task(self.refresh_player())
            while self.voice_client and self.voice_client.is_playing() or self.voice_client.is_paused():
                await asyncio.sleep(1)
                if self.voice_client.is_playing():
                    self.current_track_progress += 1
                    if self.current_track_progress % 17 == 0:
                        asyncio.get_event_loop().create_task(self.refresh_player())
        if not self.voice_client or not self.voice_client.is_connected():
            return
        self.state = MusicVCState.CONNECTED
        self.queue = []  # important to rid of anything that may have gotten it stuck
        await self.refresh_player()
        await self.initiate_dc_countdown()

    async def add_track_to_queue(self, url, added_by, play_immediately=False, seek_to=0, refresh_player=False):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        if url not in shared_memory.cached_youtube_info:
            shared_memory.cached_youtube_info[url] = await self.youtube_music_component.get_youtube_track_info(url=url)
        if not shared_memory.cached_youtube_info[url]:
            return None
        title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details =\
            shared_memory.cached_youtube_info[url]
        track_info = {
            "title": title,
            "thumbnail_url": thumbnail_url,
            "tiny_thumbnail_url": tiny_thumbnail_url,
            "duration": duration,
            "duration_text": convert_seconds_to_numeric_time(seconds=duration),
            "url": url,
            "added_by": added_by,
            "audio_url": audio_url,
            "audio_expiry": audio_expiry,
            "song_details": song_details,
            "seek_to": seek_to,
            "reset_seek": True if seek_to else False,
            "added_timestamp": int(datetime.utcnow().timestamp())
        }
        if play_immediately:
            self.queue.insert(self.currently_played_track_index+1, track_info)
            await self.skip_current_track()
        else:
            self.queue.append(track_info)
        if refresh_player:
            await self.refresh_player()
        return track_info

    async def add_youtube_playlist_to_queue(self, url, added_by, channel):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        if url not in shared_memory.cached_youtube_info:
            shared_memory.cached_youtube_info[url] = \
                await self.youtube_music_component.get_youtube_playlist_tracks(url=url)
        tracks_info = shared_memory.cached_youtube_info[url]
        if not tracks_info:
            return None
        if len(tracks_info) > 1:
            await self.add_track_to_queue(url=tracks_info[0]['youtube_url'], added_by=added_by, refresh_player=True)
            tracks_info_ = tracks_info[1:]
        else:
            tracks_info_ = tracks_info
        if tracks_info_:
            asyncio.get_event_loop().create_task(self.add_tracks_to_queue([track['youtube_url']
                                                                           for track in tracks_info_],
                                                                          added_by, channel))
        return tracks_info

    async def add_tracks_to_queue(self, urls, added_by, channel):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        number_of_tracks = len(urls) + 1
        failed_tracks = 0
        for url in urls:
            track_info = await self.add_track_to_queue(url, added_by, refresh_player=False)
            if not track_info:
                failed_tracks += 1
        await send_embed(f"Finished adding {number_of_tracks - failed_tracks} tracks to queue." +
                         (f" {failed_tracks} tracks couldn't be queued." if failed_tracks else ""),
                         channel, delete_after=3 if self.music_channel else None)
        await self.refresh_player()

    def resume_playback(self):
        if self.voice_client.is_paused():
            self.voice_client.resume()
            return True
        return False

    async def pause_playback(self):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        if not self.voice_client.is_paused():
            self.voice_client.pause()
            return True
        return False

    def change_loop_mode(self, next_mode):
        if not next_mode or next_mode not in [MusicVCLoopMode.ALL, MusicVCLoopMode.NONE, MusicVCLoopMode.ONE]:
            next_mode = next_music_vc_loop_mode[self.loop_mode]
        if next_mode in [MusicVCLoopMode.NONE, MusicVCLoopMode.ONE]:
            self.queue = self.queue[self.currently_played_track_index:]
            self.currently_played_track_index = 0
        self.loop_mode = next_mode
        return next_mode

    async def clear_queue(self, refresh=True):
        current_track = self.current_track
        self.queue = list()
        if current_track:
            self.queue.append(current_track)
        self.currently_played_track_index = 0
        if refresh:
            await self.refresh_player()

    async def move_track(self, track_index, target_index):
        track = self.queue.pop(track_index)
        self.queue.insert(target_index, track)
        await self.refresh_player()
        return track.get('title')

    async def skip_current_track(self):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        if self.loop_mode == MusicVCLoopMode.ONE:
            self.queue.pop(self.currently_played_track_index)
            if self.currently_played_track_index > len(self.queue) - 1:
                self.currently_played_track_index = 0

        if self.loop_mode == MusicVCLoopMode.ALL and len(self.queue) == 1:
            self.queue = []
        self.voice_client.stop()

    def shuffle_queue(self):
        current_track = self.queue.pop(self.currently_played_track_index)
        random.shuffle(self.queue)
        self.queue.insert(self.currently_played_track_index, current_track)

    async def skip_to_track(self, index):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        if self.loop_mode == MusicVCLoopMode.ALL:
            self.currently_played_track_index = index
        elif self.loop_mode == MusicVCLoopMode.ONE:
            self.queue = self.queue[index:]
        else:
            self.currently_played_track_index = 0
            self.queue = self.queue[index:]
        self._adjust_indices = False
        self.voice_client.stop()
        return self.current_track

    async def remove_track(self, index):
        title = self.queue.pop(index).get('title')
        if index < self.currently_played_track_index:
            self.currently_played_track_index -= 1
        await self.refresh_player()
        return title

    async def seek_to(self, seek_to_seconds):
        if self.service_mode != MusicServiceMode.PLAYER:
            return
        current_track = self.current_track
        current_track['seek_to'] = seek_to_seconds
        current_track['reset_seek'] = True
        self._adjust_indices = False
        self.voice_client.stop()
        return True

    async def change_service_mode(self, service_mode=None):
        self.service_mode = service_mode or (MusicServiceMode.PLAYER if self.service_mode == MusicServiceMode.RADIO
                                             else MusicServiceMode.RADIO)
        if service_mode == MusicServiceMode.RADIO:
            await self.clear_queue(refresh=False)
        else:
            self.radio_stream = None
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()

    def set_radio_stream(self, stream, stop_current_radio=True):
        self.radio_stream = stream
        if stop_current_radio and self.voice_client:
            self.voice_client.stop()

    async def start_radio(self, stream=None):
        self.radio_stream = stream or self.radio_stream
        if not self.radio_stream:
            raise ValueError("No radio stream provided")
        await self.change_service_mode(service_mode=MusicServiceMode.RADIO)

        guild = discord_client.get_guild(self.guild_id)
        voice_channel = discord_client.get_channel(self.voice_channel_id)
        try:
            if not guild.me.voice or not guild.me.voice.channel or \
                    guild.me.voice.channel.id != self.voice_channel_id or not self.voice_client:
                self.voice_client = guild.voice_client or await voice_channel.connect()
        except discord.ClientException as e:
            if "already connected" in str(e).lower():
                await guild.voice_client.disconnect(force=True)
                self.voice_client = await voice_channel.connect()
            else:
                raise e
        while self.radio_stream and self.voice_client and self.voice_client.is_connected():
            self.state = MusicVCState.PLAYING
            audio_source = await self.radio_stream.get_ffmpeg_audio_source()
            try:
                self.voice_client.play(source=audio_source)
            except ClientException as e:
                if "already playing" in str(e).lower():
                    return
                elif "not connected" in str(e).lower():
                    await voice_channel.connect()
                    self.voice_client.play(source=audio_source)
                else:
                    self.error_logger.log(f"Error while playing audio (.play() call): {e}\n{traceback.format_exc()}")

            asyncio.get_event_loop().create_task(self.refresh_player())
            self.current_track_progress = 0
            while self.voice_client and self.voice_client.is_playing() and self.radio_stream:
                await asyncio.sleep(1)
                if self.voice_client.is_playing():
                    self.current_track_progress += 1
                    if self.radio_stream.image_refresh_rate and \
                            self.current_track_progress % self.radio_stream.image_refresh_rate == 0:
                        asyncio.get_event_loop().create_task(self.refresh_player())
        if not self.voice_client or not self.voice_client.is_connected():
            return
        self.state = MusicVCState.CONNECTED
        self.queue = []  # important to rid of anything that may have gotten it stuck
        await self.refresh_player()
        await self.initiate_dc_countdown()

    @property
    def current_track(self):
        if self.queue and self.currently_played_track_index >= len(self.queue):
            self.currently_played_track_index = len(self.queue) - 1
        elif not self.queue:
            return {}
        return self.queue[self.currently_played_track_index]

    def _adjust_currently_played_track_index(self):
        if self.loop_mode == MusicVCLoopMode.NONE:
            self.queue.pop(0)
            self.currently_played_track_index = 0
        elif self.loop_mode == MusicVCLoopMode.ONE:
            pass
        elif self.loop_mode == MusicVCLoopMode.ALL:
            if self.currently_played_track_index >= len(self.queue) - 1:
                self.currently_played_track_index = 0
            else:
                self.currently_played_track_index += 1

    async def _get_audio_source(self, audio_url, seek_to_second=0):
        ffmpeg_options = deepcopy(self._BASE_FFMPEG_OPTIONS)
        ffmpeg_options['options'] = ffmpeg_options['options'].replace("-ss 0", f"-ss {seek_to_second}")
        if not audio_url.startswith("http"):
            ffmpeg_options.pop('before_options')
        codec = (await discord.FFmpegOpusAudio.probe(source=audio_url))[0]
        return discord.FFmpegOpusAudio(source=audio_url, codec=codec, bitrate=160, **ffmpeg_options)

    async def initiate_dc_countdown(self):
        for _ in range(60):
            await asyncio.sleep(5)
            if not self.voice_client or self.voice_client.is_playing()\
                    or self.voice_client.is_paused() or not self.voice_client.is_connected():
                return
        await self.voice_client.disconnect(force=True)

    async def _get_current_track(self):
        current_track = self.current_track
        id_ = current_track['url'].split('=')[1]
        audio_path = build_path(relative_path_params=('media', 'music', f'{id_}.opus'))
        if os.path.isfile(audio_path):
            current_track['audio_url'] = audio_path
            current_track['audio_expiry'] = 1900000000
        if int(datetime.utcnow().timestamp()) - current_track['added_timestamp'] < 10:  # if track was just added
            return current_track
        track_expiry_datetime = datetime.fromtimestamp(current_track["audio_expiry"])
        time_by_end_of_track = datetime.utcnow() + timedelta(seconds=current_track["duration"]+10)
        if time_by_end_of_track > track_expiry_datetime:
            shared_memory.cached_youtube_info[current_track['url']] =\
                await self.youtube_music_component.get_youtube_track_info(url=current_track['url'])
            title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details = \
                shared_memory.cached_youtube_info[current_track['url']]
            current_track['audio_url'] = audio_url
            current_track['audio_expiry'] = audio_expiry
        return current_track

    def calculate_time_to_queue_end(self):
        queue_items_left = self.queue[self.currently_played_track_index:]
        seconds = sum([track['duration'] for track in queue_items_left]) - self.current_track_progress
        return seconds

    def export_gms_to_dict(self):
        return {
            "guild_id": self.guild_id,
            "voice_channel_id": self.voice_channel_id,
            "text_channel_id": self.text_channel.id,
            "queue": self.queue,
            "state": self.state,
            "loop_mode": self.loop_mode,
            "currently_played_track_index": self.currently_played_track_index,
            "current_track_progress": self.current_track_progress,
            "player_page": self.player_page,
            "adjust_indices": self._adjust_indices,
            "was_paused": self.voice_client.is_paused(),
            "export_timestamp": int(datetime.utcnow().timestamp()),
            "radio_stream_code": self.radio_stream.code if self.radio_stream else None,
            "service_mode": self.service_mode,
        }

    # noinspection PyTypeChecker
    def import_gms_from_dict(self, gms_dict):
        self.guild_id = gms_dict["guild_id"]
        self.voice_channel_id = gms_dict["voice_channel_id"]
        text_channel = discord_client.get_channel(int(gms_dict["text_channel_id"]))
        self.text_channel, self.music_channel, self.player_message_id = \
            self.get_channels_and_player_info(self.guild_id, text_channel)
        self.music_channel = discord_client.get_channel(int(gms_dict["text_channel_id"]))
        self.queue = list(filter(lambda queue_item: queue_item, gms_dict["queue"]))
        self.state = gms_dict["state"]
        self.loop_mode = gms_dict["loop_mode"]
        self.currently_played_track_index = gms_dict["currently_played_track_index"]
        self.current_track_progress = gms_dict["current_track_progress"]
        self.player_page = gms_dict["player_page"]
        self._adjust_indices = gms_dict["adjust_indices"]
        if self.currently_played_track_index < len(self.queue):
            self.queue[self.currently_played_track_index]['seek_to'] = self.current_track_progress
            self.queue[self.currently_played_track_index]['reset_seek'] = True
        else:
            self.currently_played_track_index = 0
        guild = discord_client.get_guild(self.guild_id)
        self.voice_client = guild.voice_client
        self.radio_stream = shared_memory.music_streams.get(gms_dict.get("radio_stream_code"))
        self.service_mode = gms_dict.get("service_mode")

    async def refresh_player(self, page_adjustment=0, self_call=False):
        # we create a task here for 2 reasons:
        #  1. we don't want to wait for the player to refresh before continuing (especially since it has sleep)
        #  2. we don't want a refresh failure to stop whatever logic we're doing
        asyncio.get_event_loop().create_task(self._refresh_player(page_adjustment=page_adjustment, self_call=self_call))

    async def _refresh_player(self, page_adjustment=0, self_call=False):
        if not self.music_channel:
            return
        if not self.voice_client or not self.voice_client.is_connected():
            return

        self.player_page += page_adjustment
        if self.player_page < 1:
            self.player_page = ceil((len(self.queue) - (1 if self.loop_mode != MusicVCLoopMode.ALL else 0))/10)
        if (self.player_page - 1) * 10 + 1 + (1 if self.loop_mode != MusicVCLoopMode.ALL else 0) > len(self.queue):
            self.player_page = 1

        if datetime.utcnow().timestamp() - self._last_refresh_time < 2:
            if not self_call:
                await asyncio.sleep(2 - (datetime.utcnow().timestamp() - self._last_refresh_time))
                await self.refresh_player(page_adjustment=0, self_call=True)
            return
        self._last_refresh_time = datetime.utcnow().timestamp()

        if self.service_mode == MusicServiceMode.PLAYER:
            content = DEFAULT_PLAYER_MESSAGE_CONTENT
            embed = make_player_message_embed(guild=discord_client.get_guild(self.guild_id))
            views = get_player_message_views(
                is_paused=self.voice_client and self.voice_client.is_paused(),
                is_connected=self.voice_client and self.voice_client.is_connected(),
                display_previous=self.player_page > 1,
                display_next=self.player_page < ceil((len(self.queue)
                                                     - (1 if self.loop_mode != MusicVCLoopMode.ALL else 0)) / 10),
                track_queued=bool(self.queue),
                disable_refresh_button=self.guild_id in shared_memory.GUILDS_WITH_PLAYER_REFRESH_DISABLED
            )
        elif self.service_mode == MusicServiceMode.RADIO:
            content = DEFAULT_RADIO_MESSAGE_CONTENT
            embed = make_radio_message_embed(guild=discord_client.get_guild(self.guild_id))
            views = get_radio_message_views(
                currently_playing_supported=bool(self.radio_stream.status_check) if self.radio_stream else False,
                show_stop_button=self.radio_stream is not None,
                selected_stream_code=self.radio_stream.code if self.radio_stream else None,
            )
        else:
            raise Exception("???")

        if shared_memory.guilds_prefs[self.guild_id].\
                music_player_message_timestamp < datetime.utcnow().timestamp() - 86400:
            await self.recreate_player_message(embed=embed, views=views, content=content)
        else:
            player_message = self.music_channel.get_partial_message(self.player_message_id)
            try:
                await player_message.edit(embed=embed, view=views, content=content)
            except NotFound:
                await self.recreate_player_message(embed=embed, views=views, content=content)
            except Exception as e:
                if "rate limited" in str(e):
                    await self.recreate_player_message(embed=embed, views=views, content=content)
                else:
                    raise e

    async def recreate_player_message(self, embed, views, content=None):
        if self.music_channel and self.player_message_id:
            try:
                player_message = self.music_channel.get_partial_message(self.player_message_id)
                await player_message.delete()
            except NotFound:
                pass
        await self.youtube_music_component.setup_player_channel(guild=discord_client.get_guild(self.guild_id),
                                                                music_channel=self.music_channel,
                                                                send_header=False,
                                                                player_embed=embed,
                                                                player_views=views,
                                                                player_message_content=content)
        self.player_message_id = shared_memory.guilds_prefs[self.guild_id].music_player_message

    @staticmethod
    def get_channels_and_player_info(guild_id, text_channel):
        music_channel_id = shared_memory.guilds_prefs[guild_id].music_channel
        player_message_id = shared_memory.guilds_prefs[guild_id].music_player_message
        if discord_client.get_channel(music_channel_id) and player_message_id:
            text_channel = discord_client.get_channel(music_channel_id)
            music_channel = text_channel
            player_message_id = player_message_id
        else:
            text_channel = text_channel
            music_channel = None
            player_message_id = None
        return text_channel, music_channel, player_message_id
