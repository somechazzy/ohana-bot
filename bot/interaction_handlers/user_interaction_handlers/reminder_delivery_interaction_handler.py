from datetime import UTC, datetime, timedelta

import discord

from bot.utils.modal_factory.reminder_modals import ReminderSnoozeDurationModal
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.bot_actions.basic_actions import send_message
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.general_embeds import get_info_embed, get_success_embed, get_generic_embed
from bot.utils.view_factory.general_views import get_yes_no_view
from clients import discord_client
from common.exceptions import UserInputException
from components.user_settings_components.user_reminder_component import UserReminderComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import DiscordTimestamp, ReminderDeliveryAction
from models.user_settings_models import UserReminder, UserSettings
from settings import BOT_OWNER_ID
from utils.helpers.text_manipulation_helpers import get_human_readable_time
from utils.helpers.text_parsing_helpers import get_time_in_minutes_from_user_text


class ReminderDeliveryInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Reminder delivery"

    def __init__(self, reminder_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reminder_id = reminder_id
        self.reminder: UserReminder = ...
        self.user_settings: UserSettings = ...
        self.reminder_component = UserReminderComponent()

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)
        self.reminder = await self.reminder_component.get_reminder(reminder_id=self.reminder_id,
                                                                   load_user_settings=True,
                                                                   load_recurrence_settings=True)
        if not self.reminder:
            raise UserInputException("This reminder does not exist or has been deleted. Please create a new one.")
        self.user_settings = self.reminder.recipient

    async def handle_action(self, action: str):
        if action in ReminderDeliveryAction.snooze_actions():
            await self.on_snooze(self.source_interaction, action=action)
        elif action in [ReminderDeliveryAction.SETUP, ReminderDeliveryAction.EDIT]:
            await self.go_to_setup(self.source_interaction)
        elif action == ReminderDeliveryAction.BLOCK_ALL:
            await self.on_block_relayed_reminders(self.source_interaction)
        elif action == ReminderDeliveryAction.BLOCK_AUTHOR:
            await self.on_block_relayed_reminders_from_author(self.source_interaction)
        else:
            self.logger.warning(f"Unknown reminder action: {action}")
            await self.source_interaction.response.send_message("There was an issue with your request."
                                                                " We're already looking into it!")

    @interaction_handler()
    async def on_snooze(self, _: discord.Interaction, action: str):
        if action == ReminderDeliveryAction.SNOOZE_CUSTOM:
            await self.source_interaction.response.send_modal(ReminderSnoozeDurationModal(
                interactions_handler=self
            ))
            return
        minutes = int(action.split('-')[-1])
        await self.snooze_reminder(interaction=self.source_interaction, duration_in_minutes=minutes)

    @interaction_handler()
    async def on_snooze_modal_submit(self, interaction: discord.Interaction, duration_text: str):
        duration_in_minutes = get_time_in_minutes_from_user_text(duration_text)
        if not duration_in_minutes:
            raise UserInputException("Invalid time format. Valid examples:\n"
                                     "• `1d12h` means 1 day and 12 hours\n"
                                     "• `1h30m` means 1 hour and 30 minutes\n"
                                     "• `4h30m` means 4 hours and 30 minutes")
        await self.snooze_reminder(interaction=interaction, duration_in_minutes=duration_in_minutes)

    async def snooze_reminder(self, interaction: discord.Interaction, duration_in_minutes: int):
        await interaction.response.defer(thinking=True, ephemeral=True)
        new_reminder_time = datetime.now(UTC) + timedelta(minutes=duration_in_minutes)
        await self.reminder_component.create_reminder(reminder_time=new_reminder_time,
                                                      reminder_text=self.reminder.reminder_text,
                                                      owner_user_id=interaction.user.id,
                                                      recipient_user_id=interaction.user.id,
                                                      is_snoozed=True,
                                                      snoozed_from_reminder_id=self.reminder_id)
        message = await interaction.followup.send(
            embed=get_info_embed(
                f"Okie. I'll remind you again in {get_human_readable_time(minutes=duration_in_minutes)} "
                f"({DiscordTimestamp.SHORT_DATE_TIME.format(timestamp=int(new_reminder_time.timestamp()))})."
            ),
            ephemeral=True
        )
        try:
            await message.delete(delay=15)
        except:
            pass

    @interaction_handler()
    async def go_to_setup(self, _: discord.Interaction):
        from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
            ReminderSetupInteractionHandler
        interactions_handler = ReminderSetupInteractionHandler(
            source_interaction=self.source_interaction,
            context=self.context,
            guild_settings=None,
            user_settings=self.user_settings,
            reminder=self.reminder,
            view=ReminderSetupInteractionHandler.ReminderSetupView.REMINDER_SETUP
        )
        embed, view = interactions_handler.get_embed_and_view()

        await self.source_interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @interaction_handler()
    async def on_block_relayed_reminders(self, _: discord.Interaction):
        await UserSettingsComponent().update_user_settings(user_settings=self.user_settings,
                                                           relayed_reminders_disabled=True)
        await self.source_interaction.response.send_message(
            embed=get_success_embed("Got it! You will no longer receive reminders from others.\n"
                                    "You can change this behaviour using `/user-settings`\n"
                                    f"Would you like to report this reminder/user?"),
            view=get_yes_no_view(interaction_handler=self,
                                 yes_callback=self.on_reminder_report,
                                 no_callback=self.delete_original_response),
            ephemeral=True
        )

    @interaction_handler()
    async def on_block_relayed_reminders_from_author(self, _: discord.Interaction):
        await self.reminder_component.block_user_from_relaying_reminders(user_id=self.source_interaction.user.id,
                                                                         blocked_user_id=self.reminder.owner.user_id)
        await self.source_interaction.response.send_message(
            embed=get_success_embed(f"Got it! You will no longer receive reminders from "
                                    f"<@{self.reminder.owner.user_id}>.\n"
                                    f"Would you like to report this reminder/user?"),
            view=get_yes_no_view(interaction_handler=self,
                                 yes_callback=self.on_reminder_report,
                                 no_callback=self.delete_original_response),
            ephemeral=True
        )
        try:
            await self.source_interaction.message.delete()
        except:
            pass

    @interaction_handler()
    async def on_reminder_report(self, interaction: discord.Interaction):
        await send_message(
            channel=await discord_client.fetch_user(BOT_OWNER_ID),
            embed=get_generic_embed(
                f"User {self.source_interaction.user.mention} ({self.source_interaction.user}) "
                f"has reported a reminder:\n"
                f"Reminder ID:{self.reminder_id}\n"
                f"Content:\n"
                f"```{self.reminder.reminder_text}```"))
        try:
            await interaction.message.delete()
            await self.source_interaction.message.delete()
        except:
            pass
        await interaction.response.send_message(
            embed=get_success_embed("Report submitted! It'll be taken seriously and reviewed ASAP."),
            ephemeral=True
        )
