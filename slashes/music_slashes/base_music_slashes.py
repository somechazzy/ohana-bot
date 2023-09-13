import asyncio
import re

import discord

from components.music_components.library_music_component import LibraryMusicComponent
from components.music_components.music_logger_component import MusicLoggerComponent
from components.music_components.spotify_music_component import SpotifyMusicComponent
from services.third_party.youtube import YoutubeService
from utils.embed_factory import quick_embed
from globals_ import shared_memory
from globals_.constants import MusicVCState, Colour, MusicTrackSource, \
    generic_youtube_title_words, MusicServiceMode
from utils.helpers import process_music_play_arguments, quick_button_views
from utils.exceptions import PlaylistNotFoundException, MusicVoiceConnectionException
from models.music_library import Playlist
from services.background.music_service import GuildMusicService
from slashes.base_slashes import BaseSlashes


class MusicSlashes(BaseSlashes):

    def __init__(self, interaction):
        super().__init__(interaction=interaction)
        self.library_music_component = LibraryMusicComponent()
        self.spotify_music_component = SpotifyMusicComponent()
        self.youtube_service = YoutubeService()
        self.music_library = None
        self.music_service: GuildMusicService = ...
        self.music_logger_component = MusicLoggerComponent(guild_id=self.guild.id,
                                                           actor_id=self.user.id,
                                                           actor_name=self.member.name
                                                           if self.member else self.user.name)

    async def preprocess_and_validate(self, check_for_music_channel=False, **kwargs):
        if not await super().preprocess_and_validate(**kwargs):
            return False
        if check_for_music_channel and not await self.validate_music_channel():
            return False
        self.music_library = await self.library_music_component.get_user_music_library(user_id=self.user.id)
        self.music_service = shared_memory.guild_music_services.get(self.guild.id) if self.guild else None
        return True

    def get_playlist(self, playlist_input) -> Playlist:
        if playlist_input.isnumeric():
            playlist_index = int(playlist_input) - 1
            if len(self.music_library.playlists) <= playlist_index:
                playlist = self.music_library.get_playlist_by_name(playlist_input)
                if not playlist:
                    raise PlaylistNotFoundException()
            else:
                playlist = self.music_library.playlists[playlist_index]
        else:
            playlist = self.music_library.get_playlist_by_name(playlist_input)
            if not playlist:
                raise PlaylistNotFoundException()
        return playlist

    def get_user_music_channel(self):
        return self.member.voice.channel if self.member.voice else None

    def bot_can_connect_and_speak_in_vc(self):
        voice_channel = self.get_user_music_channel()
        bot_member = self.guild.me
        bot_permissions = voice_channel.permissions_for(bot_member)
        if bot_permissions.administrator:
            return
        if not bot_permissions.connect:
            return 'connect'
        if not bot_permissions.speak:
            return 'speak'
        if not bot_permissions.use_voice_activation:
            return 'use_voice_activation'

    async def check_playability_and_connect(self, edit=False, raise_=False):
        if raise_ and edit:
            raise Exception()
        delete_after = self.delete_after(longest=True)
        user_voice_channel = self.get_user_music_channel()
        if not user_voice_channel:
            message = "You must join a voice channel first."
            if edit:
                await self.interaction.edit_original_response(content=message)
            elif raise_:
                raise MusicVoiceConnectionException(message)
            else:
                await self.interaction.response.send_message(content=message, ephemeral=True)
            return False
        if self.guild.me.voice and self.guild.me.voice.channel != user_voice_channel:
            message = "Join my voice channel first."
            if edit:
                await self.interaction.edit_original_response(content=message)
            elif raise_:
                raise MusicVoiceConnectionException(message)
            else:
                await self.interaction.response.send_message(content=message, ephemeral=True)
            return False
        if not self.guild.me.voice:
            missing_permission = self.bot_can_connect_and_speak_in_vc()
            if missing_permission:
                message = f"I need the `{missing_permission}` permission on the voice channel for this command."
                if edit:
                    await self.interaction.edit_original_response(content=message)
                elif raise_:
                    raise MusicVoiceConnectionException(message)
                else:
                    await self.interaction.response.send_message(content=message,
                                                                 delete_after=delete_after)
                return False
            try:
                return await user_voice_channel.connect()
            except discord.ClientException as e:
                if "already connected" in str(e).lower():
                    await user_voice_channel.guild.voice_client.disconnect(force=True)
                    return await user_voice_channel.connect()
                else:
                    raise e
        return self.guild.voice_client

    async def get_or_initiate_guild_music_service(self, voice_client=None,
                                                  edit=False,
                                                  raise_=False) -> GuildMusicService:
        if not voice_client:
            voice_client = await self.check_playability_and_connect(edit=edit, raise_=raise_)
        if self.guild.id not in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id] =\
                GuildMusicService(guild_id=self.guild.id,
                                  voice_channel_id=voice_client.channel.id,
                                  voice_client=voice_client,
                                  text_channel=self.channel)
            shared_memory.guild_music_services[self.guild.id].state = MusicVCState.CONNECTED
            asyncio.get_event_loop().create_task(
                shared_memory.guild_music_services[self.guild.id].initiate_dc_countdown()
            )
        self.music_service = shared_memory.guild_music_services[self.guild.id]
        return self.music_service

    def delete_after(self, long=False, longest=False):
        if self.channel != \
                shared_memory.guild_music_services.get(self.guild.id,
                                                       GuildMusicService(self.guild.id, 0, None, None)).music_channel:
            return None
        return 15 if longest else 5 if long else 3

    @staticmethod
    def youtube_id_to_url(id_):
        return f"https://www.youtube.com/watch?v={id_}"

    async def handle_add_to_queue(self, input_text, interaction=None, play_immediately=False):
        if not interaction:
            interaction = self.interaction
        url_details, search_term, error_message = process_music_play_arguments(input_text)
        if error_message:
            await interaction.edit_original_response(
                embed=quick_embed(error_message, emoji='❌', color=Colour.RED)
            )
            return 0
        is_playlist = url_details and url_details['is_playlist']
        if is_playlist and play_immediately:
            await interaction.edit_original_response(
                embed=quick_embed("This command only works with one track at a time.", emoji='❌', color=Colour.RED)
            )
            return 0
        track_source = url_details.get('source') if url_details else None
        number_of_tracks = 0
        if url_details:
            if track_source == MusicTrackSource.YOUTUBE:
                url = url_details['url']
            elif track_source == MusicTrackSource.SPOTIFY:
                if is_playlist:
                    playlist_id = url_details['id']
                    is_album = url_details.get('is_album')
                    tracks_names = await self.spotify_music_component.get_playlist_tracks_names(playlist_id=playlist_id,
                                                                                                is_album=is_album)
                    if not tracks_names:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Couldn't find this {'album' if is_album else 'playlist'}"
                                              f" on Spotify. Please try again in a second.",
                                              emoji='❕', color=Colour.RED)
                        )
                        return 0
                    number_of_tracks = len(tracks_names)
                    search_results = await self.youtube_service.get_search_results(tracks_names[0], 1)
                    url = search_results[0]['url']
                    tracks_names = tracks_names[1:]
                    if tracks_names:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Adding {len(tracks_names) + 1} tracks to queue, please wait...")
                        )
                        asyncio.get_event_loop().create_task(self._search_and_add_tracks_by_names(tracks_names,
                                                                                                  interaction))
                    else:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Adding `{search_results[0]['title']}` to queue..")
                        )
                else:
                    number_of_tracks = 1
                    track_id = url_details['id']
                    track_name = await self.spotify_music_component.get_track_name(track_id=track_id)
                    if not track_name:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Couldn't find track on Spotify.", emoji='❕', color=Colour.RED)
                        )
                        return 0
                    search_results = await self.youtube_service.get_search_results(track_name, 1)
                    if not search_results:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Couldn't find track.", emoji='❕', color=Colour.RED)
                        )
                    url = search_results[0]['url']
            else:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Source `{url_details['source']}` not implemented.",
                                      emoji='❕',
                                      color=Colour.RED)
                )
                return 0
        else:
            number_of_tracks = 1
            search_results = await self.youtube_service.get_search_results(search_term)
            if not search_results:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Couldn't find track.", emoji='❕', color=Colour.RED)
                )
                return 0
            url = search_results[0]['url']
            track_source = MusicTrackSource.YOUTUBE

        if track_source == MusicTrackSource.YOUTUBE and is_playlist:
            tracks_info = await self.music_service.add_youtube_playlist_to_queue(url=url,
                                                                                 added_by=self.user.id,
                                                                                 channel=self.channel)
            if not tracks_info:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Couldn't queue this playlist.", emoji='❕', color=Colour.RED)
                )
                return 0
            number_of_tracks = len(tracks_info)
            await interaction.edit_original_response(
                embed=quick_embed(f"Adding {len(tracks_info)} tracks to queue, please wait...")
            )
        else:
            track_info = await self.music_service.add_track_to_queue(url=url,
                                                                     added_by=self.user.id,
                                                                     refresh_player=True,
                                                                     play_immediately=play_immediately)
            if not track_info:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Couldn't queue this track.", emoji='❕', color=Colour.RED)
                )
                return number_of_tracks
            if not is_playlist:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Added `{track_info['title']}` to queue.",
                                      thumbnail_url=track_info['tiny_thumbnail_url'],
                                      fields_values={'Duration': track_info['duration_text']})
                )
        await self.music_service.refresh_player()
        if self.music_service.state != MusicVCState.PLAYING:
            i = 0
            while not self.music_service.queue and is_playlist:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            asyncio.get_event_loop().create_task(self.music_service.start_worker())

        return number_of_tracks

    async def _search_and_add_tracks_by_names(self, tracks_names, interaction):
        number_of_tracks = len(tracks_names) + 1
        failed_tracks = 0
        for track_name in tracks_names:
            search_results = await self.youtube_service.get_search_results(track_name, 1)
            if not search_results:
                failed_tracks += 1
            url = search_results[0]['url']
            track_info = await self.music_service.add_track_to_queue(url=url,
                                                                     added_by=self.user.id,
                                                                     refresh_player=False)
            if not track_info:
                failed_tracks += 1
        await interaction.edit_original_response(
            embed=quick_embed(f"Finished adding {number_of_tracks - failed_tracks} tracks to queue." +
                              (f" {failed_tracks} tracks couldn't be queued." if failed_tracks else ""))
        )
        await self.music_service.refresh_player()

    def get_genius_lyrics_searchable_title_for_current_track(self):
        current_track = self.music_service.current_track
        title = f"{current_track['song_details']['artist']}  {current_track['song_details']['title']}".lower().strip()
        if not title:
            title = current_track['title'].lower()
            for generic_youtube_title_word in generic_youtube_title_words:
                title = title.replace(f"{generic_youtube_title_word}", "")
        while re.findall("[(\\[<][^()\\[\\]<>]*[)\\]>]", title):
            title = re.sub("[(\\[<][^()\\[\\]<>]*[)\\]>]", "", title)
        return re.sub(" +", " ", re.sub("-", "", title))

    async def validate_music_channel(self):
        if not self.guild_prefs.music_channel or not self.guild.get_channel(self.guild_prefs.music_channel):
            await self.interaction.response.send_message("You need a music channel in order to play music."
                                                         " Use `/music channel-create` command to create it"
                                                         " or ask an admin to do it.",
                                                         ephemeral=True)
            return False
        if not self.guild.get_channel(self.guild_prefs.music_channel).permissions_for(self.guild.me).send_messages \
                or not self.guild.get_channel(self.guild_prefs.music_channel).permissions_for(self.guild.me).embed_links:
            await self.interaction.response.send_message(
                f"I need permissions to send messages and embed links in the"
                f" music channel ({self.guild.get_channel(self.guild_prefs.music_channel).mention}).",
                ephemeral=True
            )
            return False
        return True

    async def ask_to_switch_to_player_mode(self):
        embed = quick_embed("In order to play something you need to switch to Music Player mode.",
                            bold=False)
        views = quick_button_views(button_callback_map={
            "Switch to Player mode": self._handle_prompt_to_switch_to_player_mode
        },
            styles=[discord.ButtonStyle.green],
            on_timeout=None,
            timeout=None
        )
        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    async def _handle_prompt_to_switch_to_player_mode(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.music_service = shared_memory.guild_music_services.get(self.guild.id)
        if not self.music_service:
            return
        await self.music_service.change_service_mode(service_mode=MusicServiceMode.PLAYER)
        await interaction.delete_original_response()
        await self.music_service.refresh_player()
