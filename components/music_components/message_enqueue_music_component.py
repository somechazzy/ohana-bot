import asyncio

import discord

from actions import send_embed, delete_message_from_guild
from components.music_components.base_music_component import MusicComponent
from globals_ import shared_memory
from models.guild import GuildPrefs
from services.background.music_service import GuildMusicService
from .youtube_music_component import YoutubeMusicComponent
from .spotify_music_component import SpotifyMusicComponent
from .music_logger_component import MusicLoggerComponent
from globals_.constants import MusicTrackSource, MusicServiceMode, Colour, MusicVCState, MusicLogAction, BotLogLevel, \
    MusicVCLoopMode
from utils.helpers import process_music_play_arguments, convert_seconds_to_numeric_time


class MessageEnqueueMusicComponent(MusicComponent):
    # for handling legacy queueing command (as direct messages in player channel)

    def __init__(self, message: discord.Message, guild_prefs: GuildPrefs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_music_component = YoutubeMusicComponent(**kwargs)
        self.spotify_music_component = SpotifyMusicComponent(**kwargs)
        self.youtube_service = self.youtube_music_component.youtube_service

        self.message = message
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild
        self.guild_prefs = guild_prefs
        self.author_voice_channel = None
        self.bot_voice_channel = None
        self.set_author_and_bot_voice_channels()
        self.voice_client = None
        self.music_service = shared_memory.guild_music_services.get(self.guild.id) if self.guild else None
        self.delete_after = 3

    async def handle_message(self):
        self.info_logger.log(f"Enqueue command from {self.author}/{self.author.id}."
                             f" Channel: {self.message.channel.id}.", log_to_discord=False,
                             level=BotLogLevel.LEGACY_MUSIC_ENQUEUE,
                             guild_id=self.guild.id,
                             user_id=self.author.id)

        await delete_message_from_guild(message=self.message, reason="Music channel")

        if self.bot_voice_channel and self.author not in self.bot_voice_channel.members:
            await send_embed("Join my voice channel first.", self.channel, delete_after=self.delete_after)
            return

        if not self.message.content.strip():
            return await send_embed("What should I play?", self.channel, delete_after=self.delete_after)

        if not self.bot_voice_channel and self.guild.id in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id].voice_client = None
            del shared_memory.guild_music_services[self.guild.id]
            self.delete_guild_music_service()

        if not await self.attempt_joining_vc_channel_of_author():
            return

        if not self.music_service:
            self.initiate_guild_music_service()

        number_of_tracks = 0

        if self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await send_embed("Switch to Player in order to queue tracks.", self.channel,
                                    delete_after=self.delete_after)

        url_details, search_term, error_message = process_music_play_arguments(self.message.content.strip())
        is_playlist = url_details and url_details['is_playlist']

        track_source = url_details.get('source') if url_details else None
        send_final_track_feedback_message = True
        if error_message:
            return await send_embed(error_message, self.channel, emoji='❌', color=Colour.RED,
                                    delete_after=self.delete_after)
        elif url_details:
            if track_source == MusicTrackSource.YOUTUBE:
                url = url_details['url']
            elif track_source == MusicTrackSource.SPOTIFY:
                if is_playlist:
                    playlist_id = url_details['id']
                    is_album = url_details.get('is_album')
                    tracks_names = \
                        await self.spotify_music_component.get_playlist_tracks_names(playlist_id=playlist_id,
                                                                                     is_album=is_album)
                    if not tracks_names:
                        return await send_embed(f"Couldn't find this {'album' if is_album else 'playlist'}"
                                                f" on Spotify. Please try again in a second.", self.channel,
                                                emoji='❕', delete_after=self.delete_after)
                    sent_message = await send_embed(f"Adding {len(tracks_names)} tracks to queue,"
                                                    f" please wait...", self.channel, delete_after=self.delete_after)
                    number_of_tracks = len(tracks_names)
                    search_results = await self.youtube_service.get_search_results(tracks_names[0], 1)
                    url = search_results[0]['url']
                    tracks_names = tracks_names[1:]
                    if tracks_names:
                        asyncio.get_event_loop().create_task(self._search_and_add_tracks_by_names(tracks_names,
                                                                                                  sent_message))
                    else:
                        await send_embed(f"Finished adding 1 track to queue.", self.channel,
                                         delete_after=self.delete_after)
                    send_final_track_feedback_message = not self.music_service.queue
                else:
                    number_of_tracks = 1
                    track_id = url_details['id']
                    track_name = await self.spotify_music_component.get_track_name(track_id=track_id)
                    if not track_name:
                        return await send_embed(f"Couldn't find track on Spotify.", self.channel,
                                                emoji='❕', delete_after=self.delete_after)
                    search_results = await self.youtube_service.get_search_results(track_name, 1)
                    if not search_results:
                        return await send_embed(f"Couldn't find track.", self.channel, emoji='❕',
                                                delete_after=self.delete_after)
                    url = search_results[0]['url']
            else:
                return await send_embed(f"Source `{url_details['source']}` not implemented.", self.channel,
                                        emoji='❌', color=Colour.RED, delete_after=self.delete_after)
        else:
            search_results = await self.youtube_service.get_search_results(search_term)
            if not search_results:
                return await send_embed(f"Couldn't find track.", self.channel,
                                        emoji='❕', delete_after=self.delete_after)
            url = search_results[0]['url']

        if track_source == MusicTrackSource.YOUTUBE and is_playlist:
            tracks_info = await self.music_service.add_youtube_playlist_to_queue(url=url, added_by=self.author.id,
                                                                                 channel=self.channel)
            if not tracks_info:
                return await send_embed(f"Couldn't queue this playlist.", self.channel,
                                        emoji='❕', delete_after=self.delete_after)
            number_of_tracks = len(tracks_info)
            await send_embed(f"Adding {len(tracks_info)} tracks to queue, please wait...", self.channel,
                             delete_after=self.delete_after)
        else:
            track_info = await self.music_service.add_track_to_queue(url=url, added_by=self.author.id,
                                                                     refresh_player=True)
            if send_final_track_feedback_message and self.music_service.current_track != track_info:
                await self._send_final_feedback_message_for_track_add(track_info)
        await self.music_service.refresh_player()

        if self.music_service.state != MusicVCState.PLAYING:
            i = 0
            while not self.music_service.queue and is_playlist:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            asyncio.get_event_loop().create_task(self.music_service.start_worker())

        if number_of_tracks:
            await MusicLoggerComponent(guild_id=self.guild.id, actor_id=self.author.id, actor_name=self.author.name) \
                .log_music_action(action=MusicLogAction.ADDED_TRACK, context_count=number_of_tracks)

    async def _search_and_add_tracks_by_names(self, tracks_names, parent_message):
        number_of_tracks = len(tracks_names) + 1
        failed_tracks = 0
        for track_name in tracks_names:
            search_results = await self.youtube_service.get_search_results(track_name, 1)
            if not search_results:
                failed_tracks += 1
            url = search_results[0]['url']
            track_info = await self.music_service.add_track_to_queue(url, self.author.id, refresh_player=False)
            if not track_info:
                failed_tracks += 1
        await send_embed(f"Finished adding {number_of_tracks - failed_tracks} tracks to queue." +
                         (f" {failed_tracks} tracks couldn't be queued." if failed_tracks else ""),
                         self.channel, reply_to=parent_message, delete_after=self.delete_after)
        await self.music_service.refresh_player()

    def set_author_and_bot_voice_channels(self):
        self.author_voice_channel =\
            self.author.voice.channel if self.guild and self.author.voice and self.author.voice.channel else None
        self.bot_voice_channel =\
            self.guild.me.voice.channel if self.guild and self.guild.me.voice \
            and self.guild.me.voice.channel and self.guild else None

    async def attempt_joining_vc_channel_of_author(self):
        self.set_author_and_bot_voice_channels()
        if not self.author_voice_channel:
            await send_embed("You must join a voice channel first.", self.channel,
                             emoji='❌', color=Colour.RED, reply_to=self.message, delete_after=self.delete_after)
            return False
        if self.bot_voice_channel:
            if self.bot_voice_channel.id != self.author_voice_channel.id and\
                    len(self.bot_voice_channel.members) > 1:
                await send_embed("I'm already in a different voice channel.", self.channel,
                                 delete_after=self.delete_after)
                return False
        missing_permission = self.bot_can_connect_and_speak_in_vc(self.author_voice_channel)
        if missing_permission:
            await send_embed(f"I need the `{missing_permission}` permission "
                             f"on the voice channel for this command.", self.channel,
                             emoji='❌', color=Colour.RED, reply_to=self.message, delete_after=self.delete_after)
            return False
        try:
            self.voice_client = self.guild.voice_client or await self.author.voice.channel.connect()
        except discord.ClientException as e:
            if "already connected" in str(e).lower():
                await self.guild.voice_client.disconnect(force=True)
                return await self.author.voice.channel.connect()
            else:
                raise e
        return True

    def bot_can_connect_and_speak_in_vc(self, voice_channel=None):
        if not voice_channel:
            voice_channel = self.author_voice_channel
        bot_member = self.channel.guild.me
        bot_permissions = voice_channel.permissions_for(bot_member)
        if bot_permissions.administrator:
            return
        if not bot_permissions.connect:
            return 'connect'
        if not bot_permissions.speak:
            return 'speak'
        if not bot_permissions.use_voice_activation:
            return 'use_voice_activation'

    def initiate_guild_music_service(self):
        if not self.voice_client:
            self.voice_client = self.guild.voice_client
        shared_memory.guild_music_services[self.guild.id] = GuildMusicService(
            guild_id=self.guild.id,
            voice_channel_id=self.author_voice_channel.id,
            voice_client=self.voice_client,
            text_channel=self.channel
        )
        shared_memory.guild_music_services[self.guild.id].state = MusicVCState.CONNECTED
        self.music_service: GuildMusicService = shared_memory.guild_music_services[self.guild.id]
        asyncio.get_event_loop().create_task(self.music_service.initiate_dc_countdown())
        return shared_memory.guild_music_services[self.guild.id]

    def delete_guild_music_service(self):
        if self.guild.id in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id].queue = []
            shared_memory.guild_music_services[self.guild.id].currently_played_track_index = 0
            shared_memory.guild_music_services[self.guild.id].loop_mode = MusicVCLoopMode.NONE
            shared_memory.guild_music_services.pop(self.guild.id)
        self.music_service = None

    async def _send_final_feedback_message_for_track_add(self, track_info):
        if not track_info:
            return await send_embed(f"Couldn't play this track.", self.channel,
                                    emoji='❕', delete_after=self.delete_after)
        time_left = self.music_service.calculate_time_to_queue_end() - track_info['duration']
        fields_values = {"Duration": track_info['duration_text']}
        if self.music_service.loop_mode != MusicVCLoopMode.ONE and\
                self.music_service.current_track != track_info:
            fields_values["Wait time"] = convert_seconds_to_numeric_time(time_left)
        await send_embed(f"Added `{track_info['title']}` to queue.",
                         self.channel, delete_after=self.delete_after, thumbnail_url=track_info['tiny_thumbnail_url'],
                         fields_values=fields_values)

    def has_music_channel(self):
        return self.guild_prefs.music_channel and self.guild.get_channel(self.guild_prefs.music_channel)
