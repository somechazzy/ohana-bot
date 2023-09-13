import random

import discord

from globals_.clients import discord_client
from globals_.constants import Colour, XPSettingsKey
from utils.helpers import shorten_text_if_above_x_characters
from models.guild import GuildPrefs


def make_autoroles_management_embed(guild, autoroles_ids, feedback_message=None):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    autoroles = []
    for role_id in autoroles_ids:
        role = guild.get_role(role_id)
        if role:
            autoroles.append(role.mention)
    auto_roles_text = "\n ".join(autoroles) if autoroles else "No autoroles added yet."

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"‎Select a role from below to add/remove it as an autorole.\n‎")
    embed.set_author(name=f"Autoroles - {guild.name}", icon_url=guild_icon_small or None)
    embed.add_field(name="Autoroles",
                    value=auto_roles_text,
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    embed.set_footer(icon_url=bot_avatar, text="These roles will be automatically assigned to any new member")
    return embed


def make_gallery_channels_management_embed(guild, gallery_channels_ids, feedback_message=None):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    gallery_channels = []
    for channel_id in gallery_channels_ids:
        channel = guild.get_channel(channel_id)
        if channel:
            gallery_channels.append(channel.mention)
    gallery_channels_text = "\n ".join(gallery_channels) if gallery_channels else "No gallery channels added yet."

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"‎Select a channel from below to add/remove it as a gallery channel.\n‎")
    embed.set_author(name=f"Gallery Channels - {guild.name}", icon_url=guild_icon_small or None)
    embed.add_field(name="Gallery Channels",
                    value=gallery_channels_text,
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    embed.set_footer(icon_url=bot_avatar, text="Gallery channels can be used to post images and videos only")
    return embed


def make_single_message_channels_management_embed(guild, single_message_channels_data, feedback_message=None):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    single_message_channels_text = ""
    for channel_id, data in single_message_channels_data.items():
        channel = guild.get_channel(channel_id)
        if channel:
            single_message_channels_text += f"• {channel.mention} - (<@&{data['role_id']}>)\n"
    if not single_message_channels_text:
        single_message_channels_text = "No single-message channels added yet."

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"‎Select a channel from below to add/remove it as a single-message channel.\n‎")
    embed.set_author(name=f"Single-message Channels - {guild.name}", icon_url=guild_icon_small or None)
    embed.add_field(name="Single-message Channels",
                    value=single_message_channels_text,
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    embed.set_footer(icon_url=bot_avatar, text="Single-message channels restrict users to send only one message "
                                                 "in the channel.")
    return embed


def make_overview_embed(guild_prefs: GuildPrefs, requested_by):
    guild: discord.Guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    author_icon_small = requested_by.avatar.with_size(128).url if requested_by.avatar else None

    description = f"Server settings overview. These settings can be changed using admin `/manage` commands."
    embed = discord.Embed(colour=Colour.INFO,
                          description=description)

    embed.set_author(name=f"{guild.name} - Overview",
                     icon_url=guild_icon_small or None)
    embed.set_footer(text=f"Requested by {requested_by}", icon_url=author_icon_small or None)

    channels_value = "• **Logs**: " + (f"<#{guild_prefs.logs_channel}>\n" if guild_prefs.logs_channel != 0 else
                                       "not set.\n")
    channels_value += f"⚙ Change logging channel using `/manage logging-channel`\n"
    embed.add_field(name="Channels", value=channels_value, inline=False)

    embed.add_field(name="XP Settings",
                    value=f"**To view XP settings overview**: use `/manage xp overview`.",
                    inline=False)

    if len(guild_prefs.autoroles) == 0:
        autoroles_value = f"No roles added yet.\n"
    else:
        autoroles_value = ""
        for autorole in guild_prefs.autoroles:
            autoroles_value += f"• <@&{autorole}>.\n"
        autoroles_value += f"⚙ Manage autoroles using `/manage autoroles`.\n"
    embed.add_field(name="Autoroles", value=autoroles_value, inline=False)

    embed.add_field(name="Other",
                    value=f"• **Gallery channels**: manage and view using `/manage gallery-channels`.\n"
                          f"• **Single-message channels**: manage and view using `manage single-message-channels`.\n"
                          f"• **DJ Roles**: manage and view using `/music dj`.\n",
                    inline=False)

    return embed


def make_xp_overview_embed(xp_settings, requested_by, feedback_message=None):
    guild: discord.Guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    appended_text = f"**These settings are disabled by default due to" \
                    f" XP gain being disabled**." if not xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else ""

    levelup_message = shorten_text_if_above_x_characters(xp_settings[XPSettingsKey.LEVELUP_MESSAGE].
                                                         format(member_mention=requested_by.mention,
                                                                member_tag=str(requested_by),
                                                                level=int((random.random() * 10) + 1) * 5), 240)
    if xp_settings[XPSettingsKey.LEVEL_ROLES]:
        level_roles_str = ""
        for level, role_id in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            if guild.get_role(role_id):
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

    levelup_message_channel = guild.get_channel(xp_settings[XPSettingsKey.LEVELUP_CHANNEL]).mention \
        if guild.get_channel(xp_settings[XPSettingsKey.LEVELUP_CHANNEL]) else "wherever the member is chatting."

    embed = discord.Embed(colour=Colour.INFO,
                          description=f"Overview of XP settings for this server. Change these settings to your liking."
                                      f" {appended_text}")

    embed.set_author(name=f"{guild.name} - XP Settings", icon_url=guild_icon_small or None)
    embed.set_footer(text=f"XP Settings", icon_url=bot_avatar or None)

    embed.add_field(name="XP Gain",
                    value=f"• Status: **{'enabled' if xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else 'disabled'}.**\n"
                          f"• Timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]} seconds**\n"
                          f"• Minimum gain per timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_MIN]}**\n"
                          f"• Maximum gain per timeframe: **{xp_settings[XPSettingsKey.XP_GAIN_MAX]}**\n"
                          f"• Booster Bonus: **{xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN]}%**\n"
                          f"⚙ In effect: sending any number of messages within "
                          f"**{xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]}** seconds gives you"
                          f" somewhere between **{xp_settings[XPSettingsKey.XP_GAIN_MIN]}** "
                          f"and **{xp_settings[XPSettingsKey.XP_GAIN_MAX]}** XP.",
                    inline=False)
    embed.add_field(name="LevelUp Message",
                    value=f"• Status: "
                          + (f"**{'enabled' if xp_settings[XPSettingsKey.LEVELUP_ENABLED] else 'disabled'}.**\n" if
                             xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else
                             "**disabled due to XP Gain being disabled**.\n") +
                          f"• Levelup message channel: **{levelup_message_channel}**\n"
                          f"• Levelup message:\n{levelup_message}\n"
                          f"• Max level: **{xp_settings[XPSettingsKey.LEVEL_MAX] or 'none'}**\n"
                          f"⚙ You can use placeholders for levelup message like **{{member_mention}}**, "
                          f"**{{member_tag}}** and **{{level}}**, which I will replace with the member's"
                          f" **mention**, **tag** and **level** respectively.",
                    inline=False)
    embed.add_field(name="Level Roles",
                    value=f"{level_roles_str.strip()}\n"
                          + (f"• Stack level roles: "
                             f"**{'enabled' if xp_settings[XPSettingsKey.STACK_ROLES] else 'disabled'}.**\n" if
                             xp_settings[XPSettingsKey.LEVEL_ROLES] else "") +
                          f"⚙ These roles are awarded when members reach a certain level.",
                    inline=False)
    embed.add_field(name="XP Decay",
                    value=f"• Status: "
                          + (f"**{'enabled' if xp_settings[XPSettingsKey.XP_DECAY_ENABLED] else 'disabled'}.**\n" if
                             xp_settings[XPSettingsKey.XP_GAIN_ENABLED] else
                             "**disabled due to XP Gain being disabled.**\n") +
                          f"• Percentage a day: **{xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]}%**\n"
                          f"• Grace period: **{xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]} days**\n"
                          f"⚙ In effect: a member that hasn't sent a message in the last "
                          f"**{xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]}** days will lose "
                          f"**{xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]}%** of their XP every day.",
                    inline=False)
    embed.add_field(name="Ignored Channels",
                    value=f"{ignored_channels_str}\n"
                          f"⚙ Sending a message in this channel will not give XP.",
                    inline=False)
    embed.add_field(name="Ignored Roles",
                    value=f"{ignored_roles_str}\n"
                          f"⚙ Members with this role will not gain XP.",
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info", value=feedback_message, inline=False)
    return embed
