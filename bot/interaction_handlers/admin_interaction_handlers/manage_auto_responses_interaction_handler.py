import asyncio

import discord

from bot.interaction_handlers import NavigationInteractionHandler
from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.modal_factory import ConfirmationModal
from bot.utils.modal_factory.automod_management_modals import AddAutoResponseModal, EditAutoResponseModal
from bot.utils.embed_factory.automod_management_embeds import get_auto_responses_setup_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.decorators import interaction_handler
from bot.utils.view_factory.automod_management_views import get_auto_responses_setup_view
from common.exceptions import UserInputException
from components.guild_settings_components.guild_auto_response_component import GuildAutoResponseComponent
from constants import AutoResponseMatchType
from utils.helpers.text_parsing_helpers import text_contains_offensive_words


class ManageAutoResponsesInteractionHandler(AdminInteractionHandler, NavigationInteractionHandler):
    VIEW_NAME = "Auto-responses management"
    PAGE_SIZE = 5

    def __init__(self,
                 page: int = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._page: int = page
        self.auto_response_component = GuildAutoResponseComponent()

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

    @interaction_handler()
    async def on_add_auto_response(self, interaction: discord.Interaction):
        if len(self.guild_settings.auto_responses) >= 30:
            raise UserInputException("You already have 30 auto-responses or more.")

        await interaction.response.send_modal(AddAutoResponseModal(interactions_handler=self))

    @interaction_handler()
    async def on_auto_response_select(self, interaction: discord.Interaction):
        auto_response_id = int(interaction.data["values"][0])
        auto_response = self.guild_settings.get_auto_response(guild_auto_response_id=auto_response_id)
        await interaction.response.send_modal(EditAutoResponseModal(
            interactions_handler=self,
            auto_response_id=auto_response_id,
            trigger_text=auto_response.trigger,
            response_text=auto_response.response,
            match_type=auto_response.match_type,
            delete_original=auto_response.delete_original
        ))

    @interaction_handler()
    async def on_auto_response_modal_submit(self,
                                            interaction: discord.Interaction,
                                            auto_response_id: int | None,
                                            trigger_text: str,
                                            response_text: str,
                                            match_type: str,
                                            delete_original: bool,
                                            delete_auto_response: bool):
        if delete_auto_response:
            await self.auto_response_component.remove_auto_response(guild_id=self.guild.id,
                                                                    guild_auto_response_id=auto_response_id)
            await interaction.response.defer()
            await self.refresh_message(feedback="Auto-response deleted")
            await self.log_setting_change(event_text="Deleted auto-response",
                                          fields=[GuildLogEventField(name="Trigger text",
                                                                     value=trigger_text),
                                                  GuildLogEventField(name="Response text",
                                                                     value=response_text)]),
            return

        if text_contains_offensive_words(text=response_text):
            raise UserInputException("The response text contains offensive words.\n"
                                     "If you think this is a mistake please let us know via /feedback.")
        if match_type not in AutoResponseMatchType.as_list():
            raise ValueError("Invalid match type")

        await interaction.response.defer()
        if auto_response_id:
            await self.auto_response_component.update_auto_response(guild_id=self.guild.id,
                                                                    guild_auto_response_id=auto_response_id,
                                                                    trigger_text=trigger_text,
                                                                    response_text=response_text,
                                                                    match_type=match_type,
                                                                    delete_original=delete_original)
        else:
            await self.auto_response_component.add_auto_response(guild_id=self.guild.id,
                                                                 trigger_text=trigger_text,
                                                                 response_text=response_text,
                                                                 match_type=match_type,
                                                                 delete_original=delete_original)
        await self.refresh_message(feedback=f"Auto-response {'added' if not auto_response_id else 'updated'}")
        await self.log_setting_change(event_text=f"{'Added' if not auto_response_id else 'Updated'} auto-response",
                                      fields=[GuildLogEventField(name="Trigger text",
                                                                 value=trigger_text),
                                              GuildLogEventField(name="Response text",
                                                                 value=response_text),
                                              GuildLogEventField(name="Match type",
                                                                 value=match_type.replace("_", " ").title()),
                                              GuildLogEventField(name="Delete original",
                                                                 value="Yes" if delete_original else "No")])

    @interaction_handler()
    async def clear_auto_responses(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfirmationModal(callback=self.on_clear_auto_responses_confirm))

    @interaction_handler()
    async def on_clear_auto_responses_confirm(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.auto_response_component.clear_auto_responses(guild_id=self.guild.id)
        await self.refresh_message(feedback="All auto-responses removed")
        await self.log_setting_change(event_text="Auto-responses cleared")

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_auto_responses_setup_embed(auto_responses=self.guild_settings.auto_responses,
                                               guild=self.guild,
                                               feedback_message=feedback,
                                               page=self._page,
                                               page_count=self.page_count,
                                               page_size=self.PAGE_SIZE)
        view = get_auto_responses_setup_view(interaction_handler=self,
                                             auto_responses=self.guild_settings.auto_responses,
                                             page=self._page,
                                             page_count=self.page_count,
                                             page_size=self.PAGE_SIZE)
        return embed, view

    @property
    def page_count(self) -> int:
        return ((len(self.guild_settings.auto_responses) - 1) // self.PAGE_SIZE + 1) or 1
