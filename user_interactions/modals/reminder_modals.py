import discord

from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class ReminderSnoozeDurationModal(BaseModal, title="Reminder Snooze"):
    duration_input = discord.ui.TextInput(
        label="When should I remind you again?",
        max_length=50,
        min_length=1,
        placeholder="Examples: 15m, 6h 30m, 1d 12h, 3w, etc..",
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_setup_message(feedback_message="Something went wrong. "
                                                                               "Please try again and if this persists "
                                                                               "let us know using `/feedback` command.")

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_snooze_modal_submit(
            interaction=interaction,
            duration_text=self.duration_input.value
        )
