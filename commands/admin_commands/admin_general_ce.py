from actions import send_message, edit_message
from commands.admin_command_executor import AdminCommandExecutor
from globals_.constants import AdminCommandSection
from embed_factory import make_main_admin_help_embed, \
    make_command_admin_help_embed, make_overview_embed
from helpers import get_close_embed_view, get_main_help_views
from models.guild import GuildPrefs
from user_interactions import handle_general_close_embed, admin_help_navigation


class GeneralAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def handle_command_help(self):
        if await self.routine_checks_fail():
            return

        if not self.command_options_and_arguments_fixed:
            view = get_main_help_views(AdminCommandSection)
            embed = make_main_admin_help_embed(self.guild_prefs)
            sent_message = await send_message(None, self.channel, embed=embed, view=view)
            if sent_message is not None:
                await admin_help_navigation(self.message, sent_message, embed, self.guild_prefs)
        else:
            embed = make_command_admin_help_embed(self.message, self.guild_prefs)
            sent_message = await send_message(None, self.channel, embed=embed, reply_to=self.message,
                                              view=get_close_embed_view())
            close_embed = await handle_general_close_embed(sent_message=sent_message, requested_by=self.author,)
            if close_embed:
                await edit_message(sent_message, "Help embed closed.", reason=f"Closed admin command help embed",
                                   view=None)

    async def handle_help_on_dms(self):
        if not self.command_options_and_arguments_fixed:
            view = get_main_help_views(AdminCommandSection)
            embed = make_main_admin_help_embed(GuildPrefs(0, ''))
            sent_message = await send_message(None, self.author, embed=embed, view=view)
            if sent_message is not None:
                await admin_help_navigation(self.message, sent_message, embed, GuildPrefs(0, ''))
        else:
            embed = make_command_admin_help_embed(self.message, GuildPrefs(0, ''))
            await send_message(None, self.author, embed=embed)

    async def handle_command_overview(self):
        if await self.routine_checks_fail():
            return

        embed = make_overview_embed(self.guild_prefs, self.author)
        await send_message(None, self.channel, embed=embed)
