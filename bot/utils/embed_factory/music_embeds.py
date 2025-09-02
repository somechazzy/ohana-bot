from typing import TYPE_CHECKING

import discord

from bot.utils.helpers.stats_helpers import get_member_count_connected_to_vc_with_music_radio_stream
from clients import emojis
from constants import Colour, MusicDefaults, RADIO_CATEGORY_LABEL_MAP
from models.dto.radio_stream import RadioStreamStatusCheck
from utils.helpers.text_manipulation_helpers import get_progress_bar_from_percentage, convert_seconds_to_numeric_time

if TYPE_CHECKING:
    from bot.guild_music_service import GuildMusicService


def get_music_header_embed() -> discord.Embed:
    """
    Creates the header embed for music-related interactions.
    Returns:
        discord.Embed: The header embed.
    """
    embed = discord.Embed(color=Colour.MUSIC_ACCENT)
    embed.set_image(url=MusicDefaults.PLAYER_HEADER_IMAGE)
    return embed


def get_music_player_embed(guild: discord.Guild, music_service: 'GuildMusicService') -> discord.Embed:
    """
    Creates the music player embed for the given guild.
    Args:
        guild (discord.Guild): The guild to create the embed for.
        music_service (GuildMusicService): The music service for the guild.
    Returns:
        discord.Embed: The music player embed.
    """
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT)
    embed.set_author(name="Ohana Radio",
                     icon_url=guild.me.display_avatar.with_size(128).url)

    if not music_service or not (current_stream := music_service.current_stream):
        embed.description = "Nothing playing right now."
        embed.set_image(url=MusicDefaults.PLAYER_IDLE_IMAGE)
        if not music_service:
            footer_text = "Connect me to a VC to start playing something!"
        else:
            footer_text = "Select a station to start playing something!"
    else:
        listeners = get_member_count_connected_to_vc_with_music_radio_stream(stream_code=current_stream.code)
        footer_text = f"Ohana is currently streaming this station to {listeners} listener(s)"
        embed.set_image(url=current_stream.get_image_url())
        embed.add_field(
            name=f"{emojis.player.get_station_emoji(current_stream.code)} **{current_stream.name}**\n",
            value=f"> {current_stream.description}",
            inline=False
        )
        embed.add_field(name="Genres",
                        value=f"{', '.join(current_stream.genres)}")
        embed.add_field(name="Website",
                        value=f"[Click here]({current_stream.website_url})")
        
    embed.set_footer(icon_url=guild.icon.with_size(128).url if guild.icon else None,
                     text=footer_text)

    return embed


def get_radio_currently_playing_embed(stream_status: RadioStreamStatusCheck.StreamStatus | None) -> discord.Embed:
    """
    Creates an embed showing the currently playing track on the radio stream.
    Args:
        stream_status (RadioStreamStatusCheck.StreamStatus | None): The current status of the radio stream.
    Returns:
        discord.Embed: The embed showing the currently playing track, if any.
    """
    if not stream_status:
        return discord.Embed(colour=Colour.PRIMARY_ACCENT,
                             description="Sorry! This is not supported by the selected radio stream.")

    if not stream_status.currently_playing:
        return discord.Embed(colour=Colour.PRIMARY_ACCENT,
                             description="Nothing playing.")

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"**{stream_status.currently_playing}**")

    embed.set_author(name="Currently playing...")

    if stream_status.duration and not stream_status.progress:
        embed.add_field(name="Duration",
                        value=convert_seconds_to_numeric_time(stream_status.duration))
    elif stream_status.duration and stream_status.progress:
        progress_percentage = stream_status.progress / stream_status.duration
        progress_text = f"{convert_seconds_to_numeric_time(stream_status.progress)} " \
                        f"{get_progress_bar_from_percentage(progress_percentage)} " \
                        f"{convert_seconds_to_numeric_time(stream_status.duration)}"
        embed.add_field(name="Progress", value=progress_text)

    if stream_status.artwork_url:
        embed.set_thumbnail(url=stream_status.artwork_url)

    return embed


def get_radio_category_embed(guild: discord.Guild, category: str) -> discord.Embed:
    """
    Creates an embed showing the radio stations in the given category.
    Args:
        guild (discord.Guild): The guild to create the embed for.
        category (str): The category of radio stations to display.
    Returns:
        discord.Embed: The embed showing the radio stations in the given category.
    """
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          title=f"{emojis.player.get_station_category_emoji(category)} "
                                f"**{RADIO_CATEGORY_LABEL_MAP[category]}**",
                          description="Select a station to start playing it.")
    embed.set_author(name="Ohana Radio",
                     icon_url=guild.me.display_avatar.with_size(128).url)
    return embed
