import asyncio
import time
import disnake as discord
from globals_ import variables, constants
from models.guild import GuildPrefs
from actions import send_embed
from .user_command_executor import UserCommandExecutor
from . import user_commands
from .music_command_executor import MusicCommandExecutor
from . import music_commands
from .admin_command_executor import AdminCommandExecutor
from . import admin_commands


class CommandHandler:
    def __init__(self, message: discord.Message, guild_prefs: GuildPrefs = None):
        self.is_dm = isinstance(message.channel, discord.DMChannel)
        if not guild_prefs and not self.is_dm:
            raise AssertionError("Non-dm command handlers must be initiated with GuildPrefs object")
        self.message = message
        self.message_content = message.content
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild if not self.is_dm else None
        self.guild_prefs = guild_prefs if not self.is_dm else GuildPrefs(0, '')
        self.prefix = self.guild_prefs.prefix
        self.admin_prefix = self.guild_prefs.admin_prefix
        self.music_prefix = self.guild_prefs.music_prefix

    def is_author_command_rate_limited(self):
        """
        Checks whether or not the user is command rate-limited.
        :return:
        """
        if self.author.id == constants.BOT_OWNER_ID:
            return
        if self.author.id in variables.user_command_use:
            commands_used_over_last_x_seconds = len(variables.user_command_use[self.author.id])
            if commands_used_over_last_x_seconds >= constants.COMMAND_LIMIT_PER_X_SECONDS:
                return True

        current_time = time.time()
        asyncio.get_event_loop().create_task(self.add_timed_rate_limit(current_time))
        return False

    async def add_timed_rate_limit(self, value):
        if self.author.id not in variables.user_command_use:
            variables.user_command_use[self.author.id] = [value]
        else:
            variables.user_command_use[self.author.id].append(value)
        await asyncio.sleep(constants.COMMAND_LIMIT_X_SECONDS)
        variables.user_command_use[self.author.id].remove(value)


class UserCommandHandler(CommandHandler):

    def __init__(self, message, guild_prefs=None):
        super().__init__(message, guild_prefs)
        self.assumed_command = self.message_content.lower().split(' ')[0][len(self.prefix):].strip()

    def command_issued(self, actual_command: str):
        if self.assumed_command.lower() == actual_command.strip().lower():
            return True
        aliases = variables.commands_dict[actual_command].aliases
        for alias in aliases:
            if alias.strip().lower() == self.assumed_command.lower():
                return True
        return False

    async def handle_command(self):
        """
        Finds the command that the user might have used in the message being scanned.
        If found, the command handler is called.
        If not found, checks for the closest command with a high-enough similarity distance.
        :return:
        """
        if not self.assumed_command or self.assumed_command.startswith(self.prefix):
            return
        if self.assumed_command in variables.normal_commands_names:
            if self.is_author_command_rate_limited():
                if self.author.id not in variables.users_notified_of_rate_limit:
                    await send_embed("Slow down!", self.channel)
                    variables.users_notified_of_rate_limit.append(self.author.id)
                return
        if self.author.id in variables.users_notified_of_rate_limit:
            variables.users_notified_of_rate_limit = list(filter(self.author.id.__ne__,
                                                                 variables.users_notified_of_rate_limit))

        for command_name in variables.commands_dict.keys():
            if self.command_issued(command_name):
                command_section = variables.commands_dict[command_name].section
                command_executor_name = ''.join([cs_word[0].upper() + cs_word[1:]
                                                 for cs_word in command_section.split(' ')]) + "UserCommandExecutor"
                command_executor = getattr(user_commands, command_executor_name)
                command_executor = command_executor(self.message, command_name, self.guild_prefs)
                command_method = getattr(command_executor, f"handle_command_{command_name.lower()}")
                return await command_method()

        await UserCommandExecutor(self.message, None, self.guild_prefs).handle_command_unrecognized()

    async def handle_help_on_dms(self):
        await user_commands.UtilityUserCommandExecutor(self.message, 'help', self.guild_prefs).handle_help_on_dms()


