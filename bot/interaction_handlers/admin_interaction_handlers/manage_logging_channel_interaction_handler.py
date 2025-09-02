import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.general_management_embeds import get_logging_channel_setup_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.view_factory.general_management_views import get_logging_channel_setup_view


class ManageLoggingChannelInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "Logging Channel management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True

    @interaction_handler()
    async def on_channel_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_channel_id = int(interaction.data["values"][0])
        channel = self.guild.get_channel(selected_channel_id)

        if not channel:
            await self.refresh_message(feedback="I can't see that channel.")
            return
        elif channel.id == self.guild_settings.logging_channel_id:
            await self.refresh_message(feedback="This channel is already set as the logging channel.")
            return
        elif channel.type != discord.ChannelType.text:
            await self.refresh_message(feedback="Please choose a text channel.")
            return
        elif not channel.permissions_for(self.guild.me).send_messages:
            await self.refresh_message(feedback="I can't send messages in that channel.")
            return
        elif not channel.permissions_for(self.guild.me).embed_links:
            await self.refresh_message(feedback="I need the **Embed Links** permission in that channel.")
            return

        await self.guild_settings_component.update_guild_settings(guild_id=self.guild.id,
                                                                  logging_channel_id=selected_channel_id)

        await self.refresh_message(feedback=f"Channel {channel.mention} set as logging channel.")
        await self.log_setting_change(event_text=f"Set the logging channel",
                                      fields=[GuildLogEventField(name="Channel",
                                                                 value=f"{channel.mention} (duh)")])

    @interaction_handler()
    async def create_new_channel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.guild.me.guild_permissions.manage_channels:
            await self.refresh_message(feedback="I need the **Manage Channels** permission to do that.")
            return

        logging_channel = await self.guild.create_text_channel(
            name="📃-logs",
            reason="Logging channel creation."
        )

        await self.guild_settings_component.update_guild_settings(guild_id=self.guild.id,
                                                                  logging_channel_id=logging_channel.id)

        await self.refresh_message(feedback=f"Created new logging channel: {logging_channel.mention}.")
        await self.log_setting_change(event_text="Created and set the logging channel",
                                      fields=[GuildLogEventField(name="Channel",
                                                                 value=f"{logging_channel.mention} (duh)")])

    @interaction_handler()
    async def unset_channel(self, interaction: discord.Interaction):
        await interaction.response.defer()

        channel = self.guild.get_channel(int(self.guild_settings.logging_channel_id))
        await self.guild_settings_component.update_guild_settings(guild_id=self.guild.id, logging_channel_id=None)

        await self.refresh_message(feedback=f"Unset the logging channel ({channel.mention if channel else 'deleted'}).")

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_logging_channel_setup_embed(
            logging_channel_id=self.guild_settings.logging_channel_id,
            guild=self.guild,
            feedback_message=feedback
        )
        view = get_logging_channel_setup_view(
            interaction_handler=self,
            current_logging_channel=self.guild.get_channel(self.guild_settings.logging_channel_id)
        )
        return embed, view

    async def fetch_and_cleanup_logging_channel(self):
        if self.guild_settings.logging_channel_id:
            channel = self.guild.get_channel(self.guild_settings.logging_channel_id)
            if not channel:
                await self.guild_settings_component.update_guild_settings(
                    guild_id=self.guild.id, logging_channel_id=None
                )
