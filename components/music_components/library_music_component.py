import asyncio

from components.music_components.base_music_component import MusicComponent
from globals_ import shared_memory
from globals_.clients import firebase_client
from models.music_library import MusicLibrary
from utils.embed_factory import quick_embed
from .youtube_music_component import YoutubeMusicComponent
from .spotify_music_component import SpotifyMusicComponent
from globals_.constants import MusicTrackSource
from utils.exceptions import PlaylistAddParsingException
from utils.helpers import process_music_play_arguments


class LibraryMusicComponent(MusicComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_music_component = YoutubeMusicComponent(**kwargs)
        self.spotify_music_component = SpotifyMusicComponent(**kwargs)
        self.firebase_client = firebase_client

    async def get_user_music_library(self, user_id) -> MusicLibrary:
        if user_id not in shared_memory.users_music_libraries:
            music_library_dict = (await self.firebase_client.get_user_music_library(user_id=user_id)).val()
            if music_library_dict:
                music_library = MusicLibrary.from_dict(dict_=music_library_dict)
            else:
                music_library = MusicLibrary(user_id=user_id)
            shared_memory.users_music_libraries[user_id] = music_library

        return shared_memory.users_music_libraries[user_id]

    async def sync_library_to_db(self, music_library):
        await self.firebase_client.save_user_music_library(music_library=music_library)

    async def add_track_to_playlist(self, playlist_to_add_to, track_or_playlist, interaction):
        urls_to_add, yt_playlist_tracks_info = await self.process_add_command_input(input_=track_or_playlist)
        if urls_to_add:
            await interaction.edit_original_response(embed=quick_embed(f"Adding {len(urls_to_add)} track(s)"
                                                                       f" to `{playlist_to_add_to.name}`..."))
        failed_track_count = 0
        successfully_added_count = 0
        if yt_playlist_tracks_info:
            for track in yt_playlist_tracks_info:
                playlist_to_add_to.add_track(youtube_id=track["youtube_url"].split('=')[1],
                                             title=track["title"],
                                             duration=track["duration_seconds"],
                                             thumbnail_url=track["thumbnail_url"])
            successfully_added_count = len(yt_playlist_tracks_info)
        else:
            for url in urls_to_add:
                track_info = await self.youtube_music_component.get_youtube_track_info(url)
                if not track_info:
                    failed_track_count += 1
                    continue
                title, thumbnail_url, _, duration, _, _, _ = track_info
                playlist_to_add_to.add_track(youtube_id=url.split('=')[1],
                                             title=title,
                                             duration=duration,
                                             thumbnail_url=thumbnail_url)
                successfully_added_count += 1
        feedback_message = f"Added {successfully_added_count} track(s) to `{playlist_to_add_to.name}`." \
                           + (f"\n{failed_track_count} tracks couldn't be added." if failed_track_count else "")
        return feedback_message

    async def process_add_command_input(self, input_):
        url_details, search_term, error_message = process_music_play_arguments(input_)
        is_playlist = url_details and url_details['is_playlist']
        track_source = url_details.get('source') if url_details else None
        urls = []
        yt_playlist_tracks_info = []
        if error_message:
            raise PlaylistAddParsingException(error_message)
        elif url_details:
            if track_source == MusicTrackSource.YOUTUBE:
                if is_playlist:
                    yt_playlist_tracks_info = \
                        await self.youtube_music_component.get_youtube_playlist_tracks(url=url_details['url'])
                else:
                    urls = [url_details['url']]
            elif track_source == MusicTrackSource.SPOTIFY:
                if is_playlist:
                    playlist_id = url_details['id']
                    is_album = url_details.get('is_album')
                    tracks_names = \
                        await self.spotify_music_component.get_playlist_tracks_names(playlist_id=playlist_id,
                                                                                     is_album=is_album)
                    if not tracks_names:
                        await asyncio.sleep(1)
                        tracks_names = await self.spotify_music_component.get_playlist_tracks_names(
                            playlist_id=playlist_id, is_album=is_album)
                    if not tracks_names:
                        raise PlaylistAddParsingException(f"Couldn't find this {'album' if is_album else 'playlist'}"
                                                          f" on Spotify. Please check your link or try again.")
                    for track_name in tracks_names:
                        search_results = \
                            await self.youtube_music_component.youtube_service.get_search_results(track_name, limit=1)
                        urls.append(search_results[0]['url'])
                else:
                    track_id = url_details['id']
                    track_name = await self.spotify_music_component.get_track_name(track_id=track_id)
                    if not track_name:
                        raise PlaylistAddParsingException(f"Couldn't find track on Spotify.")
                    search_results = await self.youtube_music_component.youtube_service.get_search_results(track_name,
                                                                                                           limit=1)
                    if not search_results:
                        raise PlaylistAddParsingException(f"Couldn't find track.")
                    urls = [search_results[0]['url']]
            else:
                raise PlaylistAddParsingException(f"Source `{url_details['source']}` not implemented.")
        else:
            search_results = await self.youtube_music_component.youtube_service.get_search_results(search_term)
            if not search_results:
                raise PlaylistAddParsingException(f"Couldn't find track.")
            urls = [search_results[0]['url']]

        return urls, yt_playlist_tracks_info
