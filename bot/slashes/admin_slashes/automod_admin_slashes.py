from bot.interaction_handlers.admin_interaction_handlers.manage_auto_responses_interaction_handler import \
    ManageAutoResponsesInteractionHandler
from bot.interaction_handlers.admin_interaction_handlers.manage_autoroles_interaction_handler import \
    ManageAutorolesInteractionHandler
from bot.interaction_handlers.admin_interaction_handlers.manage_gallery_channels_interaction_handler import \
    ManageGalleryChannelsInteractionHandler
from bot.interaction_handlers.admin_interaction_handlers.manage_limited_messages_channels_interaction_handler import \
    ManageLimitedMessagesChannelsInteractionHandler
from bot.slashes.admin_slashes import AdminSlashes
from bot.utils.decorators import slash_command
from bot.utils.embed_factory.general_embeds import get_info_embed, get_success_embed
from bot.utils.bot_actions.automod_actions import initialize_role_persistence_on_guild
from strings.commands_strings import AdminSlashCommandsStrings
from strings.general_strings import GeneralStrings
from utils.helpers.context_helpers import create_isolated_task


class AutomodAdminSlashes(AdminSlashes):

    @slash_command(guild_only=True,
                   bot_permissions=["manage_roles"],
                   user_permissions=["manage_guild"])
    async def role_persistence(self, enable: bool):
        """
        /manage role-persistence
        Enable or disable role persistence for this server
        """
        if enable == self.guild_settings.role_persistence_enabled:
            await self.interaction.response.send_message(
                embed=get_info_embed(AdminSlashCommandsStrings.ROLE_PERSISTENCE_ALREADY_SET_ERROR_MESSAGE.format(
                    state=GeneralStrings.ENABLED if enable else GeneralStrings.DISABLED
                )),
                ephemeral=True
            )
            return

        await self.guild_settings_component.update_guild_settings(
            guild_id=self.guild.id,
            role_persistence_enabled=enable
        )

        if enable:
            create_isolated_task(initialize_role_persistence_on_guild(guild=self.guild))

        await self.interaction.response.send_message(
            embed=get_success_embed(
                title=AdminSlashCommandsStrings.ROLE_PERSISTENCE_TITLE,
                message=AdminSlashCommandsStrings.ROLE_PERSISTENCE_SET_SUCCESS_MESSAGE.format(
                    state=GeneralStrings.ENABLED if enable else GeneralStrings.DISABLED
                )
            ),
            ephemeral=True
        )

    @slash_command(guild_only=True,
                   bot_permissions=["manage_roles"],
                   user_permissions=["manage_guild", "manage_roles"])
    async def autoroles(self):
        """
        /manage autoroles
        Configure autoroles for this server
        """
        handler = ManageAutorolesInteractionHandler(source_interaction=self.interaction,
                                                    guild_settings=self.guild_settings,
                                                    context=self.context)
        await handler.fetch_and_cleanup_autoroles()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild", "manage_messages"],
                   bot_permissions=["manage_messages"])
    async def auto_responses(self):
        """
        /manage auto-responses
        Configure auto-responses for this server
        """
        handler = ManageAutoResponsesInteractionHandler(source_interaction=self.interaction,
                                                        guild_settings=self.guild_settings,
                                                        context=self.context)
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild", "manage_messages"],
                   bot_permissions=["manage_messages"])
    async def gallery_channels(self):
        """
        /manage gallery-channels
        Configure gallery channels for this server
        """
        handler = ManageGalleryChannelsInteractionHandler(source_interaction=self.interaction,
                                                          guild_settings=self.guild_settings,
                                                          context=self.context)
        await handler.fetch_and_cleanup_gallery_channels()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild", "manage_messages"],
                   bot_permissions=["manage_roles"])
    async def limited_messages_channels(self):
        """
        /manage limited-messages-channels
        Configure limited-messages channels for this server
        """
        handler = ManageLimitedMessagesChannelsInteractionHandler(source_interaction=self.interaction,
                                                                  guild_settings=self.guild_settings,
                                                                  context=self.context)
        await handler.fetch_and_cleanup_limited_messages_channels()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
