from io import BytesIO
from math import ceil

import disnake as discord

from actions import send_embed, send_message
from commands.user_command_executor import UserCommandExecutor
from embed_factory import make_leaderboard_embed
from globals_ import variables
from globals_.clients import discord_client
from globals_.constants import UserCommandSection, XPSettingsKey
from helpers import bot_has_permission_to_send_embed_in_channel, \
    get_id_from_text_if_exists_otherwise_get_author_id, get_pagination_views
from user_interactions import handle_leaderboard_navigation
from xp.xp_helper import get_level_image


class XPAndLevelsUserCommandExecutor(UserCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)
        self.xp_settings = variables.guilds_prefs[self.guild.id].xp_settings if self.guild else None

    async def check_for_section_enabled(self):
        if self.is_dm:
            await send_embed(f"XP commands are only available on servers.", self.channel)
            return False
        if not self.guild_prefs.xp_commands_enabled:
            if int(self.guild_prefs.spam_channel) == self.channel.id:
                return True
            spam_message = f" outside the designated spam " \
                           f"channel <#{self.guild_prefs.spam_channel}>." if self.guild_prefs.spam_channel != 0 else ""
            await send_embed(f"Sorry, but an admin has disabled {UserCommandSection.XP} commands"
                             f"{spam_message}", self.channel,
                             emoji='💔', color=0xFF522D, reply_to=self.message)
            return False
        return True

    async def handle_command_level(self):
        if await self.routine_checks_fail():
            return

        all_members_xp = variables.guilds_xp[self.guild.id].members_xp

        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        member: discord.Member = self.guild.get_member(discord_id) if not_author else self.author

        if not member:
            member = await discord_client.fetch_user(discord_id)
        if not member and discord_id not in all_members_xp.keys():
            await send_embed("Member not found!", self.channel, reply_to=self.message)
            return
        member_tag = all_members_xp[discord_id].member_tag if not member else f"{member}"

        with self.channel.typing():
            im = await get_level_image(member, self.xp_settings, all_members_xp,
                                       member_tag=member_tag, member_id=discord_id)
            with BytesIO() as image_binary:
                im.save(image_binary, 'JPEG')
                image_binary.seek(0)
                await send_message(message="", channel=self.channel,
                                   files=[discord.File(fp=image_binary, filename='level.jpg'), ],
                                   reply_to=self.message)

    async def handle_command_leaderboard(self):
        if await self.routine_checks_fail():
            return

        page = self.command_options_and_arguments_fixed.split(" ")[0] \
            if self.command_options_and_arguments_fixed else 1
        page = int(page) if isinstance(page, str) and page.isdigit() else 1

        members_xp = variables.guilds_xp[self.guild.id].members_xp
        if 0 in members_xp.keys():
            members_xp.pop(0)
        embed = make_leaderboard_embed(members_xp=members_xp, requested_by=self.author, page=page)
        page_count = ceil(len(members_xp) / 10)
        if page > page_count:
            page = 1
        view = get_pagination_views(page, page_count)
        sent_message = await send_message(message=None, channel=self.channel,
                                          embed=embed, reply_to=self.message, view=view)

        await handle_leaderboard_navigation(sent_message=sent_message, members_xp=members_xp,
                                            requested_by=self.author, page=page)

    async def handle_command_roles(self):
        if await self.routine_checks_fail():
            return

        embed_perms = bot_has_permission_to_send_embed_in_channel(self.channel)
        if len(self.xp_settings[XPSettingsKey.LEVEL_ROLES]) == 0:
            await send_embed(f"No level roles added yet.", self.channel,
                             reply_to=self.message, bold=False)
            return
        level_roles_string = ""
        for level, role_id in self.xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            if embed_perms:
                level_roles_string += f"• Level **{level}**: <@&{role_id}>\n"
            else:
                role = self.guild.get_role(int(role_id))
                level_roles_string += f"• Level **{level}**: {role if not isinstance(role, type(None)) else role_id}\n"
        await send_embed(f"**Level roles:**\n‎\n{level_roles_string}".strip(), self.channel,
                         reply_to=self.message, bold=False)
        return None
