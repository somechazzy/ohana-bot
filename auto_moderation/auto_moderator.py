import os
import re
import asyncio
from datetime import datetime, timedelta
import disnake as discord
import time
import traceback
from actions import delete_message_from_guild, send_message, \
    add_roles, send_embed
from internal.bot_logging import log, log_to_server
from globals_.clients import discord_client, firebase_client
from globals_ import constants, variables
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import build_path, get_id_from_text, backup_music_services
from models.guild import GuildPrefs


async def automod(message: discord.Message, guild_prefs: GuildPrefs):
    """
    Perform a few checks on the message, mostly related to automoderation
    :param (discord.Message) message: message to perform checks on
    :param (GuildPrefs) guild_prefs: guild preferences object the guild was sent on
    :return:
    """
    # returns skip status for commands, if true then any command in the message is skipped
    deleted = await scan_for_blacklisted_words(message, guild_prefs)
    if deleted:
        return True

    if message.channel.id in guild_prefs.single_message_channels.keys():
        deleted = await handle_single_message_channel(message, guild_prefs)
        if deleted:
            return True

    if message.channel.id in guild_prefs.gallery_channels:
        deleted = await handle_gallery_channel(message)
        if deleted:
            return True

    if message.author.id == constants.BOT_OWNER_ID:
        await do_bot_owner_things(message)

    await auto_respond(message, guild_prefs)

    return False


async def scan_for_blacklisted_words(message, guild_prefs: GuildPrefs):
    whitelisted_role = message.guild.get_role(int(guild_prefs.whitelisted_role))
    if message.channel.permissions_for(message.author).administrator:
        return
    member_highest_role = message.author.roles[-1]
    if whitelisted_role and member_highest_role >= whitelisted_role:
        return False
    content = str(message.content).lower()
    content_no_spaces = content.replace(" ", "")
    banned_words_full, banned_words_partial, banned_words_regex = get_banned_words_for(guild_prefs)
    words_used = []

    def remove_word(_word):
        while _word in words_used:
            words_used.remove(_word)

    for word in banned_words_partial:
        if word in content_no_spaces:
            words_used.append(word)

    content_list = re.split("[^A-Za-z]", content)
    for word in content_list:
        if word in banned_words_full:
            words_used.append(word)

    for regex in banned_words_regex:
        words_used_regex = re.finditer(regex, content, re.IGNORECASE)
        for word in words_used_regex:
            words_used.append(word.group())

    if len(words_used) > 0:
        for command_name in variables.commands_names:
            remove_word(command_name)

    if len(words_used) > 0:
        if not await delete_message_from_guild(message, reason=f"Saying a bad word. Word: '{words_used[0]}'"):
            await log(f"Failed at deleting banned word "
                      f"({words_used[0]}) by {message.author}. Make sure I have proper permissions.",
                      level=constants.BotLogType.BOT_WARNING_IGNORE, guild_id=message.guild.id)
        if len(words_used) == 0:
            return False
        return True
    return False


async def auto_respond(message, guild_prefs: GuildPrefs):
    if is_ar_rate_limited(message.author):
        return
    content = str(message.content).lower().strip()
    auto_responses_full, auto_responses_partial, auto_responses_startswith = get_auto_responses_for(guild_prefs)

    if content in auto_responses_full.keys():
        if auto_responses_full[content]["delete"]:
            await delete_message_from_guild(message, reason=f"Auto-response")
        response = auto_responses_full[content]["response"].replace("{member_mention}",
                                                                    f"{message.author.mention}")
        await send_message(response, message.channel)
        return False

    for trigger in auto_responses_partial.keys():
        # content_list = re.split(" ", content)
        if len(trigger) == 1:
            if trigger in content:
                if auto_responses_partial[trigger]["delete"]:
                    await delete_message_from_guild(message, reason=f"Auto-response")
                response = auto_responses_partial[trigger]["response"].replace("{member_mention}",
                                                                               f"{message.author.mention}")
                await send_message(response, message.channel)
                return False
        else:
            trigger_spaced = " " + trigger + " "
            content_spaced = " " + content + " "
            content_subbed_spaced = re.sub("[ ]+", " ", (" " + re.sub("[^A-Za-z ]", " ", content) + " "))
            if trigger_spaced in content_spaced or trigger_spaced in content_subbed_spaced:
                if auto_responses_partial[trigger]["delete"]:
                    await delete_message_from_guild(message, reason=f"Auto-response")
                response = auto_responses_partial[trigger]["response"].replace("{member_mention}",
                                                                               f"{message.author.mention}")
                await send_message(response, message.channel)
                return False

    for trigger in auto_responses_startswith.keys():
        if content.startswith(trigger):
            if auto_responses_startswith[trigger]["delete"]:
                await delete_message_from_guild(message, reason=f"Auto-response")
            response = auto_responses_startswith[trigger]["response"].replace("{member_mention}",
                                                                              f"{message.author.mention}")
            await send_message(response, message.channel)
            return False


