import asyncio
import random
import re
from actions import send_embed, send_message
from globals_ import variables
from globals_.clients import discord_client
from internal.bot_logging import log_to_server
from commands.admin_command_executor import AdminCommandExecutor
from globals_.constants import XPSettingsKey, AdminSettingsAction, GuildLogType, DEFAULT_TIMEFRAME_FOR_XP, \
    DEFAULT_MIN_XP_GIVEN, DEFAULT_MAX_XP_GIVEN, DEFAULT_LEVELUP_MESSAGE, DEFAULT_XP_DECAY_PERCENTAGE, \
    DEFAULT_XP_DECAY_DAYS
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import get_id_from_text, \
    get_curly_bracketed_parameters_from_text, get_level_up_roles_command_parameters, \
    bot_has_permission_to_send_embed_in_channel, is_float_convertible, get_menu_confirmation_view
from embed_factory import make_xp_overview_embed
from xp import xp


class XPAndLevelsAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)
        self.current_xp_settings = self.guild_prefs.xp_settings

    async def handle_command_xpgain(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "enable":
            if self.current_xp_settings[XPSettingsKey.XP_GAIN_ENABLED]:
                await send_embed(f"XP gain is **already enabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_ENABLED,
                                                       value=True)
            await send_embed(f"XP gain **enabled**." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Enabled XP gain on this server.")

        elif self.used_sub_command == "disable":
            if not self.current_xp_settings[XPSettingsKey.XP_GAIN_ENABLED]:
                await send_embed(f"XP gain is **already disabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_ENABLED,
                                                       value=False)
            await send_embed(f"XP gain disabled." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Disabled XP gain on this server.")

        elif self.used_sub_command in ["timeframe", "tf"]:
            if not sub_command_options or not sub_command_options[0].isdigit():
                await self.handle_incorrect_use(feedback="`timeframe` must be followed by a number.")
                return
            old_timeframe = self.current_xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]
            new_timeframe = int(sub_command_options[0])
            if old_timeframe == new_timeframe:
                await send_embed(f"Timeframe is already set to {new_timeframe}.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if not new_timeframe >= 10 or not new_timeframe <= 86400:
                await send_embed(f"Timeframe cannot be less than 10 seconds or more than 1 day.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_TIMEFRAME,
                                                       value=new_timeframe)
            await send_embed(f"XP gain timeframe set to **{new_timeframe} seconds**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP gain timeframe.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_timeframe} seconds", f"{new_timeframe} seconds"])

        elif self.used_sub_command == "min":
            if not sub_command_options or not sub_command_options[0].isdigit():
                await self.handle_incorrect_use(feedback="`min` must be followed by a number.")
                return
            old_min = self.current_xp_settings[XPSettingsKey.XP_GAIN_MIN]
            new_min = int(sub_command_options[0])
            if old_min == new_min:
                await send_embed(f"Minimum XP gain is already set to {new_min}.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if not new_min >= 0 or not new_min <= 5000:
                await send_embed(f"Minimum XP cannot be less than 0 or more than 10k.", self.channel,
                                 emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_MIN,
                                                       value=new_min)
            await send_embed(f"Minimum XP gain set to **{new_min}**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅',
                             color=0x0AAC00, reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP gain minimum value per timeframe.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_min}", f"{new_min}"])

        elif self.used_sub_command == "max":
            if not sub_command_options or not sub_command_options[0].isdigit():
                await self.handle_incorrect_use(feedback="`max` must be followed by a number.")
                return
            old_max = self.current_xp_settings[XPSettingsKey.XP_GAIN_MAX]
            current_min = self.current_xp_settings[XPSettingsKey.XP_GAIN_MIN]
            new_max = int(sub_command_options[0])
            if old_max == new_max:
                await send_embed(f"Maximum XP gain is already set to {new_max}.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if not new_max >= 0 or not new_max <= 10000:
                await send_embed(f"Maximum XP cannot be less than 0 or more than 10k.", self.channel,
                                 emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_MAX,
                                                       value=new_max)
            appended_feedback = f" All XP gain will now be {current_min} (minimum value)." \
                if (new_max == 0 and current_min > 0) else ""
            await send_embed(f"Maximum XP gain set to **{new_max}**." + appended_feedback +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅',
                             color=0x0AAC00, reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP gain maximum value per timeframe.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_max}", f"{new_max}"])

        elif self.used_sub_command in ["booster", "boost"]:
            if not sub_command_options or not sub_command_options[0].isdigit():
                await self.handle_incorrect_use(feedback="`booster` must be followed by a number.")
                return
            old_booster = self.current_xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN]
            new_booster = int(sub_command_options[0])
            if old_booster == new_booster:
                await send_embed(f"XP gain bonus for boosters is already set to {new_booster}%.",
                                 self.channel, reply_to=self.message, bold=False)
                return
            if not new_booster >= 0 or not new_booster <= 1000:
                await send_embed(f"Booster bonus must be between 0% and 1000%", self.channel,
                                 emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.BOOST_EXTRA_GAIN,
                                                       value=new_booster)
            await send_embed(f"XP gain booster bonus set to **{new_booster}%**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP gain booster bonus.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_booster}%", f"{new_booster}%"])

        elif self.used_sub_command == "reset":
            old_timeframe = self.current_xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]
            old_min = self.current_xp_settings[XPSettingsKey.XP_GAIN_MIN]
            old_max = self.current_xp_settings[XPSettingsKey.XP_GAIN_MAX]
            new_timeframe = DEFAULT_TIMEFRAME_FOR_XP
            new_min = DEFAULT_MIN_XP_GIVEN
            new_max = DEFAULT_MAX_XP_GIVEN
            if old_timeframe == new_timeframe and old_min == new_min and old_max == new_max:
                await send_embed(f"XP gain settings are already default values.\n"
                                 f"Timeframe: **{new_timeframe} seconds**.\n"
                                 f"Min Gain: **{new_min}**.\nMax Gain: **{new_max}**.",
                                 self.channel,
                                 reply_to=self.message, bold=False)
                return

            await GuildPrefsComponent().reset_xp_gain_settings(guild=self.guild)
            await send_embed(f"XP gain settings have been reset:"
                             f"\n• XP min gain = **20**, max gain = **40**."
                             f"\n• Timeframe = **60 seconds**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Reset all XP gain settings.",
                                fields=["Old Settings", "New Settings"],
                                values=[f"Timeframe: {old_timeframe} seconds.\n"
                                        f"Min Gain: {old_min}.\nMax Gain: {old_max}.",
                                        f"Timeframe: {new_timeframe} seconds.\n"
                                        f"Min Gain: {new_min}.\nMax Gain: {new_max}."])

    async def handle_command_levelupmessage(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "enable":
            if self.current_xp_settings[XPSettingsKey.LEVELUP_ENABLED]:
                await send_embed(f"Level up messages are **already enabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_ENABLED,
                                                       value=True)
            await send_embed(f"Level up messages **enabled**." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Enabled level up messages on this server.")

        elif self.used_sub_command == "disable":
            if not self.current_xp_settings[XPSettingsKey.LEVELUP_ENABLED]:
                await send_embed(f"Level up messages are **already disabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_ENABLED,
                                                       value=False)
            await send_embed(f"Level up messages disabled." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Disabled level up messages on this server.")

        elif self.used_sub_command == "set":
            if not sub_command_options:
                example = f"{self.admin_prefix}levelupmessage set" + \
                          " Congrats {member_mention} on reaching level {level}!"
                await self.handle_incorrect_use(feedback="`set` must be followed by the text.\n"
                                                         f"Example: `{example}`")
                return
            old_message = self.current_xp_settings[XPSettingsKey.LEVELUP_MESSAGE]
            new_message = re.sub("[ ]+", " ", self.message.content.strip()).split(" ", 2)[2]
            curly_bracketed_parameters = get_curly_bracketed_parameters_from_text(new_message)
            for param in curly_bracketed_parameters:
                if param.lower() not in ['{member_mention}', '{member_tag}', '{level}']:
                    await send_embed(f"Could not recognize {param} as a replaceable value."
                                     " Please only use the following:\n"
                                     "• `{member_mention}`: for member's mention/att.\n"
                                     "• `{member_tag}`: for member's tag (e.g. Someone#5432).\n"
                                     "• `{level}`: for the level which the member just hit", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message, bold=False)
                    return

            if curly_bracketed_parameters:
                appended_feedback = f"Here's how it'll look like:\n" + \
                                    new_message.format(member_mention=self.author.mention,
                                                       member_tag=str(self.author),
                                                       level=int((random.random() * 10) + 1) * 5)
            else:
                appended_feedback = f"Note: It seems you haven't used replaceable values (such as member mention or " \
                                    f"level).\n See `{self.admin_prefix}help lvlup` for more info."
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_MESSAGE,
                                                       value=new_message)
            await send_embed(f"Levelup text set to `{new_message}`\n {appended_feedback}",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set level up text for this server.",
                                fields=["Old Message", "New Message"],
                                values=[f"`{old_message}`", f"`{new_message}`"])

        elif self.used_sub_command == "show":
            lvlup_message = self.current_xp_settings[XPSettingsKey.LEVELUP_MESSAGE]
            await send_embed(f"Your current levelup text is `{lvlup_message}`\n"
                             f"Here's how it'll look like:\n" +
                             lvlup_message.format(member_mention=self.author.mention,
                                                  member_tag=str(self.author),
                                                  level=int((random.random() * 10) + 1) * 5) +
                             self.xp_ov_tip(),
                             self.channel, reply_to=self.message, bold=False)

        elif self.used_sub_command == "reset":
            old_message = self.current_xp_settings[XPSettingsKey.LEVELUP_MESSAGE]
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_MESSAGE,
                                                       value=DEFAULT_LEVELUP_MESSAGE)
            await send_embed(f"Levelup text has been reset to `{DEFAULT_LEVELUP_MESSAGE}`\n"
                             f"Here's how it'll look like:\n" +
                             DEFAULT_LEVELUP_MESSAGE.format(member_mention=self.author.mention,
                                                            member_tag=str(self.author),
                                                            level=int((random.random() * 10) + 1) * 5) +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Reset level up text for this server.",
                                fields=["Old Message", "New (default) Message"],
                                values=[f"`{old_message}`", f"`{DEFAULT_LEVELUP_MESSAGE}`"])

    async def handle_command_levelupchannel(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="`set` needs a channel ID/mention to set to.")
                return
            old_channel_id = self.current_xp_settings[XPSettingsKey.LEVELUP_CHANNEL]
            new_channel_id = sub_command_options[0]
            new_channel_id = get_id_from_text(new_channel_id)
            if not new_channel_id:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to set as level up channel.")
                return
            if old_channel_id == new_channel_id:
                await send_embed(f"<#{new_channel_id}> is already the level up channel.",
                                 self.channel, reply_to=self.message, bold=False)
                return
            channel = self.guild.get_channel(new_channel_id)
            if await self.channel_checks_fail(channel):
                return

            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_CHANNEL,
                                                       value=new_channel_id)
            await send_embed(f"Level up channel set to <#{new_channel_id}>."
                             f" All level up messages will be sent there.", self.channel,
                             emoji='✅', color=0x0AAC00, reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set level up channel.",
                                fields=["Channel"],
                                values=[f"<#{new_channel_id}>"])

        elif self.used_sub_command == "show":
            if self.current_xp_settings[XPSettingsKey.LEVELUP_CHANNEL] == 0:
                await send_embed(f"No level up channel set. Level up messages are sent"
                                 f" to the chat the user is active in.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await send_embed(f"Level up channel is "
                             f"<#{self.current_xp_settings[XPSettingsKey.LEVELUP_CHANNEL]}>.",
                             self.channel, reply_to=self.message, bold=False)

        elif self.used_sub_command == "unset":
            await send_embed(f"Level up channel unset. Level up messages will now be sent"
                             f" to the chat the user is active in.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_CHANNEL,
                                                       value=0)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Unset level up channel.")

    async def handle_command_leveluproles(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.current_xp_settings[XPSettingsKey.LEVEL_ROLES]) >= 15:
                await send_embed("Sorry! You already have the maximum of **15 level roles**."
                                 " (might increase in the future).", self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with details please.\nExample:"
                                                         f"`{self.admin_prefix}lr add 30 726004541157539881`.")
                return
            parameters_string = ' '.join(sub_command_options)
            level, role_id = get_level_up_roles_command_parameters(parameters_string)

            if not level or not role_id:
                await send_embed(f"Couldn't make out level and role ID.\nUsage example: "
                                 f"`{self.admin_prefix}lr add 10 725749391293415447`",
                                 self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return

            for key, value in self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].items():
                if level == key:
                    await send_embed(f"Level **{key}** is already associated with the role ID={value}. "
                                     f"See `{self.admin_prefix}lr show`.",
                                     self.channel, reply_to=self.message, bold=False)
                    return

            if not level >= 0 or not level <= 400:
                await send_embed("Awarding levels can only be between 0 and 400.",
                                 self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return

            role = self.guild.get_role(int(role_id))

            if await self.role_checks_fail(role):
                return

            self.current_xp_settings[XPSettingsKey.LEVEL_ROLES][level] = role_id
            sorted_level_roles = dict(sorted(self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].items()))
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVEL_ROLES,
                                                       value=sorted_level_roles)

            await send_embed(f"Level role added."
                             f" Members will get the `{role}` role upon reaching level {level}."
                             f"\nSee all level roles using `{self.admin_prefix}lr show`",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)

            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added level role.",
                                fields=["Level", "Role"],
                                values=[level, f"<@&{role_id}>"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback=f"Provide me with details please.\n"
                                                         f"Example:`{self.admin_prefix}lr remove 30`.")
                return

            level = int(sub_command_options[0])
            if level not in self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].keys():
                await send_embed(f"Level **{level}** has no role set for it. "
                                 f"See `{self.admin_prefix}lr show`.",
                                 self.channel, emoji='❌', reply_to=self.message, bold=False)
                return

            role_id = self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].pop(level)
            role = self.guild.get_role(int(role_id))
            appended_text = f" There are still other rewarded roles at this level." \
                            f" See `{self.admin_prefix}lr show`." \
                if level in self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].keys() \
                else f"\nSee all level roles using `{self.admin_prefix}lr show`"

            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVEL_ROLES,
                                                       value=self.current_xp_settings[XPSettingsKey.LEVEL_ROLES])
            await send_embed(f"Level role removed. Members will no longer get the "
                             f"`{role if role else role_id}` role upon reaching "
                             f"**level {level}**.\n{appended_text}",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)

            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed level role.",
                                fields=["Level", "Role"],
                                values=[level, f"<@&{role_id}>"])

        elif self.used_sub_command == "show":
            embed_perms = bot_has_permission_to_send_embed_in_channel(self.channel)
            if len(self.current_xp_settings[XPSettingsKey.LEVEL_ROLES]) == 0:
                await send_embed(f"No level roles added yet.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            level_roles_string = ""
            for level, role_id in self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].items():
                if embed_perms:
                    level_roles_string += f"• Level **{level}**: <@&{role_id}>\n"
                else:
                    role = self.guild.get_role(int(role_id))
                    level_roles_string += f"• Level **{level}**: {role if role else role_id}\n"
            await send_embed(f"**Level roles:**\n‎\n{level_roles_string}".strip(), self.channel,
                             reply_to=self.message, bold=False)

        elif self.used_sub_command == "clear":
            self.current_xp_settings[XPSettingsKey.LEVEL_ROLES].clear()
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVEL_ROLES,
                                                       value=self.current_xp_settings[XPSettingsKey.LEVEL_ROLES])
            await send_embed(f"Level roles list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared all level roles.")

        elif self.used_sub_command == "stack":
            stack_enabled_before = self.current_xp_settings[XPSettingsKey.STACK_ROLES]
            stack_enabled_after = not stack_enabled_before
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.STACK_ROLES,
                                                       value=stack_enabled_after)
            await send_embed(f"Level roles stacking **{'enabled' if stack_enabled_after else 'disabled'}**. "
                             f"Each member's roles will be updated next time they level up.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Level roles stacking **{'enabled' if stack_enabled_after else 'disabled'}**.")

    async def handle_command_xpdecay(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "enable":
            if self.current_xp_settings[XPSettingsKey.XP_DECAY_ENABLED]:
                await send_embed(f"XP decay is **already enabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_DECAY_ENABLED,
                                                       value=True)
            await send_embed(f"XP decay **enabled**." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Enabled XP decay on this server.")

        elif self.used_sub_command == "disable":
            if not self.current_xp_settings[XPSettingsKey.XP_DECAY_ENABLED]:
                await send_embed(f"XP decay is **already disabled**.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_DECAY_ENABLED,
                                                       value=False)
            await send_embed(f"XP decay **disabled**." + self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Disabled XP decay on this server.")

        elif self.used_sub_command in ["percentage", "percent"]:
            if not sub_command_options or not is_float_convertible(sub_command_options[0]):
                await self.handle_incorrect_use(feedback="`percentage` must be followed by a number.")
                return
            old_percentage = self.current_xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]
            new_percentage = float(sub_command_options[0])
            if old_percentage == new_percentage:
                await send_embed(f"XP decay percentage is already set to {new_percentage}%.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if not new_percentage >= 0 or not new_percentage <= 100:
                await send_embed(f"Percentage must be between 0 and 100", self.channel,
                                 emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild,
                                                       setting=XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY,
                                                       value=new_percentage)
            await send_embed(f"XP decay percentage set to **{new_percentage}%**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP decay percentage.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_percentage}%", f"{new_percentage}%"])

        elif self.used_sub_command in ["days", "grace"]:
            if not sub_command_options or not sub_command_options[0].isdigit():
                await self.handle_incorrect_use(feedback="`days` must be followed by a number.")
                return
            old_days = self.current_xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]
            new_days = int(sub_command_options[0])
            if old_days == new_days:
                await send_embed(f"XP decay grace period is already set to {new_days} days.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if not new_days >= 1:
                await send_embed(f"XP decay grace period **cannot** be less than 1 days.", self.channel,
                                 emoji='❌', color=0xFF522D, reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.DAYS_BEFORE_XP_DECAY,
                                                       value=new_days)
            await send_embed(f"XP decay grace period set to **{new_days} days**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set XP decay grace period.",
                                fields=["Old Value", "New Value"],
                                values=[f"{old_days}", f"{new_days}"])

        elif self.used_sub_command == "reset":
            old_percentage = self.current_xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]
            old_days = self.current_xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]
            new_percentage = DEFAULT_XP_DECAY_PERCENTAGE
            new_days = DEFAULT_XP_DECAY_DAYS
            if old_percentage == new_percentage and old_days == new_days:
                await send_embed(f"XP decay settings already set to default values:\n"
                                 f"Percentage: **{new_percentage}%**.\nGrace Period: **{new_days} days**.",
                                 self.channel, reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().reset_xp_decay_settings(guild=self.guild)
            await send_embed(f"XP decay settings have been reset:"
                             f"\n• Percentage of decay per day = **{new_percentage}%**."
                             f"\n• Grace period = **{new_days} days**." +
                             self.xp_ov_tip(),
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Reset XP decay settings.",
                                fields=["Old Settings", "New Settings"],
                                values=[f"Percentage: {old_percentage}%.\nGrace Period: {old_days} days.",
                                        f"Percentage: {new_percentage}%.\nGrace Period: {new_days} days."])

    async def handle_command_xpignoredchannels(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]) >= 10:
                await send_embed("Sorry! You already have the maximum of **10 ignored channels**."
                                 " (might increase in the future).", self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel mention/ID to add.")
                return
            channel_id = get_id_from_text(sub_command_options[0])
            if not channel_id:
                await self.handle_incorrect_use(feedback="Provide me with a channel mention/ID to add.")
                return
            if channel_id in self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
                await send_embed(f"<#{channel_id}> is already an ignored channel.",
                                 self.channel, reply_to=self.message, bold=False)
                return
            channel = self.guild.get_channel(channel_id)
            if await self.channel_checks_fail(channel):
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_CHANNELS,
                                                       value=channel_id, action=AdminSettingsAction.ADD)
            await send_embed(f"<#{channel_id}> has been added to XP-gain ignored channels.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added a channel to list of XP-gain ignored channels.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel mention/ID to remove.")
                return
            requested_channel = sub_command_options[0]
            channel_id = get_id_from_text(requested_channel)
            if int(channel_id) not in self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
                await send_embed("Channel you entered isn't an ignored channel.",
                                 self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_CHANNELS,
                                                       value=channel_id, action=AdminSettingsAction.REMOVE)
            await send_embed(f"<#{channel_id}> has been removed from XP-gain ignored channels.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed a channel from list of XP-gain ignored channels.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command == "show":
            if not self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
                await send_embed(f"No XP-gain ignored channels added yet.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            channels_string = "<#" + ">, <#" \
                .join([str(i) for i in self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]]) + ">"
            await send_embed(f"XP-gain ignored channels:\n{channels_string}", self.channel,
                             reply_to=self.message, bold=False)

        elif self.used_sub_command == "clear":
            if not self.current_xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
                await send_embed(f"No XP-gain ignored channels added yet.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_CHANNELS,
                                                       value=None, action=AdminSettingsAction.CLEAR)
            await send_embed(f"XP-gain ignored channels list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared list of XP-gain ignored channels.")

    async def handle_command_xpignoredroles(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]) >= 10:
                await send_embed("Sorry! You already have the maximum of **10 ignored roles**."
                                 " (might increase in the future).", self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role mention/ID to add.")
                return
            role_id = get_id_from_text(sub_command_options[0])
            if not role_id:
                await self.handle_incorrect_use(feedback="Provide me with a role mention/ID to add.")
                return
            role = self.guild.get_role(role_id)
            if await self.role_checks_fail(role, check_if_assignable=False):
                return
            if role.id in self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]:
                await send_embed(f"`{role}` is already an ignored role.",
                                 self.channel, reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_ROLES,
                                                       value=role_id, action=AdminSettingsAction.ADD)
            await send_embed(f"`{role}` has been added to XP-gain ignored roles.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added a role to list of XP-gain ignored roles.",
                                fields=["Role"],
                                values=[f"<@&{role_id}>"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel mention/ID to un-ignore.")
                return
            role_id = get_id_from_text(sub_command_options[0])
            if int(role_id) not in self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]:
                await send_embed("Role you entered isn't an ignored role.",
                                 self.channel, emoji='❌', color=0xFF522D,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_ROLES,
                                                       value=role_id, action=AdminSettingsAction.REMOVE)
            await send_embed(f"<#{role_id}> has been removed from XP-gain ignored roles.",
                             self.channel, emoji='✅', color=0x0AAC00,
                             reply_to=self.message, bold=False)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed a role from list of XP-gain ignored roles.",
                                fields=["Role"],
                                values=[f"<@&{role_id}>"])

        elif self.used_sub_command == "show":
            if not self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]:
                await send_embed(f"No XP-gain ignored roles added yet.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            if bot_has_permission_to_send_embed_in_channel(self.channel):
                roles_string = "<@&" + ">, <@&" \
                    .join([str(i) for i in self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]]) + ">"
            else:
                roles_string = ", ".join([
                    f"{self.guild.get_role(role_id) or 'Deleted Role'} "
                    f"({role_id})" for role_id in self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]
                ])
            await send_embed(f"XP-gain ignored roles:\n{roles_string}", self.channel,
                             reply_to=self.message, bold=False)

        elif self.used_sub_command == "clear":
            if not self.current_xp_settings[XPSettingsKey.IGNORED_ROLES]:
                await send_embed(f"No XP-gain ignored roles added yet.", self.channel,
                                 reply_to=self.message, bold=False)
                return
            await GuildPrefsComponent().set_xp_setting(guild=self.guild, setting=XPSettingsKey.IGNORED_ROLES,
                                                       value=None, action=AdminSettingsAction.CLEAR)
            await send_embed(f"XP-gain ignored roles list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared list of XP-gain ignored roles.")

    async def handle_command_xpoverview(self):
        if await self.routine_checks_fail():
            return

        embed = make_xp_overview_embed(self.guild_prefs, self.author)
        await send_message(None, self.channel, embed=embed)

    async def handle_command_xp(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "give":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Whom should I give XP to?"
                                                         " Provide either a user mention/ID, or "
                                                         "just \"all\" to give to everyone.")
                return
            target = sub_command_options[0].lower()
            target_member_id = get_id_from_text(target)
            if not target_member_id and target not in ["all", "everyone"]:
                await self.handle_incorrect_use(feedback="Provide either a user mention/ID, or"
                                                         " just \"all\" to give to everyone.")
                return
            if len(sub_command_options) == 1 or not sub_command_options[1].isdigit():
                await self.handle_incorrect_use(feedback="Provide an amount to give.")
                return
            amount = int(sub_command_options[1])
            if amount == 0:
                return await send_embed(f"Giving 0 doesn't do much. Try a higher number.", self.channel)
            if target in ["all", "everyone"]:
                for member_id, member_xp in variables.guilds_xp[self.guild.id].members_xp.items():
                    member = self.guild.get_member(member_id)
                    if member:
                        if not member.bot:
                            await xp.edit_member_xp(member=member, guilds_prefs=self.guild_prefs, offset=amount)
                    else:
                        xp.edit_user_xp(user_id=member_id, guilds_prefs=self.guild_prefs, offset=amount)
                await send_embed(f"Gave {amount} XP to everyone!", self.channel)
            else:
                target_member = self.guild.get_member(target_member_id)
                if target_member:
                    if target_member.bot:
                        return await send_embed("Bots can't have XP. Duh.", self.channel, reply_to=self.message)
                    await xp.edit_member_xp(member=target_member, guilds_prefs=self.guild_prefs, offset=amount)
                elif variables.guilds_xp[self.guild.id].members_xp.get(target_member_id):
                    target_member = f"<@{target_member_id}>"
                    xp.edit_user_xp(user_id=target_member_id, guilds_prefs=self.guild_prefs, offset=amount)
                else:
                    return await send_embed("Can't find the user.", self.channel, reply_to=self.message)
                await send_embed(f"Gave {amount} XP to {target_member}!", self.channel)

        elif self.used_sub_command == "take":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Whom should I take XP from?"
                                                         " Provide either a user mention/ID, or "
                                                         "just \"all\" to take from everyone.")
                return
            target = sub_command_options[0].lower()
            target_member_id = get_id_from_text(target)
            if not target_member_id and target not in ["all", "everyone"]:
                await self.handle_incorrect_use(feedback="Provide either a user mention/ID, or"
                                                         " just \"all\" to take from everyone.")
                return
            if len(sub_command_options) == 1 or not sub_command_options[1].isdigit():
                await self.handle_incorrect_use(feedback="Provide an amount to take.")
                return
            amount = int(sub_command_options[1])
            if amount == 0:
                return await send_embed(f"Taking away 0 doesn't do much. Try a higher number.", self.channel)
            if target in ["all", "everyone"]:
                for member_id, member_xp in variables.guilds_xp[self.guild.id].members_xp.items():
                    member = self.guild.get_member(member_id)
                    if member:
                        if not member.bot:
                            await xp.edit_member_xp(member=member, guilds_prefs=self.guild_prefs, offset=amount)
                    else:
                        xp.edit_user_xp(user_id=member_id, guilds_prefs=self.guild_prefs, offset=amount)
                await send_embed(f"Took {amount} XP from everyone :(", self.channel)
            else:
                target_member = self.guild.get_member(target_member_id)
                if target_member:
                    if target_member.bot:
                        return await send_embed("Bots can't have XP. Duh.", self.channel, reply_to=self.message)
                    await xp.edit_member_xp(member=target_member, guilds_prefs=self.guild_prefs, offset=amount)
                elif variables.guilds_xp[self.guild.id].members_xp.get(target_member_id):
                    target_member = f"<@{target_member_id}>"
                    xp.edit_user_xp(user_id=target_member_id, guilds_prefs=self.guild_prefs, offset=amount)
                else:
                    return await send_embed("Can't find the user.", self.channel, reply_to=self.message)
                await send_embed(f"Took {amount} XP from {target_member} :(", self.channel)

        elif self.used_sub_command == "reset":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Whom should I reset XP for?"
                                                         " Provide either a user mention/ID, or "
                                                         "just \"all\" to reset for everyone.")
                return
            target = sub_command_options[0].lower()
            target_member_id = get_id_from_text(target)
            targeting_everyone = target in ["all", "everyone"]
            if not target_member_id and not targeting_everyone:
                await self.handle_incorrect_use(feedback="Provide either a user mention/ID, or"
                                                         " just \"all\" to reset for everyone.")
                return
            if targeting_everyone:
                if self.author.id != self.guild.owner.id:
                    return await send_embed("Resetting all XP is only available for the owner", channel=self.channel)
                view = get_menu_confirmation_view(label="I agree. Reset XP for EVERYONE.")
                sent_message = await send_embed("Resetting XP for everyone is **not reversible**. "
                                                "Are you absolutely 100% sure you want to do this?",
                                                channel=self.channel, view=view, bold=False)

                def check_interactions(interaction_):
                    if interaction_.message.id != sent_message.id:
                        return False
                    if interaction_.user.id != self.author.id:
                        asyncio.get_event_loop().create_task(interaction_.response.defer())
                        return False
                    return True

                try:
                    interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                                check=check_interactions,
                                                                timeout=300)
                except asyncio.TimeoutError:
                    try:
                        await self.channel.get_partial_message(sent_message.id).edit_message("Timed out.", view=None)
                    except:
                        pass
                    return
                await interaction.response.defer()
                if interaction.data.values and interaction.data.values[0] == "confirm":
                    await self.channel.get_partial_message(sent_message.id).edit_message("In progress...", view=None)
                    for member_id, member_xp in variables.guilds_xp[self.guild.id].members_xp.items():
                        member = self.guild.get_member(member_id)
                        if member:
                            if not member.bot:
                                await xp.edit_member_xp(member=member, guilds_prefs=self.guild_prefs, reset=True)
                        else:
                            xp.edit_user_xp(user_id=member_id, guilds_prefs=self.guild_prefs, reset=True)
                    await send_embed(f"Reset XP for everyone.", self.channel)
            else:
                target_member = self.guild.get_member(target_member_id)
                if target_member:
                    if target_member.bot:
                        return await send_embed("Bots can't have XP. Duh.", self.channel, reply_to=self.message)
                    xp_before = await xp.edit_member_xp(member=target_member, guilds_prefs=self.guild_prefs, reset=True)
                elif variables.guilds_xp[self.guild.id].members_xp.get(target_member_id):
                    target_member = f"<@{target_member_id}>"
                    xp_before = xp.edit_user_xp(user_id=target_member_id, guilds_prefs=self.guild_prefs, reset=True)
                else:
                    return await send_embed("Can't find the user.", self.channel, reply_to=self.message)
                await send_embed(f"Reset XP done for {target_member}. "
                                 f"Run `{self.admin_prefix}xp give {xp_before}` to revert.", self.channel)

    def xp_ov_tip(self):
        return f"\nYou can see current XP settings for this server using command `{self.admin_prefix}xpov`." \
            if int(random.random() * 4) == 2 else ""
