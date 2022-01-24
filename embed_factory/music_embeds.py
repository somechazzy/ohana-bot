import re
from copy import deepcopy
from math import ceil
import disnake as discord
from globals_.clients import discord_client
from globals_ import variables
from globals_.constants import MusicVCLoopMode, PLAYER_IDLE_IMAGE, GENERIC_YOUTUBE_TITLE_WORDS_TO_REMOVE, BOT_NAME, \
    BOT_COLOR
from helpers import convert_seconds_to_numeric_time, shorten_text_if_above_x_characters, \
    get_progress_bar_from_percentage


def make_music_queue_embed(guild, queue, page, currently_playing_index):
    prefix = variables.guilds_prefs[guild.id].music_prefix
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(32).url

    overall_duration = convert_seconds_to_numeric_time(sum([track.get('duration') for track in queue]))
    page_count = ceil(len(queue) / 10)
    if not (0 <= page <= page_count):
        page = 1
    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(queue)) else len(queue)

    queue_text = ""
    for i in range(starting_index, final_index):
        track = queue[i]
        currently_played = i == currently_playing_index
        track_line = f"{'**=>** ' if currently_played else ''}" \
                     f"{i+1}. **{track.get('title')}** [[{track.get('duration_text')}]({track.get('url')})] " \
                     f"- *Added by {guild.get_member(track.get('added_by'))}*"
        queue_text += f"\n{track_line}"
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"View {BOT_NAME} Player embed using `{prefix}now`."
                                      f" React with 🗑 to close the embed.\n{queue_text}")
    embed.set_author(name=f"Music Queue", icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    currently_playing_track_text = f" • Currently playing track #{currently_playing_index+1}"\
        if currently_playing_index != 0 else ""
    embed.set_footer(text=f"Showing page {page}/{page_count}{currently_playing_track_text}", icon_url=f"{bot_avatar}")
    embed.add_field(name="Queue duration",
                    value=overall_duration + f" ({len(queue)} tracks)")
    embed.set_thumbnail(url=queue[currently_playing_index].get('tiny_thumbnail_url'))

    return embed


def make_youtube_search_embed(search_results):
    bot_avatar = discord_client.user.avatar.with_size(32).url
    results_text = ""
    for i, result in enumerate(search_results, 1):
        result_line = f"{i}. **[{result.get('title')}]({result.get('url')})** [{result.get('duration')}]"
        results_text += f"\n{result_line}"
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"React with the number you want to queue."
                                      f" React with 🗑 to close the embed.\n{results_text}")
    embed.set_thumbnail(url=search_results[0]['thumbnail_url'])
    embed.set_author(name=f"Search results", icon_url=f"{bot_avatar}")
    return embed


def make_now_playing_embed(guild):
    prefix = variables.guilds_prefs[guild.id].music_prefix
    bot_avatar = discord_client.user.avatar.with_size(32).url
    music_service = variables.guild_music_services.get(guild.id)
    if not music_service or not music_service.queue:
        return discord.Embed(colour=discord.Colour(BOT_COLOR), description=f"Nothing playing or queued.")
    current_track_index = music_service.currently_played_track_index
    current_track = music_service.queue[current_track_index]
    upcoming_tracks = _get_upcoming_tracks(music_service)
    track_thumbnail_url = current_track.get('thumbnail_url')
    track_title = current_track.get('title')
    track_duration = current_track.get('duration_text')
    track_url = current_track.get('url')
    track_added_by_id = current_track.get('added_by')
    progress = music_service.current_track_progress
    duration = current_track['duration']
    progress_percentage = progress / duration
    progress_text = f"{convert_seconds_to_numeric_time(progress)} " \
                    f"{get_progress_bar_from_percentage(progress_percentage)} " \
                    f"{convert_seconds_to_numeric_time(duration)}"

    overall_duration = convert_seconds_to_numeric_time(sum([track.get('duration') for track in music_service.queue]))

    upcoming_tracks_text = ""
    for upcoming_track in upcoming_tracks:
        index = upcoming_track.get('index')
        loop_one_text = "***LOOPING***" \
            if (music_service.loop_mode == MusicVCLoopMode.ONE and current_track_index+1 == index) \
            else ""
        title = shorten_text_if_above_x_characters(upcoming_track.get('title'), 45)
        url = upcoming_track.get('url')
        duration = upcoming_track.get('duration_text')
        track_line = f"{index}. {loop_one_text} **[{title}]({url})** [{duration}] "

        upcoming_tracks_text += f"\n{track_line}"

    status = '`PLAYING`' if music_service.voice_client.is_playing() \
        else '`PAUSED`' if music_service.voice_client.is_paused()\
        else ''
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"**[{track_title}]({track_url})** {status}\n{progress_text}")
    embed.set_author(name=f"{BOT_NAME} Player", icon_url=f"{bot_avatar}")
    embed.set_image(url=track_thumbnail_url)

    embed.add_field(name="Added by",
                    value=f"<@!{track_added_by_id}>",
                    inline=True)
    embed.add_field(name="Track duration",
                    value=track_duration,
                    inline=True)
    embed.add_field(name="Loop mode",
                    value=music_service.loop_mode.capitalize(),
                    inline=True)
    embed.add_field(name="Upcoming tracks",
                    value=upcoming_tracks_text or "*Nothing else queued.*",
                    inline=False)
    embed.add_field(name="Queue duration",
                    value=overall_duration + f" • {len(music_service.queue)} tracks"
                                             f"\nView full queue using `{prefix}queue` "
                                             f"• Change loop mode using `{prefix}loop`",
                    inline=False)

    return embed


