import re
from copy import deepcopy
from math import ceil
import discord

from globals_.clients import discord_client
from globals_ import shared_memory
from globals_.constants import MusicVCLoopMode, PLAYER_IDLE_IMAGE, generic_youtube_title_words_to_remove, Colour
from models.music_library import MusicLibrary, Playlist
from models.music_stream import MusicStreamStatusCheck
from utils.helpers.string_manipulation import convert_seconds_to_numeric_time, shorten_text_if_above_x_characters, \
    get_progress_bar_from_percentage


def make_youtube_search_embed(search_results):
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
    results_text = ""
    for i, result in enumerate(search_results, 1):
        result_line = f"{i}. **[{result.get('title')}]({result.get('url')})** [{result.get('duration')}]"
        results_text += f"\n{result_line}"
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"React with the number you want to queue."
                                      f" React with 🗑 to close the embed.\n{results_text}")
    embed.set_thumbnail(url=search_results[0]['thumbnail_url'])
    embed.set_author(name=f"Search results", icon_url=bot_avatar)
    return embed


def make_lyrics_embed(lyrics_pages, requested_by, full_title, thumbnail, url, page_index):
    genius_logo_url = "https://media.discordapp.net/attachments/794891724345442316/914260270677913660/genius-logo.png"
    requested_by_avatar = requested_by.avatar.with_size(128).url if requested_by.avatar else None

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=lyrics_pages[page_index])
    embed.set_author(name=full_title, icon_url=genius_logo_url, url=url)
    embed.set_footer(text=f"Showing page {page_index + 1}/{len(lyrics_pages)} • Requested by: {requested_by}",
                     icon_url=requested_by_avatar or None)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    return embed


def make_initial_player_message_embed(guild):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description="Nothing playing right now.")
    embed.set_author(name="Player", icon_url=bot_avatar)
    embed.set_image(url=PLAYER_IDLE_IMAGE)
    embed.set_footer(text=f"Music commands: /music",
                     icon_url=guild_icon_small or None)
    return embed


def make_player_message_embed(guild):
    from services.background.music_service import GuildMusicService
    music_service: GuildMusicService = shared_memory.guild_music_services.get(guild.id)
    if not music_service or not music_service.queue:
        return make_initial_player_message_embed(guild)
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
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
        track_line = f"`{index}`.{loop_one_text} **{title.strip()}** [{duration}]({url}) "
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
    current_track_text = f"`{current_track_index+1}`. **[{track_title}]({track_url})**\n{progress_text} {status}"
    queue_page_text = f" [page {music_service.player_page}]" if music_service.player_page > 1 else ""
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"**Queue:**{queue_page_text}{upcoming_tracks_text}")
    embed.set_author(name=f"Player", icon_url=bot_avatar)
    embed.set_footer(text=f"Queue Duration: {overall_duration} • {len(music_service.queue)} tracks • "
                          f"Music commands: /music",
                     icon_url=guild_icon_small or None)
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
    for word in generic_youtube_title_words_to_remove:
        for variation in [f"({word})", f"{{{word}}}", f"「{word}」", f"[{word}]", f"{word}"]:
            compiled = re.compile(re.escape(variation), re.IGNORECASE)
            title = compiled.sub("", title)
    return title


def make_music_history_embed(guild, history, page):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

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
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"Choose a track from the list below to queue it.\n{queue_text}")
    embed.set_author(name=f"History", icon_url=guild_icon_small or None)
    embed.set_footer(text=f"Showing page {page}/{page_count}", icon_url=bot_avatar)

    return embed


