import json
import os
from math import ceil

from globals_.constants import MusicServiceMode, MusicLogAction
from utils.embed_factory import quick_embed, make_youtube_search_embed, make_lyrics_embed, make_music_history_embed
from utils.helpers import get_numbered_list_views, get_seconds_for_seek_command, get_lyrics_pages,\
    get_pagination_views, build_path, get_history_embed_views
from utils.exceptions import MusicVoiceConnectionException
from services.third_party.genius import GeniusService
from utils.decorators import slash_command
from slashes.music_slashes.base_music_slashes import MusicSlashes
from user_interactions.music_interactions.music_history_interactions_handler import MusicHistoryInteractionsHandler
from user_interactions.music_interactions.music_lyrics_interactions_handler import MusicLyricsInteractionsHandler
from user_interactions.music_interactions.music_search_interactions_handler import MusicSearchInteractionsHandler


class PlaybackMusicSlashes(MusicSlashes):

    @slash_command
    async def play(self, user_input: str):
        """
        /music play
        Queue a track/playlist to be played
        """
        if not await self.preprocess_and_validate(guild_only=True, check_for_music_channel=True):
            return

        try:
            self.music_service = await self.get_or_initiate_guild_music_service(raise_=True)
        except MusicVoiceConnectionException as e:
            await self.interaction.response.send_message(content=str(e), ephemeral=True)
            return

        if self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.ask_to_switch_to_player_mode()

        await self.interaction.response.send_message(embed=quick_embed(text="Adding to queue...", ), ephemeral=True)

        track_count = await self.handle_add_to_queue(input_text=user_input)
        
        if track_count:
            await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK,
                                                               context_count=track_count)

    @slash_command
    async def search(self, search_term: str):
        """
        /music search
        Search for a track on YouTube to play
        """
        if not await self.preprocess_and_validate(guild_only=True, check_for_music_channel=True):
            return

        search_results = await self.youtube_service.get_search_results(search_term)
        if not search_results:
            return await self.interaction.response.send_message(content="No results found", ephemeral=True)

        interactions_handler = MusicSearchInteractionsHandler(source_interaction=self.interaction,
                                                              guild_id=self.guild.id,
                                                              index_track_info_map=search_results)

        embed = make_youtube_search_embed(search_results=search_results)
        view = get_numbered_list_views(list_items=[res['title'] for res in search_results],
                                       interactions_handler=interactions_handler,
                                       add_close_button=False)
        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command
    async def play_now(self, user_input: str):
        """
        /music play-now
        Play a track immediately
        """

        if not await self.preprocess_and_validate(guild_only=True, check_for_music_channel=True):
            return

        try:
            self.music_service = await self.get_or_initiate_guild_music_service(raise_=True)
        except MusicVoiceConnectionException as e:
            await self.interaction.response.send_message(content=str(e), ephemeral=True)
            return

        if self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.ask_to_switch_to_player_mode()

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(embed=quick_embed(text="Playing now...", ))
        else:
            await self.interaction.response.send_message(embed=quick_embed(text="Playing now...", ), ephemeral=True)

        await self.handle_add_to_queue(input_text=user_input, play_immediately=True)
        await self.music_logger_component.log_music_action(action=MusicLogAction.FORCE_PLAYED_TRACK)

    @slash_command
    async def seek(self, position: str):
        """
        /music seek
        Seek to a position in the current track
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        seek_to_seconds = get_seconds_for_seek_command(position)
        if seek_to_seconds is None:
            return await self.interaction.response.send_message(content="Please provide me with a timestamp"
                                                                        " `HH:MM:SS` or `MM:SS`.", ephemeral=True)
        if self.music_service.current_track['duration'] <= seek_to_seconds:
            return await self.interaction.response.send_message(content="Track is shorter than that.", ephemeral=True)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(embed=quick_embed(text="Seeking...", ))
        else:
            await self.interaction.response.send_message(embed=quick_embed(text="Seeking...", ), ephemeral=True)

        await self.music_service.seek_to(seek_to_seconds=seek_to_seconds)
        await self.music_logger_component.log_music_action(action=MusicLogAction.TRACK_SEEK,
                                                           context_value=f"Seeked to {position}")

    @slash_command
    async def replay(self):
        """
        /music replay
        Replay the current track
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(embed=quick_embed(text="Replaying...", ))
        else:
            await self.interaction.response.send_message(embed=quick_embed(text="Replaying...", ), ephemeral=True)

        await self.music_service.seek_to(seek_to_seconds=0)
        await self.music_logger_component.log_music_action(action=MusicLogAction.REPLAYED_TRACK,)

    @slash_command
    async def clear(self):
        """
        /music clear
        Clear the queue
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(embed=quick_embed(text="Queue cleared.", ))
        else:
            await self.interaction.response.send_message(embed=quick_embed(text="Queue cleared.", ), ephemeral=True)
        
        queue_track_count = len(self.music_service.queue)
        await self.music_service.clear_queue()
        await self.music_logger_component.log_music_action(action=MusicLogAction.CLEARED_QUEUE,
                                                           context_value=f"{queue_track_count}")

    @slash_command
    async def move(self, from_position: int, to_position: int):
        """
        /music move
        Move a track in the queue
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        if from_position < 1 or from_position > len(self.music_service.queue):
            return await self.interaction.response.send_message(content="Invalid track position.", ephemeral=True)
        if to_position < 1 or to_position > len(self.music_service.queue):
            return await self.interaction.response.send_message(content="Invalid track position.", ephemeral=True)
        if from_position == to_position:
            return await self.interaction.response.send_message(content="That's the same position.", ephemeral=True)
        if self.music_service.currently_played_track_index == from_position - 1 \
                or self.music_service.currently_played_track_index == to_position - 1:
            return await self.interaction.response.send_message(content="You can't move the currently playing track.",
                                                                ephemeral=True)

        title = await self.music_service.move_track(track_index=from_position - 1, target_index=to_position - 1)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Moved `{title}` to position `{to_position}`.", )
            )
        else:
            await self.interaction.response.send_message(
                embed=quick_embed(text=f"Moved `{title}` to position `{to_position}`.", ), ephemeral=True
            )
        
        await self.music_logger_component.log_music_action(action=MusicLogAction.MOVED_TRACK)

    @slash_command
    async def remove(self, position: int):
        """
        /music remove
        Remove a track from the queue
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        if position < 1 or position > len(self.music_service.queue):
            return await self.interaction.response.send_message(content="Invalid track position.", ephemeral=True)
        if self.music_service.currently_played_track_index == position - 1:
            return await self.interaction.response.send_message(content="You can't remove the currently playing track.",
                                                                ephemeral=True)

        title = await self.music_service.remove_track(index=position - 1)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Removed `{title}` from the queue.", )
            )
        else:
            await self.interaction.response.send_message(
                embed=quick_embed(text=f"Removed `{title}` from the queue.", ),
                ephemeral=True
            )
        
        await self.music_logger_component.log_music_action(action=MusicLogAction.REMOVED_TRACK)

    @slash_command
    async def skip_to(self, position: int):
        """
        /music skip-to
        Skip to a track in the queue
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue \
                or self.music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        if self.member.voice is None or self.member.voice.channel != self.music_service.voice_client.channel:
            return await self.interaction.response.send_message(content="Join my voice channel first!", ephemeral=True)

        if position < 1 or position > len(self.music_service.queue):
            return await self.interaction.response.send_message(content="Invalid track position.", ephemeral=True)
        if self.music_service.currently_played_track_index == position - 1:
            return await self.interaction.response.send_message(content="That's already the currently playing track.",
                                                                ephemeral=True)
        number_of_tracks_to_skip = position - self.music_service.currently_played_track_index - 1
        track_info = await self.music_service.skip_to_track(index=position - 1)

        if self.interaction.response.is_done():
            await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Skipping to `{track_info['title']}`.", )
            )
        else:
            await self.interaction.response.send_message(
                embed=quick_embed(text=f"Skipping to `{track_info['title']}`.", ),
                ephemeral=True
            )
        
        await self.music_logger_component.log_music_action(action=MusicLogAction.SKIPPED_TRACK,
                                                           context_count=number_of_tracks_to_skip)

    @slash_command
    async def lyrics(self):
        """
        /music lyrics
        Get lyrics for the currently playing track
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        if not self.music_service or not self.music_service.queue:
            return await self.interaction.response.send_message(content="No music is playing", ephemeral=True)

        await self.interaction.response.send_message(content="Searching for lyrics...", ephemeral=True)

        try:
            result = await GeniusService().search_song(title=self.get_genius_lyrics_searchable_title_for_current_track())
            if not result:
                return await self.interaction.edit_original_response(content="No lyrics found for this track.")
        except NotImplementedError as e:
            return await self.interaction.edit_original_response(content=str(e))
        except Exception:
            return await self.interaction.edit_original_response(content="Genius Lyrics seems to be down.")

        full_title = result.full_title or "Track lyrics"
        thumbnail = result.header_image_thumbnail_url
        lyrics = result.lyrics or "No lyrics added :("
        lyrics_pages = get_lyrics_pages(lyrics)
        url = result.url or "https://genius.com"

        embed = make_lyrics_embed(lyrics_pages=lyrics_pages, requested_by=self.member, full_title=full_title,
                                  thumbnail=thumbnail, url=url, page_index=0)
        if len(lyrics_pages) == 1:
            return await self.interaction.edit_original_response(content=None, embed=embed, )
        else:
            interactions_handler = MusicLyricsInteractionsHandler(source_interaction=self.interaction,
                                                                  full_title=full_title,
                                                                  thumbnail=thumbnail,
                                                                  lyrics_pages=lyrics_pages,
                                                                  url=url,
                                                                  requested_by=self.member)
            await self.interaction.edit_original_response(
                content=None, embed=embed,
                view=get_pagination_views(page_count=len(lyrics_pages),
                                          page=1,
                                          add_close_button=False,
                                          interactions_handler=interactions_handler)
            )

    @slash_command
    async def history(self):
        """
        /music history
        Get playback history for the server
        """

        if not await self.preprocess_and_validate(guild_only=True):
            return

        guild_history_path = build_path(["media", "music", "history", f"{self.guild.id}.json"])
        history = {}
        if os.path.isfile(guild_history_path):
            with open(guild_history_path, 'r') as file:
                history = json.load(file)
        if not history:
            return await self.interaction.response.send_message("No playback history for this server yet.",
                                                                ephemeral=True)
        history = list(history.values())
        history.reverse()
        page = 1
        history_interactions_handler = MusicHistoryInteractionsHandler(
            source_interaction=self.interaction,
            history_list=history,
            page=page,
        )
        first_index = (page - 1) * 10
        last_index = first_index + 10
        track_index_title_map = {index: track['title'] for index, track
                                 in enumerate(history[first_index:last_index], first_index)}
        view = get_history_embed_views(interactions_handler=history_interactions_handler, show_previous=page > 1,
                                       show_next=(ceil(len(history) / 10)) > page,
                                       track_index_title_map=track_index_title_map)
        embed = make_music_history_embed(guild=self.guild, history=history, page=1)
        await self.interaction.response.send_message(content=None, embed=embed, view=view, ephemeral=True)
