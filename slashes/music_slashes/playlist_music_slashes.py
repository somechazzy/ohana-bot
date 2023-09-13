from utils.decorators import slash_command
from slashes.music_slashes.base_music_slashes import MusicSlashes
import asyncio
from utils.exceptions import PlaylistDuplicateNameException, PlaylistNotFoundException, MusicVoiceConnectionException
from globals_.constants import MusicVCState, MusicServiceMode
from utils.embed_factory import quick_embed
from user_interactions.music_interactions.music_library_interactions_handler import MusicLibraryInteractionsHandler


class PlaylistMusicSlashes(MusicSlashes):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @slash_command
    async def playlist_show(self, playlist: str, page: int = 1):
        """
        /music list show
        Display and manage one of your playlists
        """

        if not await self.preprocess_and_validate():
            return

        try:
            playlist_to_show = self.get_playlist(playlist_input=playlist)
        except PlaylistNotFoundException:
            return await self.interaction.response.send_message(content="Can't find this playlist."
                                                                        " See your playlists using `/music library`",
                                                                ephemeral=True)
        interactions_handler = MusicLibraryInteractionsHandler(
            source_interaction=self.interaction,
            music_library=self.music_library,
            library_page=page,
            selected_playlist_index=self.music_library.playlists.index(playlist_to_show),
            is_library_command=False
        )
        embed, views = interactions_handler.get_playlist_embed_and_views(refresh_if_not_found=False)
        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def playlist_play(self, playlist: str):
        """
        /music list play
        Play one of your playlists
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        try:
            playlist_to_play = self.get_playlist(playlist_input=playlist)
        except PlaylistNotFoundException:
            return await self.interaction.response.send_message(content="Can't find this playlist."
                                                                        " See your playlists using `/music library`",
                                                                ephemeral=True)
        if not playlist_to_play.tracks:
            return await self.interaction.response.send_message(content="Playlist is empty!", ephemeral=True)
        await self.interaction.response.send_message(content=f"Queuing playlist `{playlist_to_play.name}`...",
                                                     delete_after=self.delete_after(long=True))

        try:
            await self.get_or_initiate_guild_music_service(raise_=True)
        except MusicVoiceConnectionException as e:
            return await self.interaction.response.send_message(content=str(e), ephemeral=True)

        if self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.ask_to_switch_to_player_mode()

        tracks = playlist_to_play.tracks.copy()
        if len(tracks) > 1:
            await self.music_service.add_track_to_queue(url=self.youtube_id_to_url(tracks[0].youtube_id),
                                                        added_by=self.user.id,
                                                        refresh_player=True)
            tracks = tracks[1:]
        if tracks:
            asyncio.get_event_loop() \
                .create_task(self.music_service.add_tracks_to_queue([self.youtube_id_to_url(track.youtube_id)
                                                                     for track in tracks],
                                                                    added_by=self.user.id,
                                                                    channel=self.channel))
            await self.interaction.edit_original_response(
                content=None,
                embed=quick_embed(text=f"Adding {len(tracks) + 1} tracks to queue, please wait...")
            )

        if self.music_service.state != MusicVCState.PLAYING:
            i = 0
            while not self.music_service.queue:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            await self.music_service.start_worker()

    @slash_command
    async def playlist_create(self, name: str):
        """
        /music list create
        Create a new playlist
        """

        if not await self.preprocess_and_validate():
            return

        name = name.strip()
        try:
            self.music_library.create_new_playlist(user_id=self.user.id, name=name)
        except PlaylistDuplicateNameException:
            return await self.interaction.response.send_message(content=f"A playlist with this name already exists.",
                                                                ephemeral=True)
        await self.interaction.response.send_message(
            embed=quick_embed(f"Playlist `{name}` created successfully.\n Add tracks using `/music list add-track`. "
                              f"View your playlists using `/music library`."),
            ephemeral=True
        )
        await self.library_music_component.sync_library_to_db(music_library=self.music_library)
