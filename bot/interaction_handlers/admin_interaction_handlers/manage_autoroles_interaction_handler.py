import asyncio

import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.embed_factory.automod_management_embeds import get_autoroles_setup_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.helpers.moderation_helpers import bot_can_assign_role
from bot.utils.decorators import interaction_handler
from bot.utils.view_factory.automod_management_views import get_autorole_setup_view
from common.exceptions import UserInputException
from components.guild_settings_components.guild_autorole_component import GuildAutoroleComponent


class ManageAutorolesInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "Autoroles management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autorole_component = GuildAutoroleComponent()

    @interaction_handler()
    async def on_role_select(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        to_remove = role_id in self.guild_settings.autoroles_ids
        role = self.guild.get_role(role_id)
        await interaction.response.defer()
        if not to_remove:
            if not bot_can_assign_role(role=role):
                raise UserInputException(f"I can't give the role {role.mention} to others."
                                         f" Could be due to role hierarchy or the role being not assignable.")
            elif len(self.guild_settings.autoroles_ids) >= 15:
                raise UserInputException(f"You already have 15 autoroles or more.")
            await self.autorole_component.add_autorole(guild_id=self.guild.id,
                                                       role_id=role_id)
        else:
            await self.autorole_component.remove_autorole(guild_id=self.guild.id,
                                                          role_id=role_id)

        await self.refresh_message(feedback=f"Role <@&{role_id}> {'removed' if to_remove else 'added'}")
        await self.log_setting_change(event_text=f"{'Removed' if to_remove else 'Added'} autorole",
                                      fields=[GuildLogEventField(name="Role(s)", value=role.mention)])

    @interaction_handler()
    async def clear_roles(self, interaction: discord.Interaction):
        await interaction.response.defer()

        existing_autoroles = self.guild_settings.autoroles_ids.copy()

        await self.autorole_component.clear_autoroles(guild_id=self.guild.id)
        await self.refresh_message(feedback="All roles removed")

        await self.log_setting_change(event_text="Autoroles cleared",
                                      fields=[GuildLogEventField(name="Existing autoroles",
                                                                 value=", ".join(f"<@&{role_id}>"
                                                                                 for role_id in existing_autoroles))])

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_autoroles_setup_embed(selected_role_ids=self.guild_settings.autoroles_ids,
                                          guild=self.guild,
                                          feedback_message=feedback)
        view = get_autorole_setup_view(interaction_handler=self,
                                       add_clear_button=bool(self.guild_settings.autoroles_ids))

        return embed, view

    async def fetch_and_cleanup_autoroles(self):
        invalid_role_ids = []
        for role_id in self.guild_settings.autoroles_ids:
            if not self.guild.get_role(role_id):
                invalid_role_ids.append(role_id)
        for role_id in invalid_role_ids:
            await self.autorole_component.remove_autorole(guild_id=self.guild.id,
                                                          role_id=role_id)
