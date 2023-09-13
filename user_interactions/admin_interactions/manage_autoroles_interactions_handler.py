import asyncio
import discord
from utils.embed_factory import make_autoroles_management_embed
from utils.helpers import get_roles_management_views
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from utils.decorators import interaction_handler


class ManageAutoRolesInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction, guild=guild)

    @interaction_handler
    async def handle_role_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        role_id = int(inter.data["values"][0])
        removed = role_id in self.guild_prefs.autoroles

        await inter.response.defer()
        if not removed:
            if not self.is_role_assignable(role_id=role_id, check_against_user=True):
                return await self.refresh_setup_message(feedback_message="I can't give this role to others. "
                                                                         "Could be due to role hierarchy.")
            await self.guild_prefs_component.add_guild_autorole(guild=self.guild, role_id=role_id)
        else:
            await self.guild_prefs_component.remove_guild_autorole(guild=self.guild, role_id=role_id)

        await self.refresh_setup_message(feedback_message=f"Role <@&{role_id}> {'removed' if removed else 'added'}")

        await self.log_action_to_server(event=f"Changed autoroles ({'removed' if removed else 'added'} role)",
                                        field_value_map={"Role": f"<@&{role_id}>"})

    @interaction_handler
    async def handle_clear_roles(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.defer()

        existing_autoroles = self.guild_prefs.autoroles.copy()

        await self.guild_prefs_component.clear_guild_autoroles(guild=self.guild)
        await self.refresh_setup_message(feedback_message="All roles removed")

        await self.log_action_to_server(event=f"Autoroles cleared",
                                        field_value_map={"Existing autoroles":
                                                         ", ".join(f"<@&{role_id}>" for role_id in existing_autoroles)})

    async def refresh_setup_message(self, feedback_message=None):
        embed, views = self.get_embed_and_views(feedback_message=feedback_message)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    def get_embed_and_views(self, feedback_message=None):
        embed = make_autoroles_management_embed(guild=self.guild,
                                                autoroles_ids=self.guild_prefs.autoroles,
                                                feedback_message=feedback_message)
        views = get_roles_management_views(interactions_handler=self,
                                           add_clear_button=bool(self.guild_prefs.autoroles))

        return embed, views
