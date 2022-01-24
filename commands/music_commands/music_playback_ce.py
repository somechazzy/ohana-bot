import asyncio
import re

from actions import send_message, edit_message, send_embed, \
    delete_message_from_guild
from globals_ import clients
from commands.music_command_executor import MusicCommandExecutor
from globals_ import variables
from globals_.constants import MusicVCState, MusicTrackSource, GENERIC_YOUTUBE_TITLE_WORDS
from helpers import process_music_play_arguments, \
    get_lyrics_pages, convert_seconds_to_numeric_time, \
    get_seconds_for_seek_command, get_progress_bar_from_percentage, \
    get_close_embed_view, get_pagination_views, get_numbered_list_views
from embed_factory import make_youtube_search_embed, make_lyrics_embed, make_now_playing_embed
from web_parsers.music.spotify_parser import get_spotify_track_name, get_spotify_playlist_tracks_names
from web_parsers.music.youtube_parser import search_on_youtube
from user_interactions import handle_lyrics, handle_music_search, handle_general_close_embed, \
    handle_music_player


class PlaybackMusicCommandExecutor(MusicCommandExecutor):

    async def handle_command_play(self, play_immediately=False):
        # long messy method, might rewrite later
        check_for_music_channel = not self.using_music_channel
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True,
                                          check_for_music_channel=check_for_music_channel):
            return

        if not self.bot_voice_channel and self.guild.id in variables.guild_music_services:
            variables.guild_music_services[self.guild.id].voice_client = None
            del variables.guild_music_services[self.guild.id]
            self.delete_guild_music_service()

        if not await self.attempt_joining_vc_channel_of_author(send_already_joined_feedback=False):
            return

        if not self.music_service:
            self.initiate_guild_music_service()

        if not self.command_options_and_arguments:
            if self.music_service.state != MusicVCState.PLAYING and self.music_service.queue:
                await self.music_service.start_worker()
            else:
                return await send_embed("What should I play?", self.channel, reply_to=self.reply_to,
                                        delete_after=self.delete_after)
        url_details, search_term, error_message = process_music_play_arguments(self.command_options_and_arguments_fixed)
        is_playlist = url_details and url_details['is_playlist']
        if is_playlist and play_immediately:
            return await send_embed("Can only queue one track to be played immediately.",
                                    self.channel, reply_to=self.reply_to, emoji='❌', color=0xFF522D,
                                    delete_after=self.delete_after)
        track_source = url_details.get('source') if url_details else None
        send_final_track_feedback_message = not play_immediately
        if self.using_music_channel:
            await delete_message_from_guild(message=self.message, reason="Music channel text")
        if error_message:
            return await send_embed(error_message, self.channel, emoji='❌', color=0xFF522D,
                                    reply_to=self.reply_to, delete_after=self.delete_after)
        elif url_details:
            if track_source == MusicTrackSource.YOUTUBE:
                url = url_details['url']
            elif track_source == MusicTrackSource.SPOTIFY:
                if is_playlist:
                    playlist_id = url_details['id']
                    is_album = url_details.get('is_album')
                    tracks_names = await get_spotify_playlist_tracks_names(playlist_id=playlist_id, is_album=is_album)
                    if not tracks_names:
                        await send_embed(f"Couldn't resolve link. Retrying...", self.channel,
                                         reply_to=self.reply_to, delete_after=self.delete_after)
                        await asyncio.sleep(1)
                        tracks_names = await get_spotify_playlist_tracks_names(playlist_id=playlist_id,
                                                                               is_album=is_album)
                    if not tracks_names:
                        return await send_embed(f"Couldn't find this {'album' if is_album else 'playlist'}"
                                                f" on Spotify. Please try again in a second.", self.channel,
                                                emoji='❕', reply_to=self.reply_to,
                                                delete_after=self.delete_after)
                    sent_message = await send_embed(f"Adding {len(tracks_names)} tracks to queue,"
                                                    f" please wait...", self.channel, reply_to=self.reply_to,
                                                    delete_after=self.delete_after)
                    search_results = await search_on_youtube(tracks_names[0], 1)
                    url = search_results[0]['url']
                    tracks_names = tracks_names[1:]
                    if tracks_names:
                        asyncio.get_event_loop().create_task(self._search_and_add_tracks_by_names(tracks_names,
                                                                                                  sent_message))
                    else:
                        await send_embed(f"Finished adding 1 track to queue.", self.channel,
                                         reply_to=self.reply_to, delete_after=self.delete_after)
                    send_final_track_feedback_message = not self.music_service.queue
                else:
                    track_id = url_details['id']
                    track_name = await get_spotify_track_name(track_id=track_id)
                    if not track_name:
                        await send_embed(f"Couldn't resolve link. Retrying...", self.channel,
                                         reply_to=self.reply_to, delete_after=self.delete_after)
                        await asyncio.sleep(1)
                        track_name = await get_spotify_track_name(track_id=track_id)
                    if not track_name:
                        return await send_embed(f"Couldn't find track on Spotify.", self.channel,
                                                emoji='❕', reply_to=self.reply_to,
                                                delete_after=self.delete_after)
                    search_results = await search_on_youtube(track_name, 1)
                    if not search_results:
                        return await send_embed(f"Couldn't find track.", self.channel, emoji='❕',
                                                reply_to=self.reply_to, delete_after=self.delete_after)
                    url = search_results[0]['url']
            else:
                return await send_embed(f"Source `{url_details['source']}` not implemented.", self.channel,
                                        emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                        delete_after=self.delete_after)
        else:
            search_results = await search_on_youtube(search_term)
            if not search_results:
                return await send_embed(f"Couldn't find track.", self.channel,
                                        emoji='❕', reply_to=self.reply_to, delete_after=self.delete_after)
            url = search_results[0]['url']

        if is_playlist and track_source == MusicTrackSource.YOUTUBE:
            tracks_info = await self.music_service.add_youtube_playlist_to_queue(url=url, added_by=self.author.id,
                                                                                 channel=self.channel)
            if not tracks_info:
                return await send_embed(f"Couldn't queue this playlist.", self.channel,
                                        emoji='❕', reply_to=self.reply_to, delete_after=self.delete_after)
            await send_embed(f"Adding {len(tracks_info) + 1} tracks to queue, please wait...", self.channel,
                             reply_to=self.reply_to, delete_after=self.delete_after)
        else:
            track_info = await self.music_service.add_track_to_queue(url=url, added_by=self.author.id,
                                                                     play_immediately=play_immediately,
                                                                     refresh_player=True)
            if send_final_track_feedback_message and self.music_service.current_track != track_info:
                await self._send_final_feedback_message_for_track_add(track_info)
        await self.music_service.refresh_player()
        if self.music_service.state != MusicVCState.PLAYING:
            i = 0
            while not self.music_service.queue and is_playlist:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            await self.music_service.start_worker()

    async def handle_command_pause(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True, check_for_music_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing to pause", self.channel)
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Pause playback?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message)
                return
        was_playing = self.music_service.pause_playback()
        if not was_playing:
            return await send_embed("Already paused.", self.channel)
        return await send_embed("Paused.", self.channel)

    async def handle_command_resume(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True, check_for_music_channel=True):
            return
        if not self.music_service:
            return await send_embed("Nothing to resume", self.channel)
        if not self.author_is_dj_or_is_alone_in_vc():
            return await send_embed("You need DJ role for this.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.message)
        was_paused = self.music_service.resume_playback()
        if was_paused:
            return await send_embed("Resumed.", self.channel)
        return await send_embed("Nothing to resume.", self.channel)

    async def handle_command_search(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if self.using_music_channel:
            await delete_message_from_guild(message=self.message, reason="Music channel text")

        search_term = self.command_options_and_arguments_fixed
        if not search_term:
            return await send_embed("What should I search for?", self.channel, emoji='❌', color=0xFF522D,
                                    reply_to=self.reply_to, delete_after=self.delete_after)
        search_results = await search_on_youtube(search_term)
        if not search_results:
            return await send_embed(f"No results.", self.channel, emoji='❕', color=0xFF522D,
                                    reply_to=self.reply_to, delete_after=self.delete_after)
        embed = make_youtube_search_embed(search_results=search_results)
        view = get_numbered_list_views(list_items=[res['title'] for res in search_results], add_close_button=True)
        sent_message = await send_message(message=None, channel=self.channel, embed=embed, view=view,
                                          reply_to=self.reply_to, delete_after=self.delete_after_longest)

        index = await handle_music_search(sent_message=sent_message,
                                          requested_by=self.author)
        if index is None:
            return

        if not self.bot_voice_channel and self.guild.id in variables.guild_music_services:
            variables.guild_music_services[self.guild.id].voice_client = None
            del variables.guild_music_services[self.guild.id]
            self.delete_guild_music_service()

        if not await self.attempt_joining_vc_channel_of_author(send_already_joined_feedback=False):
            return
        if not self.music_service:
            self.initiate_guild_music_service()

        url = search_results[index]['url']
        track_info = await self.music_service.add_track_to_queue(url=url, added_by=self.author.id, refresh_player=True)
        if self.music_service.current_track != track_info:
            await self._send_final_feedback_message_for_track_add(track_info)
        await self.music_service.refresh_player()
        if self.music_service.state != MusicVCState.PLAYING:
            await self.music_service.start_worker()

    async def handle_command_player(self):
        if self.using_music_channel:
            return await send_embed("Player is right up there 🙄", channel=self.channel,
                                    delete_after=self.delete_after)
        if await self.routine_checks_fail(check_for_music_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing playing.", self.channel)
        embed = make_now_playing_embed(self.guild)
        sent_message = await send_message(message=None, embed=embed, channel=self.channel)
        await handle_music_player(sent_message=sent_message, requested_by=self.author)

    async def handle_command_seek(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing playing.", self.channel, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        if not self.command_options_and_arguments_fixed:
            return await send_embed("Where should I seek to?", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        seek_to_seconds = get_seconds_for_seek_command(self.command_options_and_arguments_fixed)
        if seek_to_seconds is None:
            return await send_embed("Please provide me with a timestamp `HH:MM:SS` or `MM:SS`.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        if self.music_service.current_track['duration'] <= seek_to_seconds:
            return await send_embed("Track is shorter than that.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        if not self.author_is_dj_or_is_alone_in_vc():
            track_before_vote = self.music_service.current_track
            vote_passed, send_feedback = \
                await self.hold_vote(f"Seek to {convert_seconds_to_numeric_time(seek_to_seconds)}?")
            track_after_vote = self.music_service.current_track
            if not vote_passed or not track_before_vote == track_after_vote:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                     delete_after=self.delete_after)
                return
        self.music_service.seek_to(seek_to_seconds=seek_to_seconds)
        await self.music_service.refresh_player()
        if not self.using_music_channel:
            await self.message.add_reaction('✅')

    async def handle_command_progress(self):
        if self.using_music_channel:
            return await send_embed("Click refresh reaction on the player above to refresh progress bar!",
                                    channel=self.channel, delete_after=self.delete_after)
        if await self.routine_checks_fail(check_for_music_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing playing.", self.channel)
        current_track = self.music_service.current_track
        progress = self.music_service.current_track_progress
        duration = current_track['duration']
        progress_percentage = progress / duration
        progress_text = f"{convert_seconds_to_numeric_time(progress)} " \
                        f"{get_progress_bar_from_percentage(progress_percentage)} " \
                        f"{convert_seconds_to_numeric_time(duration)}"
        return await send_embed(f"`{current_track['title']}`",
                                self.channel, thumbnail_url=current_track['tiny_thumbnail_url'],
                                fields_values={"Progress": progress_text})

    async def handle_command_lyrics(self):
        if self.using_music_channel:
            return await send_embed("Please use this command in a different channel.",
                                    channel=self.channel, delete_after=self.delete_after)
        if await self.routine_checks_fail():
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing playing.", self.channel)
        current_track_title = self._get_genius_lyrics_searchable_title_for_current_track()

        def get_genius_song_by_name(track_title):
            return clients.genius_client.search_song(title=track_title)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, get_genius_song_by_name, current_track_title)
        if not result:
            return await send_embed("No lyrics found for this track :(", self.channel)
        full_title = result.full_title or "Track lyrics"
        thumbnail = result.header_image_thumbnail_url
        lyrics = result.lyrics or "No lyrics added :("
        lyrics_pages = get_lyrics_pages(lyrics)
        url = result.url or "https://genius.com"
        embed = make_lyrics_embed(lyrics_pages=lyrics_pages, requested_by=self.author, full_title=full_title,
                                  thumbnail=thumbnail, url=url, page_index=0)
        view = get_close_embed_view() if len(lyrics_pages) == 1 \
            else get_pagination_views(page=1, page_count=len(lyrics_pages), add_close_button=True)
        sent_message = await send_message(message="", embed=embed,
                                          channel=self.channel, reply_to=self.message, view=view)
        if len(lyrics_pages) == 1:
            close_embed = await handle_general_close_embed(sent_message=sent_message, requested_by=self.author)
            if close_embed:
                await edit_message(sent_message, "Lyrics closed.", reason=f"Closed lyrics embed", view=None)
                return
        return await handle_lyrics(sent_message=sent_message,
                                   lyrics_pages=lyrics_pages,
                                   requested_by=self.author,
                                   full_title=full_title,
                                   thumbnail=thumbnail,
                                   url=url)

    async def handle_command_playnow(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Skip current track?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                     delete_after=self.delete_after)
                return
        return await self.handle_command_play(play_immediately=True)

    async def handle_command_replay(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            track_before_vote = self.music_service.current_track
            vote_passed, send_feedback = await self.hold_vote("Replay current track?")
            track_after_vote = self.music_service.current_track
            if not vote_passed or not track_before_vote == track_after_vote:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message,
                                     delete_after=self.delete_after)
                return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing playing.", self.channel,
                                    reply_to=self.reply_to, delete_after=self.delete_after)
        self.music_service.replay_current_track()

    def _get_genius_lyrics_searchable_title_for_current_track(self):
        current_track = self.music_service.current_track
        title = f"{current_track['song_details']['artist']}  {current_track['song_details']['title']}".lower().strip()
        if not title:
            title = current_track['title'].lower()
            for generic_youtube_title_word in GENERIC_YOUTUBE_TITLE_WORDS:
                title = title.replace(f"{generic_youtube_title_word}", "")
        while re.findall("[(\\[<][^()\\[\\]<>]*[)\\]>]", title):
            title = re.sub("[(\\[<][^()\\[\\]<>]*[)\\]>]", "", title)
        return re.sub("[ ]+", " ", re.sub("[-]", "", title))

    async def _search_and_add_tracks_by_names(self, tracks_names, parent_message):
        number_of_tracks = len(tracks_names) + 1
        failed_tracks = 0
        for track_name in tracks_names:
            search_results = await search_on_youtube(track_name, 1)
            if not search_results:
                failed_tracks += 1
            url = search_results[0]['url']
            track_info = await self.music_service.add_track_to_queue(url, self.author.id, refresh_player=False)
            if not track_info:
                failed_tracks += 1
        await send_embed(f"Finished adding {number_of_tracks - failed_tracks} tracks to queue." +
                         (f" {failed_tracks} tracks couldn't be queued." if failed_tracks else ""),
                         self.channel, reply_to=parent_message, delete_after=self.delete_after)
        await self.music_service.refresh_player()
