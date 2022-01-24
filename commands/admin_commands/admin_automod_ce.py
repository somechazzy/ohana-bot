import asyncio
import re
import traceback
import disnake as discord
from actions import send_embed, edit_embed, create_role, delete_message_from_guild
from auto_moderation.auto_moderator import scan_and_assign_role_for_single_message_channel
from globals_.constants import GuildLogType, ENCRYPTED_CHARACTERS
from internal.bot_logging import log_to_server, log
from globals_.clients import discord_client
from commands.admin_command_executor import AdminCommandExecutor
from globals_ import constants
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import get_id_from_text, get_auto_response_command_parameters, \
    get_banned_words_command_parameters, \
    get_single_message_command_parameters, get_react_role_add_parameters, \
    get_react_role_remove_parameters


class AutomodAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def handle_command_autoroles(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            self.guild_prefs = \
                await GuildPrefsComponent().validate_autoroles_exist_and_remove_invalid_ones(self.guild_prefs)
            if len(self.guild_prefs.autoroles) >= 10:
                await send_embed("Sorry! You already have the maximum of 10 autoroles."
                                 " (will probably increase in the future).",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to add.")
                return

            role_id = get_id_from_text(sub_command_options[0])
            if not role_id:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to add.")
                return

            role = self.guild.get_role(int(role_id))

            if await self.role_checks_fail(role):
                return

            if int(role_id) in self.guild_prefs.autoroles:
                await send_embed(f"`{role}` is already an autorole.",
                                 self.channel, reply_to=self.message)
                return
            await GuildPrefsComponent().add_guild_autorole(self.guild, role_id)
            await send_embed(f"`{role}` has been added to list of autoroles.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added role to list of autoroles.",
                                fields=["Role"],
                                values=[role])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to remove.")
                return

            role_id = get_id_from_text(sub_command_options[0])
            if int(role_id) not in self.guild_prefs.autoroles:
                await send_embed("Role you entered is not an autorole.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().remove_guild_autorole(self.guild, role_id)
            role = self.guild.get_role(int(role_id))
            if not role:
                role = "Unknown role"
            await send_embed(f"`{role}` has been removed from autoroles.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed role from list of autoroles.",
                                fields=["Role"],
                                values=[role])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.autoroles:
                await send_embed(f"No autoroles added yet.", self.channel, reply_to=self.message)
                return
            roles_string = ", ".join([f"<@&{role_id}>" for role_id in self.guild_prefs.autoroles
                                      if self.guild.get_role(int(role_id))])

            await send_embed(f"Autoroles:\n{roles_string}.", self.channel, reply_to=self.message)

        elif self.used_sub_command == "clear":
            if self.guild_prefs.autoroles:
                await GuildPrefsComponent().clear_guild_autoroles(self.guild)
                await send_embed(f"Autorole list cleared.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event="Cleared list of autoroles.")
            else:
                await send_embed(f"No autoroles added yet.", self.channel, reply_to=self.message)

    async def handle_command_autoresponses(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.guild_prefs.auto_responses) >= 30:
                await send_embed("Sorry! You already have the maximum of 30 auto responses.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with details please.")
                return
            parameters_string = ' '.join(sub_command_options)
            trigger, auto_response, delete, match_type = get_auto_response_command_parameters(parameters_string)

            if not trigger or not auto_response:
                await send_embed(f"Couldn't make out trigger and auto-response.\nUsage example: "
                                 f"`{self.admin_prefix}autoresponses add -full 'hi' 'hello'`",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if trigger in self.guild_prefs.auto_responses.keys():
                await send_embed(f"Trigger word/phrase `{trigger}` is already added. "
                                 f"See `{self.admin_prefix}autoresponses show`.",
                                 self.channel, reply_to=self.message)
                return
            for encrypted_char_value in ENCRYPTED_CHARACTERS.values():
                if encrypted_char_value in trigger:
                    await send_embed(f"Invalid input; usage of reserved string `{encrypted_char_value}`",
                                     self.channel, reply_to=self.message)
                    return

            await GuildPrefsComponent().add_guild_auto_response(self.guild, trigger, auto_response, delete, match_type)
            await send_embed(f"Auto-response added for trigger: `{trigger}`. Response: `{auto_response}`."
                             f" Word/phrase match type is {match_type}.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            dl = "Yes" if delete else "No"
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added auto-response.",
                                fields=["Trigger", "Response", "Options"],
                                values=[trigger,
                                        auto_response,
                                        f"Match type: **{match_type}** | Delete trigger text? **{dl}**"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with the auto-response's trigger to remove.")
                return

            requested_trigger_array = re.findall("[\"'][^'\"]*[\"']", ' '.join(sub_command_options))
            if not requested_trigger_array:
                await send_embed(f"Couldn't make out trigger word/phrase.\nUsage example: "
                                 f"`{self.admin_prefix}autoresponses remove 'hi'` ",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            requested_trigger = requested_trigger_array[0][1:len(requested_trigger_array[0]) - 1]
            if requested_trigger not in self.guild_prefs.auto_responses.keys():
                await send_embed(f"Trigger word/phrase you entered `{requested_trigger}` wasn't added before."
                                 f"See `{self.admin_prefix}autoresponses show`.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            auto_response = self.guild_prefs.auto_responses[requested_trigger]['response']
            match_type = self.guild_prefs.auto_responses[requested_trigger]['match']
            dl = "Yes" if self.guild_prefs.auto_responses[requested_trigger]['delete'] else "No"
            await GuildPrefsComponent().remove_guild_auto_response(self.guild, requested_trigger)
            await send_embed(f"Trigger `{requested_trigger}` has been removed from auto-responses.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed auto-response.",
                                fields=["Trigger", "Response", "Options"],
                                values=[requested_trigger, auto_response,
                                        f"Match type: **{match_type}** | Delete trigger text? **{dl}**"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.auto_responses:
                await send_embed(f"No auto-responses added yet.", self.channel,
                                 reply_to=self.message)
                return
            auto_responses_string = "Trigger / Response / Match Type / Delete Trigger\n\n"
            for i, trigger in enumerate(self.guild_prefs.auto_responses):
                response = self.guild_prefs.auto_responses.get(trigger).get("response")
                match_type = self.guild_prefs.auto_responses.get(trigger).get("match")
                delete = self.guild_prefs.auto_responses.get(trigger).get("delete")
                to_append = f"`{trigger}` / `{response}` / `{match_type}` / `{delete}`\n"
                if len(auto_responses_string + to_append) > 3800:
                    auto_responses_string += f"Displaying {i + 1} auto responses out of " \
                                             f"{len(self.guild_prefs.auto_responses)} total due to character limit. " \
                                             f"If you want to see more please DM the devs and we'll start supporting" \
                                             f" pages on this command."
                    break
                auto_responses_string += to_append
            await send_embed(f"Auto-responses:\n\n{auto_responses_string}.", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "clear":
            await GuildPrefsComponent().clear_guild_auto_responses(self.guild)
            await send_embed(f"Auto-responses list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared auto-response list.")

    async def handle_command_bannedwords(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.guild_prefs.banned_words) >= 15:
                await send_embed("Sorry! You already have the maximum of 15 banned words.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with details please.")
                return

            word, regex, warn, match_type = get_banned_words_command_parameters(' '.join(sub_command_options))

            if word is None:
                await send_embed(f"Invalid usage. See `{self.admin_prefix}help bannedwords`\n"
                                 f"Usage example: `{self.admin_prefix}bannedwords add poggers`",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if regex is None:
                await send_embed(f"Regular expression invalid.\n"
                                 f"Usage example: `{self.admin_prefix}bannedwords add -r pog(gers)?`",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if word in self.guild_prefs.banned_words.keys():
                await send_embed(f"`{word}` is already added as a banned word. "
                                 f"See `{self.admin_prefix}bannedwords show`.",
                                 self.channel, reply_to=self.message)
                return
            for encrypted_char_value in ENCRYPTED_CHARACTERS.values():
                if encrypted_char_value in word:
                    await send_embed(f"Invalid input; usage of reserved string `{encrypted_char_value}`",
                                     self.channel, reply_to=self.message)
                    return
            await GuildPrefsComponent().add_guild_banned_word(self.guild, word, regex, warn, match_type)
            await send_embed(("Word" if not regex else "Regex") + f" `{word}` added to list of banned words."
                                                                  f" Match type is {match_type}.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added banned word.",
                                fields=["Word", "Options"],
                                values=[word, f"Match type: {match_type}"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with the banned word to remove.")
                return
            assumed_requested_word = ' '.join(sub_command_options)
            if assumed_requested_word not in self.guild_prefs.banned_words.keys():
                await send_embed(f"Word you entered `{assumed_requested_word}` wasn't added before. "
                                 f"See `{self.admin_prefix}bannedwords show`.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            match_type = self.guild_prefs.banned_words[assumed_requested_word]['match']
            await GuildPrefsComponent().remove_guild_banned_word(self.guild, assumed_requested_word)
            await send_embed(f"`{assumed_requested_word}` has been removed from banned words.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed banned word.",
                                fields=["Word", "Options"],
                                values=[assumed_requested_word,
                                        f"Match type: **{match_type}**"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.banned_words:
                await send_embed(f"No banned words added yet.", self.channel,
                                 reply_to=self.message)
                return
            banned_words_string = "Word / Match Type / Is Regex?\n\n"
            index = 0
            for banned_word in self.guild_prefs.banned_words:
                index += 1
                match_type = self.guild_prefs.banned_words.get(banned_word).get("match")
                regex = self.guild_prefs.banned_words.get(banned_word).get("regex")
                banned_words_string += f"{index}: `{banned_word}` / `{match_type}` / `{regex}`\n"
            await send_embed(f"Banned Words:\n\n{banned_words_string}", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "clear":
            await GuildPrefsComponent().clear_guild_banned_words(self.guild)
            await send_embed(f"Banned words list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared list of banned words.")

    async def handle_command_singlemessage(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.guild_prefs.single_message_channels) >= 10:
                await send_embed(f"You already have the maximum of 20 gallery channels"
                                 f" (DM the devs if you need more).",
                                 self.channel, reply_to=self.message)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with details please.")
                return
            parameters_string = ' '.join(sub_command_options)
            channel_id, role_name, scan, mode = get_single_message_command_parameters(parameters_string)

            if channel_id is None or role_name is None:
                await send_embed(f"Invalid usage. See `{self.admin_prefix}help singlemessage`\n"
                                 f"Usage example: `{self.admin_prefix}sm "
                                 f"add -scan 732299154981912737 ✔ introduced`",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return

            if channel_id in self.guild_prefs.single_message_channels.keys():
                await send_embed(f"Channel <#{channel_id}> ({channel_id}) is already added. "
                                 f"See `{self.admin_prefix}singlemessage show`.",
                                 self.channel, reply_to=self.message)
                return
            channel = self.guild.get_channel(channel_id)
            if await self.channel_checks_fail(channel):
                return
            if not channel.permissions_for(self.guild.me).read_message_history and scan:
                await send_embed(f"I can't read message history in that channel and therefore can't scan old"
                                 f" messages. Consider giving me the permission or re-running the command"
                                 f" without the scan option.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            sent_message = await send_embed(f"• Creating `{role_name}` role...",
                                            self.channel, emoji=None, reply_to=self.message)
            await asyncio.sleep(1)
            created_role = await create_role(self.guild, role_name, reason=f"for single-text mode in #{channel}")
            if created_role:
                await edit_embed(f"✅ Role <@&{created_role.id}> created.\n"
                                 f"• Settings role permissions...",
                                 sent_message, emoji=None)
            else:
                await edit_embed(f"Role creation failed. Make sure I have necessary permissions.",
                                 sent_message, emoji='❌', color=0xFF522D)
                return
            if mode == 'permission':
                await asyncio.sleep(1)
                try:
                    permissions = channel.overwrites_for(created_role)
                    permissions._set("send_messages", False)
                    await channel.set_permissions(created_role, overwrite=permissions)
                except:
                    await log(f"{(traceback.format_exc())}", level=constants.BotLogType.BOT_WARNING,
                              print_to_console=False, guild_id=self.guild.id)
                    await edit_embed(f"Failed at setting permissions for created role. Make sure I have Manage Roles "
                                     f"and Manage Channels permissions in {channel.mention}!",
                                     sent_message, emoji='❌', color=0xFF522D)
                    return

            await GuildPrefsComponent().add_guild_single_message_channel(self.guild, channel_id, created_role.id, mode)
            if mode == 'permission':
                note = f"Note that the created role was placed at the bottom of the hierarchy. " \
                       f"If a higher role was explicitly given the permission to send messages in " \
                       f"{channel.mention} then you need move the created role above it."
            else:
                note = f"Each member can send only one text in <#{channel_id}> and any new messages will be deleted."

            if scan:
                await edit_embed(f"✅ Role `{role_name}` created.\n"
                                 + (f"✅ Role permissions set.\n" if mode == "permission" else "")
                                 + f"• Scanning old messages and giving members roles."
                                   f" This may take some time..",
                                 sent_message, emoji=None)
                count = await scan_and_assign_role_for_single_message_channel(channel, created_role.id)
                if count:
                    await edit_embed(f"Channel <#{channel_id}> set to single-text-per-member mode.\n"
                                     f"✅  {count} members were given the <@&{created_role.id}> role.\n{note}",
                                     sent_message, emoji='✅', color=0x0AAC00)
                else:
                    await edit_embed(f"Channel <#{channel_id}> set to single-text-per-member mode.\n"
                                     f"❕  Could not read text history of channel "
                                     f"therefore it was not scanned.\nRegardless: {note}",
                                     sent_message, emoji='✅', color=0x0AAC00)

            else:
                await edit_embed(f"Channel <#{channel_id}> set to single-text-per-member mode.\n{note}",
                                 sent_message, emoji='✅', color=0x0AAC00)

            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added single-text channel.",
                                fields=["Channel", "Role given to members", "Mode", "Scanned previous messages?"],
                                values=[f"<#{channel_id}>", f"<@&{created_role.id}>",
                                        "`Send Messages` permission disable" if mode == 'permission' else
                                        "Delete new messages", f"{scan}"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with the channel ID/mention to remove.")
                return
            assumed_channel_id = get_id_from_text(sub_command_options[0])

            if int(assumed_channel_id) not in self.guild_prefs.single_message_channels.keys():
                await send_embed(f"Channel with ID `{assumed_channel_id}` wasn't added before. "
                                 f"See `{self.admin_prefix}singlemessage show`.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().remove_guild_single_message_channel(self.guild, assumed_channel_id)
            await send_embed(f"Channel with ID `{assumed_channel_id}` has been removed from single-text"
                             f" mode. Don't forget to delete the role that was associated with it!",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Removed channel with ID `{assumed_channel_id}` from single-text mode.")
        elif self.used_sub_command == "show":
            if not self.guild_prefs.single_message_channels:
                await send_embed(f"No single-text channels added yet.", self.channel,
                                 reply_to=self.message)
                return
            single_message_channels_string = ""
            index = 0
            for i, single_message_channel in enumerate(self.guild_prefs.single_message_channels):
                index += 1
                channel_id = self.guild_prefs.single_message_channels.get(single_message_channel).get("channel_id")
                role_id = self.guild_prefs.single_message_channels.get(single_message_channel).get("role_id")
                mode = self.guild_prefs.single_message_channels.get(single_message_channel).get("mode")
                to_append = f"{index}. <#{channel_id}> with role <@&{role_id}> ({mode} mode)\n"
                if len(single_message_channels_string + to_append) > 1800:
                    single_message_channels_string += f"Displaying {i + 1} listings out of " \
                                                      f"{len(self.guild_prefs.auto_responses)} total due to character "\
                                                      f"limit."
                    break
                single_message_channels_string += to_append

            await send_embed(f"Single-text channels:\n\n{single_message_channels_string.strip()}",
                             self.channel, reply_to=self.message)

        elif self.used_sub_command == "clear":
            if self.guild_prefs.single_message_channels:
                await GuildPrefsComponent().clear_guild_single_message_channels(self.guild)
                await send_embed(f"Single-text channels list cleared. You still need to delete"
                                 f" any roles created.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event="Cleared list of single-text channels.")
            else:
                await send_embed(f"No single-text channels added yet.",
                                 self.channel, reply_to=self.message)

    async def handle_command_gallerychannel(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if len(self.guild_prefs.gallery_channels) >= 10:
                await send_embed(f"You already have the maximum of 20 gallery channels.",
                                 self.channel, reply_to=self.message)
                return

            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with channel ID/mention please.")
                return

            channel_id = get_id_from_text(' '.join(sub_command_options))

            if int(channel_id) in self.guild_prefs.gallery_channels:
                await send_embed(f"Channel <#{channel_id}> ({channel_id}) is already added. "
                                 f"See `{self.admin_prefix}gallerychannel show`.",
                                 self.channel, reply_to=self.message)
                return
            channel: discord.TextChannel = self.guild.get_channel(int(channel_id))
            if await self.channel_checks_fail(channel):
                return

            await GuildPrefsComponent().add_guild_gallery_channel(self.guild, channel_id)

            await send_embed(f"Channel <#{channel_id}> set as gallery channel.", self.channel,
                             emoji='✅', color=0x0AAC00)

            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added gallery channel.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with the channel ID/mention to remove.")
                return
            assumed_channel_id = int(get_id_from_text(sub_command_options[0]))

            if int(assumed_channel_id) not in self.guild_prefs.gallery_channels:
                await send_embed(f"Channel with ID `{assumed_channel_id}` wasn't added before. "
                                 "See `{self.admin_prefix}gallerychannel show`.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().remove_guild_gallery_channel(self.guild, assumed_channel_id)
            await send_embed(f"Disabled gallery mode on channel <#{assumed_channel_id}>"
                             f" (`{assumed_channel_id}`).",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Removed channel <#{assumed_channel_id}> "
                                      f"(`{assumed_channel_id}`) from gallery mode.")
        elif self.used_sub_command == "show":
            if not self.guild_prefs.gallery_channels:
                await send_embed(f"No gallery channels added yet.", self.channel, reply_to=self.message)
                return
            gallery_channels_string = \
                "\n".join([f"{i}. <#{gallery_channel}> ({gallery_channel})"
                           for i, gallery_channel in enumerate(self.guild_prefs.gallery_channels)])

            await send_embed(f"Gallery channels:\n\n{gallery_channels_string.strip()}",
                             self.channel, reply_to=self.message)

        elif self.used_sub_command == "clear":
            if not self.guild_prefs.gallery_channels:
                await send_embed(f"No gallery channels added yet.", self.channel,
                                 reply_to=self.message)
                return
            await GuildPrefsComponent().clear_guild_gallery_channels(self.guild)
            await send_embed(f"Gallery channels list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared list of gallery channels.")

    async def handle_command_whitelistedrole(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to set as whitelisted.")
                return

            role_id = get_id_from_text(sub_command_options[0])
            if not role_id:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to set as whitelisted.")
                return
            role = self.guild.get_role(int(role_id))
            if not role:
                await send_embed("Role doesn't seem to exist, are you sure you've used the correct role ID?",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().set_whitelisted_role(self.guild, int(role_id))
            await send_embed(f"Whitelisted role set to `{role}`. Any role above it as well will be excepted "
                             f"for banned words.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set whitelisted role for evading banned words check.",
                                fields=["Role"],
                                values=[role])

        elif self.used_sub_command == "show":
            await send_embed(f"Whitelisted role is <@&{self.guild_prefs.whitelisted_role}>.", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "unset":
            await GuildPrefsComponent().set_whitelisted_role(self.guild, 0)
            await send_embed(f"Whitelisted role removed.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Unset whitelisted role.")

    async def handle_command_rolepersistence(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        if self.used_sub_command == "enable":
            if self.guild_prefs.role_persistence_enabled:
                await send_embed(f"Role persistence is already enabled.",
                                 self.channel, reply_to=self.message)
                return
            else:
                await GuildPrefsComponent().set_role_persistence_enabled_state(self.guild, True)
                await send_embed(f"Role persistence has been enabled.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Enabled role persistence.")

        elif self.used_sub_command == "disable":
            if not self.guild_prefs.role_persistence_enabled:
                await send_embed(f"Role persistence is already disabled.",
                                 self.channel, reply_to=self.message)
                return
            else:
                await GuildPrefsComponent().set_role_persistence_enabled_state(self.guild, False)
                await send_embed(f"Role persistence has been disabled.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Disabled role persistence.")

    async def handle_command_reactrole(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            count_of_existing_react_roles = 0
            for channel_dict in self.guild_prefs.react_roles.values():
                for message_dict in channel_dict.values():
                    count_of_existing_react_roles += len(message_dict.keys())
            if count_of_existing_react_roles >= 20:
                await send_embed("Sorry! You already have the maximum of 20 react roles."
                                 " (will probably increase in the future).",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Please provide me with a text ID,"
                                                         " an emoji ID and a role ID (in order).")
                return

            message_id, emoji_id, role_id = get_react_role_add_parameters(sub_command_options)
            if any([not message_id, not emoji_id, not role_id]):
                await self.handle_incorrect_use(feedback="Please provide me with a text ID,"
                                                         " an emoji ID and a role ID (in order).")
                return
            message: discord.Message = await self.channel.fetch_message(message_id)
            emoji: discord.Emoji = discord_client.get_emoji(emoji_id)
            role: discord.Role = self.guild.get_role(int(role_id))

            if not message:
                await self.handle_incorrect_use(feedback=f"Message with ID `{message_id}` could not be found")
                return
            if message.type not in [discord.MessageType.default, discord.MessageType.reply]:
                await self.handle_incorrect_use(feedback=f"Message with ID `{message_id}` is a system text.")
                return

            if not emoji or not emoji.is_usable() or not emoji.available:
                await self.handle_incorrect_use(feedback=f"Emoji with ID `{emoji_id}` could not be found.")
                return

            if await self.role_checks_fail(role):
                return

            if self.guild_prefs.react_roles.get(self.channel.id, {}).get(message_id, {}).get(emoji_id, None):
                await self.handle_incorrect_use(feedback=f"Emoji with ID `{emoji_id}` is already being "
                                                         f"used on that text for a react role.")
                return

            await message.add_reaction(emoji)
            animated = 'a' if emoji.animated else ''
            colons = ':' if emoji.require_colons else ''

            await GuildPrefsComponent().add_guild_react_role(self.guild, self.channel.id, message_id, emoji_id, role_id)
            await delete_message_from_guild(self.message, "React role add command")
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Added react role.",
                                fields=["Role", "emoji", "Message"],
                                values=[role.mention, f"<{animated}{colons}{emoji.name}:{emoji_id}>",
                                        f"{self.channel.mention}: Message with ID {message_id} - "
                                        f"[Click here to jump to text]({message.jump_url})"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a text ID and"
                                                         " role ID (in order) to remove.")
                return

            message_id, emoji_id = get_react_role_remove_parameters(sub_command_options)
            if not self.guild_prefs.react_roles.get(self.channel.id, {}).get(message_id, {}).get(emoji_id):
                await self.handle_incorrect_use(feedback="No react role was set on "
                                                         "that text with the provided emoji")
                return
            role_id = self.guild_prefs.react_roles.get(self.channel.id, {}).get(message_id, {}).get(emoji_id)

            await GuildPrefsComponent().remove_guild_react_role(self.guild, self.channel.id, message_id, emoji_id)
            await self.message.add_reaction('👍')

            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Removed react role.",
                                fields=["Role", "Message"],
                                values=[f"<@&{role_id}>", f"{message_id}"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.react_roles:
                await send_embed(f"No react roles added yet.", self.channel, reply_to=self.message)
                return
            react_roles_str = ""
            for channel_id, channel_dict in self.guild_prefs.react_roles.items():
                for message_id, message_dict in channel_dict.items():
                    for emoji_id, role_id in message_dict.items():
                        react_roles_str += f"• <@&{role_id}>: with emoji ({emoji_id}) on message" \
                                           f" (id={message_id}) in channel (<#{channel_id}>) " \
                                           f"([jump](https://discord.com/channels/" \
                                           f"{self.guild.id}/{channel_id}/{message_id}))\n"
                        if len(react_roles_str) > 3800:
                            break
                    if len(react_roles_str) > 3800:
                        break
                if len(react_roles_str) > 3800:
                    react_roles_str += "..."
                    break

            await send_embed(f"React roles:\n{react_roles_str}.", self.channel,
                             reply_to=self.message, bold=False)

        elif self.used_sub_command == "clear":
            if self.guild_prefs.react_roles:
                await GuildPrefsComponent().clear_guild_react_roles(self.guild)
                await send_embed(f"React roles cleared.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event="Cleared list of react roles.")
            else:
                await send_embed(f"No react roles added yet.", self.channel, reply_to=self.message)
