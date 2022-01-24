import re
from actions import send_embed
from globals_.constants import BOT_NAME
from internal.bot_logging import log_to_server
from commands.admin_command_executor import AdminCommandExecutor
from globals_ import constants
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent


class PrefixAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def handle_command_prefix(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="`set` must be followed by the prefix you want to set.")
                return
            old_prefix = self.prefix
            new_prefix = ' '.join(sub_command_options)
            if await self.new_prefix_checks_fail(new_prefix):
                return
            if new_prefix == self.admin_prefix:
                await send_embed("User commands prefix cannot be the same as admin commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if new_prefix == self.music_prefix:
                await send_embed("User commands prefix cannot be the same as music commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_guild_prefix(self.guild, new_prefix)
            await send_embed(f"Prefix changed from `{old_prefix}` to `{new_prefix}`\n\n"
                             f"*Psst. It's a good idea to show my prefix in my nickname,"
                             f" something like \"[{new_prefix}] {BOT_NAME}\"*",
                             self.channel, emoji='✅', color=0x0AAC00)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Updated prefix for user commands from `{old_prefix}` to `{new_prefix}`")

        elif self.used_sub_command == "show":
            await send_embed(f"Prefix is `{self.prefix}`", self.channel)

        elif self.used_sub_command == "reset":
            old_prefix = self.prefix
            await GuildPrefsComponent().set_guild_prefix(self.guild, constants.DEFAULT_PREFIX)
            await send_embed(f"Prefix changed from `{old_prefix}` to `{constants.DEFAULT_PREFIX}`\n"
                             f"Psst. It's a good idea to show my prefix in my nickname,"
                             f" something like [{constants.DEFAULT_PREFIX}] {BOT_NAME}",
                             self.channel, emoji='✅', color=0x0AAC00)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Reset prefix for user commands from `{old_prefix}`"
                                      f" back to `{constants.DEFAULT_PREFIX}`")

    async def handle_command_adminprefix(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="`set` must be followed by the prefix you want to set.")
                return
            old_prefix = self.admin_prefix
            new_prefix = ' '.join(sub_command_options)
            if await self.new_prefix_checks_fail(new_prefix):
                return
            if new_prefix == self.prefix:
                await send_embed("Admin commands prefix cannot be the same as user commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if new_prefix == self.music_prefix:
                await send_embed("Admin commands prefix cannot be the same as music commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_guild_admin_prefix(self.guild, new_prefix)
            await send_embed(f"Admin Prefix changed from `{old_prefix}` to `{new_prefix}`",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Updated prefix for admin commands from `{old_prefix}` to `{new_prefix}`")

        elif self.used_sub_command == "show":
            await send_embed(f"Admin Prefix is `{self.admin_prefix}` 🙄", self.channel)

        elif self.used_sub_command == "reset":
            old_prefix = self.admin_prefix
            await GuildPrefsComponent().set_guild_admin_prefix(self.guild, constants.DEFAULT_ADMIN_PREFIX)
            await send_embed(f"Admin Prefix changed from `{old_prefix}` "
                             f"to `{constants.DEFAULT_ADMIN_PREFIX}`\n",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Reset prefix for admin commands from `{old_prefix}`"
                                      f" back to `{constants.DEFAULT_ADMIN_PREFIX}`")

    async def handle_command_musicprefix(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="`set` must be followed by the prefix you want to set.")
                return
            old_prefix = self.music_prefix
            new_prefix = ' '.join(sub_command_options)
            if await self.new_prefix_checks_fail(new_prefix):
                return
            if new_prefix == self.prefix:
                await send_embed("Music commands prefix cannot be the same as user commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if new_prefix == self.admin_prefix:
                await send_embed("Music commands prefix cannot be the same as admin commands prefix.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_guild_music_prefix(self.guild, new_prefix)
            await send_embed(f"Music Prefix changed from `{old_prefix}` to `{new_prefix}`",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Updated prefix for music commands from `{old_prefix}` to `{new_prefix}`")

        elif self.used_sub_command == "show":
            await send_embed(f"Music Prefix is `{self.music_prefix}`", self.channel)

        elif self.used_sub_command == "reset":
            old_prefix = self.music_prefix
            await GuildPrefsComponent().set_guild_music_prefix(self.guild, constants.DEFAULT_MUSIC_PREFIX)
            await send_embed(f"Music Prefix changed from `{old_prefix}` "
                             f"to `{constants.DEFAULT_MUSIC_PREFIX}`\n",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, constants.GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Reset prefix for music commands from `{old_prefix}`"
                                      f" back to `{constants.DEFAULT_MUSIC_PREFIX}`")

    async def new_prefix_checks_fail(self, new_prefix):
        if len(new_prefix) > 10:
            await send_embed("Prefix must be 10 characters at most.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True
        if ' ' in new_prefix:
            await send_embed("Sorry! Prefix can't contain a space.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True
        if not len(re.findall("[.+\\-*=_&^%$#@!`/\\\\[\\]{}\'\":?<>;,~()A-Za-z0-9]", new_prefix)) == len(new_prefix):
            await send_embed("Invalid prefix. Prefix must be an easily accessible character.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True
        if re.findall("[A-Za-z]", new_prefix[-1]):
            await send_embed("Prefix can't end with an alphabetic character.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return True

        return False
