from actions import send_embed
from internal.bot_logging import log_to_server
from commands.admin_command_executor import AdminCommandExecutor
from globals_.constants import UserCommandSection, GuildLogType
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import get_command_section_from_text


class ModulesAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)
        self.state_to_true = None

    async def handle_command_enablesection(self):
        self.state_to_true = True
        await self.handle_command_change_section_state()

    async def handle_command_disablesection(self):
        self.state_to_true = False
        await self.handle_command_change_section_state()

    async def handle_command_change_section_state(self):
        if await self.routine_checks_fail():
            return

        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback=f"Provide a section name please!"
                                                     f" Use `{self.prefix}help` to see available sections.")
            return

        assumed_section = self.command_options_and_arguments_fixed.split(" ")[0].lower()
        section = get_command_section_from_text(assumed_section)
        already_in_state = False
        if section is UserCommandSection.FUN:
            if self.guild_prefs.fun_commands_enabled == self.state_to_true:
                already_in_state = True
            else:
                await GuildPrefsComponent().set_guild_fun_section_enabled_state(self.guild, self.state_to_true)
        elif section is UserCommandSection.UTILITY:
            if self.guild_prefs.utility_commands_enabled == self.state_to_true:
                already_in_state = True
            else:
                await GuildPrefsComponent().set_guild_utility_section_enabled_state(self.guild, self.state_to_true)

        elif section is UserCommandSection.MODERATION:
            if self.guild_prefs.moderation_commands_enabled == self.state_to_true:
                already_in_state = True
            else:
                await GuildPrefsComponent().set_guild_moderation_section_enabled_state(self.guild, self.state_to_true)

        elif section is UserCommandSection.ANIME_AND_MANGA:
            if self.guild_prefs.mal_al_commands_enabled == self.state_to_true:
                already_in_state = True
            else:
                await GuildPrefsComponent().set_guild_anime_and_manga_section_enabled_state(self.guild,
                                                                                            self.state_to_true)

        elif section is UserCommandSection.XP:
            if self.guild_prefs.xp_commands_enabled == self.state_to_true:
                already_in_state = True
            else:
                await GuildPrefsComponent().set_guild_xp_section_enabled_state(self.guild, self.state_to_true)

        elif not section:
            await send_embed(f"Unrecognized section/category. Use `{self.prefix}help` "
                             f"to see available sections.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return

        else:
            await send_embed("Section was recognized but not programmed to be"
                             " changeable yet. Contact the dumb developers pls.",
                             self.channel, reply_to=self.message)
            return

        if already_in_state:
            await send_embed(f"{section} commands are already "
                             + ("enabled." if self.state_to_true else "disabled."),
                             self.channel, reply_to=self.message)
            return

        await send_embed(
            f"{section} commands have been " + ("enabled." if self.state_to_true else "disabled."),
            self.channel, reply_to=self.message)
        await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                            event=f"Command section/module **{section}** was " +
                                  ("enabled." if self.state_to_true else "disabled."))