def _get_upcoming_tracks(music_service):
    upcoming_tracks = deepcopy(music_service.queue)
    for i, track in enumerate(upcoming_tracks, 1):
        track['index'] = i
    if music_service.loop_mode == MusicVCLoopMode.NONE:
        return upcoming_tracks[music_service.currently_played_track_index + 1:
                               music_service.currently_played_track_index + 6]
    elif music_service.loop_mode == MusicVCLoopMode.ONE:
        return upcoming_tracks[music_service.currently_played_track_index:
                               music_service.currently_played_track_index + 5]
    else:
        return (upcoming_tracks[music_service.currently_played_track_index + 1:
                                music_service.currently_played_track_index + 6] +
                upcoming_tracks[:music_service.currently_played_track_index])[:5]


def make_lyrics_embed(lyrics_pages, requested_by, full_title, thumbnail, url, page_index):
    genius_logo_url = "https://media.discordapp.net/attachments/794891724345442316/914260270677913660/genius-logo.png"
    requested_by_avatar = requested_by.avatar.with_size(32).url if requested_by.avatar else None

    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=lyrics_pages[page_index])
    embed.set_author(name=full_title, icon_url=f"{genius_logo_url}", url=url)
    embed.set_footer(text=f"Showing page {page_index + 1}/{len(lyrics_pages)} • Requested by: {requested_by}",
                     icon_url=requested_by_avatar or discord.embeds.EmptyEmbed)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    return embed


