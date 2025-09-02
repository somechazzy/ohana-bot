import asyncio
from datetime import timedelta, datetime, UTC
from typing import TYPE_CHECKING

import discord
import pytz

from bot.utils.modal_factory.reminder_modals import ReminderEditWhatModal, ReminderEditWhenModal, \
    TimezoneSelectionModal, ReminderBasicRecurrenceInputModal, ReminderConditionedRecurrenceInputModal
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.reminder_embeds import get_reminder_confirmation_embed, get_reminder_setup_embed, \
    get_reminder_delete_confirmation_embed, get_reminder_weekdays_selection_embed
from bot.utils.embed_factory.user_embeds import get_timezone_prompt_embed
from bot.utils.view_factory.reminder_views import get_reminder_confirmation_view, get_reminder_setup_view, \
    get_delete_confirmation_view, get_weekdays_selection_view
from bot.utils.view_factory.user_views import get_timezone_prompt_view
from common.decorators import require_db_session
from common.exceptions import UserInputException
from components.user_settings_components.user_reminder_component import UserReminderComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import ReminderRecurrenceBasicUnit, ReminderRecurrenceConditionedType, Links, \
    ReminderRecurrenceType, ReminderStatus
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from models.user_settings_models import UserReminder, UserSettings
from utils.helpers.datetime_helpers import from_timestamp
from utils.helpers.text_manipulation_helpers import get_numbers_with_suffix, get_days_of_week_from_numbers
from utils.helpers.text_parsing_helpers import get_time_in_minutes_from_user_text
if TYPE_CHECKING:
    from bot.interaction_handlers.user_interaction_handlers.reminder_list_interaction_handler import \
        ReminderListInteractionHandler


class ReminderSetupInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Reminder setup"

    class ReminderSetupView:
        REMINDER_CONFIRMATION = "reminder_confirmation"
        REMINDER_SETUP = "reminder_setup"
        DELETE_CONFIRMATION = "delete_confirmation"
        WEEKDAYS_SELECTION = "weekdays_selection"
        TIMEZONE_PROMPT = "timezone_prompt"

    class RecurrenceSelectValue:
        HOURS = "reminder-recurrence-setup-hours"
        DAYS = "reminder-recurrence-setup-days"
        WEEKLY = "reminder-recurrence-setup-weekly"
        MONTHLY = "reminder-recurrence-setup-monthly"
        YEARLY = "reminder-recurrence-setup-yearly"
        WEEKLY_DAYS = "reminder-recurrence-setup-weekly-days"
        MONTHLY_DAYS = "reminder-recurrence-setup-monthly-days"
        DELETE = "reminder-recurrence-setup-delete"

    def __init__(self,
                 user_settings: UserSettings,
                 reminder: UserReminder,
                 view=ReminderSetupView.REMINDER_CONFIRMATION,
                 list_interaction_handler=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_settings = user_settings
        self.reminder: UserReminder = reminder
        self.reminder_id: int = reminder.id
        self.selected_view: str = view
        self.selected_recurrence_type_value: str | None = None
        self.list_interaction_handler: 'ReminderListInteractionHandler' = list_interaction_handler
        self.reminder_component = UserReminderComponent()

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)
        self.reminder = await self.reminder_component.get_reminder(reminder_id=self.reminder_id,
                                                                   load_user_settings=True,
                                                                   load_recurrence_settings=True)
        self.user_settings = self.reminder.owner

    @interaction_handler()
    async def go_to_setup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_view = self.ReminderSetupView.REMINDER_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def go_to_edit_what(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ReminderEditWhatModal(
            interactions_handler=self,
            current_what=self.reminder.reminder_text
        ))

    @interaction_handler()
    async def on_edit_what_modal_submit(self, interaction: discord.Interaction, what_text: str):
        await interaction.response.defer()
        await self.reminder_component.update_reminder(reminder=self.reminder, reminder_text=what_text)
        await self.refresh_message(feedback="✅ Reminder text updated.")

    @interaction_handler()
    async def go_to_edit_when(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ReminderEditWhenModal(
            interactions_handler=self,
        ))

    @interaction_handler()
    async def on_edit_when_modal_submit(self, interaction: discord.Interaction, when_text: str):
        minutes = get_time_in_minutes_from_user_text(when_text)
        error_message = None
        if not minutes:
            error_message = "Invalid time format. Valid examples:\n" \
                            "• 1d12h means 1 day and 12 hours\n" \
                            "• 1h30m means 1 hour and 30 minutes\n" \
                            "• 3d4h15m means 3 days, 4 hours and 15 minutes"
        elif minutes > 60 * 24 * 366:
            error_message = "Maximum reminder time is 1 year."

        if error_message:
            raise UserInputException(error_message)

        reminder_time = datetime.now(UTC) + timedelta(minutes=minutes)

        await interaction.response.defer()
        await self.reminder_component.update_reminder(reminder=self.reminder,
                                                      reminder_time=reminder_time,
                                                      status=ReminderStatus.ACTIVE)
        await self.refresh_message(feedback="✅ Reminder time updated.")

    @interaction_handler()
    async def go_to_delete(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_view = self.ReminderSetupView.DELETE_CONFIRMATION
        await self.refresh_message()

    @interaction_handler()
    async def on_delete_confirmation(self, interaction: discord.Interaction):
        await self.reminder_component.delete_reminder(reminder_id=self.reminder.id)
        if self.list_interaction_handler:
            await self.list_interaction_handler.fetch_reminders()
            await self.list_interaction_handler.refresh_message(feedback="✅ Reminder deleted.",
                                                                deleted_reminder_id=self.reminder.id)
        else:
            await interaction.response.send_message("✅ Reminder deleted.", ephemeral=True)
            await self.source_interaction.delete_original_response()

    @interaction_handler()
    async def on_delete_cancel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_view = self.ReminderSetupView.REMINDER_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def go_to_set_timezone(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimezoneSelectionModal(
            interactions_handler=self,
        ))

    @interaction_handler()
    async def on_timezone_modal_submit(self, interaction: discord.Interaction, timezone: str):
        await interaction.response.defer()
        if not timezone or timezone not in pytz.all_timezones:
            raise UserInputException(f"Invalid timezone. Get your timezone here: {Links.APPS_TIMEZONE}")
        await UserSettingsComponent().update_user_settings(user_id=self.original_user.id, timezone=timezone)
        self.selected_recurrence_type_value = None
        self.selected_view = self.ReminderSetupView.REMINDER_SETUP
        await self.refresh_message(feedback="✅ Timezone set. You can now set up reminder recurrence.")

    @interaction_handler()
    async def go_to_recurrence_setup(self, interaction: discord.Interaction):
        selected_setup = interaction.data["values"][0]
        self.selected_recurrence_type_value = selected_setup
        if selected_setup in [self.RecurrenceSelectValue.MONTHLY, self.RecurrenceSelectValue.YEARLY,
                              self.RecurrenceSelectValue.WEEKLY_DAYS, self.RecurrenceSelectValue.MONTHLY_DAYS]:
            if not self.user_settings.timezone:
                self.selected_view = self.ReminderSetupView.TIMEZONE_PROMPT
                await interaction.response.defer()
                await self.refresh_message()
                return

        if selected_setup in [self.RecurrenceSelectValue.HOURS, self.RecurrenceSelectValue.DAYS]:
            await interaction.response.send_modal(ReminderBasicRecurrenceInputModal(
                interactions_handler=self,
                days=selected_setup == self.RecurrenceSelectValue.DAYS,
                hours=selected_setup == self.RecurrenceSelectValue.HOURS
            ))
        elif selected_setup == self.RecurrenceSelectValue.WEEKLY:
            await self.reminder_component.set_reminder_recurrence(
                reminder=self.reminder,
                recurrence_type=ReminderRecurrenceType.BASIC,
                basic_interval=7,
                basic_unit=ReminderRecurrenceBasicUnit.DAY
            )
            await interaction.response.defer()
            await self.refresh_message(feedback="✅ Reminder recurrence set to weekly.")
        elif selected_setup == self.RecurrenceSelectValue.MONTHLY:
            day = from_timestamp(utc_timestamp=self.reminder.reminder_time.timestamp(),
                                 timezone=self.user_settings.timezone).day
            await self.reminder_component.set_reminder_recurrence(
                reminder=self.reminder,
                recurrence_type=ReminderRecurrenceType.CONDITIONED,
                conditioned_type=ReminderRecurrenceConditionedType.DAYS_OF_MONTH,
                conditioned_days=[day]
            )
            await interaction.response.defer()
            await self.refresh_message(feedback="✅ Reminder recurrence set to monthly.")
        elif selected_setup == self.RecurrenceSelectValue.YEARLY:
            await self.reminder_component.set_reminder_recurrence(
                reminder=self.reminder,
                recurrence_type=ReminderRecurrenceType.CONDITIONED,
                conditioned_type=ReminderRecurrenceConditionedType.DAY_OF_YEAR
            )
            await interaction.response.defer()
            await self.refresh_message(feedback="✅ Reminder recurrence set to yearly.")
        elif selected_setup == self.RecurrenceSelectValue.WEEKLY_DAYS:
            self.selected_view = self.ReminderSetupView.WEEKDAYS_SELECTION
            await interaction.response.defer()
            await self.refresh_message()
        elif selected_setup == self.RecurrenceSelectValue.MONTHLY_DAYS:
            await interaction.response.send_modal(ReminderConditionedRecurrenceInputModal(
                interactions_handler=self,
            ))
        elif selected_setup == self.RecurrenceSelectValue.DELETE:
            await self.reminder_component.set_reminder_recurrence(reminder=self.reminder, recurrence_type=None)
            await interaction.response.defer()
            await self.refresh_message(feedback="✅ Reminder recurrence removed.")
        else:
            raise ValueError(f"Invalid recurrence setup: {selected_setup}")

    @interaction_handler()
    async def on_basic_recurrence_input_modal_submit(self, interaction: discord.Interaction, recurrence_input: str):
        if self.selected_recurrence_type_value == self.RecurrenceSelectValue.HOURS:
            unit = ReminderRecurrenceBasicUnit.HOUR
        elif self.selected_recurrence_type_value == self.RecurrenceSelectValue.DAYS:
            unit = ReminderRecurrenceBasicUnit.DAY
        else:
            raise ValueError(f"Invalid recurrence setup: {self.selected_recurrence_type_value}")
        if not recurrence_input.isdigit() or int(recurrence_input) < 1:
            await self.refresh_message()
            raise UserInputException("Invalid interval. Please enter a number greater than 0.")

        interval = int(recurrence_input)
        await self.reminder_component.set_reminder_recurrence(reminder=self.reminder,
                                                              recurrence_type=ReminderRecurrenceType.BASIC,
                                                              basic_interval=interval,
                                                              basic_unit=unit)
        await interaction.response.defer()
        await self.refresh_message(feedback=f"✅ Reminder recurrence set to every {interval} {unit.lower()}(s).")

    @interaction_handler()
    async def on_conditioned_recurrence_input_modal_submit(self, interaction: discord.Interaction,
                                                           recurrence_input: str):
        days = {int(day) for day in recurrence_input.split(",") if day.strip().isdigit()}
        if not days or not all(1 <= day <= 31 for day in days):
            await self.refresh_message()
            raise UserInputException("Invalid days. Please enter a comma-separated list of numbers between 1 and 31.")
        await self.reminder_component.set_reminder_recurrence(
            reminder=self.reminder,
            recurrence_type=ReminderRecurrenceType.CONDITIONED,
            conditioned_type=ReminderRecurrenceConditionedType.DAYS_OF_MONTH,
            conditioned_days=list(days)
        )
        await interaction.response.defer()
        await self.refresh_message(
            feedback=f"✅ Reminder recurrence set to send on the {', '.join(get_numbers_with_suffix(sorted(days)))} "
                     f"of every month starting after the next occurrence."
        )

    @interaction_handler()
    async def go_to_weekdays_selection(self, interaction: discord.Interaction):
        selected_days = [int(day) for day in interaction.data["values"]]
        if len(selected_days) == 7:
            await self.reminder_component.set_reminder_recurrence(reminder=self.reminder,
                                                                  recurrence_type=ReminderRecurrenceType.BASIC,
                                                                  basic_interval=1,
                                                                  basic_unit=ReminderRecurrenceBasicUnit.DAY)
        else:
            await self.reminder_component.set_reminder_recurrence(
                reminder=self.reminder,
                recurrence_type=ReminderRecurrenceType.CONDITIONED,
                conditioned_type=ReminderRecurrenceConditionedType.DAYS_OF_WEEK,
                conditioned_days=selected_days
            )
        await interaction.response.defer()
        self.selected_view = self.ReminderSetupView.REMINDER_SETUP
        await self.refresh_message(feedback=f"✅ Reminder recurrence set to weekly on "
                                            f"{', '.join(get_days_of_week_from_numbers(selected_days))}.")

    @interaction_handler()
    async def on_cancel_setup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_view = self.ReminderSetupView.REMINDER_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.list_interaction_handler:
            raise ValueError("No list interaction handler to go back to.")
        await self.list_interaction_handler.fetch_reminders()
        await self.list_interaction_handler.refresh_message()

    async def refresh_message(self, no_view=False, feedback=None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback=None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        if self.selected_view == self.ReminderSetupView.REMINDER_CONFIRMATION:
            embed = get_reminder_confirmation_embed(reminder=self.reminder, feedback_message=feedback)
            view = get_reminder_confirmation_view(interactions_handler=self,
                                                  add_back_button=bool(self.list_interaction_handler))
        elif self.selected_view == self.ReminderSetupView.REMINDER_SETUP:
            embed = get_reminder_setup_embed(reminder=self.reminder, feedback_message=feedback)
            view = get_reminder_setup_view(
                interactions_handler=self,
                timezone_set=bool(self.user_settings.timezone),
                add_back_button=bool(self.list_interaction_handler),
                show_recurrence=self.reminder.owner_user_settings_id == self.reminder.recipient_user_settings_id
            )
        elif self.selected_view == self.ReminderSetupView.DELETE_CONFIRMATION:
            embed = get_reminder_delete_confirmation_embed()
            view = get_delete_confirmation_view(interactions_handler=self)
        elif self.selected_view == self.ReminderSetupView.WEEKDAYS_SELECTION:
            embed = get_reminder_weekdays_selection_embed()
            view = get_weekdays_selection_view(interactions_handler=self)
        elif self.selected_view == self.ReminderSetupView.TIMEZONE_PROMPT:
            embed = get_timezone_prompt_embed(first_time=True)
            view = get_timezone_prompt_view(interactions_handler=self)
        else:
            raise ValueError(f"Invalid view: {self.selected_view}")
        return embed, view

    @require_db_session
    async def on_timeout(self):
        self.selected_view = self.ReminderSetupView.REMINDER_CONFIRMATION
        await super().on_timeout()
