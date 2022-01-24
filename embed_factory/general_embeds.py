import datetime
import random
import time
from math import ceil
from urllib.parse import quote

import disnake as discord
from globals_.clients import discord_client
from models.member import MemberXP
from helpers import shorten_text_if_above_x_characters, human_format
from models.guild import GuildPrefs
from globals_ import variables
from globals_.constants import XPSettingsKey, BotLogType, MerriamDictionaryResponseType, BOT_NAME, BOT_COLOR


def make_countdown_embed(description, reason, author, _, cd_up=False, cd_duration=None):
    bot_avatar = discord_client.user.avatar.with_size(32).url
    embed = discord.Embed(colour=discord.Colour(0x2d6d46),
                          description=description)
    embed.set_thumbnail(url=f"https://i.pinimg.com/564x/e6/f6/ef/e6f6efb2d160cb0d487098077bdb967f.jpg")
    embed.set_author(name=f"Countdown for: {reason}",
                     icon_url=bot_avatar)
    embed.set_footer(text=f"Requested by {author}" +
                          (f"| {cd_duration} elapsed." if cd_up and cd_duration is not None else " "),
                     icon_url=author.avatar.with_size(32).url if author.avatar else discord.embeds.EmptyEmbed)
    return embed


def make_log_embed(event, event_type, author_name, author_icon,
                   guild_avatar, color_hex, footer_text=None, fields=None, values=None):
    if values is None:
        values = []
    if fields is None:
        fields = []
    footer_text = event_type + ((" | " + footer_text) if footer_text is not None else "")
    embed = discord.Embed(colour=discord.Colour(color_hex), description=f"{event}",
                          timestamp=datetime.datetime.utcfromtimestamp(int(time.time())))

    embed.set_author(name=f"{author_name}", icon_url=author_icon or discord.embeds.EmptyEmbed)
    embed.set_footer(text=f"{footer_text}", icon_url=guild_avatar or discord.embeds.EmptyEmbed)
    for i in range(0, len(fields)):
        if len(values) == i:
            break
        embed.add_field(name=f"{fields[i]}", value=f"{values[i]}", inline=False)

    return embed


