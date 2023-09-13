from utils.embed_factory import quick_embed
from utils.embed_factory import make_overview_embed
from slashes.admin_slashes.base_admin_slashes import AdminSlashes
from utils.decorators import slash_command
from user_interactions.admin_interactions.manage_autoroles_interactions_handler import \
    ManageAutoRolesInteractionsHandler
from user_interactions.admin_interactions.manage_gallery_channels_interactions_handler import \
    ManageGalleryChannelsInteractionsHandler
from user_interactions.admin_interactions.manage_logging_channel_interactions_handler import \
    ManageLoggingChannelInteractionsHandler
from user_interactions.admin_interactions.manage_single_message_channels_interactions_handler import \
    ManageSingleMessageChannelsInteractionsHandler


class GeneralAdminSlashes(AdminSlashes):

    @slash_command
    async def logging_channel(self):
        """
        /manage logging-channel
        Set or unset the logging channel for this server
        """
        if not await self.preprocess_and_validate():
            return

        current_logging_channel = self.guild.get_channel(self.guild_prefs.logs_channel)
        if not current_logging_channel:
            await self.guild_prefs_component.set_guild_logs_channel(guild=self.guild, channel_id=0)

        handler = ManageLoggingChannelInteractionsHandler(source_interaction=self.interaction,
                                                          guild=self.guild)
        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def role_persistence(self, enable: bool):
        """
        /manage role-persistence
        Enable or disable role persistence for this server
        """
        if not await self.preprocess_and_validate():
            return

        if enable == self.guild_prefs.role_persistence_enabled:
            await self.interaction.response.send_message(
                embed=quick_embed(
                    title="Role persistence",
                    text=f"Role persistence is already {'enabled' if enable else 'disabled'} for this server."
                ),
                ephemeral=True
            )
            return

        await self.guild_prefs_component.set_role_persistence_enabled_state(guild=self.guild, state=enable)

        await self.interaction.response.send_message(
            embed=quick_embed(
                title="Role persistence",
                text=f"{'Enabled' if enable else 'Disabled'} role persistence for this server."
            ),
            ephemeral=True
        )

    @slash_command
    async def autoroles(self):
        """
        /manage autoroles
        Configure autoroles for this server
        """
        if not await self.preprocess_and_validate():
            return

        handler = ManageAutoRolesInteractionsHandler(source_interaction=self.interaction,
                                                     guild=self.guild,)
        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def gallery_channels(self):
        """
        /manage gallery-channels
        Configure gallery channels for this server
        """
        if not await self.preprocess_and_validate():
            return

        handler = ManageGalleryChannelsInteractionsHandler(source_interaction=self.interaction,
                                                           guild=self.guild)
        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def single_message_channels(self):
        """
        /manage single-message-channels
        Configure single-message channels for this server
        """
        if not await self.preprocess_and_validate():
            return

        handler = ManageSingleMessageChannelsInteractionsHandler(source_interaction=self.interaction,
                                                                 guild=self.guild)
        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def settings_overview(self, make_visible: bool = False):
        """
        /manage settings-overview
        Show an overview of all settings for this server
        """
        if not await self.preprocess_and_validate():
            return

        embed = make_overview_embed(guild_prefs=self.guild_prefs,
                                    requested_by=self.interaction.user)

        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))
