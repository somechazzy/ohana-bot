import asyncio
import json
import time
from urllib.parse import quote
import auth
from internal import web_handler
from globals_.clients import firebase_client, discord_client
from commands.user_command_executor import UserCommandExecutor
from actions import delete_message_from_guild, edit_message, send_embed, send_message
import re
from globals_.constants import UserCommandSection, CachingType
from helpers import get_presentable_merriam_definition_data, get_main_help_views, get_close_embed_view, \
    get_pagination_views, get_id_from_text_if_exists_otherwise_get_author_id, get_duration_and_reason_if_exist, \
    convert_minutes_to_time_string
from embed_factory import make_countdown_embed, make_urban_embed, make_merriam_embed, \
    make_main_help_embed, make_command_help_embed, make_server_info_embed, make_member_info_embed
from models.guild import GuildPrefs
from user_interactions import handle_general_close_embed, urban_navigation, help_navigation


class UtilityUserCommandExecutor(UserCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def check_for_section_enabled(self):
        if self.is_dm:
            return True
        if not self.guild_prefs.utility_commands_enabled:
            if int(self.guild_prefs.spam_channel) == self.channel.id:
                return True
            spam_message = f" outside the designated spam " \
                           f"channel <#{self.guild_prefs.spam_channel}>." if self.guild_prefs.spam_channel != 0 else ""
            await send_embed(f"Sorry, but an admin has disabled {UserCommandSection.UTILITY}"
                             f" commands{spam_message}", self.channel, emoji='💔',
                             color=0xFF522D, reply_to=self.message)
            return False
        return True

    async def handle_command_emoji(self, recursed=False, message_to_handle=None):
        if not recursed:
            if await self.routine_checks_fail():
                return
            message_to_handle = self.message
        emoji_list = re.findall("<[a]?:[^:]+:[0-9]+", message_to_handle.content)
        if len(emoji_list) > 0:
            emoji_to_enlarge = emoji_list[0]
            emoji_id = re.findall("[0-9]+$", emoji_to_enlarge)[0]
            static = False if emoji_to_enlarge[1] == 'a' else True
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}" + (".png" if static else ".gif")
            await send_message(url, self.channel, reply_to=message_to_handle)
        else:
            message_ids = re.findall("[0-9]+", message_to_handle.content)
            if len(message_ids) == 0:
                await self.handle_incorrect_use(feedback="Provide me with an emoji or the ID"
                                                         " of a text inside this channel.")
                return
            try:
                message_to_handle = await self.channel.fetch_message(int(message_ids[0]))
                await self.handle_command_emoji(recursed=True, message_to_handle=message_to_handle)
            except:
                await self.handle_incorrect_use(feedback="Provide me with an emoji or the ID"
                                                         " of a text inside this channel.")
                return

    async def handle_command_avatar(self):
        if await self.routine_checks_fail():
            return
        if self.is_dm:
            avatar = self.author.avatar
            if not avatar:
                return await send_message(f"User has no avatar.", self.channel, reply_to=self.message)
            return await send_message(avatar.url, self.channel, reply_to=self.message)
        guild_avatar_requested = \
            any(option in self.command_options_and_arguments.lower() for option in ['-g', '-guild', '-s', '-server'])
        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        member = self.guild.get_member(int(discord_id))
        if not member:
            try:
                member = await self.guild.fetch_member(int(discord_id))
            except:
                member = None
        if not member:
            return await self.handle_incorrect_use(feedback="Couldn't get that user's avatar.")
        avatar = member.guild_avatar if guild_avatar_requested else member.avatar
        if not avatar:
            return await send_message(f"User has no{' server' if guild_avatar_requested else ''} avatar.",
                                      self.channel, reply_to=self.message)
        await send_message(avatar.url, self.channel, reply_to=self.message)

    async def handle_command_banner(self):
        if await self.routine_checks_fail():
            return
        if self.is_dm:
            try:
                user = await discord_client.fetch_user(int(self.author.id))
            except:
                user = None
            avatar = user.banner
            if not avatar:
                return await send_message(f"User has no banner.", self.channel, reply_to=self.message)
            return await send_message(avatar.url, self.channel, reply_to=self.message)

        guild_banner_requested = \
            any(option in self.command_options_and_arguments.lower() for option in ['-g', '-guild', '-s', '-server'])
        if guild_banner_requested:
            return await send_embed("Bots can't see a member's server banner yet. Check back later!",
                                    self.channel)
        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        try:
            user = await discord_client.fetch_user(int(discord_id))
        except:
            user = None
        if not user:
            return await self.handle_incorrect_use(feedback="Couldn't get that user's banner.")
        banner = user.banner
        if not banner:
            return await send_message(f"User has no banner.",
                                      self.channel, reply_to=self.message)
        await send_message(banner.url, self.channel, reply_to=self.message)

    async def handle_command_remindme(self):
        if await self.routine_checks_fail(check_section_enabled=False):
            return

        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(f"You need to at least provide me with a period of time.")
            return

        if self.command_options_and_arguments.lower().startswith("me"):
            self.command_options_and_arguments = self.command_options_and_arguments[2:]

        duration_minutes, reason = get_duration_and_reason_if_exist(self.command_options_and_arguments,
                                                                    time_mandatory=True)
        if reason == "not provided":
            reason = "no reminder specified"
        if duration_minutes > 86400 or duration_minutes == 0:
            if not duration_minutes:
                await self.handle_incorrect_use(feedback="You need to provide a period of time.")
            else:
                await send_embed("The reminder duration can be 60 days at most. Sorry :(",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
            return
        time_remaining_string = convert_minutes_to_time_string(duration_minutes)
        current_time_seconds = int(time.time()) + time.altzone
        time_of_duration_end_seconds = current_time_seconds + duration_minutes * 60

        async def wait_and_send_reminder():
            await asyncio.sleep(duration_minutes * 60)
            await send_message(f"⏱ Reminder: {reason}", self.author)
            await firebase_client.remove_reminder(db_key)

        db_key = await firebase_client.add_reminder(time_of_duration_end_seconds, reason, self.author.id)
        asyncio.get_event_loop().create_task(wait_and_send_reminder())
        await send_embed(f"Understood. I will remind you about \"{reason}\" in "
                         f"{time_remaining_string}.", self.channel, emoji='⏱',
                         color=0x0AAC00, reply_to=self.message, delete_after=5)
        if not self.is_dm:
            try:
                await asyncio.sleep(5)
                await self.message.add_reaction('✅')
            except:
                pass

    async def handle_command_countdown(self):
        # this command is a mess and i should probably delete before pushing
        # update: i decided to keep it, sorry for this abomination
        if await self.routine_checks_fail():
            return

        duration_minutes, reason = get_duration_and_reason_if_exist(self.command_options_and_arguments)
        if reason == "not provided":
            reason = "Unknown"
        if duration_minutes > 10080:
            await self.handle_incorrect_use(feedback=f"You cannot start a countdown that lasts longer than 7 days.", )
            return
        await delete_message_from_guild(self.message, "countdown command")

        time_remaining_string_initial = convert_minutes_to_time_string(duration_minutes)
        current_time_seconds = int(time.time()) + time.altzone
        time_of_countdown_end_seconds = current_time_seconds + duration_minutes * 60
        time_of_countdown_end_string = time.strftime("%H:%M, %d/%m/%Y", time.
                                                     localtime(time_of_countdown_end_seconds))

        description = f"‎‎‎\n‎‎‎ ⏳ **{time_remaining_string_initial} to go.**\n‎‎‎"
        embed = make_countdown_embed(description, reason, self.author, time_of_countdown_end_string)

        sent_message = await send_message(message=None, embed=embed, channel=self.channel)
        if sent_message is None:
            return
        sent_message_id = sent_message.id
        countdown_title = reason.replace("|", " ")
        requested_by_name = str(self.author).replace("|", " ")
        requested_by_avatar = self.author.avatar.with_size(32).url if self.author.avatar else None
        countdown_params = f"{countdown_title} | {requested_by_name} |" \
                           f" {requested_by_avatar} | {time_of_countdown_end_seconds} | {time_remaining_string_initial}"
        await firebase_client.add_countdown(sent_message, countdown_params)

        while True:
            current_time_seconds = int(time.time()) + time.altzone
            time_remaining_seconds = time_of_countdown_end_seconds - current_time_seconds
            if time_remaining_seconds < 60:
                if time_remaining_seconds < 0:
                    break
                description = f"‎‎‎\n‎‎‎ ⏳ **{time_remaining_seconds} seconds to go.**\n‎‎‎"
                embed = make_countdown_embed(description, reason, self.author, time_of_countdown_end_string)
                sent_message = self.channel.get_partial_message(sent_message_id)
                if sent_message is None:
                    return
                edited_message = await edit_message(sent_message, content=None, embed=embed)
                if edited_message is None:
                    return
                await asyncio.sleep(time_remaining_seconds)
            else:
                time_remaining_minutes = int(time_remaining_seconds / 60)
                time_remaining_string = convert_minutes_to_time_string(time_remaining_minutes)
                description = f"‎‎‎\n‎‎‎ ⏳ **{time_remaining_string} to go.**\n‎‎‎"
                embed = make_countdown_embed(description, reason, self.author, time_of_countdown_end_string)
                sent_message = self.channel.get_partial_message(sent_message_id)
                edited_message = await edit_message(sent_message, content=None, embed=embed, log_enable=False)
                if edited_message is None:
                    return
                await asyncio.sleep(30)
        description = f"‎‎‎\n‎‎‎ ⏳ Countdown is up.\n‎‎‎"
        embed = make_countdown_embed(description, reason, self.author, time_of_countdown_end_string,
                                     cd_up=True, cd_duration=time_remaining_string_initial)
        sent_message = self.channel.get_partial_message(sent_message_id)
        edited_message = await edit_message(sent_message, content=None, embed=embed)
        if edited_message is None:
            return
        await firebase_client.remove_countdown(sent_message)

    async def handle_command_urban(self):
        if await self.routine_checks_fail():
            return

        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="You need to provide the term you want to define.")
            return

        term = self.command_options_and_arguments.replace("/", " ")
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        querystring = {"term": term}
        headers = {
            'x-rapidapi-key': auth.RAPID_API_KEY,
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
        }

        response = await web_handler.request("GET", url, CachingType.URBAN_DICTIONARY,
                                             headers=headers, params=querystring)
        definition_list = response.json.get('list') if response.json else json.loads(response.content).get('list')
        if len(definition_list) == 0:
            await send_embed(f"The term \"{term}\" has no definitions.", self.channel)
            return
        embed = make_urban_embed(definition_list[0], 1, len(definition_list))
        view = get_pagination_views(page=1, page_count=len(definition_list),
                                    add_close_button=False) if len(definition_list) > 1 else None
        sent_message = await send_message("", self.channel, embed=embed, reply_to=self.message, view=view)

        await urban_navigation(sent_message, definition_list)

    async def handle_command_define(self):
        if await self.routine_checks_fail():
            return

        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="You need to provide the term you want to define.")
            return

        term = self.command_options_and_arguments
        url = f"https://dictionaryapi.com/api/v3/references/collegiate/json/{quote(term, safe='')}" \
              f"?key={auth.MERRIAM_API_KEY}"
        response = await web_handler.request("GET", url, CachingType.MERRIAM_DICTIONARY)
        data, response_type = \
            get_presentable_merriam_definition_data(response.json if response.json else json.loads(response.content))
        embed = make_merriam_embed(term, data, response_type)
        await send_message("", self.channel, embed=embed, reply_to=self.message)

    async def handle_command_help(self):
        target_channel = self.author if await self.routine_checks_fail(check_section_enabled=False) else self.channel
        if not self.command_options_and_arguments:
            view = get_main_help_views(UserCommandSection)
            embed = make_main_help_embed(self.guild_prefs)
            sent_message = await send_message(None, target_channel, embed=embed, reply_to=self.message, view=view)

            if sent_message is not None:
                await help_navigation(self.message, sent_message, embed, self.guild_prefs)
        else:
            embed = make_command_help_embed(self.message, self.guild_prefs)
            sent_message = await send_message(None, target_channel, embed=embed,
                                              reply_to=self.message, view=get_close_embed_view())
            close_embed = await handle_general_close_embed(sent_message=sent_message, requested_by=self.author)
            if close_embed:
                await edit_message(sent_message, "Help embed closed.", reason=f"Closed help embed for some command",
                                   view=None)
                return

    async def handle_command_server(self):
        if await self.routine_checks_fail():
            return
        if self.is_dm:
            return await send_embed("Command only available on servers.", self.channel)
        embed = make_server_info_embed(self.guild)
        sent_message = await send_message("", self.channel, embed=embed, reply_to=self.message)
        if sent_message:
            await handle_general_close_embed(sent_message=sent_message, requested_by=self.author)

    async def handle_command_user(self):
        if await self.routine_checks_fail():
            return
        if self.is_dm:
            return await send_embed("Command only available on servers.", self.channel)
        user_id, _ = get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments, self.author)
        member = self.guild.get_member(user_id)
        if not member:
            return await self.handle_incorrect_use("Please provide me with an existing member's att or ID")
        user = await discord_client.fetch_user(member.id)
        embed = make_member_info_embed(member, user)
        sent_message = await send_message("", self.channel, embed=embed, reply_to=self.message)
        if sent_message:
            await handle_general_close_embed(sent_message=sent_message, requested_by=self.author)

    async def handle_help_on_dms(self):
        if not self.command_options_and_arguments:
            view = get_main_help_views(UserCommandSection)
            embed = make_main_help_embed(GuildPrefs(0, ''))
            sent_message = await send_message(None, self.author, embed=embed, view=view)
            if sent_message is not None:
                await help_navigation(self.message, sent_message, embed, GuildPrefs(0, ''))
        else:
            embed = make_command_help_embed(self.message, GuildPrefs(0, ''))
            await send_message(None, self.author, embed=embed)