def make_overview_embed(guild_prefs: GuildPrefs, requested_by, setup=False):
    guild: discord.Guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    author_icon_small = requested_by.avatar.with_size(32).url if requested_by.avatar else None

    description = f"Server settings overview. These settings can be changed using admin commands " \
                  f"(see `{guild_prefs.admin_prefix}help`)." \
        if not setup else "Please review these settings before saving them. " \
                          "Once you're done click the continue navigation button."
    embed = discord.Embed(colour=discord.Colour(0xa0db8c),
                          description=description)

    embed.set_author(name=f"{guild.name} - Overview" if not setup else f"{guild.name} - Setup Overview",
                     icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    embed.set_footer(text=f"Requested by {requested_by}", icon_url=author_icon_small or discord.embeds.EmptyEmbed)

    embed.add_field(name="Prefixes",
                    value=f"**User commands**: `{guild_prefs.prefix}`\n"
                          f"**Music commands**: `{guild_prefs.music_prefix}`\n"
                          f"**Admin commands**: `{guild_prefs.admin_prefix}`",
                    inline=True)

    channels_value = "• **Logs**: " + (f"<#{guild_prefs.logs_channel}>\n" if guild_prefs.logs_channel != 0 else
                                       "not set.\n")
    channels_value += "• **Spam**: " + (f"<#{guild_prefs.spam_channel}>\n" if guild_prefs.spam_channel != 0 else
                                        "not set.\n")
    embed.add_field(name="Channels", value=channels_value, inline=True)

    if len(guild_prefs.anime_channels) == 0:
        embed.add_field(name="Anime Channels", value=f"No anime channels added yet.\n"
                                                     f"See `{guild_prefs.admin_prefix}help animeChannels`", inline=True)
    else:
        value = ""
        for anime_channel in guild_prefs.anime_channels:
            value += f"• <#{anime_channel}>\n"
        embed.add_field(name="Anime Channels", value=value, inline=True)

    embed.add_field(name="Change above settings",
                    value=f"⚙ Change prefixes using `{guild_prefs.admin_prefix}p set`,"
                          f" `{guild_prefs.admin_prefix}mp set`"
                          f" and `{guild_prefs.admin_prefix}ap set`\n"
                          f"⚙ Change logs channel using `{guild_prefs.admin_prefix}logs set`\n"
                          f"⚙ Change spam channel using `{guild_prefs.admin_prefix}spam set`\n"
                          f"⚙ Manage anime channels using `{guild_prefs.admin_prefix}anime`",
                    inline=False)

    embed.add_field(name="XP Settings",
                    value=f"**To view XP settings overview**: use `{guild_prefs.admin_prefix}xpov`.",
                    inline=False)
    en = "enabled"
    dis = "disabled"
    embed.add_field(name="Commands",
                    value=f"• **Utility**: {en if guild_prefs.utility_commands_enabled else dis}.\n"
                          f"• **Anime & Manga**: {en if guild_prefs.mal_al_commands_enabled else dis}.\n"
                          f"• **Fun**: {en if guild_prefs.fun_commands_enabled else dis}.\n"
                          f"• **Moderation**: {en if guild_prefs.moderation_commands_enabled else dis}.\n"
                          f"⚙ Enable/disable sections using `{guild_prefs.admin_prefix}enable [section]` "
                          f"or `{guild_prefs.admin_prefix}disable [section]`.\n",
                    inline=True)

    if len(guild_prefs.autoroles) == 0:
        embed.add_field(name="Autoroles", value=f"No roles added yet.\n"
                                                f"Add using `{guild_prefs.admin_prefix}autoroles add [role id]`.",
                        inline=True)
    else:
        value = ""
        for autorole in guild_prefs.autoroles:
            value += f"• <@&{autorole}>.\n"
        value += f"⚙ Manage autoroles using `{guild_prefs.admin_prefix}autoroles`"
        embed.add_field(name="Autoroles", value=value, inline=False)

    embed.add_field(name="Other",
                    value="• **Whitelisted role**: " + (f"<@&{guild_prefs.whitelisted_role}>.\n"
                                                        if guild_prefs.whitelisted_role != 0 else "not set.\n") +
                          f"• **Default banned words**: {en if guild_prefs.default_banned_words_enabled else dis}.\n"
                          f"• **Gallery channels**: manage and view using `{guild_prefs.admin_prefix}gc`.\n"
                          f"• **Single-message channels**: manage and view using `{guild_prefs.admin_prefix}sm`.\n"
                          f"• **React roles**: manage and view using `{guild_prefs.admin_prefix}rr`.\n",
                    inline=False)

    if not setup:
        value = f"• **Banned words**: Total of **{len(guild_prefs.banned_words)}** words." \
                f" See `{guild_prefs.admin_prefix}words show`.\n" \
                f"• **Auto-responses**: Total of **{len(guild_prefs.auto_responses)}** auto-responses." \
                f" See `{guild_prefs.admin_prefix}ar show`.\n"
    else:
        value = f"You can add, view or remove banned words and auto-responses using commands " \
                f"`{guild_prefs.admin_prefix}bannedWords [add/show/remove/clear]` for banned words, and " \
                f"`{guild_prefs.admin_prefix}ar [add/show/remove/clear]` for auto-responses."
    embed.add_field(name="Banned Words & Auto-Responses", value=value, inline=False)
    if setup:
        embed.add_field(name="Navigation", value="○ ✅ Confirm and save\n○ ⏪ Back\n○ ❌ Exit\n", inline=False)

    return embed


def make_xp_overview_embed(guild_prefs: GuildPrefs, requested_by):
    guild: discord.Guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    author_icon_small = requested_by.avatar.with_size(32).url if requested_by.avatar else None

    xp_settings = guild_prefs.xp_settings

    appended_appended_text = " (except for XP decay) " if xp_settings[XPSettingsKey.XP_DECAY_ENABLED] else " "
    appended_text = f"**Most of these settings{appended_appended_text}are disabled by default due to" \
                    f" XP gain being disabled**." if not xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else ""

    levelup_message = shorten_text_if_above_x_characters(xp_settings[XPSettingsKey.LEVELUP_MESSAGE].
                                                         format(member_mention=requested_by.mention,
                                                                member_tag=str(requested_by),
                                                                level=int((random.random() * 10) + 1) * 5), 120)
    if xp_settings[XPSettingsKey.LEVEL_ROLES]:
        level_roles_str = ""
        for level, role_id in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            level_roles_str += f"• Level **{level}**: <@&{role_id}>\n"
    else:
        level_roles_str = "No level roles added."

    if xp_settings[XPSettingsKey.IGNORED_ROLES]:
        ignored_roles_str = "<@&" + ">, <@&".join([str(i) for i in xp_settings[XPSettingsKey.IGNORED_ROLES]]) + ">"
    else:
        ignored_roles_str = "No ignored roles."
    if xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
        ignored_channels_str = "<#" + ">, <#".join([str(i) for i in xp_settings[XPSettingsKey.IGNORED_CHANNELS]]) + ">"
    else:
        ignored_channels_str = "No ignored channels."

    embed = discord.Embed(colour=discord.Colour(0xa0db8c),
                          description=f"XP settings overview. These settings can be changed using the"
                                      f" commands shown next to them. {appended_text}")

    embed.set_author(name=f"{guild.name} - XP Overview", icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    embed.set_footer(text=f"Requested by {requested_by}", icon_url=author_icon_small or discord.embeds.EmptyEmbed)

    embed.add_field(name="XP Gain",
                    value=f"• Status: **{'enabled' if xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else 'disabled'}**\n"
                          f"• Timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]} seconds**\n"
                          f"• Minimum gain per timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_MIN]}**\n"
                          f"• Maximum gain per timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_MAX]}**\n"
                          f"• Booster Bonus: **{xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN]}%**\n"
                          f"⚙ Change these settings using `{guild_prefs.admin_prefix}xpg`",
                    inline=False)
    embed.add_field(name="Levels",
                    value=f"• Levelup message status: "
                          f"**{'enabled' if xp_settings[XPSettingsKey.LEVELUP_ENABLED] else 'disabled'}**\n"
                          f"• Levelup message channel: **{xp_settings[XPSettingsKey.LEVELUP_CHANNEL] or 'none'}**\n"
                          f"• Levelup message:\n{levelup_message}\n"
                          f"• Max level: **{xp_settings[XPSettingsKey.LEVEL_MAX] or 'none'}**\n"
                          f"⚙ Change these settings using `{guild_prefs.admin_prefix}lum` "
                          f"and `{guild_prefs.admin_prefix}luc`",
                    inline=False)
    embed.add_field(name="Level Roles",
                    value=f"{level_roles_str.strip()}\n"
                          f"⚙ Add or remove using `{guild_prefs.admin_prefix}lr`",
                    inline=False)
    embed.add_field(name="XP Decay",
                    value=f"• Status: **{'enabled' if xp_settings[XPSettingsKey.XP_DECAY_ENABLED] else 'disabled'}**\n"
                          f"• Percentage per day: **{xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]}%**\n"
                          f"• Grace period: **{xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]} days**\n"
                          f"⚙ Change these settings using `{guild_prefs.admin_prefix}xpd`",
                    inline=False)
    embed.add_field(name="Ignored Channels",
                    value=f"{ignored_channels_str}\n"
                          f"⚙ Add or remove using `{guild_prefs.admin_prefix}xpic`",
                    inline=False)
    embed.add_field(name="Ignored Roles",
                    value=f"{ignored_roles_str}\n"
                          f"⚙ Add or remove using `{guild_prefs.admin_prefix}xpir`",
                    inline=False)
    return embed


def make_urban_embed(definition_dict: dict, index, total):
    term = definition_dict.get("word")
    permalink = definition_dict.get("permalink")
    thumbs_up = definition_dict.get("thumbs_up")
    thumbs_down = definition_dict.get("thumbs_down")
    author = definition_dict.get("author")
    definition = definition_dict.get("definition")
    example = definition_dict.get("example")

    embed = discord.Embed(colour=discord.Colour(0x6ac8fd), description=f"{definition}")

    embed.set_author(name=f"{term}", url=f"{permalink}",
                     icon_url="https://is4-ssl.mzstatic.com/image/thumb/Purple111/"
                              "v4/7e/49/85/7e498571-a905-d7dc-26c5-33dcc0dc04a8/source/512x512bb.jpg")
    embed.set_footer(text=f"Definition by {author} | Page {index}/{total}")

    if example:
        embed.add_field(name="Example", value=f"{example}\n", inline=False)
    embed.add_field(name="‎‎‎", value=f"{thumbs_up} 👍 | 👎 {thumbs_down}", inline=False)

    return embed


def make_merriam_embed(term, data, response_type):
    url = f"https://www.merriam-webster.com/dictionary/{quote(term, safe='')}"
    embed = discord.Embed(colour=discord.Colour(0x6ac8fd))
    embed.set_author(name=f"{term}", url=f"{url}",
                     icon_url="https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png")

    if response_type == MerriamDictionaryResponseType.SUCCESS and len(data) > 0:
        data = data[:3]
        for entry in data:
            embed.add_field(name=entry['pos'], value='.\n'.join(entry['definitions'][:3]) + '.\n', inline=False)
    elif response_type == MerriamDictionaryResponseType.NOT_FOUND:
        embed.description = "Couldn't find a definition for the provided term. See suggestions below."
        embed.add_field(name="Suggested", value=', '.join(data[0]['suggestions']) + '\n', inline=False)
    elif len(data) == 0:
        embed.description = "No definitions found."
    else:
        embed.description = data[0]['error'] + f"\nTry checking the definition through [this link]({url})."

    return embed


def make_leaderboard_embed(members_xp, requested_by, page=1):
    prefix = variables.guilds_prefs[requested_by.guild.id].prefix
    guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    author_icon_small = requested_by.avatar.with_size(32).url if requested_by.avatar else None

    members_ids_xp_total_map = {mid: mxp.xp for mid, mxp in members_xp.items()}
    members_dicts_sorted = {k: v for k, v in sorted(members_ids_xp_total_map.items(),
                                                    key=lambda item: item[1], reverse=True)}

    ids_sorted = list(members_dicts_sorted.keys())
    requested_by_rank = ids_sorted.index(requested_by.id) + 1 if requested_by.id in ids_sorted else '-'

    page_count = ceil(len(ids_sorted) / 10)
    if not (0 <= page <= page_count):
        page = 1

    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(ids_sorted)) else len(ids_sorted)

    members_text = ""
    for i in range(starting_index, final_index):
        user = discord_client.get_user(ids_sorted[i])
        if user:
            name = f"{user}"
        else:
            name = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).member_tag
        level = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).level
        xp = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).xp
        messages = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).messages
        decayed = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).xp_decayed
        decayed_text = f" ({human_format(decayed)} decay)" if decayed > 0 else ""
        members_text += f"**{i + 1} • {name}**\n" \
                        f"‎ ‎ ‎ ‎ ‎ ‎" \
                        f"`Level: {level} |" \
                        f" XP: {human_format(xp)}{decayed_text} |" \
                        f" Messages: {human_format(messages)}`\n"

    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"Navigate using reactions or jump to a page by"
                                      f" adding the page number to the leaderboard command (e.g. `{prefix}lb 5`).\n"
                                      f" React with 🗑 to close the embed.\n")

    embed.set_author(name=f"{guild} Leaderboard", icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    embed.set_footer(text=f"{requested_by}'s rank: #{requested_by_rank}",
                     icon_url=author_icon_small or discord.embeds.EmptyEmbed)

    embed.add_field(name="‎",
                    value=f"{members_text}", inline=False)
    embed.add_field(name="‎",
                    value=f"Showing page {page}/{page_count}", inline=False)

    return embed


def make_bot_log_embed(message, level, guild_id):
    bot_avatar = discord_client.user.avatar.with_size(32).url
    if level == BotLogType.BOT_ERROR:
        color_hex = 0xFF522D
    elif level in [BotLogType.BOT_WARNING, BotLogType.BOT_WARNING_IGNORE,
                   BotLogType.PERM_ERROR, BotLogType.GUILD_ERROR, BotLogType.GUILD_LEAVE]:
        color_hex = 0xD6581A
    elif level in [BotLogType.RECEIVED_DM, BotLogType.GUILD_JOIN]:
        color_hex = 0x63BE5F
    else:
        color_hex = BOT_COLOR

    embed = discord.Embed(colour=discord.Colour(color_hex), description=f"{message}",
                          timestamp=datetime.datetime.utcfromtimestamp(int(time.time())))

    embed.set_author(name=f"{level}")
    embed.set_footer(text=f"", icon_url=f"{bot_avatar}")
    if guild_id:
        embed.add_field(name=f"Guild ID", value=guild_id, inline=False)

    return embed


def make_server_info_embed(guild: discord.Guild):
    name = guild.name
    icon = guild.icon.url if guild.icon else None
    banner = guild.banner.url if guild.banner else None
    owner = guild.owner
    category_count = len(guild.categories)
    text_channel_count = len(guild.text_channels)
    voice_channel_count = len(guild.voice_channels)
    stage_channel_count = len(guild.stage_channels)
    created_at = guild.created_at
    description = guild.description if guild.description else None
    emoji_count = len(guild.emojis)
    sticker_count = len(guild.stickers)
    member_count = guild.member_count
    booster_count = guild.premium_subscription_count
    boost_level = guild.premium_tier
    role_count = len(guild.roles) - 1

    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=description if description else discord.embeds.EmptyEmbed)
    embed.set_author(name=f"{name}", icon_url=icon if icon else discord.embeds.EmptyEmbed)
    if icon:
        embed.set_thumbnail(url=icon)
    if banner:
        embed.set_image(url=banner)
    embed.add_field(name="Owner", value=owner.mention, inline=False)
    embed.add_field(name="Creation time", value=f"<t:{int(created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Server in Numbers",
                    value=f"• Members: {member_count}\n"
                          + (f"• Roles: {role_count}\n" if role_count else "")
                          + (f"• Categories: {category_count}\n" if category_count else "")
                          + (f"• Text Channels: {text_channel_count}\n" if text_channel_count else "")
                          + (f"• Voice Channels: {voice_channel_count}\n" if voice_channel_count else "")
                          + (f"• Stage Channels: {stage_channel_count}\n" if stage_channel_count else "")
                          + (f"• Emojis: {emoji_count}\n" if emoji_count else "")
                          + (f"• Stickers: {sticker_count}\n" if sticker_count else ""),
                    inline=False)
    embed.add_field(name="Boosts",
                    value=f"• Number of boosts: {booster_count}\n"
                          f"• Boost level: {boost_level}",
                    inline=False)
    return embed


