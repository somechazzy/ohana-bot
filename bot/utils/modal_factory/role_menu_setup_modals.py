import discord
from discord.ui import TextInput, Label

from bot.utils.modal_factory import BaseModal


class RoleMenuBasicSetupModal(BaseModal, title="Role Menu Basic Setup"):
    menu_name_label = Label(
        text="Menu Title",
        description="This appears at the top of the role menu embed",
        component=TextInput(
            max_length=1024,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )

    )
    menu_description_label = Label(
        text="Menu Short Description",
        description="This appears below the title",
        component=TextInput(
            max_length=1024,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )
    menu_color_label = Label(
        text="Menu Color (hex code)",
        description="The color of the embed, in hex format (e.g. #FF5733). Leave blank for default color.",
        component=TextInput(
            max_length=7,
            min_length=6,
            required=False,
            style=discord.TextStyle.short
        )
    )
    menu_footer_label = Label(
        text="Menu Footer Text",
        description="This appears at the bottom of the embed. Leave blank for no footer.",
        component=TextInput(
            max_length=100,
            required=False,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 existing_menu_name: str,
                 existing_menu_description: str,
                 existing_menu_color: hex,
                 existing_menu_footer: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.menu_name_label.component.default = existing_menu_name
        self.menu_description_label.component.default = existing_menu_description
        self.menu_color_label.component.default = existing_menu_color
        self.menu_color_label.component.placeholder = existing_menu_color
        self.menu_footer_label.component.default = existing_menu_footer

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_basic_setup_modal_submit(
            interaction=interaction,
            menu_name=self.menu_name_label.component.value,
            menu_description=self.menu_description_label.component.value,
            menu_color=self.menu_color_label.component.value,
            menu_footer=self.menu_footer_label.component.value
        )


class RoleMenuAddRoleModal(BaseModal, title="Add role details"):
    alias_label = Label(
        text="Display name",
        description="How the role will be displayed in the menu. Leave blank to use the role's actual name.",
        component=TextInput(
            max_length=50,
            min_length=1,
            required=False,
            style=discord.TextStyle.short
        )
    )
    emoji_label = Label(
        text="Emoji (standard or custom emoji ID)",
        description="Displayed next to the role name. Leave blank for no emoji.",
        component=TextInput(
            max_length=30,
            min_length=0,
            placeholder="Example: ♂ or 123456789012345678",
            required=False,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 role_id: int,
                 existing_alias: str,
                 existing_emoji: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.role_id = role_id
        self.alias_label.component.default = existing_alias
        self.emoji_label.component.default = existing_emoji

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_add_role_modal_submit(
            interaction=interaction,
            role_id=self.role_id,
            alias=self.alias_label.component.value,
            emoji=self.emoji_label.component.value or None
        )


class RoleMenuEditRoleModal(RoleMenuAddRoleModal, title="Edit role details"):
    rank_label = Label(
        text="Rank/position in the menu",
        description="Determines the order of roles in the menu. 1 is the top position.",
        component=TextInput(
            max_length=3,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 role_id: int,
                 existing_rank: int,
                 existing_alias: str,
                 existing_emoji: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.role_id = role_id
        self.rank_label.component.default = str(existing_rank)
        self.alias_label.component.default = existing_alias
        self.emoji_label.component.default = existing_emoji

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_edit_role_modal_submit(
            interaction=interaction,
            role_id=self.role_id,
            rank=int(self.rank_label.component.value) if self.rank_label.component.value.isdigit() else 1,
            alias=self.alias_label.component.value,
            emoji=self.emoji_label.component.value
        )


class RoleMenuEditRestrictionDescriptionModal(BaseModal, title="Edit restriction description"):
    restriction_description_label = Label(
        text="Describe who this menu is exclusive for",
        component=TextInput(
            max_length=250,
            min_length=5,
            required=True,
            style=discord.TextStyle.long
        )
    )

    def __init__(self, interactions_handler, existing_restriction_description: str, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.restriction_description_label.component.default = existing_restriction_description

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_edit_restriction_description_modal_submit(
            interaction=interaction,
            restriction_description=self.restriction_description_label.component.value
        )


class RoleMenuImageSetupModal(BaseModal, title="Role Menu Image"):
    image_url_label = Label(
        text="Image URL",
        description="The image to display in the menu embed.",
        component=TextInput(
            max_length=1024,
            min_length=1,
            required=True,
            style=discord.TextStyle.short,
            placeholder="Example: https://example.com/image.png"
        )
    )

    def __init__(self, interactions_handler, existing_image_url: str, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.image_url_label.component.default = existing_image_url

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_image_setup_modal_submit(
            interaction=interaction,
            image_url=self.image_url_label.component.value,
        )
