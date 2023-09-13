import discord
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler
from globals_.constants import Colour, HelpMenuType
from utils.decorators import interaction_handler
from utils.helpers import get_back_view, get_general_help_views
from utils.embed_factory import make_general_help_embed, make_help_embed_for_menu, quick_embed


class HelpMenuInteractionsHandler(UserInteractionsHandler):

    def __init__(self, interaction, selected_menu):
        super().__init__(interaction)
        self._selected_menu = selected_menu.value if selected_menu else None

    @interaction_handler
    async def handle_user_menu(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_menu = HelpMenuType.USER
        await self.refresh_message()

    @interaction_handler
    async def handle_admin_menu(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_menu = HelpMenuType.ADMIN
        await self.refresh_message()

    @interaction_handler
    async def handle_music_menu(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_menu = HelpMenuType.MUSIC
        await self.refresh_message()

    @interaction_handler
    async def handle_cancel(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            if not (self.guild and self.guild.get_member(inter.user.id).guild_permissions.manage_messages):
                return await inter.response.defer()
        await inter.response.defer()
        await self.source_interaction.edit_original_response(embed=quick_embed("Help menu closed",
                                                                               color=Colour.PRIMARY_ACCENT,
                                                                               bold=False),
                                                             view=None)

    @interaction_handler
    async def handle_go_back(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        self._selected_menu = None
        await self.refresh_message()

    async def refresh_message(self, no_views=False):
        embed, views = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views if not no_views else None)

    def get_embed_and_views(self):
        if self._selected_menu:
            embed = make_help_embed_for_menu(menu_type=self._selected_menu)
            views = get_back_view(interactions_handler=self,
                                  add_close_button=True)
        else:
            embed = make_general_help_embed()
            views = get_general_help_views(interactions_handler=self)

        return embed, views

    async def on_timeout(self):
        await self.refresh_message(no_views=True)
