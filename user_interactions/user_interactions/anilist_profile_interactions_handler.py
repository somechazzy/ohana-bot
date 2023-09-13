from math import ceil
import discord
from utils.embed_factory import make_anilist_profile_anime_list_embed, make_anilist_profile_manga_list_embed, \
    make_anilist_profile_favorites_embed, make_anilist_profile_embed, make_anilist_profile_analysis_embed, quick_embed
from globals_.constants import ANILIST_SCORING_SYSTEM_MAP, Colour
from utils.helpers import get_al_profile_views, get_back_view, get_pagination_views
from utils.decorators import interaction_handler
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler


class AnilistProfileInteractionsHandler(UserInteractionsHandler):

    class SelectedView:
        PROFILE = "profile"
        ANIME_LIST = "anime_list"
        MANGA_LIST = "manga_list"
        FAVORITES = "favorites"
        ANALYSIS = "analysis"

    def __init__(self, source_interaction, profile_info, anime_list, manga_list, anime_scoring_system,
                 manga_scoring_system, username, unlocked):
        super().__init__(source_interaction=source_interaction)
        self._profile_info = profile_info
        self._anime_list = anime_list
        self._manga_list = manga_list
        self._anime_scoring_system = ANILIST_SCORING_SYSTEM_MAP.get(anime_scoring_system, anime_scoring_system)
        self._manga_scoring_system = ANILIST_SCORING_SYSTEM_MAP.get(manga_scoring_system, manga_scoring_system)
        self._username = username
        self._unlocked = unlocked
        self._selected_view = self.SelectedView.PROFILE
        self._page = 1

    @interaction_handler
    async def handle_anime_list(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_view = self.SelectedView.ANIME_LIST
        await self.refresh_message()

    @interaction_handler
    async def handle_manga_list(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_view = self.SelectedView.MANGA_LIST
        await self.refresh_message()

    @interaction_handler
    async def handle_favorites(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_view = self.SelectedView.FAVORITES
        await self.refresh_message()

    @interaction_handler
    async def handle_analysis(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_view = self.SelectedView.ANALYSIS
        await self.refresh_message()

    @interaction_handler
    async def handle_unlock(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._unlocked = True
        await self.refresh_message()

    @interaction_handler
    async def handle_cancel(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            if not (self.guild and self.guild.get_member(inter.user.id).guild_permissions.manage_messages):
                return await inter.response.defer()
        await inter.response.defer()
        await self.source_interaction.edit_original_response(embed=quick_embed("Anilist Profile closed",
                                                                               color=Colour.EXT_MAL,
                                                                               bold=False),
                                                             view=None)

    @interaction_handler
    async def handle_go_back(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_view = self.SelectedView.PROFILE
        self._page = 1
        await self.refresh_message()

    @interaction_handler
    async def handle_next(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        max_pages = ceil(len(self._anime_list) / 10) if self._selected_view == self.SelectedView.ANIME_LIST\
            else ceil(len(self._manga_list) / 10)
        if self._page < max_pages:
            self._page += 1
        else:
            self._page = 1
        await self.refresh_message()

    @interaction_handler
    async def handle_previous(self, inter: discord.Interaction):
        if not self._unlocked and self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        max_pages = ceil(len(self._anime_list) / 10) if self._selected_view == self.SelectedView.ANIME_LIST\
            else ceil(len(self._manga_list) / 10)
        if self._page > 1:
            self._page -= 1
        else:
            self._page = max_pages
        await self.refresh_message()

    async def refresh_message(self, no_views=False):
        embed, views = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views if not no_views else None)

    def get_embed_and_views(self):
        if self._selected_view == self.SelectedView.ANIME_LIST:
            embed = make_anilist_profile_anime_list_embed(username=self._username,
                                                          profile_avatar=self._profile_info.avatar,
                                                          anime_list=self._anime_list,
                                                          page=self._page,
                                                          total_pages=ceil(len(self._anime_list) / 10),
                                                          scoring_system=self._anime_scoring_system)
            views = get_pagination_views(page=self._page,
                                         page_count=ceil(len(self._anime_list) / 10),
                                         add_back_button=True,
                                         add_close_button=False,
                                         interactions_handler=self)
        elif self._selected_view == self.SelectedView.MANGA_LIST:
            embed = make_anilist_profile_manga_list_embed(username=self._username,
                                                          profile_avatar=self._profile_info.avatar,
                                                          manga_list=self._manga_list,
                                                          page=self._page,
                                                          total_pages=ceil(len(self._manga_list) / 10),
                                                          scoring_system=self._manga_scoring_system)
            views = get_pagination_views(page=self._page,
                                         page_count=ceil(len(self._manga_list) / 10),
                                         add_back_button=True,
                                         add_close_button=False,
                                         interactions_handler=self)
        elif self._selected_view == self.SelectedView.FAVORITES:
            embed = make_anilist_profile_favorites_embed(profile_info=self._profile_info)
            views = get_back_view(interactions_handler=self)
        elif self._selected_view == self.SelectedView.ANALYSIS:
            embed = make_anilist_profile_analysis_embed(profile_info=self._profile_info)
            views = get_back_view(interactions_handler=self)
        else:
            embed = make_anilist_profile_embed(profile_info=self._profile_info,
                                               reacting_unlocked=self._unlocked)
            views = get_al_profile_views(add_unlock=not self._unlocked,
                                         interactions_handler=self)

        return embed, views

    async def on_timeout(self):
        self._selected_view = self.SelectedView.PROFILE
        await self.refresh_message(no_views=True)
