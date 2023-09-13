import traceback
from typing import Union

import discord

from globals_ import shared_memory
from globals_.constants import BotLogLevel
from internal.bot_logger import InfoLogger, ErrorLogger
from models.guild import GuildPrefs


class BaseSlashes:

    def __init__(self, interaction):
        self.interaction: discord.Interaction = interaction
        self.guild: discord.Guild = interaction.guild
        self.channel: Union[discord.TextChannel, discord.DMChannel] = interaction.channel
        self.user: discord.User = interaction.user
        self.is_dm = not interaction.guild
        self.member: discord.Member = interaction.guild.get_member(self.user.id) if not self.is_dm else None
        self.guild_prefs: GuildPrefs = shared_memory.guilds_prefs[self.guild.id] if not self.is_dm else None
        self.interaction_data: dict = interaction.data

        self.command_name: str = interaction.command.qualified_name
        from slashes.music_slashes.base_music_slashes import MusicSlashes
        from slashes.admin_slashes.base_admin_slashes import AdminSlashes
        if isinstance(self, MusicSlashes):
            self.command_name = self.command_name.split(" ", 1)[1]
            command_type_permissions = shared_memory.music_commands_permissions
        elif isinstance(self, AdminSlashes):
            self.command_name = self.command_name.split(" ", 1)[1]
            command_type_permissions = shared_memory.admin_commands_permissions
        else:
            command_type_permissions = shared_memory.user_commands_permissions
        self.command_user_permissions: list = command_type_permissions.get(self.command_name, {}).get("member", [])
        self.command_bot_permissions: list = command_type_permissions.get(self.command_name, {}).get("bot", [])

        self.info_logger = InfoLogger(component=self.__class__.__name__)
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def log_command(self):
        try:
            from slashes.admin_slashes.base_admin_slashes import AdminSlashes
            from slashes.music_slashes.base_music_slashes import MusicSlashes
            from slashes.user_slashes.base_user_slashes import UserSlashes
            if isinstance(self, AdminSlashes):
                log_level = BotLogLevel.ADMIN_SLASH_COMMAND_RECEIVED
            elif isinstance(self, MusicSlashes):
                log_level = BotLogLevel.MUSIC_SLASH_COMMAND_RECEIVED
            elif isinstance(self, UserSlashes):
                log_level = BotLogLevel.USER_SLASH_COMMAND_RECEIVED
            else:
                log_level = BotLogLevel.SLASH_COMMAND_RECEIVED
            handler_name = self.interaction.command.qualified_name
            self.info_logger.log(f"Slash handler for `{handler_name}` called by user: {self.user} ({self.user.id})."
                                 + f" Channel: {self.channel} ({self.channel.id})." if self.channel else ""
                                 + f" Guild: {self.guild} ({self.guild.id})." if self.guild else "",
                                 log_to_discord=False,
                                 guild_id=self.guild.id if self.guild else None,
                                 level=log_level,
                                 extras={"interaction_data": self.interaction_data})
        except Exception as e:
            print(f"Error while logging slash command handler: {e}\n{traceback.format_exc()}")

    async def check_permissions(self):
        missing_user_perms = []
        missing_bot_perms = []
        if self.is_dm:
            return missing_user_perms, missing_bot_perms
        if self.command_user_permissions:
            if not self.member:
                return missing_user_perms, missing_bot_perms
            for perm in self.command_user_permissions:
                if not getattr(self.member.guild_permissions, perm):
                    missing_user_perms.append(perm)
        if self.command_bot_permissions:
            for perm in self.command_bot_permissions:
                if not getattr(self.guild.me.guild_permissions, perm):
                    missing_bot_perms.append(perm)
        return missing_user_perms, missing_bot_perms

    async def preprocess_and_validate(self,
                                      guild_only=False,
                                      **kwargs):

        if guild_only and not self.guild:
            await self.return_error_message(message="This command can only be used in a server.")
            return False

        missing_user_perms, missing_bot_perms = await self.check_permissions()
        if missing_user_perms or missing_bot_perms:
            error_message = "Please ensure that:"
            if missing_user_perms:
                user_perms = ', '.join(["**" + missing_user_perm.replace('_', ' ').title() + "**"
                                        for missing_user_perm in missing_user_perms])
                error_message += f"\n• You have the following permissions:" \
                                 f" {user_perms}"
            if missing_bot_perms:
                bot_perms = ', '.join(["**" + missing_bot_perm.replace('_', ' ').title() + "**"
                                       for missing_bot_perm in missing_bot_perms])
                error_message += f"\n• I have the following permissions:" \
                                 f" {bot_perms}"
            await self.return_error_message(message=error_message)
            return False

        await self.log_command()

        return True

    async def return_error_message(self, message=None):
        if not message:
            message = "An error occurred while processing your command. " \
                      "We've been informed of the issue and we'll get to fixing it ASAP."
        try:
            if not self.interaction.response.is_done():
                return await self.interaction.response.send_message(message, ephemeral=True,
                                                                    delete_after=10)
            else:
                return await self.interaction.followup.send(message, ephemral=True, delete_after=10)
        except:
            return await self.channel.send(message, delete_after=5)

    @property
    def is_using_music_channel(self):
        return self.guild_prefs and self.guild_prefs.music_channel == self.channel.id

    def send_as_ephemeral(self, make_visible=True):
        if self.is_dm:
            return False
        if self.is_using_music_channel:
            return True
        if not self.channel.permissions_for(self.guild.me).embed_links:
            return True
        return not make_visible
