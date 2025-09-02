from datetime import datetime, UTC
from typing import TYPE_CHECKING

import discord

from clients import discord_client
from constants import AppLogCategory, Colour, AppLogLevel
from utils.helpers.text_manipulation_helpers import get_human_readable_app_log_category, shorten_text

if TYPE_CHECKING:
    from bot.utils.guild_logger import GuildLogEventField


def get_bot_log_embed(message: str, level: str, log_time: datetime, category: str, extras: dict) -> discord.Embed:
    """
    Generates a Discord embed for bot logs.
    Args:
        message: The log message to display.
        level: The log level (AppLogLevel).
        log_time: The time the log was created.
        category: The category of the log (AppLogCategory).
        extras: Additional information to display as embed fields.

    Returns:
        discord.Embed: The created embed.
    """
    if level in [AppLogLevel.ERROR, AppLogLevel.CRITICAL]:
        embed_color = Colour.RED
    elif level in [AppLogLevel.WARNING] or category in [AppLogCategory.BOT_GUILD_LEFT]:
        embed_color = Colour.HOT_ORANGE
    elif level in [AppLogLevel.INFO]:
        embed_color = Colour.GREEN
    elif level in [AppLogLevel.DEBUG]:
        embed_color = Colour.SILVER
    else:
        embed_color = Colour.PRIMARY_ACCENT

    embed = discord.Embed(
        title=f"{level.title()} - {get_human_readable_app_log_category(category)}",
        description=message,
        color=embed_color,
        timestamp=log_time
    )

    embed.set_footer(text="",
                     icon_url=discord_client.user.display_avatar.with_size(128).url)

    if extras:
        for key, value in extras.items():
            embed.add_field(name=key,
                            value=shorten_text(str(value), 1000),
                            inline=False)

    return embed


def get_guild_log_embed(guild: discord.Guild, author: discord.User | discord.Member, event: str, event_message: str,
                        footer_text: str | None, color: hex, event_fields: list['GuildLogEventField']) -> discord.Embed:
    """
    Generates a Discord embed for guild logs.
    Args:
        guild (discord.Guild): Guild where the event happened.
        author (discord.User | discord.Member): User who triggered the event (or the bot if unavailable).
        event (str): The event type, GuildLogEvent.
        event_message (str): Main message - displayed as embed description.
        footer_text (str | None): Text to display in the embed footer. Usually a member, channel or role ID.
        color (hex): Color of the embed.
        event_fields (list[GuildLogEventField]): List of GuildLogEventField objects to display as embed fields.

    Returns:
        discord.Embed: The created embed.
    """
    embed = discord.Embed(
        title=event,
        description=event_message,
        color=color,
        timestamp=datetime.now(UTC)
    )

    embed.set_author(name=author.name, icon_url=author.display_avatar.with_size(32).url)
    embed.set_footer(text=footer_text,
                     icon_url=guild.icon.with_size(32).url if guild.icon else None)

    for field in event_fields:
        embed.add_field(name=field.name, value=field.value, inline=False)

    return embed
