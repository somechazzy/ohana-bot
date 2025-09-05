import discord

from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.helpers.command_helpers import get_commands_under_category
from bot.utils.embed_factory.help_embeds import get_main_help_embed, get_commands_menu_embed
from bot.utils.view_factory.help_views import get_main_help_view, get_commands_menu_view
from bot.utils.decorators import interaction_handler
from constants import CommandCategory


class HelpMenuInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Help menu"

    def __init__(self, selected_menu: str | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selected_menu = selected_menu

    @interaction_handler()
    async def go_to_user_menu(self, interaction: discord.Interaction):
        if self.source_interaction.user.id != interaction.user.id:
            await interaction.response.defer()
            return
        await interaction.response.defer()
        self._selected_menu = CommandCategory.USER
        await self.refresh_message()

    @interaction_handler()
    async def go_to_admin_menu(self, interaction: discord.Interaction):
        if self.source_interaction.user.id != interaction.user.id:
            await interaction.response.defer()
            return
        await interaction.response.defer()
        self._selected_menu = CommandCategory.ADMIN
        await self.refresh_message()

    @interaction_handler()
    async def go_back(self, interaction: discord.Interaction):
        if self.source_interaction.user.id != interaction.user.id:
            await interaction.response.defer()
            return
        await interaction.response.defer()
        self._selected_menu = None
        await self.refresh_message()

    async def refresh_message(self, no_view: bool = False, *args, **kwargs):
        embed, view = self.get_embed_and_view()
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self) -> tuple[discord.Embed, discord.ui.View]:
        if self._selected_menu:
            embed = get_commands_menu_embed(category=self._selected_menu,
                                            command_list=get_commands_under_category(category=self._selected_menu))
            view = get_commands_menu_view(interaction_handler=self)
        else:
            embed = get_main_help_embed()
            view = get_main_help_view(interaction_handler=self)

        return embed, view
