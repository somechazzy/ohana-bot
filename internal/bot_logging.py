import io
import traceback
import disnake as discord
import pytz
from globals_.clients import discord_client, firebase_client
from models.guild import GuildPrefs
from globals_ import constants, variables
from datetime import datetime
from embed_factory import make_log_embed, make_bot_log_embed
from helpers.string_manipulation import build_path
from pathlib import Path


async def enable_logs():
    try:
        if not variables.logging_directory:
            initiate_logging_directory()
    except Exception as e:
        await log(f"{e}: {traceback.format_exc()}")
    await log("######### Started log_message #########")


def initiate_logging_directory():
    directory = "logs"
    variables.logging_directory = directory
    Path(build_path(["logs", directory])).mkdir(parents=True, exist_ok=True)


async def log(message, level=constants.BotLogType.GENERAL, print_to_console=True, log_to_discord=True,
              ping_me=False, log_to_db=True, guild_id=None):
    """
    Logs to console, Discord, Firebase DB and/or a local log file.
    :param (str) message: log message
    :param (str) level: level/type of log
    :param (bool) print_to_console: whether or not to print log to console
    :param (bool) log_to_discord: whether or not to log to discord
    :param (bool) ping_me: whether or not to ping the bot owner for this log
    :param (bool) log_to_db: whether or not to log to database
    :param (int or None) guild_id: guild ID this log is related to (appears on discord log message as a separate field)
    :return:
    """
    now = datetime.now(pytz.timezone(constants.MY_TIMEZONE))
    time_string = now.strftime('%Y-%m-%d, %H:%M:%S')
    time_numeral = now.strftime("%Y%m%d%H%M%S")
    day_numeral = now.strftime("%Y%m%d")

    # Console
    if print_to_console:
        print(f"{Colors.FG.blue if not level == constants.BotLogType.BOT_ERROR else Colors.FG.red}"
              f"{time_string}{Colors.reset}"
              f" - {level} - {message}")
    # Discord
    if log_to_discord:
        ping_me = True if level == constants.BotLogType.BOT_ERROR or level == constants.BotLogType.BOT_WARNING \
            else ping_me
        log_channel = discord_client.get_channel(constants.DISCORD_LOGGING_CHANNEL_ID)
        if len(message) > 4000:
            buf = io.BytesIO(str.encode(f"{time_string} - {level}"
                                        f":\n{message}"))
            await log_channel.send("<@218515152327278603>" if ping_me else "Log text:",
                                   files=[discord.File(buf, filename='log_message.txt'), ])
        else:
            embed = make_bot_log_embed(message, level, guild_id)
            await log_channel.send(content="" if not ping_me else "<@218515152327278603>", embed=embed)
    # DB
    if log_to_db:
        log_details = {
            "level": level,
            "timestamp_numeral": time_numeral,
            "timestamp": time_string,
            "text": message,
            "full_log": f"{time_string} - {level} - {message}"
        }
        await firebase_client.log_to_db(log_details, now, time_numeral, guild_id)
    # File
    if not variables.logging_directory:
        initiate_logging_directory()
    try:
        with open(build_path(['logs', str(variables.logging_directory), f'{day_numeral}.txt']),
                  'a+', encoding='utf-8') as logging_file:
            logging_file.write(f"{time_string} - {level} - {message}\n")
    except Exception as e:
        await log(f"{e}: {traceback.format_exc()}")


class Colors:
    """
    copied from some stackoverflow answer, forgot to link it
    Colors class:
    Reset all colors with colors.reset
    Two subclasses fg for foreground and bg for background.
    Use as colors.subclass.color_name.
    i.e. colors.fg.red or colors.bg.green
    Also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    """
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class FG:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        light_red = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    class BG:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'


