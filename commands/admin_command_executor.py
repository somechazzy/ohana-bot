import asyncio
import re
from difflib import SequenceMatcher
import disnake as discord
from actions import send_message, send_embed, send_perm_error_message
from internal.bot_logging import log
from commands.command_executor import CommandExecutor
from globals_ import variables
from models.command import Command
from models.guild import GuildPrefs
from globals_.constants import BotLogType, CommandType, IGNORED_UNRECOGNIZED_COMMANDS, HelpListingVisibility


class AdminCommandExecutor(CommandExecutor):

    def __init__(self, message: discord.Message, command_name, guild_prefs: GuildPrefs = None):
        super().__init__(message, command_name, guild_prefs)
        asyncio.get_event_loop().create_task(self.log_command())
        self.command_object: Command = variables.admin_commands_dict.get(command_name, Command(''))
        self.sub_commands: [] = self.command_object.sub_commands
        self.command_options, self.used_sub_command = None, None

    async def log_command(self, level=BotLogType.ADMIN_COMMAND_RECEIVED):
        assumed_command = self.message_string_lowered.split(' ')[0][len(self.admin_prefix):]
        assumed_command = \
            self.command_name if self.command_name else assumed_command if len(assumed_command) > 3 else None
        if not assumed_command or assumed_command in IGNORED_UNRECOGNIZED_COMMANDS:
            return
        channel_text = f"{self.channel}/{self.guild}" if self.guild else f"{self.author}"
        await log(
            f"'{assumed_command}' from {self.author}/{self.author.id}. Message: '{self.message_content}'."
            f" Channel: {channel_text}.", log_to_discord=False,
            level=level if self.command_name else BotLogType.UNRECOGNIZED_COMMAND_RECEIVED,
            guild_id=self.guild.id if self.guild else None)

    async def handle_incorrect_use(self, feedback="Incorrect use of command."):
        feedback += f"\nSee `{self.admin_prefix}help {self.command_name}`."
        return await send_message(feedback, self.channel, reply_to=self.message,
                                  force_send_without_embed=True)

    async def handle_command_unrecognized(self):
        assumed_command = self.message_content.lower().split(' ')[0][len(self.prefix):].strip()
        closest_command = get_closest_command_if_exists(assumed_command)
        if assumed_command in IGNORED_UNRECOGNIZED_COMMANDS or not closest_command:
            return
        await log(f"Unrecognized command '{assumed_command}'. Suggested '{closest_command}'.", log_to_discord=False,
                  guild_id=self.guild.id)
        await send_embed(f"Hmm, did you mean `{self.admin_prefix}{closest_command}`?"
                         f" Use `{self.admin_prefix}help` to see all available commands.",
                         self.channel, reply_to=self.message)

    async def routine_checks_fail(self):
        has_perms, missing_perm, who = await self.has_needed_permissions_for_command(CommandType.ADMIN)
        if not has_perms:
            await send_perm_error_message(missing_perm, who, self.channel, reply_to=self.message)
            return True
        return False

    async def subcommand_checks_fail(self):
        if not self.command_options_and_arguments:
            # noinspection PyTypeChecker
            sub_commands_text = '`' + '` | `'.join(self.sub_commands) + '`'
            await self.handle_incorrect_use(feedback=f"You must use a sub-command"
                                                     f" with this command: {sub_commands_text}.")
            return True

        self.command_options = self.command_options_and_arguments_fixed.split(' ')
        self.used_sub_command = re.sub("[^A-Za-z]", "", self.command_options[0]).lower()

        if self.used_sub_command not in self.sub_commands:
            sub_commands_text = '`' + '` | `'.join(self.sub_commands) + '`'
            await self.handle_incorrect_use(feedback=f"You must use a sub-command"
                                                     f" with this command: {sub_commands_text}.")
            return True

        return False

    async def channel_checks_fail(self, channel):
        if not channel:
            await send_embed("I can't see that channel. Make sure you've "
                             "mentioned or entered ID of a channel I have access to.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True
        if isinstance(channel, discord.VoiceChannel):
            await send_embed("Channel you entered is a voice channel.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True

        return False


def get_closest_command_if_exists(assumed_command):
    for command in variables.admin_commands_names:
        if len(command) > 3:
            if SequenceMatcher(None, assumed_command, command).ratio() >= 0.8 and \
                    variables.admin_commands_dict.get(command,
                                                      Command('')).show_on_listing != HelpListingVisibility.HIDE:
                return command
    return None
