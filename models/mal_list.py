from typing import Any, TypeVar, Type, cast

T = TypeVar("T")


def from_int(x: Any) -> int:
    if x is None:
        x = 0
    return x


def from_str(x: Any) -> str:
    if not isinstance(x, str):
        x = str(x)
    return x


def from_bool(x: Any) -> bool:
    return x


def to_class(c: Type[T], x: Any) -> dict:
    return cast(Any, x).to_dict()


class MALAnimeListItem:
    status: int
    score: int
    tags: str
    is_rewatching: int
    num_watched_episodes: int
    anime_title: str
    anime_num_episodes: int
    anime_airing_status: int
    anime_id: int
    anime_studios: str
    anime_licensors: str
    anime_season: str
    has_episode_video: bool
    has_promotion_video: bool
    has_video: bool
    video_url: str
    anime_url: str
    anime_image_path: str
    is_added_to_list: bool
    anime_media_type_string: str
    anime_mpaa_rating_string: str
    start_date_string: str
    finish_date_string: str
    anime_start_date_string: str
    anime_end_date_string: str
    days_string: str
    storage_string: str
    priority_string: str

    def __init__(self, status: int, score: int, tags: str, is_rewatching: int, num_watched_episodes: int,
                 anime_title: str, anime_num_episodes: int, anime_airing_status: int, anime_id: int, anime_studios: str,
                 anime_licensors: str, anime_season: str, has_episode_video: bool, has_promotion_video: bool,
                 has_video: bool, video_url: str, anime_url: str, anime_image_path: str, is_added_to_list: bool,
                 anime_media_type_string: str, anime_mpaa_rating_string: str, start_date_string: str,
                 finish_date_string: str, anime_start_date_string: str, anime_end_date_string: str, days_string: str,
                 storage_string: str, priority_string: str) -> None:
        self.status = status
        self.score = score
        self.tags = tags
        self.is_rewatching = is_rewatching
        self.num_watched_episodes = num_watched_episodes
        self.anime_title = anime_title
        self.anime_num_episodes = anime_num_episodes
        self.anime_airing_status = anime_airing_status
        self.anime_id = anime_id
        self.anime_studios = anime_studios
        self.anime_licensors = anime_licensors
        self.anime_season = anime_season
        self.has_episode_video = has_episode_video
        self.has_promotion_video = has_promotion_video
        self.has_video = has_video
        self.video_url = video_url
        self.anime_url = anime_url
        self.anime_image_path = anime_image_path
        self.is_added_to_list = is_added_to_list
        self.anime_media_type_string = anime_media_type_string
        self.anime_mpaa_rating_string = anime_mpaa_rating_string
        self.start_date_string = start_date_string
        self.finish_date_string = finish_date_string
        self.anime_start_date_string = anime_start_date_string
        self.anime_end_date_string = anime_end_date_string
        self.days_string = days_string
        self.storage_string = storage_string
        self.priority_string = priority_string
        self.repeat = None
        self.rating_system = None

    @staticmethod
    def from_dict(obj: Any) -> 'MALAnimeListItem':
        assert isinstance(obj, dict)
        status = from_int(obj.get("status"))
        score = from_int(obj.get("score"))
        tags = from_str(obj.get("tags"))
        is_rewatching = from_int(obj.get("is_rewatching"))
        num_watched_episodes = from_int(obj.get("num_watched_episodes"))
        anime_title = from_str(obj.get("anime_title"))
        anime_num_episodes = from_int(obj.get("anime_num_episodes"))
        anime_airing_status = from_int(obj.get("anime_airing_status"))
        anime_id = from_int(obj.get("anime_id"))
        anime_studios = from_str(obj.get("anime_studios"))
        anime_licensors = from_str(obj.get("anime_licensors"))
        anime_season = from_str(obj.get("anime_season"))
        has_episode_video = from_bool(obj.get("has_episode_video"))
        has_promotion_video = from_bool(obj.get("has_promotion_video"))
        has_video = from_bool(obj.get("has_video"))
        video_url = from_str(obj.get("video_url"))
        anime_url = from_str(obj.get("anime_url"))
        anime_image_path = from_str(obj.get("anime_image_path"))
        is_added_to_list = from_bool(obj.get("is_added_to_list"))
        anime_media_type_string = from_str(obj.get("anime_media_type_string"))
        anime_mpaa_rating_string = from_str(obj.get("anime_mpaa_rating_string"))
        start_date_string = from_str(obj.get("start_date_string"))
        finish_date_string = from_str(obj.get("finish_date_string"))
        anime_start_date_string = from_str(obj.get("anime_start_date_string"))
        anime_end_date_string = from_str(obj.get("anime_end_date_string"))
        days_string = from_str(obj.get("days_string"))
        storage_string = from_str(obj.get("storage_string"))
        priority_string = from_str(obj.get("priority_string"))
        return MALAnimeListItem(status, score, tags, is_rewatching, num_watched_episodes, anime_title,
                                anime_num_episodes, anime_airing_status, anime_id, anime_studios, anime_licensors,
                                anime_season, has_episode_video, has_promotion_video, has_video, video_url, anime_url,
                                anime_image_path, is_added_to_list, anime_media_type_string, anime_mpaa_rating_string,
                                start_date_string, finish_date_string, anime_start_date_string, anime_end_date_string,
                                days_string, storage_string, priority_string)


