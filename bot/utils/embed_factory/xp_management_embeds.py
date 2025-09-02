import discord

from constants import Colour, XPLevelUpMessageSubstitutable
from models.dto.cachables import CachedGuildSettings
from utils.helpers.text_manipulation_helpers import shorten_text


def get_xp_setup_embed(guild: discord.Guild,
                       xp_settings: CachedGuildSettings.XPSettings,
                       feedback_message: str) -> discord.Embed:
    """
    Generate an embed showing the current XP settings for the guild.
    Args:
        guild (discord.Guild): The guild to generate the embed for.
        xp_settings (CachedGuildSettings.XPSettings): The XP settings for the guild.
        feedback_message (str): A feedback message to display in the embed.
    Returns:
        discord.Embed: The generated embed.
    """
    xp_gain_disabled_notice = f"**These settings are disabled by default due to XP gain being disabled**." \
        if not xp_settings.xp_gain_enabled else ""
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"Overview of XP settings for this server. Change these settings to your liking."
                                      f" {xp_gain_disabled_notice}")
    embed.set_author(name=f"{guild.name} - XP Settings",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)
    embed.set_footer(text=f"Ohana XP Settings",
                     icon_url=guild.me.display_avatar.with_size(128).url)

    level_up_message_channel_text = guild.get_channel(xp_settings.level_up_message_channel_id).mention \
        if xp_settings.level_up_message_channel_id else "wherever the member is chatting"
    level_up_message_substitutions = {
        XPLevelUpMessageSubstitutable.LEVEL: "5",
        XPLevelUpMessageSubstitutable.MEMBER_MENTION: guild.me.mention,
        XPLevelUpMessageSubstitutable.MEMBER_NAME: guild.me.display_name,
    }
    level_up_message_text = shorten_text(xp_settings.level_up_message_text, 240).format(
        **level_up_message_substitutions
    )
    level_up_message_text = '> ' + '\n> '.join(level_up_message_text.split('\n'))
    if xp_settings.level_role_ids_map:
        levels = sorted(xp_settings.level_role_ids_map.keys())
        level_roles_str = ""
        for level in levels:
            roles = [guild.get_role(role_id) for role_id
                     in xp_settings.level_role_ids_map[level] if guild.get_role(role_id)]
            if not roles:
                continue
            level_roles_str += f"• Level **{level}**: {', '.join(role.mention for role in roles)}\n"
    else:
        level_roles_str = "No level roles added."

    embed.add_field(name="XP Gain",
                    value=f"• Status: **{'enabled' if xp_settings.xp_gain_enabled else 'disabled'}.**\n"
                          f"• Timeframe: **{xp_settings.xp_gain_timeframe} seconds**\n"
                          f"• Minimum gain per timeframe: **{xp_settings.xp_gain_minimum}**\n"
                          f"• Maximum gain per timeframe: **{xp_settings.xp_gain_maximum}**\n"
                          f"• Booster Bonus: **{round(xp_settings.booster_xp_gain_multiplier, 2)}%**\n"
                          f"⚙ In effect: sending any number of messages within **{xp_settings.xp_gain_timeframe}**"
                          f" seconds gives you somewhere between **{xp_settings.xp_gain_minimum}**"
                          f" and **{xp_settings.xp_gain_maximum}** XP.",
                    inline=False)
    embed.add_field(name="Level-up Message",
                    value=f"• Status: "
                          + (f"**{'enabled' if xp_settings.level_up_message_enabled else 'disabled'}.**\n" if
                             xp_settings.xp_gain_enabled else
                             "**disabled due to XP Gain being disabled**.\n") +
                          f"• Level-up message channel: **{level_up_message_channel_text}**.\n"
                          + (f"• Minimum level to send this message: "
                             f"**{xp_settings.level_up_message_minimum_level}**.\n"
                             if xp_settings.level_up_message_minimum_level > 1 else "") +
                          f"• Level-up message:\n{level_up_message_text}\n"
                          f"• Max level: **{xp_settings.max_level or 'none'}**\n"
                          f"⚙ You can use placeholders for level-up message like **{{member_mention}}**, "
                          f"**{{member_name}}** and **{{level}}**, which Ohana will replace with the member's"
                          f" **mention**, **name** and **level** respectively.",
                    inline=False)
    embed.add_field(name="Level Roles",
                    value=f"{level_roles_str.strip()}\n"
                          + (f"• Stack level roles: "
                             f"**{'enabled' if xp_settings.stack_level_roles else 'disabled'}.**\n" if
                             xp_settings.level_role_ids_map else "") +
                          f"⚙ These roles are awarded when members reach a certain level.",
                    inline=False)
    embed.add_field(name="XP Decay",
                    value=f"• Status: "
                          + (f"**{'enabled' if xp_settings.xp_decay_enabled else 'disabled'}.**\n" if
                             xp_settings.xp_gain_enabled else
                             "**disabled due to XP Gain being disabled.**\n") +
                          f"• Percentage a day: **{xp_settings.xp_decay_per_day_percentage}%**\n"
                          f"• Grace period: **{xp_settings.xp_decay_grace_period_days} days**\n"
                          f"⚙ In effect: a member that hasn't sent a message in the last "
                          f"**{xp_settings.xp_decay_grace_period_days}** days will lose "
                          f"**{round(xp_settings.xp_decay_per_day_percentage, 2)}%** of their XP every day.",
                    inline=False)
    embed.add_field(name="Ignored Channels",
                    value=f"{', '.join(guild.get_channel(channel_id).mention
                                       for channel_id in xp_settings.ignored_channel_ids) or 'None selected.'}\n"
                          f"⚙ Sending a message in these channels will not give XP.",
                    inline=False)
    embed.add_field(name="Ignored Roles",
                    value=f"{', '.join(guild.get_role(role_id).mention
                                       for role_id in xp_settings.ignored_role_ids) or 'None selected.'}\n"
                          f"⚙ Members with any of these roles will not gain XP.",
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info", value=feedback_message, inline=False)
    return embed