def make_member_info_embed(member: discord.Member, user: discord.User):
    name = str(member)
    nick = member.nick
    avatar_asset = member.guild_avatar if member.guild_avatar else member.avatar
    avatar = avatar_asset.with_size(256).url if avatar_asset else None
    banner = user.banner.url if user.banner else None
    color = user.accent_color
    is_bot = member.bot
    created_at = member.created_at
    joined_at = member.joined_at
    booster_since = member.premium_since
    role_count = len(member.roles) - 1

    description = f"{'`BOT` • ' if is_bot else ''} " + (f"`AKA` {nick}" if nick else "")
    roles_value = f"-" if role_count == 0 \
        else " ".join(role.mention for role in member.roles if role.name != "@everyone")
    embed = discord.Embed(colour=color or discord.Colour(BOT_COLOR),
                          description=description if description.strip() else discord.embeds.EmptyEmbed)
    embed.set_author(name=f"{name}", icon_url=avatar if avatar else discord.embeds.EmptyEmbed)
    if avatar:
        embed.set_thumbnail(url=avatar)
    if banner:
        embed.set_image(url=banner)
    embed.add_field(name="Account created", value=f"<t:{int(created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Member joined", value=f"<t:{int(joined_at.timestamp())}:F>", inline=False)
    embed.add_field(name=f"Roles ({role_count} roles)", value=roles_value, inline=False)
    if booster_since:
        embed.add_field(name="Boosting since",
                        value=f"<t:{int(booster_since.timestamp())}:F>",
                        inline=False)
    return embed


