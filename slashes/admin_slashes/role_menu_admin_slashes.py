from discord import NotFound as DiscordNotFound, Forbidden as DiscordForbidden
from actions import send_message
from utils.embed_factory import make_role_menu_setup_embed, make_role_menu_embed
from globals_.constants import RoleMenuType, RoleMenuMode
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from utils.helpers import get_role_menu_setup_views
from slashes.admin_slashes.base_admin_slashes import AdminSlashes
from utils.decorators import slash_command
from user_interactions.admin_interactions.manage_role_menu_interactions_handler import ManageRoleMenuInteractionsHandler


class RoleMenuAdminSlashes(AdminSlashes):

    @slash_command
    async def role_menu_create(self):
        """
        /manage role-menu create
        Create a new role menu
        """
        if not await self.preprocess_and_validate():
            return

        role_menu_embed = make_role_menu_embed(role_menu_name="General Role Menu",
                                               guild=self.guild,
                                               title="Use this menu to select your role(s)")
        role_menu_message = await send_message(message=None, embed=role_menu_embed, channel=self.channel)
        role_menu_setup_embed = make_role_menu_setup_embed(guild=self.guild,
                                                           added_roles_map={},
                                                           role_menu_type=RoleMenuType.SELECT,
                                                           role_menu_mode=RoleMenuMode.SINGLE,
                                                           restricted_to_roles=[])
        interactions_handler = ManageRoleMenuInteractionsHandler(source_interaction=self.interaction,
                                                                 role_menu_message=role_menu_message)
        views = get_role_menu_setup_views(interactions_handler=interactions_handler)
        await self.interaction.response.send_message(embed=role_menu_setup_embed, ephemeral=True, view=views)
        await interactions_handler.sync_config()

    @slash_command
    async def role_menu_edit(self, message_id: str):
        """
        /manage role-menu create
        Create a new role menu
        """
        if not await self.preprocess_and_validate():
            return

        if not message_id.isdigit():
            return self.return_error_message(message="Invalid message ID")

        message_id = int(message_id)

        try:
            role_menu_message = await self.channel.fetch_message(message_id)
        except DiscordNotFound:
            return self.return_error_message(message="Message not found")
        except DiscordForbidden:
            return self.return_error_message(message="I don't have permission to access that message")
        if not role_menu_message:
            return self.return_error_message(message="Message not found")

        role_menu_config = (await GuildPrefsComponent().get_guild_prefs(self.guild)).role_menus.get(message_id)
        if not role_menu_config:
            return self.return_error_message(message="No role menu found")

        role_menu_name, role_menu_description, role_menu_type, role_menu_mode, added_roles_map, restricted_to_roles, \
            image_url, image_placement, role_menu_footer, role_menu_color, restricted_description = \
            self.extract_role_menu_params(role_menu_message=role_menu_message,
                                          role_menu_config=role_menu_config)

        role_menu_setup_embed = make_role_menu_setup_embed(guild=self.guild,
                                                           added_roles_map=added_roles_map,
                                                           role_menu_type=role_menu_type,
                                                           role_menu_mode=role_menu_mode,
                                                           restricted_to_roles=restricted_to_roles)
        interactions_handler = ManageRoleMenuInteractionsHandler(source_interaction=self.interaction,
                                                                 role_menu_message=role_menu_message,
                                                                 role_menu_name=role_menu_name,
                                                                 role_menu_description=role_menu_description,
                                                                 role_menu_type=role_menu_type,
                                                                 role_menu_mode=role_menu_mode,
                                                                 added_roles_map=added_roles_map,
                                                                 image_url=image_url,
                                                                 image_placement=image_placement,
                                                                 role_menu_footer=role_menu_footer,
                                                                 role_menu_color=role_menu_color,
                                                                 restricted_to_roles=restricted_to_roles,
                                                                 restricted_description=restricted_description)
        views = get_role_menu_setup_views(interactions_handler=interactions_handler,
                                          roles_removable=bool(added_roles_map),
                                          is_restricted=bool(restricted_to_roles),
                                          image_added=bool(image_url))
        await self.interaction.response.send_message(embed=role_menu_setup_embed, ephemeral=True, view=views)
        await interactions_handler.sync_config()
