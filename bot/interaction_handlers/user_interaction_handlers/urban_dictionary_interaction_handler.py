import discord

from bot.interaction_handlers import NavigationInteractionHandler
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.embed_factory.definition_embeds import get_urban_dictionary_definition_embed
from bot.utils.embed_factory.general_embeds import get_error_embed
from bot.utils.view_factory.general_views import get_navigation_view
from bot.utils.decorators import interaction_handler
from components.user_settings_components.user_settings_component import UserSettingsComponent
from models.dto.dictionary import UrbanDictionaryDefinition


class UrbanDictionaryInteractionHandler(UserInteractionHandler, NavigationInteractionHandler):
    VIEW_NAME = "Urban definition"

    def __init__(self, definitions: list[UrbanDictionaryDefinition], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._definitions: list[UrbanDictionaryDefinition] = definitions
        self._page = 1
        self._is_closed = False
        self.user_settings_component = UserSettingsComponent()

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

    def offset_page(self, offset: int) -> None:
        self._page += offset
        if self._page < 1:
            self._page = self.page_count
        elif self._page > self.page_count:
            self._page = 1

    async def refresh_message(self, *args, **kwargs) -> None:
        embed, view = self.get_embed_and_view()
        await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View | None]:
        if not self._definitions:
            return get_error_embed(message="No definitions found for this term."), None
        embed = get_urban_dictionary_definition_embed(definitions=self._definitions,
                                                      page=self._page,
                                                      page_count=self.page_count)
        view = get_navigation_view(interaction_handler=self,
                                   page=self._page,
                                   page_count=self.page_count,
                                   add_back_button=False)
        return embed, view

    @property
    def page_count(self) -> int:
        return len(self._definitions) or 1
