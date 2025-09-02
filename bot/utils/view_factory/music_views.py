from typing import TYPE_CHECKING

from discord import ButtonStyle, SelectOption
from discord.ui import View, Button, Select

import cache
from clients import emojis
from constants import MusicPlayerAction, RadioStreamCategory, RADIO_CATEGORY_LABEL_MAP

if TYPE_CHECKING:
    from bot.guild_music_service import GuildMusicService


def get_music_player_view(music_service: 'GuildMusicService') -> View:
    """
    Creates the music player view.
    Args:
        music_service (GuildMusicService): The music service instance for the guild.

    Returns:
        View: The music player view with buttons and select menu.
    """
    view = View(timeout=None)

    if not music_service or not music_service.voice_client:
        view.add_item(Button(label="Connect", style=ButtonStyle.green,
                             custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.CONNECT}",
                             emoji=emojis.player.connect))
        return view

    options = []
    if music_service.current_stream:
        options.append(SelectOption(label=music_service.current_stream.name, value=music_service.current_stream.code,
                                    description=', '.join(music_service.current_stream.genres),
                                    emoji=emojis.player.get_station_emoji(code=music_service.current_stream.code),
                                    default=True))
    options.extend([
        SelectOption(label=stream.name, value=stream.code, description=', '.join(stream.genres),
                     emoji=emojis.player.get_station_emoji(code=stream.code),
                     default=False)
        for stream in cache.RADIO_STREAMS_BY_CATEGORY[RadioStreamCategory.DEFAULT]
        if not music_service.current_stream or stream.code != music_service.current_stream.code])
    for category in RadioStreamCategory.as_list():
        if category == RadioStreamCategory.DEFAULT:
            continue
        options.append(SelectOption(label=f"{RADIO_CATEGORY_LABEL_MAP[category]} →→→",
                                    value=f"{MusicPlayerAction.subselect_qualifier()}-{category}",
                                    description="Click to see streams in this category",
                                    emoji=emojis.player.get_station_category_emoji(category),
                                    default=False))
    view.add_item(Select(placeholder="Select Radio", min_values=1, max_values=1, row=0,
                         custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.SELECT_STREAM}",
                         options=options))

    if music_service.voice_client.is_playing():
        view.add_item(Button(label="Stop", style=ButtonStyle.grey,
                             custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.STOP}",
                             emoji=emojis.player.stop, row=1))

    view.add_item(Button(label="Disconnect", style=ButtonStyle.red,
                         custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.DISCONNECT}",
                         emoji=emojis.player.disconnect, row=1))
    view.add_item(Button(label="Report a problem..", style=ButtonStyle.grey,
                         custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.REPORT_ISSUE}", row=1))

    if music_service.current_stream and bool(music_service.current_stream.status_check):
        view.add_item(Button(label="What's Playing?", style=ButtonStyle.green,
                             custom_id=f"{MusicPlayerAction.qualifier()}-{MusicPlayerAction.SHOW_CURRENTLY_PLAYING}",
                             emoji=emojis.player.music, row=2))

    return view


def get_radio_category_view(category: str) -> View:
    """
    Creates a view for selecting radio streams within a specific category.
    Args:
        category (str): The category of radio streams to display.
    Returns:
        View: The view containing a select menu for radio streams in the specified category.
    """
    view = View(timeout=None)
    options = [
        SelectOption(label=stream.name, value=stream.code, description=', '.join(stream.genres),
                     emoji=emojis.player.get_station_emoji(code=stream.code),
                     default=False)
        for stream in cache.RADIO_STREAMS_BY_CATEGORY[category]
    ]
    view.add_item(Select(placeholder="Select Radio", min_values=1, max_values=1, row=0,
                         custom_id=f"{MusicPlayerAction.qualifier()}-"
                                   f"{MusicPlayerAction.subselect_qualifier()}-"
                                   f"{MusicPlayerAction.SELECT_STREAM}",
                         options=options))
    return view
