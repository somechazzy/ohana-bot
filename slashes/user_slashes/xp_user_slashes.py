from io import BytesIO
from typing import Union

import discord

from components.xp_components.level_image_xp_component import LevelImageXPComponent
from globals_ import shared_memory
from globals_.constants import Colour, XPSettingsKey
from slashes.user_slashes.base_user_slashes import UserSlashes
from user_interactions.user_interactions.leaderboard_interactions_handler import LeaderboardInteractionsHandler
from utils.decorators import slash_command
from utils.embed_factory import quick_embed, make_level_roles_embed


class XPUserSlashes(UserSlashes):

    @slash_command
    async def level(self, member: Union[discord.Member, discord.User] = None):
        """
        /level
        Get your current level and rank - or someone else's
        """

        if not await self.preprocess_and_validate():
            return

        member = member or self.member

        member_xp = shared_memory.guilds_xp[self.guild.id].members_xp.get(member.id)

        if member_xp is None:
            await self.interaction.response.send_message(
                embed=quick_embed(f"{member} has no XP (yet).",
                                  emoji='',
                                  color=Colour.ERROR,
                                  bold=False),
                ephemeral=True
            )
            return

        await self.interaction.response.defer(thinking=True)

        image = await LevelImageXPComponent().get_level_image(
            member=member,
            guild_xp_settings=self.guild_prefs.xp_settings,
            all_members_xp=shared_memory.guilds_xp[self.guild.id].members_xp
        )

        with BytesIO() as image_binary:
            image.save(image_binary, 'JPEG')
            image_binary.seek(0)
            await self.interaction.followup.send(files=[discord.File(fp=image_binary, filename='level.jpg'), ])

    @slash_command
    async def leaderboard(self, jump_to_page: int = 1, make_visible: bool = True):
        """
        /leaderboard
        Get the server's leaderboard
        """

        if not await self.preprocess_and_validate():
            return

        members_xp = shared_memory.guilds_xp[self.guild.id].members_xp
        if 0 in members_xp.keys():
            members_xp.pop(0)

        interactions_handler = LeaderboardInteractionsHandler(source_interaction=self.interaction,
                                                              members_xp=members_xp,
                                                              page=jump_to_page)

        embed, views = interactions_handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed,
                                                     view=views,
                                                     ephemeral=self.send_as_ephemeral(make_visible))

    @slash_command
    async def level_roles(self):
        """
        /level_roles
        Get the server's level roles
        """

        if not await self.preprocess_and_validate():
            return

        level_roles = self.guild_prefs.xp_settings[XPSettingsKey.LEVEL_ROLES]

        if not level_roles:
            return await self.interaction.response.send_message(
                embed=quick_embed("There are no level roles set up for this server.\n"
                                  "If you're an admin, check `/manage xp settings`",
                                  emoji='',
                                  color=Colour.ERROR,
                                  bold=False),
                ephemeral=True
            )

        embed = make_level_roles_embed(guild=self.guild, level_roles=level_roles)

        return await self.interaction.response.send_message(embed=embed,
                                                            ephemeral=self.send_as_ephemeral())
