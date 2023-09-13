from components.music_components.base_music_component import MusicComponent
from globals_.clients import spotify_service


class SpotifyMusicComponent(MusicComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_track_name(self, track_id, with_retry=True):
        track_info = await spotify_service.get_track(track_id)
        if not track_info:
            if with_retry:
                return await self.get_track_name(track_id, with_retry=False)
            return None
        return self.get_track_name_from_track_info(track_info)

    async def get_playlist_tracks_names(self, playlist_id, offset=0, limit=50, is_album=False, with_retry=True):
        if is_album:
            playlist_info = await spotify_service.get_album_tracks(playlist_id, offset=offset, limit=limit)
        else:
            playlist_info = await spotify_service.get_playlist_tracks(playlist_id, offset=offset, limit=limit)
        if not playlist_info:
            if with_retry:
                return await self.get_playlist_tracks_names(playlist_id, offset=offset, limit=limit, is_album=is_album,
                                                            with_retry=False)
            return None
        playlist_items = playlist_info.get('items')
        if is_album:
            tracks_info = playlist_items
        else:
            tracks_info = [playlist_item.get("track") for playlist_item in playlist_items]
        tracks_names = [self.get_track_name_from_track_info(track_info) for track_info in tracks_info]
        tracks_names = list(filter(lambda track_name: track_name, tracks_names))
        total_playlist_items = playlist_info.get('total')
        if offset + limit < total_playlist_items:
            if offset == 500:
                return tracks_names
            next_page = await self.get_playlist_tracks_names(playlist_id, offset=offset + limit, limit=limit)
            tracks_names.extend(next_page or list())
            return tracks_names
        return tracks_names

    @staticmethod
    def get_track_name_from_track_info(track_info):
        if not track_info:
            return None
        artists = track_info.get("artists", [])
        artists_names = ' '.join([artist.get("name", "") for artist in artists])
        track_name = track_info.get("name", "")
        return f"{track_name} {artists_names}".strip()