def make_music_library_embed(music_library: MusicLibrary, page=1, feedback_message=None):
    user = discord_client.get_user(music_library.user_id)
    icon_url = user.avatar.with_size(128).url if user.avatar else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    playlists_info = ""
    page_count = None
    if not music_library.playlists:
        playlists_info = "No playlists added yet. Create your first playlist using `/music list create`"
    else:
        page_count = ceil(len(music_library.playlists) / 10)
        if not (0 <= page <= page_count):
            page = 1
        starting_index = (page - 1) * 10
        final_index = (starting_index + 10) if (starting_index + 10 <= len(music_library.playlists))\
            else len(music_library.playlists)
        for i, playlist in enumerate(music_library.playlists[starting_index:final_index], (page - 1) * 10 + 1):
            playlists_info += f"\n{i}. **{playlist.name}** ({len(playlist.tracks)} tracks)."

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"‎Select a playlist from below to view/manage.")
    embed.set_author(name=f"{user.name}'s Music Library", icon_url=icon_url or None)
    embed.add_field(name="Playlists",
                    value=playlists_info.strip(),
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    if page_count:
        embed.set_footer(text=f"Showing page {page}/{page_count}", icon_url=bot_avatar)
    return embed


def make_playlist_embed(playlist: Playlist, page=1, feedback_message=None, from_library=False):
    user = discord_client.get_user(playlist.user_id)
    icon_url = user.avatar.with_size(128).url if user.avatar else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    tracks_info = ""
    thumbnail_url = None
    page_count = None
    if not playlist.tracks:
        tracks_info = "No tracks added yet. Add tracks using `/music list add-track` or use buttons below"
    else:
        thumbnail_url = playlist.tracks[0].thumbnail_url
        page_count = ceil(len(playlist.tracks) / 10)
        if not (0 <= page <= page_count):
            page = 1
        starting_index = (page - 1) * 10
        final_index = (starting_index + 10) if (starting_index + 10 <= len(playlist.tracks)) else len(playlist.tracks)
        for i, track in enumerate(playlist.tracks[starting_index:final_index], (page - 1) * 10 + 1):
            duration = convert_seconds_to_numeric_time(track.duration)
            tracks_info += f"\n{i}. **{track.title}** [[{duration}]({track.url})]"
    if from_library:
        description = f"Below listed are tracks in this playlist.\n‎\n"
    else:
        description = f"Use `/music library` to display all of your playlists.\n" \
                      f"Below listed are tracks in this playlist.\n‎\n"
    description += f"**Tracks**\n{tracks_info.strip()}"
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=description)
    embed.set_author(name=f"{user.name}'s Music Library: {playlist.name}",
                     icon_url=icon_url or None)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if page_count:
        embed.set_footer(text=f"Showing page {page}/{page_count}", icon_url=bot_avatar)
    return embed


def make_dj_role_management_embed(guild, dj_role_ids, feedback_message=None):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    dj_roles = []
    for role_id in dj_role_ids:
        role = guild.get_role(role_id)
        if role:
            dj_roles.append(role.mention)
    dj_roles_text = "\n ".join(dj_roles) if dj_roles else "No DJ roles set yet."

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"‎Select a role from below to add/remove it as a DJ role.")
    embed.set_author(name=f"DJ Roles - {guild.name}", icon_url=guild_icon_small or None)
    embed.add_field(name="DJ Roles",
                    value=dj_roles_text,
                    inline=False)
    if feedback_message:
        embed.add_field(name="Info",
                        value=feedback_message,
                        inline=False)
    embed.set_footer(icon_url=bot_avatar, text="Members with DJ roles can control a music session with 4+ people")
    return embed


def make_initial_radio_message_embed(guild):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description="Nothing playing right now.")
    embed.set_author(name="Radio", icon_url=bot_avatar)
    embed.set_image(url=PLAYER_IDLE_IMAGE)
    embed.set_footer(text=f"Music commands: /music",
                     icon_url=guild_icon_small or None)
    return embed


def make_radio_message_embed(guild):
    from services.background.music_service import GuildMusicService
    music_service: GuildMusicService = shared_memory.guild_music_services.get(guild.id)
    if not music_service or not music_service.radio_stream:
        return make_initial_radio_message_embed(guild)
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
    radio_stream = music_service.radio_stream

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT)
    embed.set_author(name=f"Radio", icon_url=bot_avatar)
    embed.set_footer(text=f"Music commands: /music",
                     icon_url=guild_icon_small or None)
    embed.set_image(url=radio_stream.get_image_url())

    embed.add_field(name=f"{radio_stream.emoji_string} **{radio_stream.name}**\n",
                    value=f"> {radio_stream.description}",
                    inline=False)
    embed.add_field(name="Genres",
                    value=f"{radio_stream.get_genres_string()}")
    embed.add_field(name="Website",
                    value=f"[Click here]({radio_stream.website_url})")

    return embed


def make_radio_currently_playing_embed(stream_status: MusicStreamStatusCheck.StreamStatus):
    if not stream_status:
        return discord.Embed(colour=Colour.PRIMARY_ACCENT,
                             description="Sorry! This is not support by the selected radio.")

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


def make_music_logs_embed(guild, logs, page, page_count):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None

    if not (0 <= page <= page_count):
        page = 1
    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(logs)) else len(logs)

    queue_text = ""
    for i in range(starting_index, final_index):
        queue_text += f"\n• {logs[i]}"
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"List of actions taken by members related to Music **sorted by latest**. "
                                      f"Logs might be aggregated by action and member.\n{queue_text}")
    embed.set_author(name=f"Music Audit Log", icon_url=guild_icon_small or None)
    embed.set_footer(text=f"Showing page {page}/{page_count}", icon_url=bot_avatar)

    return embed
