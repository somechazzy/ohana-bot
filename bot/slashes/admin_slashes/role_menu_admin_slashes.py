from discord import NotFound as DiscordNotFound, Forbidden as DiscordForbidden

from bot.interaction_handlers.admin_interaction_handlers.manage_role_menu_interaction_handler import \
    ManageRoleMenuInteractionHandler
from bot.utils.decorators import slash_command
from bot.slashes.admin_slashes import AdminSlashes
from bot.utils.embed_factory.role_menu_embeds import get_role_menu_embed
from common.exceptions import UserInputException
from components.guild_settings_components.guild_role_menu_component import GuildRoleMenuComponent
from models.dto.role_menu import RoleMenuSettings
from strings.commands_strings import AdminSlashCommandsStrings


class RoleMenuAdminSlashes(AdminSlashes):

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild", "manage_roles"],
                   bot_permissions=["send_messages", "embed_links", "read_messages",
                                    "read_message_history", "manage_roles"])
    async def role_menu_create(self):
        """
        /manage role-menu create
        Create a new role menu
        """
        if not self.channel.permissions_for(self.guild.me).send_messages \
                or not self.channel.permissions_for(self.guild.me).embed_links \
                or not self.channel.permissions_for(self.guild.me).read_message_history:
            raise UserInputException(AdminSlashCommandsStrings.ROLE_MENU_CREATE_PERMISSION_ERROR_MESSAGE)

        role_menu_message = await self.channel.send(embed=get_role_menu_embed(guild=self.guild))
        await GuildRoleMenuComponent().create_role_menu(guild_id=self.guild.id,
                                                        channel_id=role_menu_message.channel.id,
                                                        message_id=role_menu_message.id)

        handler = ManageRoleMenuInteractionHandler(source_interaction=self.interaction,
                                                   context=self.context,
                                                   guild_settings=self.guild_settings,
                                                   role_menu_message=role_menu_message,
                                                   role_menu_settings=RoleMenuSettings.with_defaults())
        await handler.fetch_and_cleanup_roles()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild", "manage_roles"],
                   bot_permissions=["send_messages", "embed_links", "read_messages",
                                    "read_message_history", "manage_roles"])
    async def role_menu_edit(self, message_id: str):
        """
        /manage role-menu edit
        Edits a role menu
        """
        if not message_id.isdigit():
            raise UserInputException(AdminSlashCommandsStrings.ROLE_MENU_EDIT_INVALID_MESSAGE_ID_ERROR_MESSAGE)

        message_id = int(message_id)

        try:
            role_menu_message = await self.channel.fetch_message(message_id)
        except DiscordNotFound:
            raise UserInputException(AdminSlashCommandsStrings.ROLE_MENU_EDIT_MESSAGE_NOT_FOUND_ERROR_MESSAGE)
        except DiscordForbidden:
            raise UserInputException(AdminSlashCommandsStrings.ROLE_MENU_EDIT_PERMISSION_ERROR_MESSAGE)
        if not role_menu_message:
            raise UserInputException(AdminSlashCommandsStrings.ROLE_MENU_EDIT_MESSAGE_NOT_FOUND_ERROR_MESSAGE)

        handler = await ManageRoleMenuInteractionHandler.from_role_menu_message(source_interaction=self.interaction,
                                                                                role_menu_message=role_menu_message)
        await handler.fetch_and_cleanup_roles()
        embed, view = handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
