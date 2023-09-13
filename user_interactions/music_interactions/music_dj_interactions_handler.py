import asyncio

import discord
from utils.embed_factory import make_dj_role_management_embed
from globals_ import shared_memory
from utils.helpers import get_roles_management_views
from utils.decorators import interaction_handler
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicDJInteractionsHandler(MusicInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction)
        self.guild = guild

    @interaction_handler
    async def handle_role_select(self, inter: discord.Interaction):
        current_roles = shared_memory.guilds_prefs[self.guild.id].dj_roles
        role_id = int(inter.data["values"][0])

        removed = False
        if role_id in current_roles:
            current_roles.remove(role_id)
            removed = True
        else:
            current_roles.append(role_id)

        await inter.response.defer()
        await self.refresh_dj_embed(current_roles=current_roles)
        if not removed:
            await self.guild_prefs_component.add_guild_dj_role(guild=self.guild, role_id=role_id)
        else:
            await self.guild_prefs_component.remove_guild_dj_role(guild=self.guild, role_id=role_id)

    @interaction_handler
    async def handle_clear_roles(self, inter: discord.Interaction):
        current_roles = shared_memory.guilds_prefs[self.guild.id].dj_roles
        current_roles.clear()
        await inter.response.defer()
        await self.refresh_dj_embed(current_roles=current_roles)
        await self.guild_prefs_component.clear_guild_dj_roles(guild=self.guild)

    async def refresh_dj_embed(self, current_roles):
        embed = make_dj_role_management_embed(guild=self.guild, dj_role_ids=current_roles)
        views = get_roles_management_views(interactions_handler=self,
                                           add_clear_button=bool(current_roles))
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)
