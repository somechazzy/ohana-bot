import re

from globals_ import variables
from globals_.clients import discord_client
from globals_.constants import CommandType, UserCommandSection, AdminCommandSection, MusicCommandSection, \
    LETTER_EMOTES_COMMANDS, USER_COMMAND_SECTION_TOP_COMMANDS, ADMIN_COMMAND_SECTION_TOP_COMMANDS, \
    LETTER_EMOTES_ADMIN_COMMANDS, LETTER_EMOTES_MUSIC_COMMANDS, MUSIC_COMMAND_SECTION_TOP_COMMANDS, BOT_NAME, \
    BOT_INVITE, HelpListingVisibility, HELP_EMBED_THUMBNAIL, BOT_COLOR
import disnake as discord


def make_main_help_embed(guild_prefs):
    return make_main_help_embed_for(guild_prefs, CommandType.USER)


def make_main_admin_help_embed(guild_prefs):
    return make_main_help_embed_for(guild_prefs, CommandType.ADMIN)


def make_main_music_help_embed(guild_prefs):
    return make_main_help_embed_for(guild_prefs, CommandType.MUSIC)


def make_main_help_embed_for(guild_prefs, command_type):
    """
    Makes the main help embed for any of the command types (user, admin, music).
    :param (models.guild.GuildPrefs) guild_prefs:
    :param (str) command_type: type of commands
    :return: discord.Embed
    """
    prefix = guild_prefs.prefix
    admin_prefix = guild_prefs.admin_prefix
    music_prefix = guild_prefs.music_prefix
    context_prefix = guild_prefs.prefix if command_type == CommandType.USER \
        else guild_prefs.admin_prefix if command_type == CommandType.ADMIN \
        else guild_prefs.music_prefix if command_type == CommandType.MUSIC \
        else None
    if not context_prefix:
        return None
    bot_avatar = discord_client.user.avatar.with_size(32).url
    description = f"**Viewing {command_type.capitalize()} help embed.**\n‎\n" \
                  f"• **User** commands prefix: `{prefix}` -" \
                  f" use `{prefix}help` to see all commands.\n"\
                  f"• **Music** commands prefix: `{music_prefix}` -" \
                  f" use `{music_prefix}help` to see all commands.\n" \
                  f"• **Admin** commands prefix: `{admin_prefix}` -" \
                  f" use `{admin_prefix}help` to see all commands.\n‎‎‎"
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=description)
    if HELP_EMBED_THUMBNAIL:
        embed.set_thumbnail(url=HELP_EMBED_THUMBNAIL)
    embed.set_author(name=f"{BOT_NAME} Help")
    embed.set_footer(text=f"Use {context_prefix}help CommandName "
                          f"to show help on a specific command.", icon_url=f"{bot_avatar}")

    sections_list = ""
    command_sections = UserCommandSection.as_list() if command_type == CommandType.USER \
        else AdminCommandSection.as_list() if command_type == CommandType.ADMIN \
        else MusicCommandSection.as_list() if command_type == CommandType.MUSIC \
        else []
    for command_section in command_sections:
        if command_type == CommandType.USER:
            emoji = LETTER_EMOTES_COMMANDS[str(command_section).lower()[0]]
            top_commands = USER_COMMAND_SECTION_TOP_COMMANDS[command_section]
        elif command_type == CommandType.ADMIN:
            emoji = LETTER_EMOTES_ADMIN_COMMANDS[str(command_section).lower()[0]]
            top_commands = ADMIN_COMMAND_SECTION_TOP_COMMANDS[command_section]
        elif command_type == CommandType.MUSIC:
            emoji = LETTER_EMOTES_MUSIC_COMMANDS[str(command_section).lower()[0]]
            top_commands = MUSIC_COMMAND_SECTION_TOP_COMMANDS[command_section]
        else:
            return
        sections_list += f"{emoji} **{command_section}**: "
        top_commands_string = '`' + '` | `'.join(top_commands) + '` ...\n'
        sections_list += top_commands_string

    commands_field_name = f"{command_type.lower().capitalize()} Commands"
    embed.add_field(name=commands_field_name, value=f"Below listed are command sections."
                                                    f" Select one from the list to show all commands in it.\n"
                                                    f"{sections_list}\n‎",
                    inline=False)
    embed.add_field(name=f"Invite {BOT_NAME} to your server", value=f"{BOT_INVITE}\n",
                    inline=False)

    return embed


def make_section_help_embed(section, guild_prefs):
    return make_section_help_embed_for(section, guild_prefs, CommandType.USER)


def make_section_admin_help_embed(section, guild_prefs):
    return make_section_help_embed_for(section, guild_prefs, CommandType.ADMIN)


def make_section_music_help_embed(section, guild_prefs):
    return make_section_help_embed_for(section, guild_prefs, CommandType.MUSIC)


def make_section_help_embed_for(section, guild_prefs, command_type):
    """
    Makes the section help embed, listing available commands in that section with a short description
    :param (str) section: section/module of a command type (e.g. Queue commands of type Music)
    :param (models.guild.GuildPrefs) guild_prefs:
    :param (str) command_type: type of commands
    :return: discord.Embed or None
    """
    context_prefix = guild_prefs.prefix if command_type == CommandType.USER \
        else guild_prefs.admin_prefix if command_type == CommandType.ADMIN \
        else guild_prefs.music_prefix if command_type == CommandType.MUSIC \
        else None
    if not context_prefix:
        return None
    bot_avatar = discord_client.user.avatar.with_size(32).url
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"Showing full command list for {section} section.")
    if HELP_EMBED_THUMBNAIL:
        embed.set_thumbnail(url=HELP_EMBED_THUMBNAIL)
    embed.set_author(name=f"{command_type.lower().capitalize()} Command List: {section}")
    embed.set_footer(text=f"Use {context_prefix}help [command] for more details on that command.",
                     icon_url=bot_avatar)

    commands_dicts = variables.commands_dict.values() if command_type == CommandType.USER \
        else variables.admin_commands_dict.values() if command_type == CommandType.ADMIN \
        else variables.music_commands_dict.values() if command_type == CommandType.MUSIC \
        else None

    for command in commands_dicts:
        if command.section != section or command.show_on_listing == HelpListingVisibility.HIDE:
            continue
        embed.add_field(name=f"{context_prefix}{command.name}",
                        value=f"{command.short_description}.\n", inline=False)

    return embed