async def handle_single_message_channel(message, guild_prefs):
    if message.channel.permissions_for(message.author).administrator:
        return
    for single_message_channel_dict in guild_prefs.single_message_channels.values():
        if single_message_channel_dict.get("channel_id") in [message.channel.id, str(message.channel.id)]:
            role_id = int(single_message_channel_dict.get("role_id"))
            role = message.guild.get_role(role_id)
            if not role:
                await log_to_server(message.guild, constants.GuildLogType.ACTION_ERROR, message=message,
                                    event=f"Cannot find role with ID {role_id}, necessary for single-text channel "
                                          f"#{message.channel}.\nSingle-text mode "
                                          f"has been disabled for that channel.")
                await GuildPrefsComponent().remove_guild_single_message_channel(message.guild, str(message.channel.id))
                return False

            if role in message.author.roles:
                if single_message_channel_dict.get("mode") == 'delete':
                    await delete_message_from_guild(message, reason=f"Single-text channel: member "
                                                                    f"already has <@&{role_id}> role.")
                    return True
            else:
                await asyncio.sleep(5)
                try:
                    if not message.channel.permissions_for(message.guild.me).manage_roles:
                        return False
                    await message.author.add_roles(role, reason=f"single-text channel role (#{message.channel})")
                    await log_to_server(message.guild, constants.GuildLogType.ASSIGNED_ROLE, message=message,
                                        role=role, member=message.author,
                                        fields=["Reason"],
                                        values=[f"Single-text channel role (#{message.channel})"])
                    return True
                except:
                    await log(f"{(traceback.format_exc())}", level=constants.BotLogType.BOT_WARNING,
                              print_to_console=False, guild_id=message.guild.id)
                    await log_to_server(message.guild, constants.GuildLogType.ACTION_ERROR, message=message,
                                        event=f"Failed at assigning role with ID {role_id} to"
                                              f" member {message.author.mention}.")
                    return False


async def handle_gallery_channel(message):
    if message.channel.permissions_for(message.author).administrator:
        return False
    if len(message.attachments) == 0:
        await delete_message_from_guild(message, reason="text-only text in gallery channel")

        await send_message(f"Sorry, {message.author.mention}. Only images are allowed in this channel :(",
                           message.channel, delete_after=6)
        return True
    return False


async def assign_autoroles(member, wait=3):
    autoroles = (await GuildPrefsComponent().get_guild_prefs(member.guild)).autoroles
    if wait:
        await asyncio.sleep(wait)
    await add_roles(member, autoroles, reason="Autorole")


