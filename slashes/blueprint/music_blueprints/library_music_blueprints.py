from discord import app_commands
from discord.ext.commands import Cog

from slashes.music_slashes.library_music_slashes import LibraryMusicSlashes


class LibraryMusicBlueprints(Cog):
    LIBRARY = app_commands.command(name="library",
                                   description="List and manage all of your playlists")

    @LIBRARY
    @app_commands.rename(page="jump-to-page")
    async def library(self, inter, page: int = 1):
        """List and manage all of your playlists

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        page: int
            Jump to page in playlists
        """

        await LibraryMusicSlashes(interaction=inter).library(page=page)
