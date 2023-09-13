from globals_.constants import XPTransferAction, XPTransferActionTarget
from slashes.admin_slashes.base_admin_slashes import AdminSlashes
from discord.ext.commands import GroupCog

from utils.decorators import slash_command
from user_interactions.admin_interactions.manage_xp_settings_interactions_handler import \
    ManageXPSettingsInteractionsHandler
from user_interactions.admin_interactions.manage_xp_transfer_interactions_handler import \
    ManageXPTransferInteractionsHandler
from user_interactions.modals.admin_xp_modals import XPTransferResetConfirmationModal, XPTransferAmountModal


class XPAdminSlashes(GroupCog, AdminSlashes):

    @slash_command
    async def settings(self):
        """
        /manage xp settings
        Manage XP and levels settings for this server
        """
        if not await self.preprocess_and_validate():
            return

        await self.validate_xp_roles_and_channels()

        handler = ManageXPSettingsInteractionsHandler(source_interaction=self.interaction,
                                                      guild=self.guild)
        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def overview(self, make_visible: bool = False):
        """
        /manage xp overview
        Overview of XP and levels settings for this server
        """
        if not await self.preprocess_and_validate():
            return

        await self.validate_xp_roles_and_channels()

        feedback_message = None

        handler = ManageXPSettingsInteractionsHandler(source_interaction=self.interaction,
                                                      guild=self.guild)
        embed, views = handler.get_embed_and_views(is_overview=True,
                                                   feedback_message=feedback_message)

        await self.interaction.response.send_message(embed=embed, view=views,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command
    async def transfer(self, action: XPTransferAction, target: XPTransferActionTarget):
        """
        /manage xp transfer
        Award or remove XP from users
        """
        if not await self.preprocess_and_validate():
            return

        if action not in XPTransferAction:
            await self.interaction.response.send_message("Invalid action", ephemeral=True)
            return

        if target not in XPTransferActionTarget:
            await self.interaction.response.send_message("Invalid target", ephemeral=True)
            return

        if target in (XPTransferActionTarget.EVERYONE, XPTransferActionTarget.ROLE):
            if not self.member.guild_permissions.administrator:
                await self.interaction.response.send_message("This action is too powerful and can only be performed by "
                                                             "server administrators",
                                                             ephemeral=True)
                return

        handler = ManageXPTransferInteractionsHandler(source_interaction=self.interaction,
                                                      guild=self.guild,
                                                      target=target,
                                                      action=action)

        if action == XPTransferAction.RESET:
            if target == XPTransferActionTarget.EVERYONE:
                await self.interaction.response.send_modal(XPTransferResetConfirmationModal(
                    interactions_handler=handler,
                ))
                return

        if target == XPTransferActionTarget.EVERYONE:
            await self.interaction.response.send_modal(XPTransferAmountModal(interactions_handler=handler,
                                                                             action=action,
                                                                             target=target))
            return

        embed, views = handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)
