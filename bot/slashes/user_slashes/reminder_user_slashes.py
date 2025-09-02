from datetime import timedelta, datetime, UTC

import discord

from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
    ReminderSetupInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.reminder_list_interaction_handler import \
    ReminderListInteractionHandler
from bot.slashes.user_slashes import UserSlashes
from bot.utils.decorators import slash_command
from bot.utils.embed_factory.general_embeds import get_generic_embed, get_success_embed
from common.exceptions import UserInputException
from components.user_settings_components.user_reminder_component import UserReminderComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import DiscordTimestamp
from strings.commands_strings import UserSlashCommandsStrings
from utils.helpers.text_manipulation_helpers import get_human_readable_time
from utils.helpers.text_parsing_helpers import get_time_in_minutes_from_user_text


class RemindUserSlashes(UserSlashes):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reminder_component = UserReminderComponent()

    @slash_command()
    async def me(self, when: str, what: str):
        """
        /remind me
        Remind me of something at a specific time
        """
        minutes = get_time_in_minutes_from_user_text(when)

        if not minutes:
            raise UserInputException(UserSlashCommandsStrings.INVALID_DURATION_ERROR_MESSAGE)
        if minutes > 60 * 24 * 366:
            raise UserInputException(UserSlashCommandsStrings.REMIND_EXCEEDS_MAX_ERROR_MESSAGE)

        try:
            reminder = await self.reminder_component.create_reminder(
                reminder_text=what,
                reminder_time=datetime.now(UTC) + timedelta(minutes=minutes),
                owner_user_id=self.user.id,
                recipient_user_id=self.user.id
            )
        except Exception as e:
            self.logger.error(f"Failed at creating reminder for {self.user.id}. Error: {e}.")
            return await self.interaction.response.send_message(
                embed=get_generic_embed(UserSlashCommandsStrings.GENERIC_REMINDER_CREATION_ERROR_MESSAGE),
                ephemeral=True
            )

        interactions_handler = ReminderSetupInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            user_settings=await UserSettingsComponent().get_user_settings(self.user.id),
            guild_settings=self.guild_settings,
            reminder=reminder,
            view=ReminderSetupInteractionHandler.ReminderSetupView.REMINDER_CONFIRMATION
        )

        embed, view = interactions_handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command()
    async def someone(self, who: discord.Member | discord.User, when: str, what: str):
        """
        /remind someone
        Remind someone of something at a specific time
        """
        minutes = get_time_in_minutes_from_user_text(when)

        if not minutes:
            raise UserInputException(UserSlashCommandsStrings.INVALID_DURATION_ERROR_MESSAGE)
        if minutes > 60 * 24 * 366:
            raise UserInputException(UserSlashCommandsStrings.REMIND_EXCEEDS_MAX_ERROR_MESSAGE)

        reminder_time = datetime.now(UTC) + timedelta(minutes=minutes)
        try:
            await self.reminder_component.create_reminder(
                reminder_text=what,
                reminder_time=reminder_time,
                owner_user_id=self.user.id,
                recipient_user_id=who.id
            )
        except Exception as e:
            self.logger.error(f"Failed at creating reminder for {self.user.id}. Error: {e}.")
            return await self.interaction.response.send_message(
                embed=get_generic_embed(UserSlashCommandsStrings.GENERIC_REMINDER_CREATION_ERROR_MESSAGE),
                ephemeral=True
            )

        await self.interaction.response.send_message(
            embed=get_success_embed(
                UserSlashCommandsStrings.REMIND_OTHER_SUCCESS_FEEDBACK.format(
                    member_name=who.display_name,
                    member_mention=who.mention,
                    duration=get_human_readable_time(minutes),
                    timestamp=DiscordTimestamp.SHORT_DATE_TIME.format(timestamp=int(reminder_time.timestamp()))
                )
            ),
            ephemeral=True
        )

    @slash_command()
    async def list(self):
        """
        /remind list
        List & manage all of your reminders
        """
        user_settings = await UserSettingsComponent().get_user_settings(self.user.id)
        interactions_handler = ReminderListInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            user_settings=user_settings,
            guild_settings=self.guild_settings,
            reminders=await self.reminder_component.get_user_reminders(user_id=self.user.id),
            page=1
        )

        embed, view = interactions_handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
