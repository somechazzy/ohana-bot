from math import ceil
import discord
from user_interactions.base_interactions_handler import NavigationInteractions
from utils.embed_factory import make_music_logs_embed
from utils.helpers import get_pagination_views
from utils.decorators import interaction_handler
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicLogsInteractionsHandler(MusicInteractionsHandler, NavigationInteractions):

    def __init__(self, source_interaction, logs_list, page=1):
        super().__init__(source_interaction=source_interaction)
        self.logs_list = logs_list
        self.page = page
        self.page_count = ceil(len(self.logs_list) / 10)

    @interaction_handler
    async def handle_previous(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == 1:
            self.page = self.page_count
        else:
            self.page -= 1

        await inter.response.defer()
        await self.refresh_embed()

    @interaction_handler
    async def handle_next(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == self.page_count:
            self.page = 1
        else:
            self.page += 1

        await inter.response.defer()
        await self.refresh_embed()

    def get_embed_and_views(self):
        view = get_pagination_views(interactions_handler=self, page=self.page, page_count=self.page_count,
                                    add_close_button=False)
        embed = make_music_logs_embed(guild=self.guild, logs=self.logs_list, page=self.page,
                                      page_count=self.page_count)
        return embed, view

    async def refresh_embed(self):
        embed, view = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=view)
