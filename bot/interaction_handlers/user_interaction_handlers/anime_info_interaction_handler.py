import discord

from bot.interaction_handlers import NavigationInteractionHandler, NumberedListInteractionHandler
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.embed_factory.animanga_embeds import get_anime_info_embed, get_anime_search_results_embed
from bot.utils.embed_factory.general_embeds import get_generic_embed
from bot.utils.view_factory.animanga_views import get_animanga_info_view
from bot.utils.view_factory.general_views import get_numbered_list_view
from clients import emojis
from bot.utils.decorators import interaction_handler
from components.integration_component.anilist_component import AnilistComponent
from components.integration_component.mal_component import MALComponent
from constants import AnimangaProvider, Colour
from models.dto.animanga import AnimeInfo, AnimeSearchResult, UserAnimeListEntry


class AnimeInfoInteractionHandler(UserInteractionHandler, NavigationInteractionHandler, NumberedListInteractionHandler):
    VIEW_NAME = "Anime info"
    SEARCH_RESULT_PAGE_SIZE = 5

    class SelectedView:
        ANIME_INFO = "anime_info"
        SEARCH_RESULTS = "search_results"

    def __init__(self,
                 anime_info: AnimeInfo,
                 user_stats: UserAnimeListEntry,
                 search_result: AnimeSearchResult,
                 user_username: str | None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True
        self._anime_info = anime_info
        self._user_stats = user_stats
        self._search_result = search_result
        self._user_username = user_username
        self.synopsis_expanded = False
        self._is_closed = False
        self._selected_view = self.SelectedView.ANIME_INFO
        if anime_info.source_provider == AnimangaProvider.MAL:
            self._embed_color = Colour.EXT_MAL
            self.animanga_component = MALComponent()
        elif anime_info.source_provider == AnimangaProvider.ANILIST:
            self._embed_color = Colour.EXT_ANILIST
            self.animanga_component = AnilistComponent()

    @interaction_handler()
    async def expand_synopsis(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.synopsis_expanded = True
        await self.refresh_message()

    @interaction_handler()
    async def go_to_search(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.SEARCH_RESULTS
        await self.refresh_message()

    @interaction_handler()
    async def select_item(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.synopsis_expanded = False
        await interaction.edit_original_response(
            embed=get_generic_embed(description=f"Getting anime info {emojis.loading.get_random()}",
                                    color=self._embed_color),
            view=None
        )
        selected_index = int(interaction.data["values"][0])
        selected_anime_id = self._search_result.entries[selected_index].anime_id
        anime_info = await self.animanga_component.get_anime_info(anime_id=selected_anime_id)
        try:
            user_stats = await self.animanga_component.get_user_stats_for_anime(anime_id=selected_anime_id,
                                                                                username=self._user_username)
        except Exception as e:
            if getattr(e, 'alert_worthy', True):
                self.logger.error(f"Error fetching user stats for anime {selected_anime_id}: {e}")
            else:
                self.logger.debug(f"Error fetching user stats for anime {selected_anime_id}: {e}")
            user_stats = UserAnimeListEntry.as_empty_entry(anime_id=selected_anime_id,
                                                           username=self._user_username,
                                                           provider=self._search_result.source_provider)
        self._anime_info = anime_info
        self._user_stats = user_stats
        self._selected_view = self.SelectedView.ANIME_INFO
        await self.refresh_message()

    async def refresh_message(self, no_view: bool = False, *args, **kwargs) -> None:
        embed, view = self.get_embed_and_view()
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        if self._selected_view == self.SelectedView.ANIME_INFO:
            embed = get_anime_info_embed(anime_info=self._anime_info,
                                         anime_user_entry=self._user_stats,
                                         synopsis_expanded=self.synopsis_expanded)
            view = get_animanga_info_view(interaction_handler=self)
        else:
            embed = get_anime_search_results_embed(search_results=self._search_result,
                                                   page_size=self.SEARCH_RESULT_PAGE_SIZE)
            view = get_numbered_list_view(
                interaction_handler=self,
                label_description_list=[(result_entry.native_title, result_entry.english_title)
                                        for result_entry in self._search_result.entries[:self.SEARCH_RESULT_PAGE_SIZE]],
                add_close_button=True
            )
        return embed, view

    def synopsis_expandable(self) -> bool:
        return len(self._anime_info.synopsis) > 600 and not self.synopsis_expanded

    async def on_timeout(self):
        self._selected_view = self.SelectedView.ANIME_INFO
        await super().on_timeout()
