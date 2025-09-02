from typing import Dict

import discord

from bot.interaction_handlers import NavigationInteractionHandler
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.reminder_embeds import get_reminder_list_embed
from bot.utils.view_factory.reminder_views import get_reminder_list_view
from components.user_settings_components.user_reminder_component import UserReminderComponent
from models.user_settings_models import UserSettings, UserReminder


class ReminderListInteractionHandler(UserInteractionHandler, NavigationInteractionHandler):
    VIEW_NAME = "Reminder list"
    PAGE_SIZE = 5

    def __init__(self,
                 user_settings: UserSettings,
                 reminders: list[UserReminder],
                 page: int = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reminders: list[UserReminder] = reminders
        self._page: int = page
        self.user_settings = user_settings
        self.reminder_component = UserReminderComponent()

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)
        await self.fetch_reminders()

    async def fetch_reminders(self):
        self.reminders = await self.reminder_component.get_user_reminders(user_id=self.original_user.id)
        if self.reminders:
            self.user_settings = self.reminders[0].owner

    @interaction_handler()
    async def on_reminder_select(self, interaction: discord.Interaction):
        from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
            ReminderSetupInteractionHandler
        reminder_id = interaction.data["values"][0]
        reminder = self.reminder_id_reminder_map.get(int(reminder_id))
        await interaction.response.defer()
        interactions_handler = ReminderSetupInteractionHandler(
            source_interaction=self.source_interaction,
            context=self.context,
            guild_settings=self.guild_settings,
            user_settings=self.user_settings,
            reminder=reminder,
            view=ReminderSetupInteractionHandler.ReminderSetupView.REMINDER_SETUP,
            list_interaction_handler=self,
        )
        await interactions_handler.refresh_message()

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

    async def refresh_message(self,
                              no_view: bool = False,
                              feedback: str | None = None, 
                              deleted_reminder_id=None,
                              *args, **kwargs) -> None:
        for reminder in self.reminders:
            if reminder.id == deleted_reminder_id:
                self.reminders.remove(reminder)
                break
        if self._page > self.page_count:
            self._page = self.page_count
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        reminders = sorted(self.reminders, key=lambda r: r.reminder_time)
        embed = get_reminder_list_embed(reminders=reminders,
                                        page=self._page,
                                        page_count=self.page_count,
                                        page_size=self.PAGE_SIZE,
                                        feedback_message=feedback)
        view = get_reminder_list_view(interactions_handler=self,
                                      reminders=reminders,
                                      page=self._page,
                                      page_count=self.page_count,
                                      page_size=self.PAGE_SIZE)
        return embed, view

    @property
    def page_count(self) -> int:
        return ((len(self.reminder_id_reminder_map) - 1) // self.PAGE_SIZE + 1) or 1

    @property
    def reminder_id_reminder_map(self) -> Dict[int, UserReminder]:
        return {reminder.id: reminder for reminder in self.reminders if not reminder.is_snoozed}