def make_snipe_embed(sniped_message, member):
    author_icon = f"{member.avatar.with_size(32).url}" if member.avatar else None
    author_name = str(member)
    message_content = sniped_message.get('content')
    message_timestamp = sniped_message.get('created_at')
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR), description=message_content, timestamp=message_timestamp)
    embed.set_author(name=author_name, icon_url=author_icon or discord.embeds.EmptyEmbed)
    return embed


def make_welcoming_embed(guild: discord.Guild):
    guild_name = guild.name
    bot_avatar = discord_client.user.avatar.with_size(32).url
    guild_prefs = variables.guilds_prefs[guild.id]
    prefix = guild_prefs.prefix
    admin_prefix = guild_prefs.admin_prefix
    music_prefix = guild_prefs.music_prefix
    description = f"Thank you for adding {BOT_NAME} to {guild_name}! \n" \
                  f"Before getting started, let's make sure no other bots" \
                  f" have conflicting prefixes with {BOT_NAME}.\n‎\n"

    embed = discord.Embed(colour=discord.Colour(BOT_COLOR), description=description)
    embed.set_author(name=f"{BOT_NAME} - Getting Started", icon_url=bot_avatar)

    prefixes = f"• __User commands__: `{prefix}` - change it using `{admin_prefix}p set [new prefix]`\n" \
               f"• __Music commands__: `{music_prefix}` - change it using `{admin_prefix}mp set [new prefix]`\n" \
               f"• __Admin commands__: `{admin_prefix}` - change it using `{admin_prefix}ap set [new prefix]`\n‎\n"

    getting_started = f"• **Basic**: {BOT_NAME}'s user commands include utility, Anime/Manga, and fun commands."\
                      f" Use `{prefix}help` to see if there's anything you like.\n‎\n"\
                      f"• **Music**: {BOT_NAME} offers music!" \
                      f" Start immediately by using `{music_prefix}setup` to create the player channel." \
                      f" Alternatively, you can look at available commands using `{music_prefix}help`\n‎\n"\
                      f"• **Admin**: Customize the way {BOT_NAME} works on your server using admin commands." \
                      f" Use `{admin_prefix}help` to see what you can do."
    embed.add_field(name="Current prefixes", value=prefixes, inline=False)
    embed.add_field(name="Getting started", value=getting_started, inline=False)
    return embed
