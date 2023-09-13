from datetime import timedelta, datetime

import discord

from globals_.constants import Colour
from user_interactions.modals.reminder_modals import ReminderSnoozeDurationModal
from utils.decorators import interaction_handler
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler
from utils.embed_factory import quick_embed
from utils.helpers import get_duration_in_minutes_from_text, convert_minutes_to_time_string, get_reminder_views
from globals_.clients import reminder_service


class ReminderInteractionsHandler(UserInteractionsHandler):

    def __init__(self, source_interaction):
        super().__init__(source_interaction=source_interaction)
        self._reminder = source_interaction.message.embeds[0].description

    async def handle_snooze(self):
        if self.source_interaction.data["values"][0] == "custom":
            await self.source_interaction.response.send_modal(ReminderSnoozeDurationModal(
                interactions_handler=self
            ))
        elif self.source_interaction.data["values"][0].isdigit():
            await self.snooze_reminder(interaction=self.source_interaction,
                                       duration_in_minutes=int(self.source_interaction.data["values"][0]))
        else:
            await self.source_interaction.response.defer()

    @interaction_handler
    async def handle_snooze_modal_submit(self, interaction: discord.Interaction, duration_text: str):
        duration_in_minutes = get_duration_in_minutes_from_text(duration_text)
        if not duration_in_minutes:
            await interaction.response.send_message(
                embed=quick_embed("Invalid time format. Valid examples:\n"
                                  "• `1d12h` means 1 day and 12 hours\n"
                                  "• `1h30m` means 1 hour and 30 minutes\n"
                                  "• `4h30m` means 4 hours and 30 minutes",
                                  emoji='',
                                  color=Colour.ERROR,
                                  bold=False),
                ephemeral=True
            )
            return
        await self.snooze_reminder(interaction=interaction, duration_in_minutes=duration_in_minutes)

    @interaction_handler
    async def snooze_reminder(self, interaction: discord.Interaction, duration_in_minutes: int):
        await reminder_service.add_reminder(
            timestamp=(datetime.utcnow() + timedelta(minutes=duration_in_minutes)).timestamp(),
            reason=self._reminder,
            user_id=self.source_interaction.user.id
        )
        await interaction.response.send_message(
            embed=quick_embed(
                f"Okie. I'll remind you again in {convert_minutes_to_time_string(duration_in_minutes)}.",
                color=Colour.PRIMARY_ACCENT,
                bold=False
            ),
            ephemeral=True
        )
        original_reminder_embed = self.source_interaction.message.embeds[0]
        reminder_views = get_reminder_views()
        await self.source_interaction.message.edit(
            embed=original_reminder_embed,
            view=reminder_views
        )