def get_banned_words_for(guild_prefs):
    guild_id = guild_prefs.guild_id

    def generate_banned_words():
        banned_words_full_ = []
        banned_words_partial_ = []
        banned_words_regex_ = []
        if guild_prefs.default_banned_words_enabled:
            banned_words_full_ += constants.BLACKLISTED_WORDS_FULL
            banned_words_partial_ += constants.BLACKLISTED_WORDS_PARTIAL
        for banned_word in guild_prefs.banned_words.keys():
            if guild_prefs.banned_words[banned_word]["match"] == "full":
                banned_words_full_.append(banned_word)
            elif guild_prefs.banned_words[banned_word]["match"] == "partial":
                banned_words_partial_.append(banned_word)
            elif guild_prefs.banned_words[banned_word]["match"] == "regex":
                banned_words_regex_.append(banned_word)
        banned_words_dict = {
            "valid": True,
            "banned_words_full": banned_words_full_,
            "banned_words_partial": banned_words_partial_,
            "banned_words_regex": banned_words_regex_
        }
        variables.banned_words_cache[guild_id] = banned_words_dict

    if guild_id not in variables.banned_words_cache.keys() \
            or not variables.banned_words_cache[guild_prefs.guild_id]["valid"]:
        generate_banned_words()
    banned_words_full = variables.banned_words_cache[guild_prefs.guild_id]["banned_words_full"]
    banned_words_partial = variables.banned_words_cache[guild_prefs.guild_id]["banned_words_partial"]
    banned_words_regex = variables.banned_words_cache[guild_prefs.guild_id]["banned_words_regex"]
    return banned_words_full, banned_words_partial, banned_words_regex


def get_auto_responses_for(guild_prefs: GuildPrefs):
    guild_id = guild_prefs.guild_id

    def generate_auto_responses():
        auto_responses_full_ = {}
        auto_responses_partial_ = {}
        auto_responses_startswith_ = {}
        for auto_response in guild_prefs.auto_responses.keys():
            if guild_prefs.auto_responses[auto_response]["match"] == "full":
                auto_responses_full_[auto_response] = guild_prefs.auto_responses[auto_response]
            elif guild_prefs.auto_responses[auto_response]["match"] == "partial":
                auto_responses_partial_[auto_response] = guild_prefs.auto_responses[auto_response]
            elif guild_prefs.auto_responses[auto_response]["match"] == "startswith":
                auto_responses_startswith_[auto_response] = guild_prefs.auto_responses[auto_response]
        auto_responses_dict = {
            "valid": True,
            "auto_responses_full": auto_responses_full_,
            "auto_responses_partial": auto_responses_partial_,
            "auto_responses_startswith": auto_responses_startswith_
        }
        variables.auto_responses_cache[guild_id] = auto_responses_dict

    if guild_id not in variables.auto_responses_cache.keys() \
            or not variables.auto_responses_cache[guild_prefs.guild_id]["valid"]:
        generate_auto_responses()
    auto_responses_full = variables.auto_responses_cache[guild_prefs.guild_id]["auto_responses_full"]
    auto_responses_partial = variables.auto_responses_cache[guild_prefs.guild_id]["auto_responses_partial"]
    auto_responses_startswith = variables.auto_responses_cache[guild_prefs.guild_id]["auto_responses_startswith"]
    return auto_responses_full, auto_responses_partial, auto_responses_startswith


async def scan_and_assign_role_for_single_message_channel(channel, created_role_id):
    counter = 0
    members = []
    created_role = channel.guild.get_role(created_role_id)
    async for message in channel.history(limit=500):
        if message.author not in members:
            members.append(message.author)
    for member in members:
        if member is channel.guild.me:
            continue
        try:
            await member.add_roles(created_role, reason=f"single-text mode role for #{channel}")
        except:
            await log(traceback.format_exc(), level=constants.BotLogType.BOT_ERROR, guild_id=member.guild.id)
            await asyncio.sleep(1)
            continue
        counter += 1
        await asyncio.sleep(1)
    return counter


