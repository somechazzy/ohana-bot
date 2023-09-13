import discord

from utils.embed_factory import make_lyrics_embed
from utils.helpers import get_pagination_views
from user_interactions.base_interactions_handler import NavigationInteractions
from utils.decorators import interaction_handler
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicLyricsInteractionsHandler(MusicInteractionsHandler, NavigationInteractions):

    def __init__(self, source_interaction: discord.Interaction, lyrics_pages, requested_by, full_title,
                 thumbnail, url, page_index=0):
        super().__init__(source_interaction=source_interaction)
        self.lyrics_pages = lyrics_pages
        self.requested_by = requested_by
        self.full_title = full_title
        self.thumbnail = thumbnail
        self.url = url
        self.page_index = page_index

    @interaction_handler
    async def handle_next(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index == len(self.lyrics_pages) - 1:
            self.page_index = 0
        else:
            self.page_index += 1
        await self.send_lyrics_page()

    @interaction_handler
    async def handle_previous(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index == 0:
            self.page_index = len(self.lyrics_pages) - 1
        else:
            self.page_index -= 1
        await self.send_lyrics_page()

    async def send_lyrics_page(self):
        embed = make_lyrics_embed(lyrics_pages=self.lyrics_pages, requested_by=self.requested_by,
                                  full_title=self.full_title, thumbnail=self.thumbnail, url=self.url,
                                  page_index=self.page_index)
        await self.source_interaction.edit_original_response(
            content=None,
            embed=embed,
            view=get_pagination_views(page_count=len(self.lyrics_pages),
                                      page=self.page_index + 1,
                                      add_close_button=False,
                                      interactions_handler=self)
        )

    @interaction_handler
    async def handle_cancel(self, interaction: discord.Interaction):
        # delete the message
        await interaction.message.delete()
        del self

    async def on_timeout(self):
        try:
            await self.source_interaction.edit_original_response(view=None)
        except discord.NotFound:
            pass
