import datetime
import json
from difflib import SequenceMatcher
from utils.exceptions import PlaylistDuplicateNameException


class PlaylistTrack:
    def __init__(self, youtube_id, title, duration=0, thumbnail_url=None, added_on=datetime.datetime.utcnow()):
        self.youtube_id = youtube_id
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.duration = int(duration)
        self.added_on = added_on

    def to_dict(self):
        return {
            "youtube_id": self.youtube_id,
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "duration": int(self.duration),
            "added_on": int(self.added_on.timestamp())
        }

    @staticmethod
    def from_dict(track_dict):
        youtube_id = track_dict["youtube_id"]
        title = track_dict.get("title", "-")
        thumbnail_url = track_dict.get("thumbnail_url")
        duration = int(track_dict.get("duration"))
        added_on = datetime.datetime.fromtimestamp(track_dict["added_on"])
        return PlaylistTrack(youtube_id=youtube_id,
                             title=title,
                             duration=duration,
                             thumbnail_url=thumbnail_url,
                             added_on=added_on)

    @property
    def url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"


class Playlist:
    def __init__(self, id_, user_id, name=str(), tracks=None,
                 created=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
        if tracks is None:
            tracks = list()
        self.id = id_
        self.user_id = user_id
        self.name = name.strip()
        self.tracks = tracks
        self.created = created
        self.updated = updated

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "name": self.name,
            "tracks": [track.to_dict() for track in self.tracks],
            "created": int(self.created.timestamp()),
            "updated": int(self.updated.timestamp())
        }

    @staticmethod
    def from_dict(playlist_dict):
        id_ = playlist_dict["id"]
        user_id = int(playlist_dict["user_id"])
        name = playlist_dict["name"]
        tracks = [PlaylistTrack.from_dict(track_dict) for track_dict in playlist_dict.get("tracks", []) if track_dict]
        created = datetime.datetime.fromtimestamp(playlist_dict["created"])
        updated = datetime.datetime.fromtimestamp(playlist_dict["updated"])
        return Playlist(id_=id_,
                        user_id=user_id,
                        tracks=tracks,
                        name=name,
                        created=created,
                        updated=updated)

    @staticmethod
    def get_default_playlist(user_id):
        return Playlist(id_=1, user_id=user_id, name="Favorites")

    def add_track(self, youtube_id, title, duration=0, thumbnail_url=None):
        self.tracks.append(PlaylistTrack(youtube_id=youtube_id,
                                         title=title,
                                         duration=duration,
                                         thumbnail_url=thumbnail_url))
        self.updated = datetime.datetime.utcnow()

    def add_tracks(self, tracks):
        self.tracks.extend(tracks)
        self.updated = datetime.datetime.utcnow()

    def rename_playlist(self, new_name):
        self.name = new_name
        self.updated = datetime.datetime.utcnow()

    def remove_track(self, index):
        self.updated = datetime.datetime.utcnow()
        return self.tracks.pop(index)

    def clear_playlist(self):
        self.updated = datetime.datetime.utcnow()
        return self.tracks.clear()

    def move_track(self, from_, to_):
        self.updated = datetime.datetime.utcnow()
        track = self.tracks.pop(from_)
        self.tracks.insert(to_, track)
        return track


class MusicLibrary:
    def __init__(self, user_id, playlists=None):
        if playlists is None:
            playlists = [Playlist.get_default_playlist(user_id=user_id)]
        self.user_id = user_id
        self.playlists = playlists
        self._playlist_name_playlist_map = dict()
        self.refresh_playlist_mapping()

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "playlists": [playlist.to_dict() for playlist in self.playlists]
        }

    @staticmethod
    def from_dict(dict_):
        user_id = int(dict_["user_id"])
        playlists = [Playlist.from_dict(playlist_dict) for playlist_dict in dict_.get("playlists", []) if playlist_dict]
        return MusicLibrary(user_id=user_id,
                            playlists=playlists)

    def set_playlists(self, playlists):
        if playlists is None:
            playlists = [Playlist.get_default_playlist(user_id=self.user_id)]
        self.playlists = playlists

    def clear_playlists(self):
        self.playlists = [Playlist.get_default_playlist(user_id=self.user_id)]

    def add_playlist(self, playlist: Playlist):
        self.check_playlist_name_availability(name=playlist.name)
        self.playlists.append(playlist)
        return playlist

    def check_playlist_name_availability(self, name):
        self.refresh_playlist_mapping()
        if name.lower().strip() in self._playlist_name_playlist_map:
            raise PlaylistDuplicateNameException(f"Attempting to add playlist with name `{name}` to user `"
                                                 f"{self.user_id}` who already has a playlist with the same name hash.")

    def get_playlist_by_name(self, name: str):
        name = name.strip().lower()
        self.refresh_playlist_mapping()
        if name not in self._playlist_name_playlist_map:
            for playlist in self.playlists:
                if SequenceMatcher(None, playlist.name, name).ratio() >= 0.9:
                    return self._playlist_name_playlist_map.get(playlist.name)
        return self._playlist_name_playlist_map.get(name)

    def refresh_playlist_mapping(self):
        self._playlist_name_playlist_map = {playlist.name.strip().lower(): playlist for playlist in self.playlists}

    def create_new_playlist(self, user_id=None, name=str(), tracks=None):
        if not user_id:
            user_id = self.user_id
        if not name:
            name = self._generate_playlist_name()
        new_id = (max(playlist.id for playlist in self.playlists) + 1) if self.playlists else 1
        new_playlist = Playlist(id_=new_id, user_id=user_id, name=name, tracks=tracks)
        self.add_playlist(new_playlist)
        return new_playlist

    def _generate_playlist_name(self):
        base_name = 'Untitled'
        try:
            self.check_playlist_name_availability(base_name)
            name = base_name
        except PlaylistDuplicateNameException:
            i = 2
            while 1:
                try:
                    name = f"{base_name} ({i})"
                    self.check_playlist_name_availability(name)
                    break
                except PlaylistDuplicateNameException:
                    i += 1
        return name


class MusicLog:

    def __init__(self, actor_id: int, actor_name: str, action: str,
                 context_value: str = None, context_count: int = 1, timestamp: float = None):
        self.actor_id = actor_id
        self.actor_name = actor_name
        self.action = action
        self.timestamp = timestamp or datetime.datetime.utcnow().timestamp()
        self.context_value = context_value
        self.context_count = context_count

    def to_dict(self):
        return {
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "action": self.action,
            "timestamp": self.timestamp,
            "context_value": self.context_value,
            "context_count": self.context_count
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def to_json_list(data: list):
        return json.dumps([d.to_dict() for d in data])

    @staticmethod
    def from_dict(data: dict):
        return MusicLog(
            actor_id=data["actor_id"],
            actor_name=data["actor_name"],
            action=data["action"],
            timestamp=data["timestamp"],
            context_value=data["context_value"],
            context_count=data["context_count"]
        )

    @staticmethod
    def from_json(data: str):
        return MusicLog.from_dict(json.loads(data))

    @staticmethod
    def from_json_list(data: str):
        return [MusicLog.from_dict(d) for d in json.loads(data)]
