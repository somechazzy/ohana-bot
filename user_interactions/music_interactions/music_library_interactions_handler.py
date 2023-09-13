from copy import deepcopy
from datetime import datetime
from math import ceil
import discord

from globals_.constants import Colour, MusicServiceMode, MusicLogAction
from utils.embed_factory import make_music_library_embed, make_playlist_embed, quick_embed
from utils.helpers import get_music_library_views, get_playlist_views
from utils.exceptions import PlaylistDuplicateNameException, PlaylistAddParsingException, \
    MusicVoiceConnectionException
from utils.decorators import interaction_handler
from user_interactions.modals.music_library_modals import MusicLibraryCreatePlaylistModal, \
    MusicLibraryPlaylistAddTrackModal, MusicLibraryPlaylistRemoveTrackModal, MusicLibraryPlaylistRenameModal, \
    MusicLibraryPlaylistCloneModal, MusicLibraryPlaylistMoveTrackModal
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicLibraryInteractionsHandler(MusicInteractionsHandler):

    def __init__(self, source_interaction, music_library, selected_playlist_index=0, library_page=1, playlist_page=1,
                 is_library_command=False):
        super().__init__(source_interaction=source_interaction)
        self.music_library = music_library
        self.selected_playlist_index = selected_playlist_index
        self.page = library_page
        self.playlist_page = playlist_page
        self.is_library_command = is_library_command
        self.last_queued = None
        self.show_playlist_more_button = True

    @interaction_handler
    async def handle_library_previous_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == 1:
            self.page = self.library_page_count
        else:
            self.page -= 1

        await inter.response.defer()
        await self.refresh_library_embed()

    @interaction_handler
    async def handle_library_next_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == self.library_page_count:
            self.page = 1
        else:
            self.page += 1

        await inter.response.defer()
        await self.refresh_library_embed()

    @interaction_handler
    async def handle_create_playlist(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryCreatePlaylistModal(interactions_handler=self))

    async def handle_create_playlist_modal_submit(self, inter, playlist_name):
        try:
            new_playlist = self.music_library.create_new_playlist(user_id=inter.user.id, name=playlist_name)
        except PlaylistDuplicateNameException:
            await inter.response.send_message("You already have a playlist with that name.", ephemeral=True)
            return
        await inter.response.defer()
        await self.refresh_library_embed(note=f"New playlist `{new_playlist.name}` created!")
        await self.sync_library()

    @interaction_handler
    async def handle_library_playlist_select(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        self.selected_playlist_index = int(inter.data["values"][0]) - 1
        self.playlist_page = 1
        await inter.response.defer()
        await self.refresh_playlist_embed()

    @interaction_handler
    async def handle_playlist_play(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        if not self.guild:
            await inter.response.defer()
            return await self.refresh_playlist_embed(note="You can only play in servers.")
        if not await self.validate_music_channel(interaction=inter):
            return

        playlist = self.music_library.playlists[self.selected_playlist_index]

        if not playlist.tracks:
            feedback_message = "Playlist empty!"
            await inter.response.defer()
        elif self.last_queued and self.last_queued + 10 > datetime.utcnow().timestamp():
            feedback_message = "Slow down."
            await inter.response.defer()
        else:
            try:
                voice_client = await self.check_playablity_and_connect(raise_=True)
                music_service = self.get_or_initiate_guild_music_service(voice_channel_id=voice_client.channel.id,
                                                                         voice_client=voice_client)
                if music_service.service_mode != MusicServiceMode.PLAYER:
                    return await self.ask_to_switch_to_player_mode(interaction=inter)

                await inter.response.defer()
                await self.handle_play_playlist_from_view(playlist=playlist, music_service=music_service)
                feedback_message = "Playlist is being queued..."
                self.last_queued = datetime.utcnow().timestamp()
            except MusicVoiceConnectionException as e:
                feedback_message = str(e)
                await inter.response.defer()
        await self.refresh_playlist_embed(note=feedback_message)

        await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK,
                                                           context_count=len(playlist.tracks))

    @interaction_handler
    async def handle_playlist_previous_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.playlist_page == 1:
            self.playlist_page = self.playlist_page_count
        else:
            self.playlist_page -= 1

        await inter.response.defer()
        await self.refresh_playlist_embed()

    @interaction_handler
    async def handle_playlist_next_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.playlist_page == self.playlist_page_count:
            self.playlist_page = 1
        else:
            self.playlist_page += 1

        await inter.response.defer()
        await self.refresh_playlist_embed()

    @interaction_handler
    async def handle_playlist_go_back(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        self.playlist_page = 1
        self.selected_playlist_index = 0
        self.show_playlist_more_button = True
        await inter.response.defer()
        await self.refresh_library_embed()

    @interaction_handler
    async def handle_playlist_add_track(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryPlaylistAddTrackModal(interactions_handler=self))

    async def handle_playlist_add_track_modal_submit(self, inter, track_input):
        await inter.response.send_message(content="Adding track(s)...", ephemeral=True)
        try:
            feedback = await self.library_music_component.add_track_to_playlist(
                playlist_to_add_to=self.music_library.playlists[self.selected_playlist_index],
                track_or_playlist=track_input,
                interaction=inter
            )
        except PlaylistAddParsingException as e:
            feedback = str(e)
        await inter.edit_original_response(content=feedback, embed=None)
        await self.refresh_playlist_embed(note=feedback)
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_show_all_buttons(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        self.show_playlist_more_button = False
        await inter.response.defer()
        await self.refresh_playlist_embed()

    @interaction_handler
    async def handle_playlist_remove_track(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryPlaylistRemoveTrackModal(interactions_handler=self))

    async def handle_playlist_remove_track_modal_submit(self, inter, track_input):
        await inter.response.defer()
        if not track_input.isdigit():
            return await self.refresh_playlist_embed(
                note=f"Invalid track number. Enter a number between 1 and "
                     f"{len(self.music_library.playlists[self.selected_playlist_index].tracks)}.")
        track_index = int(track_input) - 1
        if track_index < 0 or track_index >= len(self.music_library.playlists[self.selected_playlist_index].tracks):
            return await self.refresh_playlist_embed(
                note=f"Invalid track number. Enter a number between 1 and "
                     f"{len(self.music_library.playlists[self.selected_playlist_index].tracks)}.")
        track = self.music_library.playlists[self.selected_playlist_index].remove_track(index=track_index)
        await self.refresh_playlist_embed(note=f"Removed track {track.title}.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_move_track(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryPlaylistMoveTrackModal(interactions_handler=self))

    async def handle_playlist_move_track_modal_submit(self, inter, target_track_index, destination_track_index):
        await inter.response.defer()
        if not target_track_index.isdigit() or not destination_track_index.isdigit():
            return await self.refresh_playlist_embed(
                note=f"Invalid track number. Enter a number between 1 and "
                     f"{len(self.music_library.playlists[self.selected_playlist_index].tracks)}.")
        current_index = int(target_track_index) - 1
        new_index = int(destination_track_index) - 1

        if current_index not in range(len(self.music_library.playlists[self.selected_playlist_index].tracks)) \
                or new_index not in range(len(self.music_library.playlists[self.selected_playlist_index].tracks)):
            return await self.refresh_playlist_embed(
                note=f"Invalid track number. Enter a number between 1 and "
                     f"{len(self.music_library.playlists[self.selected_playlist_index].tracks)}.")

        if current_index == new_index:
            return await self.refresh_playlist_embed(note=f"That's the same position...")

        track = self.music_library.playlists[self.selected_playlist_index].move_track(from_=current_index,
                                                                                      to_=new_index)
        await self.refresh_playlist_embed(note=f"Moved track `{track.title}` to position {new_index + 1}.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_rename(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryPlaylistRenameModal(interactions_handler=self))

    async def handle_playlist_rename_modal_submit(self, inter, playlist_name):
        await inter.response.defer()
        try:
            self.music_library.check_playlist_name_availability(playlist_name)
        except PlaylistDuplicateNameException:
            return await self.refresh_playlist_embed(note=f"Playlist `{playlist_name}` already exists.")
        self.music_library.playlists[self.selected_playlist_index].rename_playlist(new_name=playlist_name)
        await self.refresh_playlist_embed(note=f"Renamed playlist to `{playlist_name}`.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_clone(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(MusicLibraryPlaylistCloneModal(interactions_handler=self))

    async def handle_playlist_clone_modal_submit(self, inter, playlist_name):
        await inter.response.defer()
        try:
            self.music_library.check_playlist_name_availability(playlist_name)
        except PlaylistDuplicateNameException:
            return await self.refresh_playlist_embed(note=f"Playlist `{playlist_name}` already exists.")
        self.music_library.create_new_playlist(
            name=playlist_name,
            tracks=deepcopy(self.music_library.playlists[self.selected_playlist_index].tracks)
        )
        await self.refresh_playlist_embed(note=f"Cloned playlist to `{playlist_name}`.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_clear(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        self.music_library.playlists[self.selected_playlist_index].clear_playlist()
        await inter.response.defer()
        await self.refresh_playlist_embed(note="Playlist cleared.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_delete(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        self.music_library.playlists.pop(self.selected_playlist_index)
        await inter.response.defer()
        await self.refresh_library_embed(note="Playlist deleted.")
        await self.sync_library()

    @interaction_handler
    async def handle_playlist_track_select(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()

        track_index = int(inter.data["values"][0])
        if track_index < 0 or track_index >= len(self.music_library.playlists[self.selected_playlist_index].tracks):
            return await inter.response.defer()
        track = self.music_library.playlists[self.selected_playlist_index].tracks[track_index]

        voice_client = await self.check_playablity_and_connect(raise_=True)
        music_service = self.get_or_initiate_guild_music_service(voice_channel_id=voice_client.channel.id,
                                                                 voice_client=voice_client)
        if music_service.service_mode != MusicServiceMode.PLAYER:
            await self.ask_to_switch_to_player_mode(interaction=inter)
            return self.refresh_playlist_embed(note="Cannot play while in radio mode.")

        await inter.response.defer()
        await self.handle_play_track_from_view(track_url=track.url, voice_client=voice_client)
        await self.refresh_playlist_embed(note=f"Adding track `{track.title}` to queue...")
        await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK,
                                                           context_count=1)

    def get_library_embed_and_views(self, note=None):
        embed = make_music_library_embed(self.music_library, page=self.page, feedback_message=note)
        views = get_music_library_views(page=self.page,
                                        page_count=self.library_page_count,
                                        playlists=self.music_library.playlists,
                                        interactions_handler=self)
        return embed, views

    async def refresh_library_embed(self, note=None):
        self.show_playlist_more_button = True
        embed, views = self.get_library_embed_and_views(note=note)
        await self.source_interaction.edit_original_response(content=None, embed=embed, view=views)

    def get_playlist_embed_and_views(self, note=None, refresh_if_not_found=True):
        if self.selected_playlist_index >= len(self.music_library.playlists):
            if refresh_if_not_found:
                return self.refresh_library_embed(note="Playlist you selected does not exist anymore!")
            else:
                return quick_embed("Playlist you selected does not exist anymore!", color=Colour.WARNING), None
        playlist_to_show = self.music_library.playlists[self.selected_playlist_index]
        embed = make_playlist_embed(playlist=playlist_to_show,
                                    page=self.playlist_page,
                                    feedback_message=note,
                                    from_library=self.is_library_command)

        first_index = (self.playlist_page - 1) * 10
        last_index = first_index + 10
        track_index_title_map = {index: track.title for index, track
                                 in enumerate(playlist_to_show.tracks[first_index:last_index], first_index)}
        views = get_playlist_views(page=self.playlist_page,
                                   page_count=self.playlist_page_count,
                                   interactions_handler=self,
                                   is_playlist_empty=not playlist_to_show.tracks,
                                   add_back_button=self.is_library_command,
                                   show_more_button=self.show_playlist_more_button,
                                   track_index_title_map=track_index_title_map)
        return embed, views

    async def refresh_playlist_embed(self, note=None):
        embed, views = self.get_playlist_embed_and_views(note=note)
        await self.source_interaction.edit_original_response(content=None, embed=embed, view=views)

    async def refresh_embeds(self, playlist_view=False):
        if playlist_view:
            await self.refresh_playlist_embed()
        else:
            await self.refresh_library_embed()

    @property
    def library_page_count(self):
        return ceil(len(self.music_library.playlists) / 10)

    @property
    def playlist_page_count(self):
        return ceil(len(self.music_library.playlists[self.selected_playlist_index].tracks) / 10)

    async def sync_library(self):
        await self.library_music_component.sync_library_to_db(music_library=self.music_library)
