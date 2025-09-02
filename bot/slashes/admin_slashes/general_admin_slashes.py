from bot.interaction_handlers.admin_interaction_handlers.manage_logging_channel_interaction_handler import \
    ManageLoggingChannelInteractionHandler
from bot.slashes.admin_slashes import AdminSlashes
from bot.utils.decorators import slash_command
from bot.utils.embed_factory.general_management_embeds import get_guild_settings_embed


class GeneralAdminSlashes(AdminSlashes):

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild"])
    async def logging_channel(self):
        """
        /manage logging-channel
        Manage the logging channel for this server
        """
        handler = ManageLoggingChannelInteractionHandler(source_interaction=self.interaction,
                                                         context=self.context,
                                                         guild_settings=self.guild_settings)
        await handler.fetch_and_cleanup_logging_channel()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild"])
    async def settings(self, make_visible: bool = False):
        """
        /manage settings
        View a summary and manage all the settings for this server
        """
        embed = get_guild_settings_embed(guild=self.guild, guild_settings=self.guild_settings)
        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))