def get_transfer_xp_from_member_embed() -> discord.Embed:
    """
    Generate an embed for selecting a member to transfer XP from.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Member selection - transfer XP from',
                          description='Select the XP you would like to transfer from',
                          color=Colour.PRIMARY_ACCENT)
    embed.set_footer(text="Use the User ID button if the member isn't in the server")
    return embed


def get_transfer_xp_to_member_embed() -> discord.Embed:
    """
    Generate an embed for selecting a member to transfer XP to.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Member selection - transfer XP to',
                          description='Select the XP you would like to transfer to',
                          color=Colour.PRIMARY_ACCENT)
    return embed


def get_award_xp_to_member_embed() -> discord.Embed:
    """
    Generate an embed for selecting a member to award XP to.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Award XP to member',
                          description=f'Select the member to award XP to',
                          color=Colour.PRIMARY_ACCENT)
    return embed


def get_take_away_xp_from_member_embed() -> discord.Embed:
    """
    Generate an embed for selecting a member to take away XP from.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Take away XP from member',
                          description=f'Select the member to take away XP from',
                          color=Colour.PRIMARY_ACCENT)
    embed.set_footer(text="Use the User ID button if the member isn't in the server")
    return embed


def get_reset_xp_for_member_embed() -> discord.Embed:
    """
    Generate an embed for selecting a member to reset XP for.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Reset XP for member',
                          description=f'Select the member to reset XP for',
                          color=Colour.PRIMARY_ACCENT)
    embed.set_footer(text="Use the User ID button if the member isn't in the server")
    return embed


def get_award_xp_to_role_embed() -> discord.Embed:
    """
    Generate an embed for selecting a role to award XP to.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Award XP to role',
                          description=f'Select the role to award XP to',
                          color=Colour.PRIMARY_ACCENT)
    return embed


def get_take_away_xp_from_role_embed() -> discord.Embed:
    """
    Generate an embed for selecting a role to take away XP from.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Take away XP from role',
                          description=f'Select the role to take away XP from',
                          color=Colour.PRIMARY_ACCENT)
    return embed


def get_reset_xp_for_role_embed() -> discord.Embed:
    """
    Generate an embed for selecting a role to reset XP for.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(title='Reset XP for role',
                          description=f'Select the role to reset XP for',
                          color=Colour.PRIMARY_ACCENT)
    return embed
