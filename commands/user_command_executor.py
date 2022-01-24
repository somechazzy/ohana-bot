import asyncio
from difflib import SequenceMatcher
from actions import send_perm_error_message, send_message, send_embed
from internal.bot_logging import log
from commands.command_executor import CommandExecutor
from globals_ import variables
from models.command import Command
from models.guild import GuildPrefs
from globals_.constants import BotLogType, CommandType, IGNORED_UNRECOGNIZED_COMMANDS, HelpListingVisibility


class UserCommandExecutor(CommandExecutor):
    def __init__(self, message, command_name, guild_prefs: GuildPrefs = None):
        super().__init__(message, command_name, guild_prefs)
        asyncio.get_event_loop().create_task(self.log_command())

    async def log_command(self, level=BotLogType.USER_COMMAND_RECEIVED):
        assumed_command = self.message_string_lowered.split(' ')[0][len(self.prefix):]
        assumed_command = \
            self.command_name if self.command_name else assumed_command if len(assumed_command) > 2 else None
        if not assumed_command or assumed_command in IGNORED_UNRECOGNIZED_COMMANDS:
            return
        channel_text = f"{self.channel}/{self.guild}" if self.guild else f"{self.author}"
        await log(
            f"'{assumed_command}' from {self.author}/{self.author.id}. Message: '{self.message_content}'."
            f" Channel: {channel_text}.", log_to_discord=False,
            level=level if self.command_name else BotLogType.UNRECOGNIZED_COMMAND_RECEIVED,
            guild_id=self.guild.id if self.guild else None)

    async def handle_incorrect_use(self, feedback="Incorrect use of command."):
        feedback += f"\nSee `{self.prefix}help {self.command_name}`."
        return await send_message(feedback, self.channel, reply_to=self.message)

    async def routine_checks_fail(self, check_section_enabled=True):
        if check_section_enabled:
            if not await self.check_for_section_enabled():
                return True
        has_perms, missing_perm, who = await self.has_needed_permissions_for_command(command_type=CommandType.USER)
        if not has_perms:
            await send_perm_error_message(missing_perm, who, self.channel, reply_to=self.message)
            return True
        return False

    async def handle_command_unrecognized(self):
        assumed_command = self.message_content.lower().split(' ')[0][len(self.prefix):].strip()
        closest_command = get_closest_command_if_exists(assumed_command)
        if assumed_command in IGNORED_UNRECOGNIZED_COMMANDS or not closest_command:
            return
        await log(f"Unrecognized command '{assumed_command}'. Suggested '{closest_command}'.", log_to_discord=False,
                  guild_id=self.guild.id)
        await send_embed(f"Hmm, did you mean `{self.prefix}{closest_command}`? Use `{self.prefix}help` "
                         f"to see all available commands.", self.channel, reply_to=self.message)

    async def check_for_section_enabled(self):
        raise NotImplementedError


def get_closest_command_if_exists(assumed_command):
    for command in variables.normal_commands_names:
        if len(command) > 2:
            if SequenceMatcher(None, assumed_command, command).ratio() >= 0.75 and \
                    variables.commands_dict.get(command, Command('')).show_on_listing != HelpListingVisibility.HIDE:
                return command
    return None