def make_initial_player_message_embed(guild):
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(32).url
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description="Nothing playing right now.")
    embed.set_author(name=f"{BOT_NAME} Player", icon_url=bot_avatar)
    embed.set_image(url=PLAYER_IDLE_IMAGE)
    embed.set_footer(text=f"Music prefix is {variables.guilds_prefs.get(guild.id).music_prefix}",
                     icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    return embed


def make_player_message_embed(guild):
    music_service = variables.guild_music_services.get(guild.id)
    from services.music_service import GuildMusicService
    music_service: GuildMusicService
    if not music_service or not music_service.queue:
        return make_initial_player_message_embed(guild)
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(32).url
    current_track_index = music_service.currently_played_track_index
    current_track = music_service.queue[current_track_index]
    upcoming_tracks = _get_player_queue(music_service, page=music_service.player_page)
    track_thumbnail_url = current_track.get('thumbnail_url')
    track_title = _strip_title_from_unnecessary_words(current_track.get('title'))
    track_duration = current_track.get('duration_text')
    track_url = current_track.get('url')
    track_added_by_id = current_track.get('added_by')
    progress = music_service.current_track_progress
    duration = current_track['duration']
    progress_percentage = progress / duration
    progress_text = f"{convert_seconds_to_numeric_time(progress)} " \
                    f"{get_progress_bar_from_percentage(progress_percentage)} " \
                    f"{convert_seconds_to_numeric_time(duration)}"

    overall_duration = convert_seconds_to_numeric_time(sum([track.get('duration') for track in music_service.queue]))

    upcoming_tracks_text = ""
    upcoming_tracks.reverse()
    for upcoming_track in upcoming_tracks:
        index = upcoming_track.get('index')
        loop_one_text = " [***LOOPING***]" \
            if (music_service.loop_mode == MusicVCLoopMode.ONE and current_track_index + 1 == index) \
            else ""
        title = shorten_text_if_above_x_characters(_strip_title_from_unnecessary_words(upcoming_track.get('title')), 45)
        url = upcoming_track.get('url')
        duration = upcoming_track.get('duration_text')
        track_line = f"{index}.{loop_one_text} **{title}** [{duration}]({url}) "
        upcoming_tracks_text += f"\n{track_line}"
    status = '`PLAYING`' if music_service.voice_client.is_playing() \
        else '`PAUSED`' if music_service.voice_client.is_paused() \
        else ''
    if not upcoming_tracks_text:
        upcoming_tracks_text = "\n*Nothing else queued.*"
    elif music_service.player_page > 1:
        upcoming_tracks_text += "\n•••"
    if upcoming_tracks \
            and music_service.queue \
            and len(music_service.queue) > max(upcoming_track.get('index') for upcoming_track in upcoming_tracks):
        upcoming_tracks_text = "\n•••" + upcoming_tracks_text
    current_track_text = f"{current_track_index+1}. **[{track_title}]({track_url})**\n{progress_text} {status}"
    queue_page_text = f" [page {music_service.player_page}]" if music_service.player_page > 1 else ""
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"**Queue:**{queue_page_text}{upcoming_tracks_text}")
    embed.set_author(name=f"{BOT_NAME} Player", icon_url=f"{bot_avatar}")
    embed.set_footer(text=f"Queue Duration: {overall_duration} • {len(music_service.queue)} tracks • "
                          f"Music prefix is {variables.guilds_prefs.get(guild.id).music_prefix}",
                     icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    embed.set_image(url=track_thumbnail_url)

    embed.add_field(name="Current Track",
                    value=current_track_text,
                    inline=False)
    embed.add_field(name="Added by",
                    value=f"<@!{track_added_by_id}>",
                    inline=True)
    embed.add_field(name="Track duration",
                    value=track_duration,
                    inline=True)
    embed.add_field(name="Loop mode",
                    value=music_service.loop_mode.capitalize(),
                    inline=True)
    return embed


def _get_player_queue(music_service, page=1):
    upcoming_tracks = deepcopy(music_service.queue)
    offset = (page-1)*10
    offset_offset = 0 if music_service.loop_mode == MusicVCLoopMode.ALL else 1
    for i, track in enumerate(upcoming_tracks, 1):
        track['index'] = i
    return upcoming_tracks[offset+offset_offset: (offset+offset_offset) + 10]


def _strip_title_from_unnecessary_words(title: str):
    for word in GENERIC_YOUTUBE_TITLE_WORDS_TO_REMOVE:
        for variation in [f"({word})", f"{{{word}}}", f"「{word}」", f"{word}"]:
            compiled = re.compile(re.escape(variation), re.IGNORECASE)
            title = compiled.sub("", title)
    return title


def make_music_history_embed(guild, history, page):
    guild_icon_small = guild.icon.with_size(32).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(32).url

    page_count = ceil(len(history) / 10)
    if not (0 <= page <= page_count):
        page = 1
    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(history)) else len(history)

    queue_text = ""
    for i in range(starting_index, final_index):
        track = history[i]
        ts_text = f" (<t:{track.get('timestamp')}:R>)" if track.get('timestamp') else ''
        track_line = f"{i+1}. **{track.get('title')}** [[{track.get('duration_text')}]({track.get('url')})]{ts_text}"
        queue_text += f"\n{track_line}"
    embed = discord.Embed(colour=discord.Colour(BOT_COLOR),
                          description=f"Choose a track from the list below to queue it.\n{queue_text}")
    embed.set_author(name=f"History", icon_url=guild_icon_small or discord.embeds.EmptyEmbed)
    embed.set_footer(text=f"Showing page {page}/{page_count}", icon_url=f"{bot_avatar}")

    return embed
