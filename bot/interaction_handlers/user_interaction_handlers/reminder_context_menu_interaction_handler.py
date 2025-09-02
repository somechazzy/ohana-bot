from datetime import datetime, UTC, timedelta

import discord

from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
    ReminderSetupInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.general_embeds import get_generic_embed
from common.exceptions import UserInputException
from components.user_settings_components.user_reminder_component import UserReminderComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from utils.helpers.text_parsing_helpers import get_time_in_minutes_from_user_text


class ReminderContextMenuInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Reminder setup - context menu"

    def __init__(self, target_message: discord.Message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_message: discord.Message = target_message
        self.reminder_component = UserReminderComponent()

    @interaction_handler()
    async def on_set_when_modal_submit(self, interaction: discord.Interaction, when_text: str):
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

        try:
            reminder = await self.reminder_component.create_reminder(
                reminder_text=self.target_message.jump_url,
                reminder_time=reminder_time,
                owner_user_id=self.original_user.id,
                recipient_user_id=self.original_user.id,
            )
        except Exception as e:
            self.logger.error(f"Failed at creating reminder for {self.original_user.id}. Error: {e}.")
            return await interaction.response.send_message(
                embed=get_generic_embed("😔 Failed at setting up your reminder. "
                                        "We're already looking into it."),
                ephemeral=True
            )

        interactions_handler = ReminderSetupInteractionHandler(
            source_interaction=interaction,
            context=self.context,
            user_settings=await UserSettingsComponent().get_user_settings(self.original_user.id),
            guild_settings=None,
            reminder=reminder,
            view=ReminderSetupInteractionHandler.ReminderSetupView.REMINDER_CONFIRMATION
        )

        embed, view = interactions_handler.get_embed_and_view()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
