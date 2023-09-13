import discord

from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class RoleMenuSetupBasicModal(BaseModal, title="Role Menu Basic Setup"):
    menu_title_input = discord.ui.TextInput(label="Enter a title for the menu",
                                            max_length=100,
                                            min_length=3,
                                            placeholder="Example: Age group Roles, Gender Roles, etc.",
                                            required=True,
                                            style=discord.TextStyle.long)
    menu_description_input = discord.ui.TextInput(label="Enter a short description for the menu",
                                                  max_length=150,
                                                  min_length=3,
                                                  placeholder="Example: You can select your region here",
                                                  required=True,
                                                  style=discord.TextStyle.long)
    menu_footer_input = discord.ui.TextInput(label="Enter a footer for the menu embed",
                                             max_length=100,
                                             placeholder="Example: You can change your selection at any time",
                                             required=False,
                                             style=discord.TextStyle.long)
    menu_color_input = discord.ui.TextInput(label="Enter a color for the menu embed (color code)",
                                            max_length=7,
                                            min_length=7,
                                            placeholder="#ff0000",
                                            required=False,
                                            style=discord.TextStyle.short)

    def __init__(self, interactions_handler, existing_menu_title=None, existing_menu_description=None,
                 existing_menu_footer=None, existing_menu_color=None, **kwargs):
        super().__init__(interactions_handler=interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.menu_title_input.default = existing_menu_title
        self.menu_description_input.default = existing_menu_description
        self.menu_footer_input.default = existing_menu_footer
        if isinstance(existing_menu_color, int):
            self.menu_color_input.default = f"#{existing_menu_color:0>6x}"
        else:
            self.menu_color_input.default = str(existing_menu_color)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(inter=self.interactions_handler.source_interaction,
                                                       defer=False)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_basic_setup_modal_submit(
            inter=interaction,
            menu_title=self.menu_title_input.value,
            menu_description=self.menu_description_input.value,
            menu_footer=self.menu_footer_input.value,
            menu_color=self.menu_color_input.value
        )


class RoleMenuSetupAddRoleModal(BaseModal, title="Role Configuration"):
    alias_input = discord.ui.TextInput(
        label="Enter an alias for the role option",
        max_length=50,
        placeholder="Example: 'I am from Asia'",
        required=False,
        style=discord.TextStyle.short
    )
    emoji_input = discord.ui.TextInput(label="Enter a custom emoji ID or a default emoji",
                                       max_length=30,
                                       placeholder="Example: ♂ or 123456789012345678",
                                       required=False,
                                       style=discord.TextStyle.short)

    def __init__(self, interactions_handler, selected_role, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.selected_role = selected_role

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(inter=self.interactions_handler.source_interaction,
                                                       defer=False)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_add_role_modal_submit(
            inter=interaction,
            role=self.selected_role,
            alias=self.alias_input.value,
            emoji=self.emoji_input.value
        )


class RoleMenuSetupAddRestrictionModal(BaseModal, title="Role Menu Restriction Message"):
    restriction_description_input = discord.ui.TextInput(
        label="Describe who this menu is exclusive for",
        max_length=250,
        min_length=5,
        placeholder="Example: 'This menu is exclusive to people who boost the server!'",
        required=True,
        style=discord.TextStyle.long
    )

    def __init__(self, interactions_handler, selected_role_ids, existing_restriction_description, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.selected_role_ids = selected_role_ids
        self.restriction_description_input.default = existing_restriction_description

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(inter=self.interactions_handler.source_interaction,
                                                       defer=False)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_restrict_menu_modal_submit(
            inter=interaction,
            restriction_description=self.restriction_description_input.value,
            selected_role_ids=self.selected_role_ids
        )


class RoleMenuSetupAddImageModal(BaseModal, title="Role Menu Image Link"):
    image_url_input = discord.ui.TextInput(
        label="Enter a link to the image",
        max_length=300,
        placeholder="Example: 'https://example.com/image.png'",
        required=True,
        style=discord.TextStyle.long
    )

    def __init__(self, interactions_handler, image_placement, existing_image_url, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.image_placement = image_placement
        self.image_url_input.default = existing_image_url

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(inter=self.interactions_handler.source_interaction,
                                                       defer=False)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_add_image_modal_submit(inter=interaction,
                                                                      image_url=self.image_url_input.value,
                                                                      image_placement=self.image_placement)
