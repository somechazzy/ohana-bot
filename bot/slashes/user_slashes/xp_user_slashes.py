from io import BytesIO

import discord

from bot.interaction_handlers.user_interaction_handlers.xp_leaderboard_interaction_handler import \
    XPLeaderboardInteractionHandler
from bot.slashes.user_slashes import UserSlashes
from bot.utils.decorators import slash_command
from bot.utils.embed_factory.xp_user_embeds import get_level_roles_embed
from bot.utils.helpers.xp_helpers import get_user_username_for_xp
from common.exceptions import UserInputException
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from components.guild_user_xp_components.xp_rank_image_component import XPRankImageComponent
from strings.commands_strings import UserSlashCommandsStrings


class XPUserSlashes(UserSlashes):

    @slash_command(guild_only=True, bot_permissions=["attach_files"])
    async def level(self, member: discord.Member | discord.User | None = None):
        """
        /level
        Get your current level or the level of a specified user.
        """
        member = member or self.member
        if not member:
            raise UserInputException(UserSlashCommandsStrings.LEVEL_USER_NOT_FOUND_ERROR_MESSAGE)

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())

        image = await XPRankImageComponent().get_member_rank_image(
            user_id=member.id,
            display_username=member.display_name,
            user_username=get_user_username_for_xp(member),
            user_avatar=member.display_avatar.with_size(256).url if member.display_avatar else None,
            guild_id=self.guild.id
        )

        with BytesIO() as image_binary:
            image.save(image_binary, 'JPEG')
            image_binary.seek(0)
            await self.interaction.followup.send(files=[discord.File(fp=image_binary, filename='level.jpg'), ])

    @slash_command(guild_only=True)
    async def leaderboard(self, jump_to_page: int, show_decays: bool, make_visible: bool):
        """
        /leaderboard
        View the XP leaderboard for this server.
        """
        guild_xp = await GuildUserXPComponent().get_guild_xp(guild_id=self.guild.id)
        interactions_handler = XPLeaderboardInteractionHandler(source_interaction=self.interaction,
                                                               context=self.context,
                                                               guild_settings=self.guild_settings,
                                                               guild_xp=guild_xp,
                                                               page=jump_to_page,
                                                               show_decays=show_decays)
        embed, view = interactions_handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed, view=view,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command(guild_only=True)
    async def level_roles(self):
        """
        /level-roles
        View the roles you can earn based on your level.
        """
        embed = get_level_roles_embed(guild=self.guild,
                                      level_role_ids_map=self.guild_settings.xp_settings.level_role_ids_map)
        return await self.interaction.response.send_message(embed=embed,
                                                            ephemeral=self.send_as_ephemeral())