class MALMangaListItem:
    id: int
    status: int
    score: int
    tags: str
    is_rereading: str
    num_read_chapters: int
    num_read_volumes: int
    manga_title: str
    manga_num_chapters: int
    manga_num_volumes: int
    manga_publishing_status: int
    manga_id: int
    manga_magazines: str
    manga_url: str
    manga_image_path: str
    is_added_to_list: bool
    manga_media_type_string: str
    start_date_string: str
    finish_date_string: str
    manga_start_date_string: str
    manga_end_date_string: str
    days_string: int
    retail_string: str
    priority_string: str

    def __init__(self, id: int, status: int, score: int, tags: str, is_rereading: str, num_read_chapters: int,
                 num_read_volumes: int, manga_title: str, manga_num_chapters: int, manga_num_volumes: int,
                 manga_publishing_status: int, manga_id: int, manga_magazines: str, manga_url: str,
                 manga_image_path: str, is_added_to_list: bool, manga_media_type_string: str, start_date_string: str,
                 finish_date_string: str, manga_start_date_string: str, manga_end_date_string: str, days_string: int,
                 retail_string: str, priority_string: str) -> None:
        self.id = id
        self.status = status
        self.score = score
        self.tags = tags
        self.is_rereading = is_rereading
        self.num_read_chapters = num_read_chapters
        self.num_read_volumes = num_read_volumes
        self.manga_title = manga_title
        self.manga_num_chapters = manga_num_chapters
        self.manga_num_volumes = manga_num_volumes
        self.manga_publishing_status = manga_publishing_status
        self.manga_id = manga_id
        self.manga_magazines = manga_magazines
        self.manga_url = manga_url
        self.manga_image_path = manga_image_path
        self.is_added_to_list = is_added_to_list
        self.manga_media_type_string = manga_media_type_string
        self.start_date_string = start_date_string
        self.finish_date_string = finish_date_string
        self.manga_start_date_string = manga_start_date_string
        self.manga_end_date_string = manga_end_date_string
        self.days_string = days_string
        self.retail_string = retail_string
        self.priority_string = priority_string
        self.repeat = None
        self.rating_system = None

    @staticmethod
    def from_dict(obj: Any) -> 'MALMangaListItem':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        status = from_int(obj.get("status"))
        score = from_int(obj.get("score"))
        tags = from_str(obj.get("tags"))
        is_rereading = from_str(str(obj.get("is_rereading")))
        num_read_chapters = from_int(obj.get("num_read_chapters"))
        num_read_volumes = from_int(obj.get("num_read_volumes"))
        manga_title = from_str(obj.get("manga_title"))
        manga_num_chapters = from_int(obj.get("manga_num_chapters"))
        manga_num_volumes = from_int(obj.get("manga_num_volumes"))
        manga_publishing_status = from_int(obj.get("manga_publishing_status"))
        manga_id = from_int(obj.get("manga_id"))
        manga_magazines = from_str(obj.get("manga_magazines"))
        manga_url = from_str(obj.get("manga_url"))
        manga_image_path = from_str(obj.get("manga_image_path"))
        is_added_to_list = from_bool(obj.get("is_added_to_list"))
        manga_media_type_string = from_str(obj.get("manga_media_type_string"))
        start_date_string = from_str(obj.get("start_date_string"))
        finish_date_string = from_str(obj.get("finish_date_string"))
        manga_start_date_string = from_str(obj.get("manga_start_date_string"))
        manga_end_date_string = from_str(obj.get("manga_end_date_string"))
        days_string = from_int(obj.get("days_string"))
        retail_string = from_str(obj.get("retail_string"))
        priority_string = from_str(obj.get("priority_string"))
        return MALMangaListItem(id, status, score, tags, is_rereading, num_read_chapters, num_read_volumes,
                                manga_title, manga_num_chapters, manga_num_volumes, manga_publishing_status,
                                manga_id, manga_magazines, manga_url, manga_image_path, is_added_to_list,
                                manga_media_type_string, start_date_string, finish_date_string, manga_start_date_string,
                                manga_end_date_string, days_string, retail_string, priority_string)
