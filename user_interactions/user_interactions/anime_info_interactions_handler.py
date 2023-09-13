import discord

from utils.embed_factory import quick_embed, make_mal_anime_info_embed, make_mal_anime_search_results_embed
from utils.helpers import get_numbered_list_views, make_mal_info_views
from globals_.constants import Colour
from utils.helpers import get_user_stats_for_anime
from services.third_party.myanimelist import MyAnimeListService
from utils.decorators import interaction_handler
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler


class AnimeInfoInteractionsHandler(UserInteractionsHandler):

    class SelectedView:
        INFO = "info"
        SEARCH = "search"

    def __init__(self, source_interaction, anime_info, search_result, user_stats, query):
        super().__init__(source_interaction=source_interaction)
        self._anime_info = anime_info
        self._search_result = search_result
        self._query = query
        self._user_stats = user_stats
        self._synopsis_expanded = False
        self._selected_view = self.SelectedView.INFO
        self._mal_service = MyAnimeListService()

    @interaction_handler
    async def handle_expand_synopsis(self, inter: discord.Interaction):
        await inter.response.defer()
        self._synopsis_expanded = True
        await self.refresh_message()

    @interaction_handler
    async def handle_back_to_search(self, inter: discord.Interaction):
        await inter.response.defer()
        self._selected_view = self.SelectedView.SEARCH
        await self.refresh_message()

    @interaction_handler
    async def handle_selection(self, inter: discord.Interaction):
        await inter.response.defer()

        await inter.edit_original_response(embed=quick_embed("Loading anime...",
                                           color=Colour.EXT_MAL,
                                           bold=False),
                                           view=None)

        selected_index = int(inter.data["values"][0])
        self._anime_info = await self._mal_service.get_anime_info(
            anime_id=self._search_result['entries'][selected_index]['id']
        )
        self._user_stats = await get_user_stats_for_anime(anime_id=self._anime_info['id'],
                                                          user_id=self.source_interaction.user.id)
        self._selected_view = self.SelectedView.INFO
        self._synopsis_expanded = False

        await self.refresh_message()

    @interaction_handler
    async def handle_cancel(self, inter: discord.Interaction):
        await inter.response.defer()
        await self.source_interaction.edit_original_response(embed=quick_embed("Anime info closed",
                                                                               color=Colour.EXT_MAL,
                                                                               bold=False),
                                                             view=None)

    async def refresh_message(self, no_views=False):
        embed, views = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views if not no_views else None)

    def get_embed_and_views(self):
        if self._selected_view == self.SelectedView.SEARCH:
            embed = make_mal_anime_search_results_embed(query=self._query,
                                                        results=self._search_result['entries'],
                                                        thumbnail=self._search_result['thumbnail'],
                                                        author=self.source_interaction.user)
            views = get_numbered_list_views(list_items=[result['title'] for result in self._search_result['entries']],
                                            interactions_handler=self,
                                            add_close_button=True)
        else:
            embed, include_expand_button = make_mal_anime_info_embed(anime_info=self._anime_info,
                                                                     user_stats=self._user_stats,
                                                                     synopsis_expanded=self._synopsis_expanded)
            views = make_mal_info_views(interactions_handler=self,
                                        add_expand_button=include_expand_button and not self._synopsis_expanded)

        return embed, views

    async def on_timeout(self):
        self._selected_view = self.SelectedView.INFO
        self._synopsis_expanded = True
        await self.refresh_message(no_views=True)
