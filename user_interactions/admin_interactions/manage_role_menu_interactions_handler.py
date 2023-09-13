import re
import discord
import emoji as emoji_lib
from actions import edit_message
from utils.embed_factory import make_role_menu_setup_embed, make_role_menu_embed
from globals_.clients import discord_client
from globals_.constants import RoleMenuType, RoleMenuMode, RoleMenuImagePlacement, Colour
from utils.helpers import get_role_menu_setup_views, get_role_menu_views
from utils.decorators import interaction_handler
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from user_interactions.modals.admin_role_menu_setup_modals import RoleMenuSetupBasicModal, RoleMenuSetupAddImageModal, \
    RoleMenuSetupAddRestrictionModal, RoleMenuSetupAddRoleModal


class ManageRoleMenuInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, role_menu_message, added_roles_map=None, role_menu_type=RoleMenuType.SELECT,
                 role_menu_mode=RoleMenuMode.SINGLE, restricted_to_roles=None, image_url=None,
                 image_placement=RoleMenuImagePlacement.THUMBNAIL, role_menu_name="General Role Menu",
                 role_menu_description="Use this menu to select your role(s)", role_menu_footer=None,
                 role_menu_color=Colour.PRIMARY_ACCENT, restricted_description=None):
        super().__init__(source_interaction=source_interaction)
        self.role_menu_message: discord.Message = role_menu_message
        self.added_roles_map = added_roles_map or {}
        self.role_menu_type = role_menu_type
        self.role_menu_mode = role_menu_mode
        self.restricted_to_roles = restricted_to_roles or []
        self.image_url = image_url
        self.image_placement = image_placement
        self.role_menu_name = role_menu_name
        self.role_menu_description = role_menu_description
        self.role_menu_footer = role_menu_footer
        self.role_menu_color = role_menu_color
        self.restricted_description = restricted_description or ""

    @interaction_handler
    async def handle_basic_setup(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(RoleMenuSetupBasicModal(interactions_handler=self,
                                                                existing_menu_title=self.role_menu_name,
                                                                existing_menu_description=self.role_menu_description,
                                                                existing_menu_footer=self.role_menu_footer,
                                                                existing_menu_color=self.role_menu_color))

    async def handle_basic_setup_modal_submit(self, inter: discord.Interaction, menu_title, menu_description,
                                              menu_footer, menu_color):
        self.role_menu_name = menu_title
        self.role_menu_description = menu_description
        self.role_menu_footer = menu_footer
        warning_message = ""
        if menu_color:
            try:
                if menu_color.startswith("#"):
                    menu_color = menu_color[1:]
                self.role_menu_color = int(menu_color, 16)
            except (ValueError, TypeError):
                warning_message = "However, your color input was invalid, so the color was not changed."

        await self.refresh_embeds(inter=inter, setup_info=f"Updated basic info. {warning_message}", defer=True)

    @interaction_handler
    async def handle_role_menu_type(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if self.role_menu_type == RoleMenuType.SELECT:
            self.role_menu_type = RoleMenuType.BUTTON
            from_to = "from **Dropdown Select** to **Buttons**"
        else:
            self.role_menu_type = RoleMenuType.SELECT
            from_to = "from **Buttons** to **Dropdown Select**"

        await self.refresh_embeds(inter=inter, setup_info=f"Changed menu type {from_to}", defer=True)
        await self.sync_config()

    @interaction_handler
    async def handle_role_menu_mode(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if self.role_menu_mode == RoleMenuMode.SINGLE:
            self.role_menu_mode = RoleMenuMode.MULTIPLE
            from_to = "from **Single Role** to **Multiple Roles**"
        else:
            self.role_menu_mode = RoleMenuMode.SINGLE
            from_to = "from **Multiple Roles** to **Single Role**"
        await self.refresh_embeds(inter=inter, setup_info=f"Changed selection mode {from_to}", defer=True)
        await self.sync_config()

    @interaction_handler
    async def handle_add_role(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if len(self.added_roles_map) >= 25:
            return await self.refresh_embeds(inter=inter,
                                             setup_info="You can't add more than 25 roles to a menu",
                                             defer=True,
                                             setting_changed=False)

        embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                              multiple=False,
                                                              message="Select a role to add to the menu")
        await inter.response.defer()
        await inter.edit_original_response(embed=embed, view=view)

    @interaction_handler
    async def handle_add_role_select_submit(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        selected_role_id = int(inter.data["values"][0])
        if selected_role_id in self.added_roles_map:
            embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                  multiple=False,
                                                                  message="Select a role to add to the menu",
                                                                  info="This role is already in the menu")
            await inter.response.defer()
            return await inter.edit_original_response(embed=embed, view=view)

        selected_role = self.guild.get_role(selected_role_id)

        if selected_role >= self.guild.me.top_role:
            embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                  multiple=False,
                                                                  message="Select a role to add to the menu",
                                                                  info="This role is above my highest role")
            await inter.response.defer()
            return await inter.edit_original_response(embed=embed, view=view)
        if self.guild.owner_id != inter.user.id and selected_role >= self.guild.get_member(inter.user.id).top_role:
            embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                  multiple=False,
                                                                  message="Select a role to add to the menu",
                                                                  info="This role is above your highest role")
            await inter.response.defer()
            return await inter.edit_original_response(embed=embed, view=view)
        if str(selected_role) == "@everyone" \
                or selected_role.is_bot_managed() \
                or selected_role.is_premium_subscriber() \
                or selected_role.is_integration() \
                or selected_role.is_default():
            embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                  multiple=False,
                                                                  message="Select a role to add to the menu",
                                                                  info="Selected role is invalid - Cannot be assigned")
            await inter.response.defer()
            return await inter.edit_original_response(embed=embed, view=view)

        await inter.response.send_modal(RoleMenuSetupAddRoleModal(interactions_handler=self,
                                                                  selected_role=selected_role))

    async def handle_add_role_modal_submit(self, inter: discord.Interaction, role, alias, emoji):
        if emoji and re.sub(r"[^0-9]", "", emoji):
            emoji_obj = discord_client.get_emoji(int(re.sub(r"[^0-9]", "", emoji)))
            if not emoji_obj:
                embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                      multiple=False,
                                                                      message="Select a role to add to the menu",
                                                                      info="I cannot see this emoji, make sure it's "
                                                                           "in a server I have access to")
                await inter.response.defer()
                return await inter.edit_original_response(embed=embed, view=view)
            emoji = emoji_obj
        elif emoji:
            if not emoji_lib.is_emoji(emoji):
                embed, view = self._build_select_role_embed_and_views(callback=self.handle_add_role_select_submit,
                                                                      multiple=False,
                                                                      message="Select a role to add to the menu",
                                                                      info="Emoji you entered is invalid")
                await inter.response.defer()
                return await inter.edit_original_response(embed=embed, view=view)
        if not alias:
            alias = role.name
        self.added_roles_map[role.id] = {
            "role": role,
            "alias": alias,
            "emoji": emoji,
            "rank": len(self.added_roles_map) + 1
        }
        await self.refresh_embeds(inter=inter, setup_info=f"Added role **{alias}** to the menu", defer=True)
        await self.sync_config()

    @interaction_handler
    async def handle_remove_role(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        embed, view = self._build_select_role_embed_and_views(callback=self.handle_remove_role_select_submit,
                                                              multiple=False,
                                                              message="Select a role to remove from the menu")
        await inter.response.defer()
        await inter.edit_original_response(embed=embed, view=view)

    @interaction_handler
    async def handle_remove_role_select_submit(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        selected_role_id = int(inter.data["values"][0])
        if selected_role_id not in self.added_roles_map:
            embed, view = self._build_select_role_embed_and_views(callback=self.handle_remove_role_select_submit,
                                                                  multiple=False,
                                                                  message="Select a role to remove from the menu",
                                                                  info="This role is not in the menu")
            await inter.response.defer()
            return await inter.edit_original_response(embed=embed, view=view)

        removed_role = self._remove_role(selected_role_id)
        await self.refresh_embeds(inter=inter, setup_info=f"Removed role **{removed_role['alias']}** from the menu",
                                  defer=True)
        await self.sync_config()

    @interaction_handler
    async def handle_restrict_menu(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if self.restricted_to_roles:
            self.restricted_to_roles = []
            await self.refresh_embeds(inter=inter, setup_info=f"Removed role restriction from the menu", defer=True)
            return await self.sync_config()

        embed, view = self._build_select_role_embed_and_views(callback=self.handle_restrict_menu_select_submit,
                                                              multiple=True,
                                                              message="Select roles to restrict the menu to")
        await inter.response.defer()
        await inter.edit_original_response(embed=embed, view=view)

    @interaction_handler
    async def handle_restrict_menu_select_submit(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        selected_role_ids = [int(role_id) for role_id in inter.data["values"]]

        await inter.response.send_modal(RoleMenuSetupAddRestrictionModal(
            interactions_handler=self,
            existing_restriction_description=self.restricted_description,
            selected_role_ids=selected_role_ids)
        )

    async def handle_restrict_menu_modal_submit(self, inter, selected_role_ids, restriction_description):
        
        self.restricted_to_roles = selected_role_ids
        self.restricted_description = restriction_description
        await self.refresh_embeds(
            inter=inter,
            setup_info=f"Restricted menu to people with roles: "
                       f"{', '.join([self.guild.get_role(role_id).mention for role_id in selected_role_ids])}",
            defer=True
        )
        await self.sync_config()

    @interaction_handler
    async def handle_add_image(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        image_placement_select = discord.ui.Select(options=[
            discord.SelectOption(label="Small Image", value=RoleMenuImagePlacement.THUMBNAIL),
            discord.SelectOption(label="Large Image", value=RoleMenuImagePlacement.IMAGE)
        ])
        image_placement_select.callback = self.handle_add_image_select_submit
        view = discord.ui.View()
        view.add_item(image_placement_select)
        close_button = discord.ui.Button(label="Nevermind", style=discord.ButtonStyle.gray)
        close_button.callback = self.refresh_embeds
        view.add_item(close_button)
        embed = discord.Embed(title="Role Menu Creation - Add Image",
                              description="Select where you want the image to appear.")
        embed.add_field(name="Small Image", value="Appears as a small image at the top right corner of the embed",
                        inline=False)
        embed.add_field(name="Large Image", value="Appears as a large image at the middle of the embed",
                        inline=False)
        await inter.response.defer()
        await inter.edit_original_response(embed=embed, view=view)

    @interaction_handler
    async def handle_add_image_select_submit(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        image_placement = inter.data["values"][0]

        await inter.response.send_modal(RoleMenuSetupAddImageModal(interactions_handler=self,
                                                                   existing_image_url=self.image_url,
                                                                   image_placement=image_placement))

    async def handle_add_image_modal_submit(self, inter: discord.Interaction, image_url, image_placement):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        self.image_url = image_url
        self.image_placement = image_placement
        try:
            await self.refresh_embeds(inter=inter, setup_info=f"Added image to the menu", defer=True)
        except discord.HTTPException:
            self.image_url = None
            await self.refresh_embeds(inter=inter, setup_info=f"Image URL is invalid", defer=True,
                                      setting_changed=False)

    async def refresh_embeds(self, inter: discord.Interaction, setup_info=None, setting_changed=True, defer=True):
        await edit_message(message=self.role_menu_message,
                           content=None,
                           embed=self._build_role_menu_embed(),
                           view=self._role_menu_views)
        if defer:
            await inter.response.defer()
        await inter.edit_original_response(
            embed=self._build_setup_embed(info=setup_info),
            view=self._setup_views
        )

        if setting_changed:
            await self.log_action_to_server(event=setup_info,
                                            field_value_map={"Role Menu": f"[Jump to message]"
                                                                          f"({self.role_menu_message.jump_url})"})

    def _build_setup_embed(self, info=None):
        return make_role_menu_setup_embed(guild=self.source_interaction.guild,
                                          added_roles_map=self.added_roles_map,
                                          role_menu_type=self.role_menu_type,
                                          role_menu_mode=self.role_menu_mode,
                                          restricted_to_roles=self.restricted_to_roles,
                                          info=info)

    def _build_role_menu_embed(self):
        return make_role_menu_embed(
            role_menu_name=self.role_menu_name,
            guild=self.source_interaction.guild,
            title=self.role_menu_description,
            color=self.role_menu_color,
            image=self.image_url if self.image_placement == RoleMenuImagePlacement.IMAGE else None,
            thumbnail=self.image_url if self.image_placement == RoleMenuImagePlacement.THUMBNAIL else None,
            footer_note=self.role_menu_footer,
            role_menu_mode=self.role_menu_mode,
            role_menu_type=self.role_menu_type,
            is_restricted=len(self.restricted_to_roles) > 0,
            restricted_description=self.restricted_description
        )

    @property
    def _setup_views(self):
        return get_role_menu_setup_views(interactions_handler=self,
                                         roles_removable=len(self.added_roles_map) > 0,
                                         is_restricted=len(self.restricted_to_roles) > 0,
                                         image_added=bool(self.image_url))

    @property
    def _role_menu_views(self):
        return get_role_menu_views(roles_map=self.added_roles_map,
                                   role_menu_type=self.role_menu_type,
                                   role_menu_mode=self.role_menu_mode)

    def _build_select_role_embed_and_views(self, callback, multiple=False, message="Select a role", info=None):
        embed = discord.Embed(title="Role Menu Setup - Role Selection",
                              description=message,
                              color=Colour.PRIMARY_ACCENT)
        if info:
            embed.add_field(name="Info", value=info, inline=False)
        view = discord.ui.View(timeout=600)
        role_select = discord.ui.RoleSelect(placeholder=message,
                                            min_values=1 if multiple else None,
                                            max_values=1 if not multiple else 5)
        role_select.callback = callback
        view.add_item(role_select)
        close_button = discord.ui.Button(label="Nevermind", style=discord.ButtonStyle.gray)
        close_button.callback = self.refresh_embeds
        view.add_item(close_button)
        return embed, view

    def _remove_role(self, selected_role_id):
        removed_role = self.added_roles_map.pop(selected_role_id)
        for role_id in self.added_roles_map:
            if self.added_roles_map[role_id]['rank'] > removed_role['rank']:
                self.added_roles_map[role_id]['rank'] -= 1

        return removed_role

    async def sync_config(self):
        if not self.added_roles_map:
            return
        await self.guild_prefs_component.update_role_menu_config(
            guild=self.source_interaction.guild,
            message_id=self.role_menu_message.id,
            role_menu_type=self.role_menu_type,
            role_menu_mode=self.role_menu_mode,
            restricted_to_roles=self.restricted_to_roles,
            restricted_description=self.restricted_description,
        )
