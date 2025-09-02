import asyncio

import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.automod_management_embeds import get_gallery_channels_setup_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.view_factory.automod_management_views import get_gallery_channels_setup_view
from components.guild_settings_components.guild_channel_settings_component import GuildChannelSettingsComponent


class ManageGalleryChannelsInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "Gallery channels management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True
        self.guild_channel_settings_component = GuildChannelSettingsComponent()

    @interaction_handler()
    async def on_channel_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_channel_id = int(interaction.data["values"][0])
        channel = self.guild.get_channel(selected_channel_id)
        existing = self.guild_settings.channel_id_is_gallery_channel.get(selected_channel_id)

        if not existing:
            if not channel:
                await self.refresh_message(feedback="I can't see that channel.")
                return
            elif channel.type != discord.ChannelType.text:
                await self.refresh_message(feedback="Please choose a text channel.")
                return
            elif not channel.permissions_for(self.guild.me).manage_messages:
                await self.refresh_message(feedback="I can't delete messages in that channel.")
                return
            await self.guild_channel_settings_component.set_guild_channel_settings(
                guild_id=self.guild.id,
                guild_settings_id=self.guild_settings.guild_settings_id,
                channel_id=selected_channel_id,
                is_gallery_channel=True
            )
        else:
            await self.guild_channel_settings_component.set_guild_channel_settings(
                guild_id=self.guild.id,
                guild_settings_id=self.guild_settings.guild_settings_id,
                channel_id=selected_channel_id,
                is_gallery_channel=False
            )

        await self.refresh_message(feedback=f"Channel <#{selected_channel_id}> "
                                            f"{'removed' if existing else 'added'}")
        await self.log_setting_change(event_text=f"{'Removed' if existing else 'Added'} gallery channel",
                                      fields=[GuildLogEventField(name="Channel", value=f"<#{selected_channel_id}>")])

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_gallery_channels_setup_embed(
            selected_channel_ids=[channel_id for channel_id, is_gallery_channel
                                  in self.guild_settings.channel_id_is_gallery_channel.items()
                                  if is_gallery_channel],
            guild=self.guild,
            feedback_message=feedback
        )
        view = get_gallery_channels_setup_view(interaction_handler=self)
        return embed, view

    async def fetch_and_cleanup_gallery_channels(self):
        invalid_gallery_channel_ids = []
        for channel_id, is_gallery_channel in self.guild_settings.channel_id_is_gallery_channel.items():
            if is_gallery_channel:
                channel = self.guild.get_channel(channel_id)
                if not channel:
                    invalid_gallery_channel_ids.append(channel_id)
        for channel_id in invalid_gallery_channel_ids:
            await self.guild_channel_settings_component.set_guild_channel_settings(
                guild_id=self.guild.id,
                guild_settings_id=self.guild_settings.guild_settings_id,
                channel_id=channel_id,
                is_gallery_channel=False
            )
