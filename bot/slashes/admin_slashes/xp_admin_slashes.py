from bot.interaction_handlers.admin_interaction_handlers.manage_xp_settings_interaction_handler import \
    ManageXPSettingsInteractionHandler
from bot.interaction_handlers.admin_interaction_handlers.manage_xp_transfer_interaction_handler import \
    ManageXPTransferInteractionHandler
from bot.slashes.admin_slashes import AdminSlashes
from bot.utils.decorators import slash_command


class XPAdminSlashes(AdminSlashes):

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild"])
    async def settings(self):
        """
        /manage xp settings
        Manage XP and levels settings for this server
        """
        handler = ManageXPSettingsInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            guild_settings=self.guild_settings
        )
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild"])
    async def transfer(self):
        """
        /manage xp transfer
        Award or remove XP from users
        """
        handler = ManageXPTransferInteractionHandler(source_interaction=self.interaction,
                                                     context=self.context,
                                                     guild_settings=self.guild_settings)
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
