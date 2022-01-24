from globals_ import clients


async def get_spotify_track_name(track_id):
    track_info = await clients.spotify_client.get_track(track_id)
    if not track_info:
        return None
    return get_track_name_from_track_info(track_info)


async def get_spotify_playlist_tracks_names(playlist_id, offset=0, limit=50, is_album=False):
    if is_album:
        playlist_info = await clients.spotify_client.get_album_tracks(playlist_id, offset=offset, limit=limit)
    else:
        playlist_info = await clients.spotify_client.get_playlist_tracks(playlist_id, offset=offset, limit=limit)
    if not playlist_info:
        return None
    playlist_items = playlist_info.get('items')
    if is_album:
        tracks_info = playlist_items
    else:
        tracks_info = [playlist_item.get("track") for playlist_item in playlist_items]
    tracks_names = [get_track_name_from_track_info(track_info) for track_info in tracks_info]
    total_playlist_items = playlist_info.get('total')
    if offset + limit < total_playlist_items:
        if offset == 500:
            return tracks_names
        next_page = await get_spotify_playlist_tracks_names(playlist_id, offset=offset+limit, limit=limit)
        tracks_names.extend(next_page or list())
        return tracks_names
    return tracks_names


def get_track_name_from_track_info(track_info):
    artists = track_info.get("artists", [])
    artists_names = ' '.join([artist.get("name", "") for artist in artists])
    track_name = track_info.get("name", "")
    return f"{track_name} {artists_names}".strip()
