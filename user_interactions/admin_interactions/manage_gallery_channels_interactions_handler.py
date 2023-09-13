import asyncio
import discord
from utils.embed_factory import make_gallery_channels_management_embed
from utils.helpers import get_channels_management_views
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from utils.decorators import interaction_handler


class ManageGalleryChannelsInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction, guild=guild)

    @interaction_handler
    async def handle_channel_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        channel_id = int(inter.data["values"][0])
        removed = channel_id in self.guild_prefs.gallery_channels

        await inter.response.defer()
        channel = self.guild.get_channel(channel_id)
        if not removed:
            if not channel or not channel.type == discord.ChannelType.text:
                return await self.refresh_setup_message(feedback_message="I can't see that channel.")
            if not channel.permissions_for(self.guild.me).manage_messages:
                return await self.refresh_setup_message(feedback_message="I don't have the permission"
                                                                         "to delete messages there "
                                                                         "(**Manage Messages** permission missing).")
            await self.guild_prefs_component.add_guild_gallery_channel(guild=self.guild, channel_id=channel_id)
        else:
            await self.guild_prefs_component.remove_guild_gallery_channel(guild=self.guild, channel_id=channel_id)

        await self.refresh_setup_message(feedback_message=f"Channel {channel.mention}"
                                                          f" {'removed' if removed else 'added'}")

        await self.log_action_to_server(event=f"Changed gallery channels ({'removed' if removed else 'added'} channel)",
                                        field_value_map={"Channel": f"{channel.mention}"})

    @interaction_handler
    async def handle_clear_channels(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.defer()

        existing_channels = self.guild_prefs.gallery_channels.copy()

        await self.guild_prefs_component.clear_guild_gallery_channels(guild=self.guild)
        await self.refresh_setup_message(feedback_message="All gallery channels removed")

        await self.log_action_to_server(event=f"Changed gallery channels (removed all channels)",
                                        field_value_map={"Channels": ", ".join([f"{channel.mention}"
                                                                                for channel in existing_channels])})

    async def refresh_setup_message(self, feedback_message=None):
        embed, views = self.get_embed_and_views(feedback_message=feedback_message)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    def get_embed_and_views(self, feedback_message=None):
        embed = make_gallery_channels_management_embed(guild=self.guild,
                                                       gallery_channels_ids=self.guild_prefs.gallery_channels,
                                                       feedback_message=feedback_message)
        views = get_channels_management_views(interactions_handler=self,
                                              add_clear_button=bool(self.guild_prefs.gallery_channels))

        return embed, views
