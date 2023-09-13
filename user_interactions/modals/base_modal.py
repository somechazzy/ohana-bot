import traceback
import discord
from globals_.constants import BotLogLevel
from internal.bot_logger import ErrorLogger


class BaseModal(discord.ui.Modal, title="Form"):

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(**kwargs)
        self.interactions_handler = interactions_handler
        self.modal_name = self.__class__.__name__
        self.error_logger = ErrorLogger(component=self.modal_name)

    async def interaction_check(self, interaction: discord.Interaction):
        return self.interactions_handler.source_interaction.user.id == interaction.user.id

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("An error occurred while processing your input."
                                                " We're working on fixing it.", ephemeral=True)
        self.error_logger.log(message=f"An error occurred while processing {self.modal_name} modal input: "
                                      f"{error}\n{traceback.format_exc()}",
                              level=BotLogLevel.ERROR,
                              guild_id=self.interactions_handler.source_interaction.guild.id
                              if self.interactions_handler.source_interaction.guild else None,
                              user_id=interaction.user.id)

    async def on_submit(self, interaction: discord.Interaction):
        raise NotImplementedError
