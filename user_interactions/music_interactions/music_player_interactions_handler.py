import asyncio
import json
import os
import traceback
from math import ceil

import discord

from actions import send_message
from components.music_components.spotify_music_component import SpotifyMusicComponent
from services.third_party.youtube import YoutubeService
from utils.embed_factory import quick_embed, make_music_library_embed, make_music_history_embed
from globals_ import shared_memory
from globals_.clients import discord_client
from globals_.constants import BotLogLevel, MusicVCLoopMode, next_music_vc_loop_mode, MusicTrackSource, MusicVCState, \
    BOT_OWNER_ID, Colour, MusicServiceMode, MusicLogAction
from utils.helpers import reset_music_player_message, process_music_play_arguments, get_music_library_views,\
    build_path, get_history_embed_views
from utils.exceptions import MusicVoiceConnectionException
from models.music_library import Playlist
from services.background.music_service import GuildMusicService
from utils.decorators import interaction_handler
from user_interactions.modals.music_player_modals import MusicPlayerAddTrackModal, MusicPlayerReportModal
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler
from user_interactions.music_interactions.music_history_interactions_handler import MusicHistoryInteractionsHandler
from user_interactions.music_interactions.music_library_interactions_handler import MusicLibraryInteractionsHandler


class MusicPlayerInteractionsHandler(MusicInteractionsHandler):

    def __init__(self, source_interaction: discord.Interaction):
        super().__init__(source_interaction=source_interaction)
        self.guild_prefs = shared_memory.guilds_prefs[self.guild.id]
        self.music_service: GuildMusicService = shared_memory.guild_music_services.get(self.guild.id)
        self.member = self.source_interaction.guild.get_member(self.source_interaction.user.id)
        self.voice_client = self.guild.voice_client
        self.youtube_service = YoutubeService()
        self.spotify_music_component = SpotifyMusicComponent()

    async def handle_action(self, action: str):
        if not hasattr(self, f"_handle_{action.lower()}"):
            self.error_logger.log(f"Music player action handler not found: {action}")
        action_handler = getattr(self, f"_handle_{action.lower()}")
        try:
            await action_handler(self.source_interaction)
        except Exception as e:
            self.error_logger.log(f"Error encountered while handling music player interaction: {e}\n"
                                  f"{traceback.format_exc()}", level=BotLogLevel.ERROR)
            try:
                await self._refresh_player_embed_and_views()
                if not self.source_interaction.response.is_done():
                    self.source_interaction.response.send_message(f"I am facing an issue right now. "
                                                                  f"We've been notified and will fix it ASAP.",
                                                                  ephemeral=True,
                                                                  delete_after=5)
            except Exception:
                pass
            if not self.source_interaction.response.is_done():
                try:
                    await self.source_interaction.response.defer()
                except (discord.ClientException, discord.HTTPException, discord.NotFound):
                    pass
        if not self.source_interaction.response.is_done():
            self.error_logger.log(f"Music player handler did not respond to interaction: {action}\n"
                                  f"Interaction data: {self.source_interaction.data}")
            try:
                await self.source_interaction.response.defer()
            except (discord.ClientException, discord.HTTPException, discord.NotFound):
                pass

    @interaction_handler
    async def _handle_connect(self, _):
        try:
            self.voice_client = await self.check_playablity_and_connect(raise_=True)
        except MusicVoiceConnectionException as e:
            return await self.source_interaction.response.send_message(str(e), ephemeral=True, delete_after=5)

        await self.source_interaction.response.defer()
        if not self.music_service:
            self.music_service = self._initiate_guild_music_service()
        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.CONNECTED_BOT)

    @interaction_handler
    async def _handle_disconnect(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return

        if self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
        else:
            channel = await self.member_voice_channel.connect()
            await channel.disconnect(force=True)

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.defer()

        await self._delete_guild_music_service()
        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.DISCONNECTED_BOT)

    @interaction_handler
    async def _handle_pause(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            await self.source_interaction.response.send_message("Nothing to pause.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.defer()

        await self.music_service.pause_playback()
        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.PAUSED_PLAYBACK)

    @interaction_handler
    async def _handle_resume(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service or not self.music_service.queue:
            await self.source_interaction.response.send_message("Nothing to resume.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.defer()

        self.music_service.resume_playback()
        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.RESUMED_PLAYBACK)

    @interaction_handler
    async def _handle_skip(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            await self.source_interaction.response.send_message("Nothing to skip.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.defer()

        await self.music_service.skip_current_track()
        await self.music_logger_component.log_music_action(action=MusicLogAction.SKIPPED_TRACK)

    @interaction_handler
    async def _handle_shuffle(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service or not self.music_service.queue:
            await self.source_interaction.response.send_message("Nothing to shuffle.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        self.music_service.shuffle_queue()

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.send_message("Queue shuffled.", ephemeral=True, delete_after=5)

        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.SHUFFLED_QUEUE)

    @interaction_handler
    async def _handle_loop(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service or not self.music_service.queue:
            await self.source_interaction.response.send_message("Nothing to loop.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        next_loop_mode = next_music_vc_loop_mode[self.music_service.loop_mode]
        loop_mode_text = f"Change loop mode from {self.music_service.loop_mode} to {next_loop_mode.lower()}?"
        if next_loop_mode == MusicVCLoopMode.ALL:
            loop_mode_text += f" This will loop the entire queue.."
        if next_loop_mode == MusicVCLoopMode.NONE:
            loop_mode_text += f" This will disable looping.."
        if next_loop_mode == MusicVCLoopMode.ONE:
            loop_mode_text += f" This will loop only the current track.."

        self.music_service.change_loop_mode(next_loop_mode)

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.send_message(f"Loop mode changed to {next_loop_mode}.",
                                                                ephemeral=True, delete_after=5)

        await self._refresh_player_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.CHANGED_LOOP_MODE,
                                                           context_value=next_loop_mode)

    @interaction_handler
    async def _handle_refresh(self, _):
        if not await self._check_for_voice_channels():
            await self._refresh_player_embed_and_views()
            return
        await self.source_interaction.response.defer()
        self.info_logger.log(f"Refresh player requested by {self.source_interaction_user}"
                             f" ({self.source_interaction_user.id}) in {self.guild} ({self.guild.id})")
        await self._refresh_player_embed_and_views()

    @interaction_handler
    async def _handle_previous_page(self, _):
        if not self.music_service or not self.music_service.queue:
            return
        await self.source_interaction.response.defer()
        await self.music_service.refresh_player(page_adjustment=-1)

    @interaction_handler
    async def _handle_next_page(self, _):
        if not self.music_service or not self.music_service.queue:
            return
        await self.source_interaction.response.defer()
        await self.music_service.refresh_player(page_adjustment=+1)

    @interaction_handler
    async def _handle_favorite(self, _):
        if not self.music_service or not self.music_service.queue:
            await self.source_interaction.response.send_message("Nothing to favorite.", ephemeral=True, delete_after=5)
            return await self._refresh_player_embed_and_views()

        music_library = await self.library_music_component.get_user_music_library(
            user_id=self.source_interaction_user.id
        )

        if not music_library.playlists:
            playlist = \
                music_library.add_playlist(Playlist.get_default_playlist(user_id=self.source_interaction_user.id))
        elif music_library.get_playlist_by_name("Favorites"):
            playlist = \
                music_library.get_playlist_by_name("Favorites")
        else:
            playlist = \
                music_library.create_new_playlist(user_id=self.source_interaction_user.id, name="Favorites")

        current_track = self.music_service.current_track
        playlist.add_track(youtube_id=current_track["url"].split('=')[1],
                           title=current_track["title"],
                           duration=current_track["duration"],
                           thumbnail_url=current_track["thumbnail_url"])

        await self.library_music_component.sync_library_to_db(music_library=music_library)
        await self.source_interaction.response.send_message(
            f"`{current_track['title']}` added to your `{playlist.name}` playlist. View all of your playlists using "
            f"`/music library` command.",
            ephemeral=True,
            delete_after=10
        )

    @interaction_handler
    async def _handle_add_track(self, _):
        return await self.source_interaction.response.send_modal(MusicPlayerAddTrackModal(interactions_handler=self))

    async def handle_add_track_modal_submit(self, inter, input_text):
        if not await self._check_for_voice_channels(interaction=inter):
            await self._refresh_player_embed_and_views()
            return
        self.voice_client = self.voice_client or self.check_playablity_and_connect()
        if not self.music_service:
            self._initiate_guild_music_service()

        if self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await inter.response.send_message(
                embed=quick_embed("You can't add tracks while in radio mode.", emoji='❌', color=Colour.RED)
            )
        await inter.response.send_message(embed=quick_embed("Adding to queue..."),
                                          ephemeral=True)
        track_count = await self._handle_add_to_queue(input_text=input_text, interaction=inter)
        if track_count:
            await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK,
                                                               context_count=track_count)

    @interaction_handler
    async def _handle_report(self, _):
        return await self.source_interaction.response.send_modal(MusicPlayerReportModal(interactions_handler=self))

    async def handle_report_modal_submit(self, inter, input_text):
        await inter.response.send_message(embed=quick_embed("Thank you for the feedback. "
                                                            "We'll work on fixing the issue ASAP and "
                                                            "will inform you once the issue is fixed."),
                                          ephemeral=True)

        await send_message(f"Received music player feedback",
                           embed=quick_embed(input_text, bold=False, emoji=None,
                                             fields_values={
                                                 "User": f"**{inter.user}** ({inter.user.id})",
                                                 "Channel": f"**{self.channel}** ({self.channel.id})",
                                                 "Guild": f"**{self.guild}** ({self.guild.id})",
                                             }),
                           channel=discord_client.get_user(BOT_OWNER_ID))

    @interaction_handler
    async def _handle_history(self, _):
        guild_history_path = build_path(["media", "music", "history", f"{self.guild.id}.json"])
        history = {}
        if os.path.isfile(guild_history_path):
            with open(guild_history_path, 'r') as file:
                history = json.load(file)
        if not history:
            return await self.source_interaction.response.send_message("No playback history for this server (yet.)",
                                                                       ephemeral=True,
                                                                       delete_after=5)
        history = list(history.values())
        history.reverse()
        page = 1
        history_interactions_handler = MusicHistoryInteractionsHandler(
            source_interaction=self.source_interaction,
            history_list=history,
            page=page,
        )
        first_index = (page - 1) * 10
        last_index = first_index + 10
        track_index_title_map = {index: track['title'] for index, track
                                 in enumerate(history[first_index:last_index], first_index)}
        view = get_history_embed_views(interactions_handler=history_interactions_handler, show_previous=page > 1,
                                       show_next=(ceil(len(history) / 10)) > page,
                                       track_index_title_map=track_index_title_map)
        embed = make_music_history_embed(guild=self.guild, history=history, page=1)
        await self.source_interaction.response.send_message(content=None, embed=embed, view=view, ephemeral=True)

    @interaction_handler
    async def _handle_library(self, _):
        music_library = await self.library_music_component.get_user_music_library(
            user_id=self.source_interaction_user.id
        )
        interactions_handler = MusicLibraryInteractionsHandler(
            source_interaction=self.source_interaction,
            music_library=music_library,
            library_page=1,
            is_library_command=True
        )
        embed = make_music_library_embed(music_library, page=1)
        views = get_music_library_views(page=1,
                                        page_count=ceil(len(music_library.playlists) / 10),
                                        playlists=music_library.playlists,
                                        interactions_handler=interactions_handler)
        await self.source_interaction.response.send_message(content=None, embed=embed, view=views, ephemeral=True)

    @interaction_handler
    async def _handle_switch_to_radio(self, _):
        if not await self._check_for_voice_channels(interaction=self.source_interaction):
            await self._refresh_player_embed_and_views()
            return
        if not self.music_service:
            self.voice_client = self.voice_client or self.check_playablity_and_connect()
            if not self.voice_client:
                return
            self._initiate_guild_music_service()
        if self.music_service.service_mode == MusicServiceMode.RADIO:
            return await self.source_interaction.response.send_message(
                embed=quick_embed("You're already in radio mode.", emoji='❌', color=Colour.RED),
                ephemeral=True,
                delete_after=5
            )
        await self.source_interaction.response.defer()
        await self.music_service.change_service_mode(service_mode=MusicServiceMode.RADIO)
        await self.music_service.refresh_player()

        await self.music_logger_component.log_music_action(action=MusicLogAction.SWITCHED_TO_RADIO)

    async def _refresh_player_embed_and_views(self):
        if self.music_service:
            await self.music_service.refresh_player()
        else:
            await reset_music_player_message(self.guild)

    async def _handle_add_to_queue(self, input_text, interaction):
        url_details, search_term, error_message = process_music_play_arguments(input_text)
        if error_message:
            await interaction.edit_original_response(
                embed=quick_embed(error_message, emoji='❌', color=Colour.RED)
            )
            return 0
        is_playlist = url_details and url_details['is_playlist']
        track_source = url_details.get('source') if url_details else None
        number_of_tracks = 0
        if url_details:
            if track_source == MusicTrackSource.YOUTUBE:
                url = url_details['url']
            elif track_source == MusicTrackSource.SPOTIFY:
                if is_playlist:
                    playlist_id = url_details['id']
                    is_album = url_details.get('is_album')
                    tracks_names = await self.spotify_music_component.get_playlist_tracks_names(
                        playlist_id=playlist_id,
                        is_album=is_album,
                        with_retry=True
                    )
                    number_of_tracks = len(tracks_names)
                    if tracks_names is None:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"Couldn't find this {'album' if is_album else 'playlist'}"
                                              f" on Spotify. Please try again in a second.",
                                              emoji='❕', color=Colour.RED)
                        )
                        return 0
                    elif not tracks_names:
                        await interaction.edit_original_response(
                            embed=quick_embed(f"This {'album' if is_album else 'playlist'} is empty.",
                                              emoji='❕', color=Colour.RED)
                        )
                        return 0
                    await interaction.edit_original_response(
                        embed=quick_embed(f"Adding {len(tracks_names)} tracks to queue, please wait...")
                    )
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
                        interaction.edit_original_response(
                            embed=quick_embed(f"Couldn't find track.", emoji='❕', color=Colour.RED)
                        )
                        return 0
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

        if track_source == MusicTrackSource.YOUTUBE and is_playlist:
            tracks_info = await self.music_service.add_youtube_playlist_to_queue(
                url=url,
                added_by=self.source_interaction_user.id,
                channel=self.channel
            )
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
                                                                     added_by=self.source_interaction_user.id,
                                                                     refresh_player=True)
            if not track_info:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Couldn't queue this track.", emoji='❕', color=Colour.RED)
                )
                return 0
            if not is_playlist:
                await interaction.edit_original_response(
                    embed=quick_embed(f"Added `{track_info['title']}` to queue.",
                                      thumbnail_url=track_info['tiny_thumbnail_url'])
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
                                                                     added_by=self.source_interaction_user.id,
                                                                     refresh_player=False)
            if not track_info:
                failed_tracks += 1
        await interaction.edit_original_response(
            embed=quick_embed(f"Finished adding {number_of_tracks - failed_tracks} tracks to queue." +
                              (f" {failed_tracks} tracks couldn't be queued." if failed_tracks else ""))
        )
        await self._refresh_player_embed_and_views()