# This logs events related to your bot to the server's logs channel, if set
async def log_to_server(guild: discord.Guild, event_type: constants.GuildLogType, event=None, member=None,
                        message=None, role=None, roles=None, roles_removed=None, fields=None, values=None):
    """
    Logs events related to your bot in a server if the server had set an update channel
    :param (discord.Guild) guild: guild this log is related to and will be logged to
    :param (str) event_type: type of event (GuildLogType)
    :param (str or None) event: text to add to log message
    :param (discord.Member or None) member: member this log is related to
    :param (discord.Message or None) message: message this log is related to
    :param (discord.Role or None) role: role this log is related to
    :param (list of discord.Role or None) roles: roles (added) this log is related to
    :param (list of discord.Role or None) roles_removed: roles (removed) this log is related to
    :param (list of str or None) fields: iterable of fields to appear in the log embed
    :param (list of str or None) values: values of fields passed, must be the same number of fields passed
    (fields are mapped to values in order)
    :return:
    """
    if guild.id not in variables.guilds_prefs:
        return
    guilds_prefs: GuildPrefs = variables.guilds_prefs[guild.id]
    logs_channel: discord.TextChannel = guild.get_channel(int(guilds_prefs.logs_channel))
    if not logs_channel:
        return
    if not logs_channel.permissions_for(guild.me).embed_links or \
            not logs_channel.permissions_for(guild.me).send_messages:
        return
    if values is None:
        values = []
    if fields is None:
        fields = []
    guild_avatar = guild.icon.with_size(32).url if guild.icon else None

    if event_type is constants.GuildLogType.GENERAL:
        author_name = f"{guild.me}" if member is None else f"{member}"
        author_icon = f"{guild.me.avatar.with_size(32).url}" if member is None\
            else f"{member.avatar.with_size(32).url}" if member.avatar\
            else None
        color_hex = 0xA8A8A8
        footer_text = f"ID: {member.id}" if member is not None else None
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.MEMBER_JOINED:
        event = ("Member" if not member.bot else "Bot") + " has joined the server."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0x156F3F
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.MEMBER_LEFT:
        event = "Member has left the server."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xA73939
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type in [constants.GuildLogType.ASSIGNED_ROLE, constants.GuildLogType.UNASSIGNED_ROLE]:
        action = 'given' if event_type is constants.GuildLogType.ASSIGNED_ROLE else 'removed from'
        event = f"{member.mention} was {action} the {role.mention} role."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xAC7731
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.ASSIGNED_ROLES:
        roles_mentions = []
        for role in roles:
            roles_mentions.append(str(role.mention))
        roles_mentions_string = ", ".join(roles_mentions)
        event = f"{member.mention} was given the following roles: {roles_mentions_string}"
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xAC7731
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.EDITED_ROLES:
        roles_string_list = [str(role.mention) for role in roles]
        roles_string = ", ".join(roles_string_list)
        roles_removed_string_list = [str(role.mention) for role in roles_removed]
        roles_removed_string = ", ".join(roles_removed_string_list)
        event = f"{member.mention} was:" + \
                (f"\nGiven the following roles: {roles_string}. " if roles else "") +\
                (f"\nRemoved from the following roles: {roles_removed_string}. " if roles_removed else "")
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xAC7731
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.CREATED_ROLE:
        event = f"Role `{role}` was created."
        author_name = f"{role}"
        author_icon = guild_avatar
        color_hex = 0xAC7731
        footer_text = f"ID: {role.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.KICKED_MEMBER:
        event = f"Member `{member}` was kicked."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xA73939
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.BANNED_MEMBER:
        event = f"Member `{member}` was banned."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0xA73939
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.MUTED_MEMBER:
        event = f"Member `{member}` was muted - on timeout."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0x9C5D5D
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.UNMUTED_MEMBER:
        event = f"Member `{member}` was unmuted - timeout lifted."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0x5D9C66
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.DELETED_MESSAGE:
        event = f"Message by `{message.author}` was deleted."
        author_name = f"{message.author}"
        author_icon = f"{message.author.avatar.with_size(32).url}" if message.author.avatar else None
        color_hex = 0x9C5D5D
        footer_text = f"UID: {message.author.id}"
        fields.append("Channel")
        values.append(f"<#{message.channel.id}>")
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is constants.GuildLogType.PERM_ERROR:
        author_name = f"Permission Error"
        author_icon = f"{guild.me.avatar.with_size(32).url}"
        color_hex = 0x9C5D5D
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    elif event_type is constants.GuildLogType.ACTION_ERROR:
        author_name = f"Action Failed"
        author_icon = f"{guild.me.avatar.with_size(32).url}"
        color_hex = 0x9C5D5D
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    elif event_type is constants.GuildLogType.SETTING_CHANGE:
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
        color_hex = 0x5D9C66
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    else:
        await log(f"Failed at recognizing event log type '{event_type}'.", level=constants.BotLogType.BOT_ERROR,
                  guild_id=guild.id)
        return

    await logs_channel.send(" ", embed=embed)
