from discord.ext.commands import GroupCog
from typing import Literal
from discord import app_commands, Interaction

from slashes.music_slashes.playlist_music_slashes import PlaylistMusicSlashes


class PlaylistMusicBlueprints(GroupCog):
    playlist_group = app_commands.Group(name="list",
                                        description="Manage your playlists",
                                        extras={"unlisted": True})

    PLAYLIST_SHOW = playlist_group.command(name="show",
                                           description="Display and manage one of your playlists")
    PLAYLIST_PLAY = playlist_group.command(name="play",
                                           description="Play one of your playlists")
    PLAYLIST_CREATE = playlist_group.command(name="create",
                                             description="Create a new playlist")

    @PLAYLIST_SHOW
    @app_commands.rename(page="jump-to-page")
    async def playlist_show(self, inter, playlist: str, page: int = 1):
        """Display and manage one of your playlists

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        playlist: str
            Playlist name or number
        page: int
            Jump to page in playlist tracks
        """

        await PlaylistMusicSlashes(interaction=inter).playlist_show(playlist=playlist, page=page)

    @PLAYLIST_PLAY
    async def playlist_play(self, inter, playlist: str):
        """Play one of your playlists

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        playlist: str
            Playlist name or number
        """

        await PlaylistMusicSlashes(interaction=inter).playlist_play(playlist=playlist)

    @PLAYLIST_CREATE
    async def playlist_create(self, inter, name: str):
        """Create a new playlist

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        name: str
            Give your playlist a name
        """

        await PlaylistMusicSlashes(interaction=inter).playlist_create(name=name)
