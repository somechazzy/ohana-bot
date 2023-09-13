import discord

from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class SingleMessageChannelsRoleNameModal(BaseModal, title="Choose role name"):
    role_name_input = discord.ui.TextInput(
        label="Role Name",
        max_length=50,
        min_length=1,
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

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_role_name_modal_submit(
            inter=interaction,
            role_name=self.role_name_input.value
        )
