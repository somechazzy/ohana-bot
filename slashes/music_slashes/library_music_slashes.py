from math import ceil
from utils.decorators import slash_command
from slashes.music_slashes.base_music_slashes import MusicSlashes
from user_interactions.music_interactions.music_library_interactions_handler import MusicLibraryInteractionsHandler


class LibraryMusicSlashes(MusicSlashes):

    @slash_command
    async def library(self, page: int = 1):
        """
        /music library
        List and manage all of your playlists
        """
        if not await self.preprocess_and_validate():
            return

        if ceil(len(self.music_library.playlists)/10) < page:
            page = 1
        interactions_handler = MusicLibraryInteractionsHandler(
            source_interaction=self.interaction,
            music_library=self.music_library,
            library_page=page,
            is_library_command=True
        )
        embed, views = interactions_handler.get_library_embed_and_views()
        await self.interaction.response.send_message(content=None, embed=embed, view=views, ephemeral=True)
