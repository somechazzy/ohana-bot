from typing import Optional, Any, List, TypeVar, Type, cast, Callable
from enum import Enum


#  AUTO-GENERATED JSON-TO-OBJECT PARSER, FORGOT WHICH TOOL I USED FOR THIS
T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_dict(x: Any) -> dict:
    assert isinstance(x, dict)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class Title:
    romaji: Optional[str]
    english: Optional[str]

    def __init__(self, romaji: Optional[str], english: Optional[str]) -> None:
        self.romaji = romaji
        self.english = english

    @staticmethod
    def from_dict(obj: Any) -> 'Title':
        assert isinstance(obj, dict)
        romaji = from_union([from_str, from_none], obj.get("romaji"))
        english = from_union([from_none, from_str], obj.get("english"))
        return Title(romaji, english)

    def to_dict(self) -> dict:
        result: dict = {"romaji": from_union([from_str, from_none], self.romaji),
                        "english": from_union([from_none, from_str], self.english)}
        return result


class Media:
    title: Optional[Title]
    site_url: Optional[str]
    mal_id: Optional[int]

    def __init__(self, title: Optional[Title], site_url: Optional[str], mal_id: Optional[int]) -> None:
        self.title = title
        self.site_url = site_url
        self.mal_id = mal_id

    @staticmethod
    def from_dict(obj: Any) -> 'Media':
        assert isinstance(obj, dict)
        title = from_union([Title.from_dict, from_none], obj.get("title"))
        site_url = from_union([from_str, from_none], obj.get("siteUrl"))
        mal_id = from_union([from_int, from_none], obj.get("idMal"))
        return Media(title, site_url, mal_id)

    def to_dict(self) -> dict:
        result: dict = {"title": from_union([lambda x: to_class(Title, x), from_none], self.title),
                        "siteUrl": from_union([from_str, from_none], self.site_url),
                        "idMal": from_union([from_int, from_none], self.mal_id)}
        return result


class Status(Enum):
    COMPLETED = "COMPLETED"
    CURRENT = "CURRENT"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    PLANNING = "PLANNING"


class Entry:
    media: Optional[Media]
    status: Optional[Status]
    score: Optional[int]
    progress: Optional[int]
    repeat: Optional[int]
    started_at: Optional[dict]
    completed_at: Optional[dict]

    def __init__(self, media: Optional[Media], status: Optional[Status], score: Optional[int], progress: Optional[int],
                 repeat: Optional[int], started_at: Optional[dict], completed_at: Optional[dict]) -> None:
        self.media = media
        self.status = status
        self.score = score
        self.progress = progress
        self.repeat = repeat
        self.started_at = started_at
        self.completed_at = completed_at

    @staticmethod
    def from_dict(obj: Any) -> 'Entry':
        assert isinstance(obj, dict)
        media = from_union([Media.from_dict, from_none], obj.get("media"))
        status = from_union([Status, from_none], obj.get("status"))
        score = from_union([from_int, from_none], obj.get("score"))
        progress = from_union([from_int, from_none], obj.get("progress"))
        repeat = from_union([from_int, from_none], obj.get("repeat"))
        started_at = from_union([from_dict, from_none], obj.get("startedAt"))
        completed_at = from_union([from_dict, from_none], obj.get("completedAt"))
        return Entry(media, status, score, progress, repeat, started_at, completed_at)

    def to_dict(self) -> dict:
        result: dict = {"media": from_union([lambda x: to_class(Media, x), from_none], self.media),
                        "status": from_union([lambda x: to_enum(Status, x), from_none], self.status),
                        "score": from_union([from_int, from_none], self.score),
                        "progress": from_union([from_int, from_none], self.progress),
                        "repeat": from_union([from_int, from_none], self.repeat),
                        "startedAt": from_union([from_dict, from_none], self.started_at),
                        "completedAt": from_union([from_dict, from_none], self.completed_at)}
        return result


class ListElement:
    entries: Optional[List[Entry]]

    def __init__(self, entries: Optional[List[Entry]]) -> None:
        self.entries = entries

    @staticmethod
    def from_dict(obj: Any) -> 'ListElement':
        assert isinstance(obj, dict)
        entries = from_union([lambda x: from_list(Entry.from_dict, x), from_none], obj.get("entries"))
        return ListElement(entries)

    def to_dict(self) -> dict:
        result: dict = {
            "entries": from_union([lambda x: from_list(lambda x: to_class(Entry, x), x), from_none], self.entries)}
        return result


class MediaListOptions:
    score_format: Optional[str]

    def __init__(self, score_format: Optional[str]) -> None:
        self.score_format = score_format

    @staticmethod
    def from_dict(obj: Any) -> 'MediaListOptions':
        assert isinstance(obj, dict)
        score_format = from_union([from_str, from_none], obj.get("scoreFormat"))
        return MediaListOptions(score_format)

    def to_dict(self) -> dict:
        result: dict = {"scoreFormat": from_union([from_str, from_none], self.score_format)}
        return result


class User:
    id: Optional[int]
    media_list_options: Optional[MediaListOptions]

    def __init__(self, id_: Optional[int], media_list_options: Optional[MediaListOptions]) -> None:
        self.id = id_
        self.media_list_options = media_list_options

    @staticmethod
    def from_dict(obj: Any) -> 'User':
        assert isinstance(obj, dict)
        _id = from_union([from_int, from_none], obj.get("id"))
        media_list_options = from_union([MediaListOptions.from_dict, from_none], obj.get("mediaListOptions"))
        return User(_id, media_list_options)

    def to_dict(self) -> dict:
        result: dict = {"id": from_union([from_int, from_none], self.id),
                        "mediaListOptions": from_union([lambda x: to_class(MediaListOptions, x), from_none],
                                                       self.media_list_options)}
        return result


class MediaListCollection:
    user: Optional[User]
    lists: Optional[List[ListElement]]

    def __init__(self, user: Optional[User], lists: Optional[List[ListElement]]) -> None:
        self.user = user
        self.lists = lists

    @staticmethod
    def from_dict(obj: Any) -> 'MediaListCollection':
        assert isinstance(obj, dict)
        user = from_union([User.from_dict, from_none], obj.get("user"))
        lists = from_union([lambda x: from_list(ListElement.from_dict, x), from_none], obj.get("lists"))
        return MediaListCollection(user, lists)

    def to_dict(self) -> dict:
        result: dict = {"user": from_union([lambda x: to_class(User, x), from_none], self.user),
                        "lists": from_union([lambda x: from_list(lambda x: to_class(ListElement, x), x), from_none],
                                            self.lists)}
        return result


class Data:
    media_list_collection: Optional[MediaListCollection]

    def __init__(self, media_list_collection: Optional[MediaListCollection]) -> None:
        self.media_list_collection = media_list_collection

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        assert isinstance(obj, dict)
        media_list_collection = from_union([MediaListCollection.from_dict, from_none], obj.get("MediaListCollection"))
        return Data(media_list_collection)

    def to_dict(self) -> dict:
        result: dict = {"MediaListCollection": from_union([lambda x: to_class(MediaListCollection, x), from_none],
                                                          self.media_list_collection)}
        return result


class AnilistList:
    data: Optional[Data]

    def __init__(self, data: Optional[Data]) -> None:
        self.data = data

    @staticmethod
    def from_dict(obj: Any) -> 'AnilistList':
        assert isinstance(obj, dict)
        data = from_union([Data.from_dict, from_none], obj.get("data"))
        return AnilistList(data)

    def to_dict(self) -> dict:
        result: dict = {"data": from_union([lambda x: to_class(Data, x), from_none], self.data)}
        return result
