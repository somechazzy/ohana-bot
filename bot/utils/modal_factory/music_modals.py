import discord
from discord.ui import TextInput, Label

from bot.utils.modal_factory import BaseModal


class MusicPlayerReportModal(BaseModal, title="Report a problem"):
    report_label = Label(
        text="Report",
        description="Describe the problem you're facing",
        component=TextInput(
            max_length=4000,
            min_length=1,
            required=True,
            style=discord.TextStyle.long
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_report_modal_submit(
            interaction=interaction,
            report_text=self.report_label.component.value
        )
