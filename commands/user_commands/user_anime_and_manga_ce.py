import re
import traceback
from commands.user_command_executor import UserCommandExecutor
from globals_.constants import UserCommandSection, BotLogType
from helpers import link_mal_username, link_al_username, get_mal_username, \
    get_al_username, al_username_exists_for_user, mal_username_exists_for_user, get_mal_username_mapping, \
    get_al_username_mapping, unlink_mal_username, unlink_al_username, ensure_mal_exists, \
    get_id_from_text_if_exists_otherwise_get_author_id, ensure_anilist_exists
from embed_factory import make_mal_profile_embed, make_anilist_profile_embed
from user_interactions import mal_profile_navigation, anilist_profile_navigation, mal_anime_search_navigation, \
    mal_manga_search_navigation
from web_parsers.anilist.anilist_api_handler import get_anilist_profile, get_anilist_lists
from internal.bot_logging import log
from actions import edit_embed, send_embed, send_message
from web_parsers.mal.mal_list_handler import get_mal_anime_list_for_user, get_mal_manga_list_for_user
from web_parsers.mal.mal_profile_parser import get_mal_profile
from web_parsers.mal.mal_search_parser import get_mal_anime_search_results, get_mal_manga_search_results


class AnimeAndMangaUserCommandExecutor(UserCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)
        self.discord_id, self.not_author, self.sent_message, self.query = None, None, None, None

    async def check_for_section_enabled(self):
        if self.is_dm:
            return True
        if not self.guild_prefs.mal_al_commands_enabled:
            if int(self.guild_prefs.spam_channel) == self.channel.id or \
                    self.channel.id in self.guild_prefs.anime_channels:
                return True
            if self.guild_prefs.anime_channels:
                anime_channels = self.guild_prefs.anime_channels.copy()
                if self.guild_prefs.spam_channel:
                    anime_channels.append(self.guild_prefs.spam_channel)
                channels = '<#' + '> | <#'.join([str(i) for i in anime_channels]) + '>'
                spam_message = f" outside the designated Anime/Manga " \
                               f"channel(s) {channels}."
            elif self.guild_prefs.spam_channel:
                spam_message = f" outside the designated spam " \
                               f"channel <#{self.guild_prefs.spam_channel}>."
            else:
                spam_message = "."
            await send_embed(f"Sorry, but an admin has disabled {UserCommandSection.ANIME_AND_MANGA} "
                             f"commands{spam_message}", self.channel, emoji='💔', color=0xFF522D, reply_to=self.message)
            return False
        return True

    async def handle_command_linkmal(self):
        if await self.routine_checks_fail(check_section_enabled=False):
            return

        already_linked = mal_username_exists_for_user(self.author.id)
        if not self.command_options_and_arguments:
            if not already_linked:
                await self.handle_incorrect_use(feedback="You need to provide me with your"
                                                         " MyAnimeList username for me to link it.")
                return
            else:
                username = get_mal_username_mapping(self.author.id).username
        else:
            username = self.command_options_and_arguments_fixed.split(" ")[0]
            username = re.sub('[:/%]', '', username).strip()
            if not username:
                await self.handle_incorrect_use(feedback="You need to provide me with your"
                                                         " MyAnimeList username for me to link it.")
                return
            profile_response = await ensure_mal_exists(username)
            if not profile_response == 200:
                four_oh_four = profile_response == 404
                await log(
                    f"User {self.author} attempted to assign their MAL username to '{username}' but was met with a "
                    f"{profile_response}.", level=BotLogType.MEMBER_INFO,
                    log_to_discord=False if four_oh_four else True, ping_me=False if four_oh_four else True,
                    guild_id=self.guild.id if self.guild else None)
                reply = f"Username {username} doesn't exist." if four_oh_four else "Cannot connect to " \
                                                                                   "MAL at the moment :("
                await send_embed(reply, self.channel, emoji='❗', color=0xFF522D,
                                 reply_to=self.message)
                return

        success, feedback_message = await link_mal_username(self.author, username)
        if success:
            await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                             emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log(
                f"A change has occurred on {self.author}/{self.author.id}'s MAL. Message: \"{feedback_message}\"",
                level=BotLogType.MEMBER_INFO, log_to_db=True, log_to_discord=False,
                guild_id=self.guild.id if self.guild else None)
        else:
            await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                             reply_to=self.message)

    async def handle_command_getmal(self):
        if await self.routine_checks_fail():
            return

        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        if not not_author and self.command_options_and_arguments:
            username = self.command_options_and_arguments_fixed.split(" ")[0]
            username = re.sub('[:/%]', '', username).strip()
            feedback_message = "Unknown error happened."
        else:
            username, feedback_message = get_mal_username(discord_id)
        if username:

            sent_message = await send_message(f"Fetching {username}'s profile, "
                                              f"please wait...",
                                              self.channel, reply_to=self.message)
            if sent_message is None:
                return
            try:
                profile_info = await get_mal_profile(username)
            except:
                await edit_embed(f"There was a problem fetching the profile."
                                 f" We've been notified of this and we'll investigate asap!",
                                 sent_message, emoji='❔', color=0xffbf52)
                await log(f"MAL profile error for username {username} (ID:{discord_id})\n"
                          f"{traceback.format_exc()}", level=BotLogType.BOT_WARNING, ping_me=True,
                          guild_id=self.guild.id if self.guild else None)
                return
            profile_status_code = profile_info.get("status_code")
            if profile_status_code != 200:
                if profile_status_code == 404:
                    await edit_embed(f"Profile returned a 404 page. Please make sure username"
                                     f" '{username}' exists.", sent_message, emoji='❗', color=0xFF522D)
                else:
                    await edit_embed(f"Received a {profile_status_code} response. Please try again or "
                                     f"message the devs about it!", sent_message, emoji='❗', color=0xFF522D)
                    await log(f"Status code {profile_status_code} while getting MAL profile '{username}'. "
                              f"User ID: {discord_id}.", level=BotLogType.BOT_WARNING, ping_me=True,
                              guild_id=self.guild.id if self.guild else None)
                return
            await log(f"Fetched MAL profile of {username} as requested by {self.author}.",
                      level=BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False,
                      guild_id=self.guild.id if self.guild else None)
            profile_embed = make_mal_profile_embed(profile_info, reacting_unlocked=False)
            try:
                anime_list = await get_mal_anime_list_for_user(username)
                manga_list = await get_mal_manga_list_for_user(username)
            except:
                await edit_embed(f"There was a problem fetching anime and manga lists. "
                                 f" We've been notified of this and we'll investigate asap!",
                                 sent_message, emoji='❔', color=0xffbf52)
                await log(f"Anime/Manga MAL lists error for username {username} (ID:{discord_id})\n"
                          f"{(traceback.format_exc())}", level=BotLogType.BOT_WARNING, ping_me=True,
                          guild_id=self.guild.id if self.guild else None)
                return
            await mal_profile_navigation(self.message, sent_message, profile_embed,
                                         profile_info, anime_list, manga_list)
        else:
            reply = feedback_message.replace("[prefix]", self.prefix)
            if not_author:
                reply = "Requested user doesn't have their MAL linked."
            await send_embed(reply, self.channel, emoji='❗', color=0xFF522D,
                             reply_to=self.message)

    async def handle_command_linkal(self):
        if await self.routine_checks_fail(check_section_enabled=False):
            return

        already_linked = al_username_exists_for_user(self.author.id)
        if not self.command_options_and_arguments:
            if not already_linked:
                await self.handle_incorrect_use(feedback="You need to provide me with your"
                                                         " AniList username for me to link it.")
                return
            else:
                username = get_al_username_mapping(self.author.id).username
        else:
            username = self.command_options_and_arguments_fixed.split(" ")[0]
            username = re.sub('[:/%]', '', username).strip()
            if not username:
                await self.handle_incorrect_use(feedback="You need to provide me with your"
                                                         " AniList username for me to link it.")
                return
            profile_response = await ensure_anilist_exists(username)
            if not profile_response == 200:
                four_oh_four = profile_response == 404
                await log(
                    f"User {self.author} attempted to assign their Anilist username to '{username}' but was met with a "
                    f"{profile_response}.", level=BotLogType.MEMBER_INFO,
                    log_to_discord=False if four_oh_four else True, ping_me=False if four_oh_four else True,
                    guild_id=self.guild.id if self.guild else None)
                reply = f"Username {username} doesn't exist." if four_oh_four else "Cannot connect to " \
                                                                                   "Anilist at the moment :("
                await send_embed(reply, self.channel, emoji='❗', color=0xFF522D,
                                 reply_to=self.message)
                return

        success, feedback_message = await link_al_username(self.author, username)
        if success:
            await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                             emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log(f"A change has occurred on {self.author}/{self.author.id}'s AL. Message: \"{feedback_message}\"",
                      level=BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False,
                      guild_id=self.guild.id if self.guild else None)
        else:
            await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                             reply_to=self.message)

    async def handle_command_getal(self):
        if await self.routine_checks_fail():
            return

        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        if not not_author and self.command_options_and_arguments:
            username = self.command_options_and_arguments_fixed.split(" ")[0]
            username = re.sub('[:/%]', '', username).strip()
            feedback_message = "Unknown error happened."
        else:
            username, feedback_message = get_al_username(discord_id)
        if username:

            sent_message = await send_message(f"Fetching {username}'s profile, "
                                              f"please wait...",
                                              self.channel, reply_to=self.message)
            if sent_message is None:
                return
            try:
                profile_info = await get_anilist_profile(username)
            except:
                await edit_embed(f"There was a problem fetching the profile."
                                 f" We've been notified of this and we'll investigate asap!",
                                 sent_message, emoji='❔', color=0xffbf52)
                await log(f"AL profile error for username {username} (ID:{discord_id})\n"
                          f"{traceback.format_exc()}", level=BotLogType.BOT_WARNING, ping_me=True,
                          guild_id=self.guild.id if self.guild else None)
                return
            profile_status_code = profile_info.status
            if profile_status_code != 200:
                if profile_status_code == 404:
                    await edit_embed(f"Profile returned a 404 page. Please make sure username"
                                     f" '{username}' exists.", sent_message, emoji='❗', color=0xFF522D)
                else:
                    await edit_embed(f"Received a {profile_status_code} response. Please try again or "
                                     f"message the devs about it!", sent_message, emoji='❗', color=0xFF522D)
                    await log(f"Status code {profile_status_code} while getting AL profile '{username}'. "
                              f"User ID: {discord_id}.", level=BotLogType.BOT_WARNING, ping_me=True,
                              guild_id=self.guild.id if self.guild else None)
                return
            await log(f"Fetched Anilist profile of {username} as requested by {self.author}.",
                      level=BotLogType.MEMBER_INFO, log_to_db=False, log_to_discord=False,
                      guild_id=self.guild.id if self.guild else None)
            profile_embed = make_anilist_profile_embed(profile_info)
            try:
                anime_list, manga_list, scoring_system = await get_anilist_lists(username)
            except:
                await edit_embed(f"There was a problem fetching anime and manga lists. "
                                 f" We've been notified of this and we'll investigate asap!",
                                 sent_message, emoji='❔', color=0xffbf52)
                await log(f"Anime/Manga AL lists error for username {username} (ID:{discord_id})\n"
                          f"{(traceback.format_exc())}", level=BotLogType.BOT_WARNING, ping_me=True,
                          guild_id=self.guild.id if self.guild else None)
                return
            await anilist_profile_navigation(self.message, sent_message, profile_embed,
                                             profile_info, anime_list, manga_list, scoring_system)
        else:
            reply = feedback_message.replace("[prefix]", self.prefix)
            if not_author:
                reply = "Requested user doesn't have their Anilist linked."
            await send_embed(reply, self.channel, emoji='❗', color=0xFF522D,
                             reply_to=self.message)

    async def handle_command_anime(self):
        if await self.routine_checks_fail():
            return

        if await self.search_checks_fail():
            return

        try:
            results, thumbnail = await get_mal_anime_search_results(self.query)
        except:
            await edit_embed(f"There was a problem grabbing results :( "
                             f"We've been notified of this and will get it fixed ASAP.",
                             self.sent_message, emoji='❔', color=0xffbf52)
            await log(f"{(traceback.format_exc())}", level=BotLogType.BOT_WARNING, ping_me=True,
                      guild_id=self.guild.id if self.guild else None)
            return
        await mal_anime_search_navigation(self.message, self.sent_message, self.discord_id,
                                          self.not_author, self.query, results, thumbnail, self.prefix)

    async def handle_command_manga(self):
        if await self.routine_checks_fail():
            return

        if await self.search_checks_fail():
            return

        try:
            results, thumbnail = await get_mal_manga_search_results(self.query)
        except:
            await edit_embed(f"There was a problem grabbing results :( "
                             f"We've been notified of this and will get it fixed ASAP.",
                             self.sent_message, emoji='❔', color=0xffbf52)
            await log(f"{(traceback.format_exc())}", level=BotLogType.BOT_WARNING, ping_me=True,
                      guild_id=self.guild.id if self.guild else None)
            return
        await mal_manga_search_navigation(self.message, self.sent_message, self.discord_id,
                                          self.not_author, self.query, results, thumbnail, self.prefix)

    async def handle_command_unlinkmal(self):
        if await self.routine_checks_fail(check_section_enabled=False):
            return

        success, feedback_message = await unlink_mal_username(self.author.id)
        await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                         emoji='✅' if success else '❌', color=0x0AAC00 if success else 0xFF522D,
                         reply_to=self.message)

    async def handle_command_unlinkal(self):
        if await self.routine_checks_fail(check_section_enabled=False):
            return

        success, feedback_message = await unlink_al_username(self.author.id)
        await send_embed(feedback_message.replace("[prefix]", self.prefix), self.channel,
                         emoji='✅' if success else '❌', color=0x0AAC00 if success else 0xFF522D,
                         reply_to=self.message)

    async def search_checks_fail(self):
        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="Provide a query to search for.")
            return True

        self.discord_id, self.not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(self.command_options_and_arguments_fixed, self.author)
        if self.not_author:
            self.query = self.command_options_and_arguments_fixed.split(' ', 1)[1].strip()
        else:
            self.query = self.command_options_and_arguments_fixed

        self.sent_message = await send_message(f"Grabbing results for \"{self.query}\","
                                               f" please wait...",
                                               self.channel, reply_to=self.message)
        if not self.sent_message:
            return True

        return False
