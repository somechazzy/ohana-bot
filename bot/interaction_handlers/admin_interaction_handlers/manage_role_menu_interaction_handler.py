import asyncio
import re

import discord

import emoji as emoji_lib
from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.modal_factory.role_menu_setup_modals import RoleMenuBasicSetupModal, RoleMenuAddRoleModal, \
    RoleMenuEditRoleModal, RoleMenuEditRestrictionDescriptionModal, RoleMenuImageSetupModal
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.role_menu_embeds import get_role_menu_setup_embed, get_role_menu_restriction_setup_embed, \
    get_role_menu_image_setup_embed, get_role_menu_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.helpers.moderation_helpers import bot_can_assign_role, actor_can_assign_role
from bot.utils.view_factory.role_menu_views import get_role_menu_setup_view, get_role_menu_restriction_setup_view, \
    get_role_menu_image_setup_view, get_role_menu_view
from common.exceptions import UserInputException
from components.guild_settings_components.guild_role_menu_component import GuildRoleMenuComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import RoleMenuType, CommandContext, RoleMenuImagePlacement, RoleMenuMode
from models.dto.role_menu import RoleMenuSettings, RoleMenuRole


class ManageRoleMenuInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "Role menu management"

    class SelectedView:
        MAIN_SETUP = "main_setup"
        RESTRICTION_SETUP = "restriction_setup"
        IMAGE_SETUP = "image_setup"

    def __init__(self,
                 role_menu_message: discord.Message,
                 role_menu_settings: RoleMenuSettings,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selected_view: str = self.SelectedView.MAIN_SETUP
        self.role_menu_message: discord.Message = role_menu_message
        self.role_menu_settings: RoleMenuSettings = role_menu_settings
        self.guild_role_menu = self.guild_settings.get_role_menu(message_id=role_menu_message.id)
        self.guild_role_menu_component = GuildRoleMenuComponent()

    @interaction_handler()
    async def go_to_basic_setup(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleMenuBasicSetupModal(
            interactions_handler=self,
            existing_menu_name=self.role_menu_settings.name,
            existing_menu_description=self.role_menu_settings.description,
            existing_menu_color=f"#{self.role_menu_settings.embed_color:0>6x}",
            existing_menu_footer=self.role_menu_settings.footer_note
        ))

    @interaction_handler()
    async def on_basic_setup_modal_submit(self,
                                          interaction: discord.Interaction,
                                          menu_name: str,
                                          menu_description: str,
                                          menu_color: str | None,
                                          menu_footer: str | None):
        if menu_color:
            try:
                menu_color = int(menu_color.lstrip("#"), 16)
            except ValueError:
                raise UserInputException("Invalid color code. "
                                         "Please use a valid hex color code (example: #ff0000).")

        updated_settings = {}
        if menu_name != self.role_menu_settings.name:
            updated_settings["Menu Title"] = f"{self.role_menu_settings.name} -> {menu_name}"
            self.role_menu_settings.name = menu_name
        if menu_description != self.role_menu_settings.description:
            updated_settings["Menu Description"] = f"{self.role_menu_settings.description} -> {menu_description}"
            self.role_menu_settings.description = menu_description
        if menu_color != self.role_menu_settings.embed_color:
            updated_settings["Embed Color"] = f"#{self.role_menu_settings.embed_color:0>6x} -> #{menu_color:0>6x}"
            self.role_menu_settings.embed_color = menu_color
        if menu_footer != self.role_menu_settings.footer_note:
            updated_settings["Footer Note"] = f"{self.role_menu_settings.footer_note} -> {menu_footer}"
            self.role_menu_settings.footer_note = menu_footer

        await interaction.response.defer()
        if not updated_settings:
            await self.refresh_message(feedback="No changes made.")
            return
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback="✅ Basic setup updated.")
        await self.log_setting_change(event_text="Role menu basic setup updated",
                                      fields=[GuildLogEventField(name=key, value=value)
                                              for key, value in updated_settings.items()] +
                                             [GuildLogEventField(name="Menu",
                                                                 value=f"[Click here]"
                                                                       f"({self.role_menu_message.jump_url})")])

    @interaction_handler()
    async def change_menu_type(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_role_menu.menu_type == RoleMenuType.SELECT:
            new_type = RoleMenuType.BUTTON
            new_type_text = "buttons"
        else:
            new_type = RoleMenuType.SELECT
            new_type_text = "dropdown select"
        await self.guild_role_menu_component.update_role_menu(
            guild_id=interaction.guild.id,
            guild_role_menu_id=self.guild_role_menu.guild_role_menu_id,
            menu_type=new_type
        )
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Menu type changed to **{new_type_text}**.")
        await self.log_setting_change(event_text=f"Role menu type changed to {new_type_text}.",
                                      fields=[GuildLogEventField(name="Menu",
                                                                 value=f"[Click here]"
                                                                       f"({self.role_menu_message.jump_url})")])

    @interaction_handler()
    async def change_menu_mode(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_role_menu.menu_mode == RoleMenuMode.SINGLE:
            new_mode = RoleMenuMode.MULTI
            new_mode_text = "multiple role selection"
        else:
            new_mode = RoleMenuMode.SINGLE
            new_mode_text = "single role selection"
        await self.guild_role_menu_component.update_role_menu(
            guild_id=interaction.guild.id,
            guild_role_menu_id=self.guild_role_menu.guild_role_menu_id,
            menu_mode=new_mode
        )
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Menu mode changed to **{new_mode_text}**.")
        await self.log_setting_change(event_text=f"Role menu mode changed to {new_mode_text}.",
                                      fields=[GuildLogEventField(name="Menu",
                                                                 value=f"[Click here]"
                                                                       f"({self.role_menu_message.jump_url})")])

    @interaction_handler()
    async def go_to_restriction_setup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.RESTRICTION_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def go_to_image_setup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.IMAGE_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self._selected_view = self.SelectedView.MAIN_SETUP
        await self.refresh_message()

    @interaction_handler()
    async def on_add_or_edit_role_select(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        existing = next((role for role in self.role_menu_settings.roles if role.role_id == role_id), None)
        role = self.guild.get_role(role_id)
        if not existing:
            if not bot_can_assign_role(role=role) \
                    or not actor_can_assign_role(actor=self.guild.get_member(self.original_user.id),
                                                 role=role):
                raise UserInputException("Either you or I can't assign this role to users. "
                                         "Could be due to role hierarchy or the role being unassignable.")
            await interaction.response.send_modal(RoleMenuAddRoleModal(interactions_handler=self,
                                                                       role_id=role_id,
                                                                       existing_alias=role.name,
                                                                       existing_emoji=str(role.unicode_emoji)
                                                                       if role.unicode_emoji else ""))
        else:
            self.role_menu_settings.refresh_role_ranks()
            await interaction.response.send_modal(RoleMenuEditRoleModal(interactions_handler=self,
                                                                        role_id=existing.role_id,
                                                                        existing_rank=existing.rank,
                                                                        existing_alias=existing.alias,
                                                                        existing_emoji=existing.emoji.id
                                                                        or existing.emoji.name))

    @interaction_handler()
    async def on_add_role_modal_submit(self,
                                       interaction: discord.Interaction,
                                       role_id: int,
                                       alias: str | None,
                                       emoji: str | None):
        role = self.guild.get_role(role_id)
        if not role:
            await self.refresh_message()
            raise UserInputException("Role not found.")
        if next((role for role in self.role_menu_settings.roles if role.role_id == role_id), None):
            await self.refresh_message()
            raise UserInputException("Role already added to the menu.")
        if emoji:
            if emoji_lib.is_emoji(emoji):
                emoji = discord.PartialEmoji.from_str(emoji)
            elif (emoji_id := re.sub(r"[^0-9]", "", emoji or "")) \
                    and self.guild.get_emoji(int(emoji_id)):  # noqa
                emoji = self.guild.get_emoji(int(emoji_id))
            else:
                await self.refresh_message()
                raise UserInputException("Invalid emoji format. Please use a valid emoji or emoji ID.")

        await interaction.response.defer()
        self.role_menu_settings.add_role(role_id=role_id, alias=alias or role.name, emoji=emoji)
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Role **{role.name}** added to the menu.")
        await self.log_setting_change(event_text="Role menu role added",
                                      fields=[
                                          GuildLogEventField(name="Role",
                                                             value=f"{role.mention} ({role.name})"),
                                          GuildLogEventField(name="Alias",
                                                             value=alias or role.name),
                                          GuildLogEventField(name="Emoji",
                                                             value=str(emoji) if emoji else "None"),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def on_edit_role_modal_submit(self,
                                        interaction: discord.Interaction,
                                        role_id: int,
                                        rank: int,
                                        alias: str | None,
                                        emoji: str | None):
        role = self.guild.get_role(role_id)
        existing_role = next((role for role in self.role_menu_settings.roles if role.role_id == role_id), None)
        if not existing_role:
            raise UserInputException("Role not found in the menu.")
        if emoji:
            if not re.sub(r"[^0-9]", "", emoji or "") or not emoji_lib.is_emoji(emoji):
                raise UserInputException("Invalid emoji format. Please use a valid emoji or emoji ID.")
            emoji = discord.PartialEmoji.from_str(emoji)

        updated_settings = {}
        if alias and alias != role.name:
            updated_settings["Role Alias"] = f"{role.name} -> {alias}"
            existing_role.alias = alias or role.name
        if emoji and str(emoji) != str(role.unicode_emoji):
            updated_settings["Role Emoji"] = f"{role.unicode_emoji} -> {emoji}"
            existing_role.emoji = emoji
        if rank != existing_role.rank:
            updated_settings["Role Rank"] = f"{existing_role.rank} -> {rank}"
            existing_role.rank = rank
            self.role_menu_settings.refresh_role_ranks()

        await interaction.response.defer()
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Role **{existing_role.alias}** updated.")
        await self.log_setting_change(event_text="Role menu role updated",
                                      fields=[
                                          GuildLogEventField(name="Role",
                                                             value=f"{role.mention} ({role.name})"),
                                          GuildLogEventField(name="Alias",
                                                             value=existing_role.alias),
                                          GuildLogEventField(name="Emoji",
                                                             value=str(existing_role.emoji)),
                                          GuildLogEventField(name="Rank",
                                                             value=str(existing_role.rank)),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def on_remove_role_select(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        existing_role = next((role for role in self.role_menu_settings.roles if role.role_id == role_id), None)
        if not existing_role:
            raise UserInputException("Role not found in the menu.")
        await interaction.response.defer()
        self.role_menu_settings.remove_role(role_id=role_id)
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Role **{existing_role.alias}** updated.")
        await self.log_setting_change(event_text="Role menu role removed",
                                      fields=[
                                          GuildLogEventField(name="Role",
                                                             value=f"{existing_role.emoji} {existing_role.alias} "
                                                                   f"({existing_role.role_id})"),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def edit_restriction_description(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleMenuEditRestrictionDescriptionModal(
            interactions_handler=self,
            existing_restriction_description=self.guild_role_menu.role_restriction_description
        ))

    @interaction_handler()
    async def on_edit_restriction_description_modal_submit(self,
                                                           interaction: discord.Interaction,
                                                           restriction_description: str):
        await interaction.response.defer()
        old_description = self.guild_role_menu.role_restriction_description
        if restriction_description == old_description:
            await self.refresh_message(feedback="No changes made.")
            return
        await self.guild_role_menu_component.update_role_menu(
            guild_id=self.guild.id,
            guild_role_menu_id=self.guild_role_menu.guild_role_menu_id,
            role_restriction_description=restriction_description
        )
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback="✅ Restriction description updated.")
        await self.log_setting_change(event_text="Role menu restriction description updated",
                                      fields=[
                                          GuildLogEventField(name="Old Description",
                                                             value=old_description or "None"),
                                          GuildLogEventField(name="New Description",
                                                             value=restriction_description or "None"),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def on_restricted_role_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        role_ids = [int(role_id) for role_id in interaction.data["values"]]
        removed_role_ids = set(self.guild_role_menu.restricted_role_ids) - set(role_ids)
        added_role_ids = set(role_ids) - set(self.guild_role_menu.restricted_role_ids)
        if not removed_role_ids and not added_role_ids:
            await self.refresh_message(feedback="No changes made.")
            return
        await self.guild_role_menu_component.update_role_menu_restricted_role(
            guild_id=self.guild.id,
            guild_role_menu_id=self.guild_role_menu.guild_role_menu_id,
            role_ids=role_ids
        )
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback="✅ Restricted roles updated.")
        await self.log_setting_change(event_text="Role menu restricted roles updated",
                                      fields=[
                                          GuildLogEventField(name="Added Roles",
                                                             value=", ".join(
                                                                 [self.guild.get_role(role_id).mention
                                                                  for role_id in added_role_ids])),
                                          GuildLogEventField(name="Removed Roles",
                                                             value=", ".join(
                                                                 [self.guild.get_role(role_id).mention
                                                                  for role_id in removed_role_ids])),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def go_to_image_url_input(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleMenuImageSetupModal(
            interactions_handler=self,
            existing_image_url=self.role_menu_settings.image_url or self.role_menu_settings.thumbnail_url)
        )

    @interaction_handler()
    async def on_image_setup_modal_submit(self, interaction: discord.Interaction, image_url: str):
        if self.role_menu_settings.thumbnail_url:
            old_image_url = self.role_menu_settings.thumbnail_url
            self.role_menu_settings.thumbnail_url = image_url
        else:
            old_image_url = self.role_menu_settings.image_url
            self.role_menu_settings.image_url = image_url
        if not image_url:
            raise UserInputException("Image URL cannot be empty.")
        try:
            await self.refresh_role_menu_message()
        except discord.HTTPException:
            raise UserInputException("Invalid image URL.")
        await interaction.response.defer()
        await self.refresh_message(feedback="✅ Image updated.")
        await self.log_setting_change(event_text="Role menu image updated",
                                      fields=[
                                          GuildLogEventField(name="Old Image URL",
                                                             value=old_image_url or "None"),
                                          GuildLogEventField(name="New Image URL",
                                                             value=image_url),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def change_image_placement(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.role_menu_settings.image_url, self.role_menu_settings.thumbnail_url = \
            self.role_menu_settings.thumbnail_url, self.role_menu_settings.image_url
        if self.role_menu_settings.image_url:
            image_placement = RoleMenuImagePlacement.IMAGE
        else:
            image_placement = RoleMenuImagePlacement.THUMBNAIL
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback=f"✅ Image placement changed to **{image_placement}**.")
        await self.log_setting_change(event_text="Role menu image placement changed",
                                      fields=[
                                          GuildLogEventField(name="Image Placement",
                                                             value=image_placement),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    @interaction_handler()
    async def remove_image(self, interaction: discord.Interaction):
        await interaction.response.defer()
        old_image_url = self.role_menu_settings.image_url or self.role_menu_settings.thumbnail_url
        self.role_menu_settings.image_url = None
        self.role_menu_settings.thumbnail_url = None
        await self.refresh_role_menu_message()
        await self.refresh_message(feedback="✅ Image removed.")
        await self.log_setting_change(event_text="Role menu image removed",
                                      fields=[
                                          GuildLogEventField(name="Old Image URL",
                                                             value=old_image_url),
                                          GuildLogEventField(name="Menu",
                                                             value=f"[Click here]({self.role_menu_message.jump_url})")
                                      ])

    async def refresh_role_menu_message(self):
        embed = get_role_menu_embed(guild=self.guild,
                                    role_menu_name=self.role_menu_settings.name,
                                    role_menu_description=self.role_menu_settings.description,
                                    embed_color=self.role_menu_settings.embed_color,
                                    thumbnail=self.role_menu_settings.thumbnail_url,
                                    image=self.role_menu_settings.image_url,
                                    footer_note=self.role_menu_settings.footer_note,
                                    role_menu_type=self.guild_role_menu.menu_type,
                                    role_menu_mode=self.guild_role_menu.menu_mode,
                                    is_restricted=bool(self.guild_role_menu.restricted_role_ids),
                                    restricted_description=self.guild_role_menu.role_restriction_description)
        view = get_role_menu_view(role_menu_type=self.guild_role_menu.menu_type,
                                  role_menu_mode=self.guild_role_menu.menu_mode,
                                  role_menu_roles=self.role_menu_settings.roles)
        await self.role_menu_message.edit(embed=embed, view=view)

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(1)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        if self._selected_view == self.SelectedView.MAIN_SETUP:
            embed = get_role_menu_setup_embed(guild=self.guild,
                                              role_menu_roles=self.role_menu_settings.roles,
                                              role_menu_type=self.guild_role_menu.menu_type,
                                              role_menu_mode=self.guild_role_menu.menu_mode,
                                              restricted_to_roles=[self.guild.get_role(role_id) for role_id
                                                                   in self.guild_role_menu.restricted_role_ids],
                                              feedback_message=feedback)
            view = get_role_menu_setup_view(interactions_handler=self,
                                            roles_selected=bool(self.role_menu_settings.roles),
                                            is_restricted=bool(self.guild_role_menu.restricted_role_ids),
                                            image_added=bool(self.role_menu_settings.image_url
                                                             or self.role_menu_settings.thumbnail_url), )
        elif self._selected_view == self.SelectedView.RESTRICTION_SETUP:
            embed = get_role_menu_restriction_setup_embed(
                guild=self.guild,
                restricted_to_roles=[self.guild.get_role(role_id) for role_id
                                     in self.guild_role_menu.restricted_role_ids],
                restriction_description=self.guild_role_menu.role_restriction_description,
                feedback_message=feedback
            )
            view = get_role_menu_restriction_setup_view(
                interactions_handler=self,
                existing_roles=[self.guild.get_role(role_id) for role_id in self.guild_role_menu.restricted_role_ids]
            )
        elif self._selected_view == self.SelectedView.IMAGE_SETUP:
            image_url = None
            image_placement = RoleMenuImagePlacement.IMAGE
            if self.role_menu_settings.image_url:
                image_url = self.role_menu_settings.image_url
            elif self.role_menu_settings.thumbnail_url:
                image_url = self.role_menu_settings.thumbnail_url
                image_placement = RoleMenuImagePlacement.THUMBNAIL
            embed = get_role_menu_image_setup_embed(guild=self.guild,
                                                    image_url=image_url,
                                                    image_placement=image_placement)
            view = get_role_menu_image_setup_view(interactions_handler=self,
                                                  image_added=bool(image_url))
        else:
            raise NotImplementedError(self._selected_view)

        return embed, view

    async def fetch_and_cleanup_roles(self):
        """
        Fetches the roles from the role menu message and cleans up any invalid roles.
        """
        valid_roles = []
        for role in self.role_menu_settings.roles:
            if self.role_menu_message.guild.get_role(role.role_id):
                valid_roles.append(role)
        self.role_menu_settings.roles = valid_roles
        await self.refresh_role_menu_message()

    @classmethod
    async def from_role_menu_message(cls,
                                     source_interaction: discord.Interaction,
                                     role_menu_message: discord.Message) -> "ManageRoleMenuInteractionHandler":
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=role_menu_message.guild.id)
        role_menu_settings = guild_settings.get_role_menu(message_id=role_menu_message.id)
        if not role_menu_settings:
            raise UserInputException("This message is not configured as a role menu.")

        roles = []
        if role_menu_settings.menu_type == RoleMenuType.SELECT:
            for select_menu in role_menu_message.components[0].children:
                for option in select_menu.options:
                    if not role_menu_message.guild.get_role(int(option.value)):
                        continue
                    roles.append(RoleMenuRole(
                        role_id=int(option.value),
                        alias=option.label,
                        emoji=option.emoji,
                        rank=len(roles) + 1
                    ))
        else:
            for component in role_menu_message.components:
                for button in component.children:
                    if not role_menu_message.guild.get_role(int(button.custom_id)):
                        continue
                    roles.append(RoleMenuRole(
                        role_id=int(button.custom_id),
                        alias=button.label,
                        emoji=button.emoji,
                        rank=len(roles) + 1
                    ))
        menu_embed: discord.Embed = role_menu_message.embeds[0]

        role_menu_settings = RoleMenuSettings(name=menu_embed.author.name, description=menu_embed.title, roles=roles,
                                              embed_color=menu_embed.colour.value,
                                              thumbnail_url=menu_embed.thumbnail.url if menu_embed.thumbnail else None,
                                              image_url=menu_embed.image.url if menu_embed.image else None,
                                              footer_note=menu_embed.footer.text if menu_embed.footer else None)
        return cls(
            source_interaction=source_interaction,
            context=CommandContext.GUILD,
            role_menu_message=role_menu_message,
            role_menu_settings=role_menu_settings,
            guild_settings=guild_settings
        )
