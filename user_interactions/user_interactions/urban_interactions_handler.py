import discord

from utils.embed_factory import quick_embed, make_urban_embed
from utils.helpers import get_pagination_views
from globals_.constants import Colour
from utils.decorators import interaction_handler
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler


class UrbanInteractionsHandler(UserInteractionsHandler):

    def __init__(self, source_interaction, definitions):
        super().__init__(source_interaction=source_interaction)
        self._definitions = definitions
        self._selected_definition_index = 0

    @interaction_handler
    async def handle_cancel(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        await self.source_interaction.edit_original_response(embed=quick_embed("Urban definition closed.",
                                                                               color=Colour.EXT_URBAN,
                                                                               bold=False),
                                                             view=None)

    @interaction_handler
    async def handle_next(self, inter: discord.Interaction):
        await inter.response.defer()

        if self._selected_definition_index + 1 < len(self._definitions):
            self._selected_definition_index += 1
        else:
            self._selected_definition_index = 0

        await self.refresh_message()

    @interaction_handler
    async def handle_previous(self, inter: discord.Interaction):
        await inter.response.defer()
        if self._selected_definition_index - 1 >= 0:
            self._selected_definition_index -= 1
        else:
            self._selected_definition_index = len(self._definitions) - 1

        await self.refresh_message()

    async def refresh_message(self, no_views=False):
        embed, views = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views if not no_views else None)

    def get_embed_and_views(self):
        embed = make_urban_embed(definition_dict=self._definitions[self._selected_definition_index],
                                 index=self._selected_definition_index + 1,
                                 total=len(self._definitions))
        views = get_pagination_views(page=self._selected_definition_index + 1,
                                     page_count=len(self._definitions),
                                     interactions_handler=self,
                                     add_close_button=True)

        return embed, views

    async def on_timeout(self):
        await self.refresh_message(no_views=True)
