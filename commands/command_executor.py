import re
import disnake as discord
from actions import send_embed
from internal.bot_logging import log
from globals_ import variables
from models.guild import GuildPrefs
from globals_.constants import CommandType, BotLogType, VOICE_PERMISSIONS


class CommandExecutor:
    def __init__(self, message, command_name, guild_prefs: GuildPrefs = None):
        self.message = message
        self.message_content = message.content
        self.message_string_lowered = str(self.message_content).lower()
        self.author = message.author
        self.channel = message.channel
        self.is_dm = isinstance(message.channel, discord.channel.DMChannel)
        if not guild_prefs and not self.is_dm:
            raise AssertionError("Non-dm command handlers must be initiated with GuildPrefs object")
        self.guild = message.guild if not self.is_dm else None
        self.guild_prefs = guild_prefs if not self.is_dm else GuildPrefs(0, '')
        self.prefix = self.guild_prefs.prefix
        self.music_prefix = self.guild_prefs.music_prefix
        self.admin_prefix = self.guild_prefs.admin_prefix
        self.command_name = command_name
        self.command_options_and_arguments = (self.message_content.strip().split(' ', 1)[1]
                                              if self.message_content.__contains__(' ') else "").strip()
        self.command_options_and_arguments_fixed = re.sub('[ ]+', ' ', self.command_options_and_arguments)

    async def has_needed_permissions_for_command(self, command_type, voice_channel=None):
        if self.is_dm:
            return True, "None", "None"
        member_has_perm, member_missing_perm = await self.member_has_needed_permissions_for_command(command_type)
        if not member_has_perm:
            return False, member_missing_perm, "member"
        bot_has_perm, bot_missing_perm = await self.bot_has_needed_permissions_for_command(command_type,
                                                                                           voice_channel=voice_channel)
        if not bot_has_perm:
            return False, bot_missing_perm, "bot"
        return True, "None", "None"

    async def bot_has_needed_permissions_for_command(self, command_type, voice_channel=None):
        bot_member = self.channel.guild.me
        bot_permissions = self.channel.permissions_for(bot_member)
        bot_permissions_in_voice = voice_channel.permissions_for(bot_member) if voice_channel else None
        if command_type == CommandType.USER:
            command = variables.commands_dict.get(self.command_name)
        elif command_type == CommandType.MUSIC:
            command = variables.music_commands_dict.get(self.command_name)
        else:
            command = variables.admin_commands_dict.get(self.command_name)
        if not command.bot_perms:
            return True, "None"
        if not command:
            await log(f"Command can't be recognized. Command: {self.command_name}",
                      level=BotLogType.BOT_ERROR)
            return False, "Unknown"
        if bot_permissions.administrator:
            return True, "None"
        for perm in command.bot_perms:
            if perm in VOICE_PERMISSIONS:
                if not voice_channel:
                    continue
                if hasattr(bot_permissions_in_voice, perm):
                    if not getattr(bot_permissions_in_voice, perm):
                        return False, perm
                else:
                    await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                              level=BotLogType.BOT_ERROR)
                    return True, "None"
            else:
                if hasattr(bot_permissions, perm):
                    if not getattr(bot_permissions, perm):
                        return False, perm
                else:
                    await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                              level=BotLogType.BOT_ERROR)
                    return True, "None"
        return True, "None"

    async def member_has_needed_permissions_for_command(self, command_type):
        member_permissions = self.channel.permissions_for(self.author)
        if command_type == CommandType.USER:
            command = variables.commands_dict.get(self.command_name)
        elif command_type == CommandType.MUSIC:
            command = variables.music_commands_dict.get(self.command_name)
        else:
            command = variables.admin_commands_dict.get(self.command_name)
        if not command.member_perms:
            return True, "None"
        if not command:
            await log(f"Command can't be recognized. Command: {self.command_name}", level=BotLogType.BOT_ERROR)
            return False, "Unknown"
        if member_permissions.administrator:
            return True, "None"
        for perm in command.member_perms:
            if hasattr(member_permissions, perm):
                if not getattr(member_permissions, perm):
                    return False, perm
            else:
                await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                          level=BotLogType.BOT_ERROR)
                return True, "None"
        return True, "None"

    async def role_checks_fail(self, role, check_if_assignable=True, delete_after=None):
        if not role:
            await send_embed("Role doesn't seem to exist. Are you sure you've used the correct role ID?",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message,
                             delete_after=delete_after)
            return True
        if check_if_assignable:
            if self.guild.me.roles[-1] <= role or role.is_bot_managed() or role.is_premium_subscriber() \
                    or role.is_integration() or role.is_default():
                await send_embed("I cannot assign this role to others due to hierarchy"
                                 " or due to it being a managed role.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message,
                                 delete_after=delete_after)
                return True
        return False

    async def routine_checks_fail(self):
        raise NotImplementedError