def make_command_help_embed(message, guild_prefs, assumed_command=None):
    return make_command_help_embed_for(message, guild_prefs, CommandType.USER, assumed_command)


def make_command_admin_help_embed(message, guild_prefs, assumed_command=None):
    return make_command_help_embed_for(message, guild_prefs, CommandType.ADMIN, assumed_command)


def make_command_music_help_embed(message, guild_prefs, assumed_command=None):
    return make_command_help_embed_for(message, guild_prefs, CommandType.MUSIC, assumed_command)


def make_command_help_embed_for(message, guild_prefs, command_type, assumed_command=None):
    """
    Makes help embed for a particular command
    :param (discord.Message) message: message requesting the help embed, used for obtaining the requested command
    :param (models.guild.GuildPrefs) guild_prefs:
    :param (str) command_type: type of commands
    :param (str) assumed_command: if not passed, then the assumed command is taken from the message
    :return: discord.Embed or None
    """
    prefix = guild_prefs.prefix
    admin_prefix = guild_prefs.admin_prefix
    music_prefix = guild_prefs.music_prefix
    context_prefix = guild_prefs.prefix if command_type == CommandType.USER \
        else guild_prefs.admin_prefix if command_type == CommandType.ADMIN \
        else guild_prefs.music_prefix if command_type == CommandType.MUSIC \
        else None
    if not context_prefix:
        return None
    bot_avatar = discord_client.user.avatar.with_size(32).url
    if assumed_command is None:
        message_content = re.sub("[ ]+", " ", message.content.strip()).lower()
        message_split = message_content.split(" ")
        assumed_command = message_split[1].strip()

    command = None
    commands_dicts = variables.commands_dict.values() if command_type == CommandType.USER \
        else variables.admin_commands_dict.values() if command_type == CommandType.ADMIN \
        else variables.music_commands_dict.values() if command_type == CommandType.MUSIC \
        else None
    for loop_command in commands_dicts:
        if loop_command.name.lower() == assumed_command:
            command = loop_command
            break
        for alias in [i.lower() for i in loop_command.aliases]:
            if alias == assumed_command:
                command = loop_command
                break
        if command:
            break
    if command is None:
        normal_help_description = f"❌  Command not found. Use `{context_prefix}help`" \
                                  f" to check available commands."
        admin_help_description = f"{normal_help_description}\n" \
                                 f"If you meant to display help for user commands, use `{prefix}help` instead."
        embed = discord.Embed(colour=discord.Colour.dark_red(),
                              description=normal_help_description if command_type != CommandType.ADMIN
                              else admin_help_description)
        return embed

    aliases = f"`{context_prefix}{command.name}` "
    for alias in command.aliases:
        aliases += f"`{context_prefix}{alias}` "

    member_perms = f""
    for member_perm in command.member_perms:
        member_perms += f"`{member_perm}` - "
    if member_perms.strip().endswith("-"):
        member_perms = member_perms.strip()[:len(member_perms) - 2]
    member_perms = member_perms.strip()
    bot_perms = f""
    for bot_perm in command.bot_perms:
        bot_perms += f"`{bot_perm}` - "
    if bot_perms.strip().endswith("-"):
        bot_perms = bot_perms.strip()[:len(bot_perms) - 2]
    bot_perms = bot_perms.strip()

    usage_examples = ""
    for usage_example in command.usage_examples:
        usage_example = usage_example \
            .replace("[prefix]", prefix) \
            .replace("[admin_prefix]", admin_prefix) \
            .replace("[music_prefix]", music_prefix)
        usage_examples += f"`{usage_example}`\n"

    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"Aliases: {aliases.strip()}.")
    if HELP_EMBED_THUMBNAIL:
        embed.set_thumbnail(url=HELP_EMBED_THUMBNAIL)
    embed.set_author(name=f"{command_type.lower().capitalize()} Command: {context_prefix}{command.name}")
    embed.set_footer(text=f"Section: {command.section}.", icon_url=bot_avatar)

    if command.sub_commands:
        sub_commands = '`' + '`, `'.join(command.sub_commands) + '`'
        embed.add_field(name="Sub-commands", value=f"{sub_commands}.", inline=False)
    if command.description:
        description = command.description \
            .replace("[prefix]", prefix) \
            .replace("[admin_prefix]", admin_prefix) \
            .replace("[music_prefix]", music_prefix)
        embed.add_field(name="Description", value=f"{description}.", inline=False)
    if command.further_details:
        notes = command.further_details \
            .replace("[prefix]", prefix) \
            .replace("[admin_prefix]", admin_prefix) \
            .replace("[music_prefix]", music_prefix)
        embed.add_field(name="Notes", value=f"{notes}.", inline=False)
    if usage_examples:
        embed.add_field(name="Usage", value=f"{usage_examples}", inline=False)
    if member_perms or bot_perms:
        embed.add_field(name="Permissions Required", value="" +
                                                           (f"**Member**: {member_perms}\n" if member_perms else "") +
                                                           (f"**Bot**: {bot_perms}" if bot_perms else ""))
    return embed