async def do_bot_owner_things(message: discord.Message):
    # ONLY UNCOMMENT IF YOU MANAGED TO INSTALL PSUTIL LIBRARY, WHICH REQUIRES EXTRA SOFTWARE IF YOU'RE ON WINDOWS
    # if message.content.lower().strip() == "show memory":
    #     usage = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2)
    #     await send_embed(f"Memory usage = {usage} MB", message.channel, emoji="🚀",
    #                                color=0x000000, log_message=False)
    #
    # elif message.content.lower().strip() == "show memory percent":
    #     usage = round(psutil.virtual_memory().percent, 2)
    #     await send_embed(f"Memory usage = {usage}%", message.channel, emoji="🚀",
    #                                color=0x000000, log_message=False)
    #
    # if message.content.lower().strip() == "show disk":
    #     usage = round(psutil.disk_usage(os.sep).used / 1024 ** 2, 2)
    #     await send_embed(f"Disk usage = {usage} MB", message.channel, emoji="🚀",
    #                                color=0x000000, log_message=False)
    #
    # elif message.content.lower().strip() == "show disk percent":
    #     usage = round(psutil.disk_usage(os.sep).percent, 2)
    #     await send_embed(f"Disk usage = {usage}%", message.channel, emoji="🚀",
    #                                color=0x000000, log_message=False)
    #
    # elif message.content.lower().strip() == "show cpu percent":
    #     usage = round(psutil.cpu_percent(), 2)
    #     await send_embed(f"CPU usage = {usage}%", message.channel, emoji="🚀",
    #                                color=0x000000, log_message=False)
    if message.content.lower().startswith("..guild leave"):
        guild_id = get_id_from_text(str(message.content))
        if not guild_id:
            await send_embed("Enter proper ID.", message.channel)
            return
        guild = discord_client.get_guild(guild_id)
        if not guild:
            await send_embed("Guild not found.", message.channel)
            return
        await guild.leave()
        await send_embed("Left guild.", message.channel)
    elif message.content.lower().startswith("..guild stats") or message.content.lower().startswith("..guild info"):
        message_split = message.content.lower().split('-')
        days = 3
        if len(message_split) > 1:
            option = message_split[1]
            days = re.sub('[^0-9]+', '', option)
            days = int(days) if days else 3
        guild_id = get_id_from_text(message_split[0])
        if not guild_id:
            await send_embed("Enter proper ID.", message.channel)
            return
        guild = discord_client.get_guild(guild_id)
        if not guild:
            await send_embed("Guild not found.", message.channel)
            return
        member_count = guild.member_count
        human_count = len([member for member in guild.members if not member.bot])
        bot_count = len([member for member in guild.members if member.bot])
        owner_other_guild_count =\
            len([guild_ for guild_ in discord_client.guilds
                 if guild_.owner.id == guild.owner.id and guild_.id != guild.id])
        commands_used, other_logs = await _get_count_of_logs_for_guild_over_x_days(guild_id=guild.id, days=days)
        await send_embed(
            f"**{guild}** ({guild.id})\n\n"
            f"**Member count**: {member_count}.\n"
            f"**Owned by** {guild.owner} ({guild.owner.id}).\n" +
            (f"**Bot is in** {owner_other_guild_count} other guilds they own.\n" if owner_other_guild_count else "") +
            f"**Created at** <t:{int(datetime.timestamp(guild.created_at))}:f>.\n"
            f"**Joined at** <t:{int(datetime.timestamp(guild.me.joined_at))}:f>.\n"
            f"**Human count** = {human_count}.\n"
            f"**Bot count** = {bot_count}.\n"
            f"**Bot Percentage** = {round(bot_count * 100 / member_count, 2)}%\n"
            f"**Bot admin status**: {guild.me.guild_permissions.administrator}.\n"
            f"**Commands used ({days} days)**: {commands_used}.\n"
            f"**Other logs ({days} days)**: {other_logs}.",
            message.channel, bold=False)
    elif message.content.lower().startswith("..guilds breakdown"):
        by_id = "by id" in str(message.content).lower()
        guilds_dict = {}
        for guild in discord_client.guilds:
            bot_count = len([member for member in guild.members if member.bot])
            bot_percentage = round(bot_count * 100 / guild.member_count, 2)
            bolded_percentage = "**" if bot_percentage > 50 else ""
            bolded_member_count = "**" if guild.member_count < 11 else ""
            guilds_dict[guild.id if by_id else guild.name] =\
                f"Total count = {bolded_member_count}{guild.member_count}{bolded_member_count}, " \
                f"Bots = {bolded_percentage}{bot_percentage}{bolded_percentage}%."
        list_of_message_contents_to_send = []
        message_content = ""
        for guild_key, guild_stats in guilds_dict.items():
            message_extension = f"**{guild_key}**: {guild_stats}\n"
            if len(message_content) + len(message_extension) > 1500:
                list_of_message_contents_to_send.append(f"{message_content}")
                message_content = ""
            message_content += message_extension
        list_of_message_contents_to_send.append(f"{message_content}")
        number_of_messages = len(list_of_message_contents_to_send)
        for i, message_content_to_send in enumerate(list_of_message_contents_to_send, 1):
            await send_embed(f"**Guilds** ({i}/{number_of_messages})\n\n" + message_content_to_send.strip(),
                             message.channel, bold=False)
    elif message.content.lower().startswith("..stats"):
        member_ids = []
        bot_ids = []
        channel_count = 0
        for guild in discord_client.guilds:
            for user in guild.members:
                member_ids.append(user.id)
                if user.bot:
                    bot_ids.append(user.id)
            channel_count += len(guild.channels)
        total_member_count = len(member_ids)
        total_bot_count = len(bot_ids)
        unique_user_count = len(set(member_ids))
        unique_bot_count = len(set(bot_ids))
        total_human_percentage = round((total_member_count - total_bot_count) * 100 / total_member_count, 2)
        total_bot_percentage = round(100 - total_human_percentage, 2)
        unique_human_percentage = round((unique_user_count - unique_bot_count) * 100 / unique_user_count, 2)
        unique_bot_percentage = round(100 - unique_human_percentage, 2)
        await send_embed(f"**Bot Stats**\n"
                         f"**Guild count** = {len(discord_client.guilds)}\n"
                         f"**Total channel count** = {channel_count}\n"
                         f"**Total member count** = {total_member_count}\n"
                         f"  **-of which are bots** = {total_bot_count}\n"
                         f"**Unique user count** = {unique_user_count}\n"
                         f"  **-of which are bots** = {unique_bot_count}\n"
                         f"**Total human/bot ratio** = {total_human_percentage}% humans,"
                         f" {total_bot_percentage}% bots\n"
                         f"**Unique user/bot ratio** = {unique_human_percentage}% humans,"
                         f" {unique_bot_percentage}% bots",
                         message.channel, bold=False)
    elif message.content.lower().startswith("..music backup"):
        # used for when you want to restart the bot without resetting everyone's music queue/settings
        if 'notify' in message.content.lower():
            await send_embed("Informing current users...", message.channel)
            for gms in variables.guild_music_services.values():
                if gms.voice_client and gms.voice_client.is_playing():
                    await send_embed("I am restarting soon. Don't worry, your queue "
                                     "will be restored in few seconds...", message.channel)
                    await asyncio.sleep(1)
            await send_embed("Everyone informed", message.channel)
        await backup_music_services()
        await send_embed("Backup complete", message.channel)
    elif message.content.lower().startswith("..logs"):
        date = re.findall('[0-9]+', message.content)
        if not date:
            date = datetime.utcnow().strftime('%Y%m%d')
        else:
            date = date[0]
        path = build_path(('logs', 'logs', f'{date}.txt'))
        if not os.path.isfile(path):
            return await send_embed(f"date \"{date}\" logs not found", message.channel)
        await message.channel.send(f"Logs for {date}", files=[discord.File(path, filename=f'{date}.txt'), ])


async def _get_count_of_logs_for_guild_over_x_days(guild_id, days):
    days_back = 0
    command_logs = []
    other_logs = []
    for _ in range(days):
        day = (datetime.today() - timedelta(days=days_back)).strftime("%Y%m%d")
        all_logs = (await firebase_client.get_logs_for_server(guild_id=guild_id, day_yyyymmdd=day)).val()
        if all_logs:
            for log_ in all_logs.values():
                if log_.get("level") in [constants.BotLogType.USER_COMMAND_RECEIVED,
                                         constants.BotLogType.ADMIN_COMMAND_RECEIVED]:
                    command_logs.append(log_)
                else:
                    other_logs.append(log_)
        days_back += 1
    return len(command_logs), len(other_logs)


def is_ar_rate_limited(user):
    current_time = int(time.time())
    if user.id in variables.user_ar_trigger:
        if variables.user_ar_trigger[user.id] + constants.AR_LIMIT_SECONDS > current_time:
            return True

    variables.user_ar_trigger[user.id] = current_time
    return False