class MusicCommandHandler(CommandHandler):

    def __init__(self, message, guild_prefs=None):
        super().__init__(message, guild_prefs)
        self.assumed_command = message.content.lower().split(' ')[0][len(self.music_prefix):].strip()

    def command_issued(self, actual_command: str):
        if self.assumed_command == actual_command.strip().lower():
            return True
        aliases = variables.music_commands_dict[actual_command].aliases
        for alias in aliases:
            if alias.strip().lower() == self.assumed_command:
                return True
        return False

    async def handle_command(self):
        if not self.assumed_command or self.assumed_command.startswith(self.admin_prefix):
            return
        if self.assumed_command in variables.music_commands_names:
            if self.is_author_command_rate_limited():
                if self.message.author.id not in variables.users_notified_of_rate_limit:
                    await send_embed("Slow down!", self.message.channel)
                    variables.users_notified_of_rate_limit.append(self.message.author.id)
                return
        if self.message.author.id in variables.users_notified_of_rate_limit:
            variables.users_notified_of_rate_limit = list(filter(self.message.author.id.__ne__,
                                                                 variables.users_notified_of_rate_limit))

        for command_name in variables.music_commands_dict.keys():
            if self.command_issued(command_name):
                command_section = variables.music_commands_dict[command_name].section
                command_executor_name = ''.join([cs_word[0].upper() + cs_word[1:]
                                                 for cs_word in command_section.split(' ')]) + "MusicCommandExecutor"
                command_executor = getattr(music_commands, command_executor_name)
                command_executor = command_executor(self.message, command_name, self.guild_prefs)
                command_method = getattr(command_executor, f"handle_command_{command_name.lower()}")
                return await command_method()

        await MusicCommandExecutor(self.message, None, self.guild_prefs).handle_command_unrecognized()

    async def handle_help_on_dms(self):
        await music_commands.GeneralMusicCommandExecutor(self.message, 'help',
                                                         self.guild_prefs).handle_help_on_dms()


class AdminCommandHandler(CommandHandler):

    def __init__(self, message, guild_prefs=None):
        super().__init__(message, guild_prefs)
        self.assumed_command = message.content.lower().split(' ')[0][len(self.admin_prefix):].strip()

    def command_issued(self, actual_command: str):
        if self.assumed_command == actual_command.strip().lower():
            return True
        aliases = variables.admin_commands_dict[actual_command].aliases
        for alias in aliases:
            if alias.strip().lower() == self.assumed_command:
                return True
        return False

    async def handle_command(self):
        if not self.assumed_command or self.assumed_command.startswith(self.admin_prefix):
            return
        if self.assumed_command in variables.admin_commands_names:
            if self.is_author_command_rate_limited():
                if self.message.author.id not in variables.users_notified_of_rate_limit:
                    await send_embed("Slow down!", self.message.channel)
                    variables.users_notified_of_rate_limit.append(self.message.author.id)
                return
        if self.message.author.id in variables.users_notified_of_rate_limit:
            variables.users_notified_of_rate_limit = list(filter(self.message.author.id.__ne__,
                                                                 variables.users_notified_of_rate_limit))

        for command_name in variables.admin_commands_dict.keys():
            if self.command_issued(command_name):
                command_section = variables.admin_commands_dict[command_name].section
                command_executor_name = ''.join([cs_word[0].upper() + cs_word[1:]
                                                 for cs_word in command_section.split(' ')]) + "AdminCommandExecutor"
                command_executor = getattr(admin_commands, command_executor_name)
                command_executor = command_executor(self.message, command_name, self.guild_prefs)
                command_method = getattr(command_executor, f"handle_command_{command_name.lower()}")
                return await command_method()

        await AdminCommandExecutor(self.message, None, self.guild_prefs).handle_command_unrecognized()

    async def handle_help_on_dms(self):
        await admin_commands.GeneralAdminCommandExecutor(self.message, 'help',
                                                         self.guild_prefs).handle_help_on_dms()
