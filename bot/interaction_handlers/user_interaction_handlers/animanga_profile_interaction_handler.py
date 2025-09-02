import asyncio
import discord

from bot.interaction_handlers import NavigationInteractionHandler
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.embed_factory.animanga_embeds import get_user_anime_list_embed, get_user_manga_list_embed, \
    get_user_animanga_favorites_embed, get_user_animanga_analyses_embed, get_user_animanga_profile_embed
from bot.utils.view_factory.animanga_views import get_animanga_profile_view
from bot.utils.view_factory.general_views import get_navigation_view
from bot.utils.decorators import interaction_handler
from constants import AnimangaProvider, AnimangaListLoadingStatus, Colour
from models.dto.animanga import UserAnimangaProfile


class AnimangaProfileInteractionHandler(UserInteractionHandler, NavigationInteractionHandler):
    VIEW_NAME = "Animanga profile"
    MEDIA_LIST_PAGE_SIZE = 10

    class SelectedView:
        PROFILE = "profile"
        ANIME_LIST = "anime_list"
        MANGA_LIST = "manga_list"
        FAVORITES = "favorites"
        ANALYSIS = "analysis"
    
    def __init__(self, user_profile: UserAnimangaProfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True
        self._user_profile: UserAnimangaProfile = user_profile
        self._selected_view = self.SelectedView.PROFILE
        self._page = 1
        self._is_closed = False
        if user_profile.source_provider == AnimangaProvider.MAL:
            self.VIEW_NAME = "MyAnimeList profile"
            self._embed_color = Colour.EXT_MAL
        elif user_profile.source_provider == AnimangaProvider.ANILIST:
            self.VIEW_NAME = "AniList profile"
            self._embed_color = Colour.EXT_ANILIST

    @interaction_handler()
    async def go_to_anime_list(self, interaction: discord.Interaction):
        slept = 0
        while self._user_profile.anime_list_loading_status == AnimangaListLoadingStatus.LOADING:
            await asyncio.sleep(0.1)
            slept += 0.1
            if slept > 3:
                break
        await interaction.response.defer()
        self._selected_view = self.SelectedView.ANIME_LIST
        await self.refresh_message()

    @interaction_handler()
    async def go_to_manga_list(self, interaction: discord.Interaction):
        slept = 0
        while self._user_profile.manga_list_loading_status == AnimangaListLoadingStatus.LOADING:
            await asyncio.sleep(0.1)
            slept += 0.1
            if slept > 3:
                break
        await interaction.response.defer()
        self._selected_view = self.SelectedView.MANGA_LIST
        await self.refresh_message()

    @interaction_handler()
    async def go_to_favorites(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.FAVORITES
        await self.refresh_message()
    
    @interaction_handler()
    async def go_to_analysis(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.ANALYSIS
        await self.refresh_message()

    @interaction_handler()
    async def unlock(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.interactions_restricted = False
        await self.refresh_message()
    
    @interaction_handler()
    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.offset_page(1)
        await self.refresh_message()

    @interaction_handler()
    async def previous_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.offset_page(-1)
        await self.refresh_message()
        
    @interaction_handler()
    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.PROFILE
        self._page = 1
        await self.refresh_message()
    
    def offset_page(self, offset: int) -> None:
        self._page += offset
        if self._page < 1:
            self._page = self.page_count
        elif self._page > self.page_count:
            self._page = 1

    async def refresh_message(self, no_view: bool = False, *args, **kwargs) -> None:
        embed, view = self.get_embed_and_view()
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        if self._selected_view == self.SelectedView.ANIME_LIST:
            embed = get_user_anime_list_embed(user_profile=self._user_profile,
                                              page=self._page,
                                              page_count=self.page_count,
                                              page_size=self.MEDIA_LIST_PAGE_SIZE)
            view = get_navigation_view(interaction_handler=self,
                                       page=self._page,
                                       page_count=self.page_count,
                                       add_back_button=True)
        elif self._selected_view == self.SelectedView.MANGA_LIST:
            embed = get_user_manga_list_embed(user_profile=self._user_profile,
                                              page=self._page,
                                              page_count=self.page_count,
                                              page_size=self.MEDIA_LIST_PAGE_SIZE)
            view = get_navigation_view(interaction_handler=self,
                                       page=self._page,
                                       page_count=self.page_count,
                                       add_back_button=True)
        elif self._selected_view == self.SelectedView.FAVORITES:
            embed = get_user_animanga_favorites_embed(user_profile=self._user_profile)
            view = get_navigation_view(interaction_handler=self, add_back_button=True)
        elif self._selected_view == self.SelectedView.ANALYSIS:
            embed = get_user_animanga_analyses_embed(user_profile=self._user_profile)
            view = get_navigation_view(interaction_handler=self, add_back_button=True)
        else:
            embed = get_user_animanga_profile_embed(user_profile=self._user_profile,
                                                    navigation_locked=self.interactions_restricted)
            view = get_animanga_profile_view(
                interaction_handler=self,
                add_analysis_button=self._user_profile.source_provider == AnimangaProvider.ANILIST
            )
        return embed, view

    async def on_timeout(self):
        self._selected_view = self.SelectedView.PROFILE
        await super().on_timeout()

    @property
    def page_count(self) -> int:
        if self._selected_view == self.SelectedView.ANIME_LIST:
            if not self._user_profile.anime_list or not self._user_profile.anime_list.entries:
                return 1
            return (len(self._user_profile.anime_list.entries) - 1) // self.MEDIA_LIST_PAGE_SIZE + 1
        elif self._selected_view == self.SelectedView.MANGA_LIST:
            if not self._user_profile.manga_list or not self._user_profile.manga_list.entries:
                return 1
            return (len(self._user_profile.manga_list.entries) - 1) // self.MEDIA_LIST_PAGE_SIZE + 1
        else:
            return 1  # ??
