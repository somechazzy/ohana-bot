import discord

from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class MusicPlayerAddTrackModal(BaseModal, title="Add to Queue"):
    track_input = discord.ui.TextInput(
        label="Enter a playlist/track name or URL",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_add_track_modal_submit(
            inter=interaction,
            input_text=self.track_input.value
        )


class MusicPlayerReportModal(BaseModal, title="Report a problem"):
    report_input = discord.ui.TextInput(
        label="Describe the problem you're facing..",
        max_length=4000,
        min_length=1,
        required=True,
        style=discord.TextStyle.long
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_report_modal_submit(
            inter=interaction,
            input_text=self.report_input.value
        )
