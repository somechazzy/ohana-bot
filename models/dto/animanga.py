"""
To contain DTOs of entities enriched with data from MyAnimeList and AniList. Profiles, lists. anime, manga, etc...
"""
from datetime import datetime, UTC

from constants import AnimangaProvider, UserAnimangaListScoringSystem, MAL_USER_ANIME_STATUS_MAPPING, \
    MAL_USER_MANGA_STATUS_MAPPING, MAL_ANIME_MEDIA_TYPE_MAPPING, MAL_MANGA_MEDIA_TYPE_MAPPING, \
    MAL_ANIME_AIRING_STATUS_MAPPING, MAL_ANIME_SEASON_MAPPING, MAL_ANIME_MEDIA_SOURCE_MAPPING, \
    MAL_MANGA_PUBLISHING_STATUS_MAPPING, UserAnimeStatus, UserMangaStatus, ANILIST_ANIME_MEDIA_TYPE_MAPPING, \
    ANILIST_MANGA_MEDIA_TYPE_MAPPING, ANILIST_ANIME_AIRING_STATUS_MAPPING, ANILIST_ANIME_SEASON_MAPPING, \
    ANILIST_ANIME_MEDIA_SOURCE_MAPPING, ANILIST_MANGA_PUBLISHING_STATUS_MAPPING, ANILIST_SCORING_SYSTEM_MAPPING, \
    ANILIST_USER_ANIME_STATUS_MAPPING, ANILIST_USER_MANGA_STATUS_MAPPING, Links, AnimangaListLoadingStatus
from strings.integrations_strings import AnilistStrings
from utils.helpers.datetime_helpers import parse_mal_user_entry_date, parse_fuzzy_anilist_date_into_str
from utils.helpers.text_parsing_helpers import clean_text_with_html_tags
from utils.web_parsers.mal_profile_parser import MyAnimeListProfileParser


class UserAnimangaProfile:
    def __init__(self,
                 source_data: str | dict,
                 source_provider: str,  # AnimangaProvider
                 username: str,
                 user_id: int | None,
                 display_name: str,
                 avatar_image_url: str,
                 banner_image_url: str,
                 anime_stats: 'UserAnimeStats',
                 manga_stats: 'UserMangaStats',
                 favorites: 'UserAnimangaFavorites',
                 created_at: datetime | str,
                 updated_at: datetime | str,
                 location: str | None = None,
                 birthday: str | None = None,
                 gender: str | None = None,
                 anime_list: 'UserAnimeList | None' = None,
                 manga_list: 'UserMangaList | None' = None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.username: str = username
        self.user_id: int | None = user_id
        self.display_name: str = display_name
        self.avatar_image_url: str = avatar_image_url
        self.banner_image_url: str = banner_image_url
        self.anime_stats: 'UserAnimeStats' = anime_stats
        self.manga_stats: 'UserMangaStats' = manga_stats
        self.favorites: 'UserAnimangaFavorites' = favorites
        self.created_at: datetime | str = created_at
        self.updated_at: datetime | str = updated_at
        self.location: str | None = location
        self.birthday: str | None = birthday
        self.gender: str | None = gender
        self.anime_list: 'UserAnimeList | None' = anime_list
        self.manga_list: 'UserMangaList | None' = manga_list
        self._anime_analysis: 'UserAnimeAnalysis | None' = None
        self._manga_analysis: 'UserMangaAnalysis | None' = None
        self.anime_list_loading_status: str = AnimangaListLoadingStatus.PENDING
        self.manga_list_loading_status: str = AnimangaListLoadingStatus.PENDING

    @classmethod
    def from_mal_data(cls,
                      username: str,
                      profile_webpage: str,
                      anime_list: list[dict] | None = None,
                      manga_list: list[dict] | None = None) -> 'UserAnimangaProfile':
        profile_parser = MyAnimeListProfileParser(webpage_html=profile_webpage)

        return cls(
            source_data=profile_webpage,
            source_provider=AnimangaProvider.MAL,
            username=username,
            user_id=None,
            display_name=username,
            avatar_image_url=profile_parser.get_avatar_url(),
            banner_image_url=profile_parser.get_banner_url(),
            anime_stats=UserAnimeStats.from_mal_data(profile_parser=profile_parser),
            manga_stats=UserMangaStats.from_mal_data(profile_parser=profile_parser),
            favorites=UserAnimangaFavorites.from_mal_data(profile_parser=profile_parser),
            created_at=profile_parser.get_joined_at(),
            updated_at=profile_parser.get_last_online_at(),
            location=profile_parser.get_location(),
            birthday=profile_parser.get_birthday(),
            gender=profile_parser.get_gender(),
            anime_list=UserAnimeList.from_mal_data(anime_list, username=username) if anime_list else None,
            manga_list=UserMangaList.from_mal_data(manga_list, username=username) if manga_list else None
        )

    @classmethod
    def from_anilist_data(cls,
                          profile_data: dict,
                          username: str,
                          anime_list: dict | None = None,
                          manga_list: dict | None = None) -> 'UserAnimangaProfile':
        return cls(
            source_data=profile_data,
            source_provider=AnimangaProvider.ANILIST,
            username=username,
            user_id=profile_data['id'],
            display_name=profile_data['name'],
            avatar_image_url=profile_data['avatar']['large'],
            banner_image_url=profile_data['bannerImage'],
            anime_stats=UserAnimeStats.from_anilist_data(profile_data['statistics']['anime']),
            manga_stats=UserMangaStats.from_anilist_data(profile_data['statistics']['manga']),
            favorites=UserAnimangaFavorites.from_anilist_data(profile_data['favourites']),
            created_at=datetime.fromtimestamp(profile_data['createdAt'], tz=UTC),
            updated_at=datetime.fromtimestamp(profile_data['updatedAt'], tz=UTC),
            location=None,
            birthday=None,
            gender=None,
            anime_list=UserAnimeList.from_anilist_data(anime_list, username=username) if anime_list else None,
            manga_list=UserMangaList.from_anilist_data(manga_list, username=username) if manga_list else None
        )

    @property
    def anime_analysis(self) -> 'UserAnimeAnalysis':
        if self.source_provider == AnimangaProvider.MAL:
            raise NotImplementedError
        if self._anime_analysis is None:
            self._anime_analysis = UserAnimeAnalysis.from_user_profile(self)
        return self._anime_analysis
    
    @property
    def manga_analysis(self) -> 'UserMangaAnalysis':
        if self.source_provider == AnimangaProvider.MAL:
            raise NotImplementedError
        if self._manga_analysis is None:
            self._manga_analysis = UserMangaAnalysis.from_user_profile(self)
        return self._manga_analysis

    @property
    def web_url(self) -> str:
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_PROFILE_URL.format(username=self.username)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_PROFILE_URL.format(username=self.username)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class UserAnimeStats:
    def __init__(self,
                 source_data: str | dict,
                 source_provider: str,  # AnimangaProvider
                 total_entries_count: int,
                 mean_score: float,
                 days_watched: float,
                 completed_count: int,
                 watching_count: int | None,
                 total_episodes: int | None,
                 rewatched_count: int | None):
        self.source_data: str | dict = source_data
        self.source_provider: str = source_provider
        self.total_entries_count: int = total_entries_count
        self.mean_score: float = mean_score
        self.days_watched: float = days_watched
        self.completed_count: int = completed_count
        self.watching_count: int | None = watching_count
        self.total_episodes: int | None = total_episodes
        self.rewatched_count: int | None = rewatched_count

    @classmethod
    def from_mal_data(cls,
                      profile_webpage: str | None = None,
                      profile_parser: MyAnimeListProfileParser | None = None) -> 'UserAnimeStats':
        if not profile_webpage and not profile_parser:
            raise ValueError("Either profile_webpage or profile_parser must be passed.")
        if not profile_parser:
            profile_parser = MyAnimeListProfileParser(webpage_html=profile_webpage)

        return cls(
            source_data=profile_webpage or profile_parser.webpage_html,
            source_provider=AnimangaProvider.MAL,
            total_entries_count=profile_parser.get_anime_total_entries_count(),
            mean_score=round(profile_parser.get_anime_mean_score() or 0, 2),
            days_watched=round(profile_parser.get_anime_days_watched() or 0, 2),
            completed_count=profile_parser.get_anime_completed_count(),
            watching_count=profile_parser.get_anime_watching_count(),
            total_episodes=profile_parser.get_anime_total_episodes(),
            rewatched_count=profile_parser.get_anime_rewatched_count()
        )

    @classmethod
    def from_anilist_data(cls, stats_data: dict) -> 'UserAnimeStats':
        status_count_map = {
            status['status']: status['count'] for status in stats_data['statuses']
        }
        return cls(
            source_data=stats_data,
            source_provider=AnimangaProvider.ANILIST,
            total_entries_count=stats_data['count'],
            mean_score=round(stats_data['meanScore'] / 10, 2),
            days_watched=round(stats_data['minutesWatched'] / (60 * 24), 1),
            completed_count=status_count_map.get('COMPLETED'),
            watching_count=status_count_map.get('CURRENT'),
            total_episodes=None,
            rewatched_count=status_count_map.get('REPEATING', 0)
        )


class UserMangaStats:
    def __init__(self,
                 source_data: str | dict,
                 source_provider: str,  # AnimangaProvider
                 total_entries_count: int,
                 mean_score: float,
                 days_read: float,
                 completed_count: int | None,
                 reading_count: int,
                 total_chapters: int,
                 reread_count: int | None):
        self.source_data: str | dict = source_data
        self.source_provider: str = source_provider
        self.total_entries_count: int = total_entries_count
        self.mean_score: float = mean_score
        self.days_read: float = days_read
        self.completed_count: int | None = completed_count
        self.reading_count: int = reading_count
        self.total_chapters: int = total_chapters
        self.reread_count: int | None = reread_count

    @classmethod
    def from_mal_data(cls,
                      profile_webpage: str | None = None,
                      profile_parser: MyAnimeListProfileParser | None = None) -> 'UserMangaStats':
        if not profile_webpage and not profile_parser:
            raise ValueError("Either profile_webpage or profile_parser must be passed.")
        if not profile_parser:
            profile_parser = MyAnimeListProfileParser(webpage_html=profile_webpage)

        return cls(
            source_data=profile_webpage or profile_parser.webpage_html,
            source_provider=AnimangaProvider.MAL,
            total_entries_count=profile_parser.get_manga_total_entries_count(),
            mean_score=round(profile_parser.get_manga_mean_score() or 0, 2),
            days_read=round(profile_parser.get_manga_days_read() or 0, 2),
            completed_count=profile_parser.get_manga_completed_count(),
            reading_count=profile_parser.get_manga_reading_count(),
            total_chapters=profile_parser.get_manga_total_chapters(),
            reread_count=profile_parser.get_manga_reread_count()
        )

    @classmethod
    def from_anilist_data(cls, stats_data: dict) -> 'UserMangaStats':
        status_count_map = {
            status['status']: status['count'] for status in stats_data['statuses']
        }
        return cls(
            source_data=stats_data,
            source_provider=AnimangaProvider.ANILIST,
            total_entries_count=stats_data['count'],
            mean_score=round(stats_data['meanScore'] / 10, 2),
            days_read=round(stats_data['chaptersRead'] * 7.5 / (60 * 24), 1),  # Assuming 7.5 minutes per chapter
            completed_count=status_count_map.get('COMPLETED'),
            reading_count=status_count_map.get('CURRENT'),
            total_chapters=stats_data['chaptersRead'],
            reread_count=status_count_map.get('REPEATING', 0)
        )


class UserAnimeList:
    def __init__(self,
                 source_data: list | dict,
                 source_provider: str,  # AnimangaProvider
                 username: str,
                 entries: list['UserAnimeListEntry'],
                 scoring_system: str):
        self.source_data: list | dict = source_data
        self.source_provider: str = source_provider
        self.username: str = username
        self.entries: list['UserAnimeListEntry'] = entries
        self.scoring_system: str = scoring_system  # UserAnimangaListScoringSystem

    @classmethod
    def from_mal_data(cls, list_data: list[dict], username: str) -> 'UserAnimeList':
        return cls(
            source_data=list_data,
            source_provider=AnimangaProvider.MAL,
            username=username,
            entries=[UserAnimeListEntry.from_mal_data(entry_data=entry_data, username=username)
                     for entry_data in list_data],
            scoring_system=UserAnimangaListScoringSystem.ZERO_TO_TEN
        )

    @classmethod
    def from_anilist_data(cls, list_data: dict, username: str) -> 'UserAnimeList':
        return cls(
            source_data=list_data,
            source_provider=AnimangaProvider.ANILIST,
            username=username,
            entries=[UserAnimeListEntry.from_anilist_data(entry_data=entry_data, username=username)
                     for entry_data in UserAnimeList.merge_anilist_ordered_anime_lists(lists=list_data['lists'])],
            scoring_system=ANILIST_SCORING_SYSTEM_MAPPING[list_data['user']['mediaListOptions']['scoreFormat']]
        )

    @staticmethod
    def merge_anilist_ordered_anime_lists(lists: dict,) -> list[dict]:
        """
        Merge user's AniList's lists and order them by status
        """
        status_list_map = {list_data['status']: list_data['entries'] for list_data in lists}
        ordered_entries = []
        for status in ['REPEATING', 'CURRENT', 'COMPLETED', 'PAUSED', 'PLANNING', 'DROPPED']:
            if status in status_list_map:
                ordered_entries.extend(status_list_map[status])
        return ordered_entries

    @property
    def web_url(self):
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_ANIME_LIST_URL.format(username=self.username)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_ANIME_LIST_URL.format(username=self.username)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class UserMangaList:
    def __init__(self,
                 source_data: list | dict,
                 source_provider: str,  # AnimangaProvider
                 username: str,
                 entries: list['UserMangaListEntry'],
                 scoring_system: str):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.username: str = username
        self.entries: list['UserMangaListEntry'] = entries
        self.scoring_system: str = scoring_system

    @classmethod
    def from_mal_data(cls, list_data: list[dict], username: str) -> 'UserMangaList':
        return cls(
            source_data=list_data,
            source_provider=AnimangaProvider.MAL,
            username=username,
            entries=[UserMangaListEntry.from_mal_data(entry_data=entry_data, username=username)
                     for entry_data in list_data],
            scoring_system=UserAnimangaListScoringSystem.ZERO_TO_TEN
        )

    @classmethod
    def from_anilist_data(cls, list_data: dict, username: str) -> 'UserMangaList':
        return cls(
            source_data=list_data,
            source_provider=AnimangaProvider.ANILIST,
            username=username,
            entries=[UserMangaListEntry.from_anilist_data(entry_data=entry_data, username=username)
                     for entry_data in UserMangaList.merge_anilist_ordered_manga_lists(lists=list_data['lists'])],
            scoring_system=ANILIST_SCORING_SYSTEM_MAPPING[list_data['user']['mediaListOptions']['scoreFormat']]
        )

    @staticmethod
    def merge_anilist_ordered_manga_lists(lists: dict,) -> list[dict]:
        """
        Merge user's AniList's lists and order them by status
        """
        status_list_map = {list_data['status']: list_data['entries'] for list_data in lists}
        ordered_entries = []
        for status in ['REPEATING', 'CURRENT', 'COMPLETED', 'PAUSED', 'PLANNING', 'DROPPED']:
            if status in status_list_map:
                ordered_entries.extend(status_list_map[status])
        return ordered_entries

    @property
    def web_url(self):
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_MANGA_LIST_URL.format(username=self.username)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_MANGA_LIST_URL.format(username=self.username)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class UserAnimangaFavorites:
    def __init__(self,
                 source_data: str | dict,
                 source_provider: str,  # AnimangaProvider
                 anime: list['UserAnimangaFavoritesEntry'],
                 manga: list['UserAnimangaFavoritesEntry'],
                 characters: list['UserAnimangaFavoritesEntry'],
                 people: list['UserAnimangaFavoritesEntry'],
                 studios: list['UserAnimangaFavoritesEntry']):
        self.source_data: str | dict = source_data
        self.source_provider: str = source_provider
        self.anime: list['UserAnimangaFavoritesEntry'] = anime
        self.manga: list['UserAnimangaFavoritesEntry'] = manga
        self.characters: list['UserAnimangaFavoritesEntry'] = characters
        self.people: list['UserAnimangaFavoritesEntry'] = people
        self.studios: list['UserAnimangaFavoritesEntry'] = studios

    @classmethod
    def from_mal_data(cls,
                      profile_webpage: str | None = None,
                      profile_parser: MyAnimeListProfileParser | None = None) -> 'UserAnimangaFavorites':
        if not profile_webpage and not profile_parser:
            raise ValueError("Either profile_webpage or profile_parser must be passed.")
        if not profile_parser:
            profile_parser = MyAnimeListProfileParser(webpage_html=profile_webpage)

        return cls(
            source_data=profile_webpage or profile_parser.webpage_html,
            source_provider=AnimangaProvider.MAL,
            anime=[UserAnimangaFavoritesEntry(
                profile_parser.webpage_html,
                AnimangaProvider.MAL,
                *parsed_anime_favorite_url_and_title
            ) for parsed_anime_favorite_url_and_title in profile_parser.get_anime_favorites_urls_and_titles()],
            manga=[UserAnimangaFavoritesEntry(
                profile_parser.webpage_html,
                AnimangaProvider.MAL,
                *parsed_manga_favorite_url_and_title
            ) for parsed_manga_favorite_url_and_title in profile_parser.get_manga_favorites_urls_and_titles()],
            characters=[UserAnimangaFavoritesEntry(
                profile_parser.webpage_html,
                AnimangaProvider.MAL,
                *parsed_character_favorite_url_and_name
            ) for parsed_character_favorite_url_and_name in profile_parser.get_character_favorites_urls_and_titles()],
            people=[UserAnimangaFavoritesEntry(
                profile_parser.webpage_html,
                AnimangaProvider.MAL,
                *parsed_person_favorite_url_and_name
            ) for parsed_person_favorite_url_and_name in profile_parser.get_person_favorites_urls_and_titles()],
            studios=[UserAnimangaFavoritesEntry(
                profile_parser.webpage_html,
                AnimangaProvider.MAL,
                *parsed_studio_favorite_url_and_name
            ) for parsed_studio_favorite_url_and_name in profile_parser.get_studio_favorites_urls_and_titles()],
        )

    @classmethod
    def from_anilist_data(cls, favorites_data: dict) -> 'UserAnimangaFavorites':
        return cls(
            source_data=favorites_data,
            source_provider=AnimangaProvider.ANILIST,
            anime=[UserAnimangaFavoritesEntry.from_anilist_anime_or_manga(entry_data)
                   for entry_data in (favorites_data.get('anime') or {}).get('nodes', [])],
            manga=[UserAnimangaFavoritesEntry.from_anilist_anime_or_manga(entry_data)
                   for entry_data in (favorites_data.get('manga') or {}).get('nodes', [])],
            characters=[UserAnimangaFavoritesEntry.from_anilist_character_or_staff(entry_data)
                        for entry_data in (favorites_data.get('characters') or {}).get('nodes', [])],
            people=[UserAnimangaFavoritesEntry.from_anilist_character_or_staff(entry_data)
                    for entry_data in (favorites_data.get('staff') or {}).get('nodes', [])],
            studios=[UserAnimangaFavoritesEntry.from_anilist_studio(entry_data)
                     for entry_data in (favorites_data.get('studios') or {}).get('nodes', [])]
        )


class UserAnimeListEntry:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 username: str,
                 anime_id: int,
                 title: str,
                 status: str,
                 watched_episodes_count: int | None,
                 rewatch_count: int | None,
                 started_at: datetime | str | None,
                 finished_at: datetime | str | None,
                 user_score: float | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.username: str = username
        self.anime_id: int = anime_id
        self.title: str = title
        self.status: str = status
        self.watched_episodes_count: int | None = watched_episodes_count
        self.rewatch_count: int | None = rewatch_count
        self.started_at: datetime | str | None = started_at
        self.finished_at: datetime | str | None = finished_at
        self.user_score: float | None = user_score

    @classmethod
    def from_mal_data(cls, entry_data: dict, username: str) -> 'UserAnimeListEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.MAL,
            username=username,
            anime_id=entry_data['anime_id'],
            title=entry_data['anime_title'],
            status=MAL_USER_ANIME_STATUS_MAPPING.get(entry_data['status'], "?"),
            watched_episodes_count=entry_data['num_watched_episodes'],
            rewatch_count=None,
            started_at=parse_mal_user_entry_date(entry_data['start_date_string']),
            finished_at=parse_mal_user_entry_date(entry_data['finish_date_string']),
            user_score=entry_data['score'] or None
        )

    @classmethod
    def from_anilist_data(cls, entry_data: dict, username: str) -> 'UserAnimeListEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            username=username,
            anime_id=entry_data['media']['id'],
            title=entry_data['media']['title'].get('romaji') or entry_data['media']['title'].get('english'),
            status=ANILIST_USER_ANIME_STATUS_MAPPING[entry_data['status']],
            watched_episodes_count=entry_data['progress'],
            rewatch_count=entry_data['repeat'],
            started_at=parse_fuzzy_anilist_date_into_str(entry_data['startedAt']),
            finished_at=parse_fuzzy_anilist_date_into_str(entry_data['completedAt']),
            user_score=entry_data['score'] or None
        )

    @classmethod
    def as_empty_entry(cls,
                       anime_id: int,
                       username: str,
                       provider: str) -> 'UserAnimeListEntry':
        return cls(
            source_data={},
            source_provider=provider,
            username=username,
            anime_id=anime_id,
            title="",
            status=UserAnimeStatus.NOT_ON_LIST,
            watched_episodes_count=None,
            rewatch_count=0,
            started_at=None,
            finished_at=None,
            user_score=None
        )

    @property
    def anime_web_url(self) -> str:
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_ANIME_URL.format(anime_id=self.anime_id)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_ANIME_URL.format(anime_id=self.anime_id)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class UserMangaListEntry:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 username: str,
                 manga_id: int,
                 title: str,
                 status: str,
                 read_chapters_count: int | None,
                 started_at: datetime | str | None,
                 finished_at: datetime | str | None,
                 user_score: float | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.username: str = username
        self.manga_id: int = manga_id
        self.title: str = title
        self.status: str = status
        self.read_chapters_count: int | None = read_chapters_count
        self.started_at: datetime | str | None = started_at
        self.finished_at: datetime | str | None = finished_at
        self.user_score: float | None = user_score

    @classmethod
    def from_mal_data(cls, entry_data: dict, username: str) -> 'UserMangaListEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.MAL,
            username=username,
            manga_id=entry_data['manga_id'],
            title=entry_data['manga_title'],
            status=MAL_USER_MANGA_STATUS_MAPPING.get(entry_data['status'], "?"),
            read_chapters_count=entry_data['num_read_chapters'],
            started_at=parse_mal_user_entry_date(entry_data['start_date_string']),
            finished_at=parse_mal_user_entry_date(entry_data['finish_date_string']),
            user_score=entry_data['score'] or None
        )

    @classmethod
    def from_anilist_data(cls, entry_data: dict, username: str) -> 'UserMangaListEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            username=username,
            manga_id=entry_data['media']['id'],
            title=entry_data['media']['title'].get('romaji') or entry_data['media']['title'].get('english'),
            status=ANILIST_USER_MANGA_STATUS_MAPPING[entry_data['status']],
            read_chapters_count=entry_data['progress'],
            started_at=parse_fuzzy_anilist_date_into_str(entry_data['startedAt']),
            finished_at=parse_fuzzy_anilist_date_into_str(entry_data['completedAt']),
            user_score=entry_data['score'] or None
        )

    @classmethod
    def as_empty_entry(cls,
                       manga_id: int,
                       username: str,
                       provider: str) -> 'UserMangaListEntry':
        return cls(
            source_data={},
            source_provider=provider,
            username=username,
            manga_id=manga_id,
            title="",
            status=UserMangaStatus.NOT_ON_LIST,
            read_chapters_count=None,
            started_at=None,
            finished_at=None,
            user_score=None
        )

    @property
    def manga_web_url(self) -> str:
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_MANGA_URL.format(manga_id=self.manga_id)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_MANGA_URL.format(manga_id=self.manga_id)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class UserAnimangaFavoritesEntry:
    def __init__(self,
                 source_data: str | dict,
                 source_provider: str,  # AnimangaProvider
                 title: str,
                 item_url: str):
        self.source_data: str | dict = source_data
        self.source_provider: str = source_provider
        self.item_url: str = item_url
        self.title: str = title

    @classmethod
    def from_anilist_anime_or_manga(cls, entry_data: dict) -> 'UserAnimangaFavoritesEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            item_url=entry_data['siteUrl'],
            title=entry_data['title'].get('romaji') or entry_data['title'].get('english')
        )

    @classmethod
    def from_anilist_character_or_staff(cls, entry_data: dict) -> 'UserAnimangaFavoritesEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            item_url=entry_data['siteUrl'],
            title=entry_data['name'].get('full')
        )

    @classmethod
    def from_anilist_studio(cls, entry_data: dict) -> 'UserAnimangaFavoritesEntry':
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            item_url=entry_data['siteUrl'],
            title=entry_data['name']
        )


class AnimeInfo:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 anime_id: int,
                 native_title: str,
                 english_title: str | None,
                 score: float | None,
                 score_count: int,
                 user_count: int,
                 rank: int | None,
                 episode_count: int | None,
                 duration_in_minutes: int | None,
                 status: str,  # AnimeAiringStatus
                 start_date: datetime | str | None,
                 end_date: datetime | str | None,
                 year: int | None,
                 season: str | None,  # AnimeSeason
                 genres: list[str],
                 themes: list[str] | None,
                 studios: list[str] | None,
                 synopsis: str | None,
                 media_type: str | None,  # AnimeMediaType
                 media_source: str | None,  # AnimeMediaSource
                 poster_url: str | None,
                 banner_url: str | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.anime_id: int = anime_id
        self.native_title: str = native_title
        self.english_title: str | None = english_title
        self.score: float | None = score
        self.score_count: int = score_count
        self.user_count: int = user_count
        self.rank: int | None = rank
        self.episode_count: int | None = episode_count
        self.duration_in_minutes: int | None = duration_in_minutes
        self.status: str = status
        self.start_date: datetime | str | None = start_date
        self.end_date: datetime | str | None = end_date
        self.year: int | None = year
        self.season: str | None = season
        self.genres: list[str] = genres
        self.themes: list[str] | None = themes
        self.studios: list[str] | None = studios
        self.synopsis: str | None = synopsis
        self.media_type: str | None = media_type
        self.media_source: str | None = media_source
        self.poster_url: str | None = poster_url
        self.banner_url: str | None = banner_url

    @classmethod
    def from_mal_data(cls, anime_data: dict) -> 'AnimeInfo':
        return cls(
            source_data=anime_data,
            source_provider=AnimangaProvider.MAL,
            anime_id=anime_data['id'],
            native_title=anime_data['title'],
            english_title=anime_data['alternative_titles'].get('en'),
            score=anime_data.get('mean'),
            score_count=anime_data.get('num_scoring_users'),
            user_count=anime_data.get('num_list_users'),
            rank=anime_data.get('rank'),
            episode_count=anime_data.get('num_episodes'),
            duration_in_minutes=anime_data.get('average_episode_duration') // 60
            if anime_data.get('average_episode_duration') else None,
            status=MAL_ANIME_AIRING_STATUS_MAPPING.get(anime_data['status'], '?'),
            start_date=anime_data.get('start_date'),
            end_date=anime_data.get('end_date'),
            year=(anime_data.get('start_season') or {}).get('year'),
            season=MAL_ANIME_SEASON_MAPPING.get((anime_data.get('start_season') or {}).get('season')),
            genres=[genre['name'] for genre in anime_data.get('genres', [])],
            themes=None,
            studios=[studio['name'] for studio in anime_data.get('studios', [])],
            synopsis=anime_data.get('synopsis'),
            media_type=MAL_ANIME_MEDIA_TYPE_MAPPING.get(anime_data.get('media_type', '').lower(),
                                                        anime_data.get('media_type', '').replace('_', ' ').title())
            if anime_data.get('media_type') else None,
            media_source=MAL_ANIME_MEDIA_SOURCE_MAPPING.get(anime_data.get('source', '').lower(),
                                                            anime_data.get('source', '').replace('_', ' ').title())
            if anime_data.get('source') else None,
            poster_url=anime_data.get('main_picture', {}).get('medium')
            or anime_data.get('main_picture', {}).get('large'),
            banner_url=None
        )

    @classmethod
    def from_anilist_data(cls, anime_data: dict) -> 'AnimeInfo':
        rated_all_time_rank = [ranking for ranking in anime_data['rankings']
                               if ranking['type'] == 'RATED' and ranking['allTime']]
        start_date_parsed = parse_fuzzy_anilist_date_into_str(anime_data['startDate'])
        end_date_parsed = parse_fuzzy_anilist_date_into_str(anime_data['endDate'])
        return cls(
            source_data=anime_data,
            source_provider=AnimangaProvider.ANILIST,
            anime_id=anime_data['id'],
            native_title=anime_data['title'].get('romaji'),
            english_title=anime_data['title'].get('english'),
            score=round(anime_data['meanScore']/10, 2) if anime_data.get('meanScore') else None,
            score_count=sum(score['amount'] for score in anime_data['stats']['scoreDistribution']),
            user_count=anime_data['popularity'],
            rank=rated_all_time_rank[0]['rank'] if rated_all_time_rank else None,
            episode_count=anime_data['episodes'],
            duration_in_minutes=anime_data['duration'],
            status=ANILIST_ANIME_AIRING_STATUS_MAPPING.get(anime_data['status'],
                                                           anime_data['status'].replace('_', ' ').title()),
            start_date=start_date_parsed,
            end_date=end_date_parsed,
            year=anime_data['seasonYear'],
            season=ANILIST_ANIME_SEASON_MAPPING.get(anime_data['season']),
            genres=anime_data['genres'],
            themes=[tag['name'] for tag in anime_data['tags']
                    if not tag['isMediaSpoiler'] and not tag['isGeneralSpoiler']],
            studios=[studio['name'] for studio in anime_data['studios']['nodes']],
            synopsis=clean_text_with_html_tags(html_text=anime_data.get('description')),
            media_type=ANILIST_ANIME_MEDIA_TYPE_MAPPING.get(anime_data['format'].lower(),
                                                            anime_data['format'].replace('_', ' ').title())
            if anime_data.get('format') else None,
            media_source=ANILIST_ANIME_MEDIA_SOURCE_MAPPING.get(anime_data['source'].lower(),
                                                                anime_data['source'].replace('_', ' ').title())
            if anime_data.get('source') else None,
            poster_url=anime_data.get('coverImage', {}).get('large'),
            banner_url=anime_data.get('bannerImage')
        )

    @property
    def web_url(self) -> str:
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_ANIME_URL.format(anime_id=self.anime_id)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_ANIME_URL.format(anime_id=self.anime_id)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class MangaInfo:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 manga_id: int,
                 native_title: str,
                 english_title: str | None,
                 score: float | None,
                 score_count: int,
                 user_count: int,
                 rank: int | None,
                 chapter_count: int | None,
                 volume_count: int | None,
                 status: str,  # MangaStatus
                 start_date: datetime | str | None,
                 end_date: datetime | str | None,
                 year: int | None,
                 genres: list[str],
                 themes: list[str] | None,
                 authors: list[str] | None,
                 synopsis: str | None,
                 media_type: str | None,  # MangaMediaType
                 poster_url: str | None,
                 banner_url: str | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.manga_id: int = manga_id
        self.native_title: str = native_title
        self.english_title: str | None = english_title
        self.score: float | None = score
        self.score_count: int = score_count
        self.user_count: int = user_count
        self.rank: int | None = rank
        self.chapter_count: int | None = chapter_count
        self.volume_count: int | None = volume_count
        self.status: str = status
        self.start_date: datetime | str | None = start_date
        self.end_date: datetime | str | None = end_date
        self.year: int | None = year
        self.genres: list[str] = genres
        self.themes: list[str] | None = themes
        self.authors: list[str] | None = authors
        self.synopsis: str | None = synopsis
        self.media_type: str | None = media_type
        self.poster_url: str | None = poster_url
        self.banner_url: str | None = banner_url

    @classmethod
    def from_mal_data(cls, manga_data: dict) -> 'MangaInfo':
        return cls(
            source_data=manga_data,
            source_provider=AnimangaProvider.MAL,
            manga_id=manga_data['id'],
            native_title=manga_data['title'],
            english_title=manga_data['alternative_titles'].get('en'),
            score=manga_data['mean'],
            score_count=manga_data['num_scoring_users'],
            user_count=manga_data['num_list_users'],
            rank=manga_data.get('rank'),
            chapter_count=manga_data.get('num_chapters'),
            volume_count=manga_data.get('num_volumes'),
            status=MAL_MANGA_PUBLISHING_STATUS_MAPPING.get(manga_data['status'],
                                                           manga_data['status'].replace('_', ' ').title()),
            start_date=manga_data.get('start_date'),
            end_date=manga_data.get('end_date'),
            year=int(manga_data['start_date'].split('-')[0]) if manga_data.get('start_date') else None,
            genres=[genre['name'] for genre in manga_data.get('genres', [])],
            themes=None,
            authors=[
                (author['node']['first_name'] + ' ' + author['node']['last_name']).strip()
                + ((' (' + author['role'] + ')') if author.get('role') else '')
                for author in manga_data.get('authors', [])
            ],
            synopsis=manga_data.get('synopsis'),
            media_type=MAL_MANGA_MEDIA_TYPE_MAPPING.get(manga_data.get('media_type', '').lower(),
                                                        manga_data.get('media_type').replace('_', ' ').title())
            if manga_data.get('media_type') else None,
            poster_url=manga_data.get('main_picture', {}).get('medium')
            or manga_data.get('main_picture', {}).get('large'),
            banner_url=None
        )

    @classmethod
    def from_anilist_data(cls, manga_data: dict) -> 'MangaInfo':
        rated_all_time_rank = [ranking for ranking in manga_data['rankings']
                               if ranking['type'] == 'RATED' and ranking['allTime']]
        start_date_parsed = parse_fuzzy_anilist_date_into_str(manga_data['startDate'])
        end_date_parsed = parse_fuzzy_anilist_date_into_str(manga_data['endDate'])
        authors = [f"{edge['node']['name']['full']} ({edge['role']})"
                   for edge in manga_data['staff']['edges']
                   if any(role_name in edge['role'].lower() for role_name in ['writer', 'story', 'art'])]
        return cls(
            source_data=manga_data,
            source_provider=AnimangaProvider.ANILIST,
            manga_id=manga_data['id'],
            native_title=manga_data['title'].get('romaji'),
            english_title=manga_data['title'].get('english'),
            score=round(manga_data['meanScore']/10, 2) if manga_data.get('meanScore') else None,
            score_count=sum(score['amount'] for score in manga_data['stats']['scoreDistribution']),
            user_count=manga_data['popularity'],
            rank=rated_all_time_rank[0]['rank'] if rated_all_time_rank else None,
            chapter_count=manga_data.get('chapters'),
            volume_count=manga_data.get('volumes'),
            status=ANILIST_MANGA_PUBLISHING_STATUS_MAPPING.get(manga_data['status'], '?'),
            start_date=start_date_parsed,
            end_date=end_date_parsed,
            year=manga_data['startDate'].get('year') if manga_data.get('startDate') else None,
            genres=manga_data['genres'],
            themes=[tag['name'] for tag in manga_data['tags']
                    if not tag['isMediaSpoiler'] and not tag['isGeneralSpoiler']],
            authors=authors,
            synopsis=clean_text_with_html_tags(html_text=manga_data.get('description')),
            media_type=ANILIST_MANGA_MEDIA_TYPE_MAPPING.get(manga_data['format'].lower(),
                                                            manga_data['format'].replace('_', ' ').title())
            if manga_data.get('format') else None,
            poster_url=manga_data.get('coverImage', {}).get('large'),
            banner_url=manga_data.get('bannerImage')
        )

    @property
    def web_url(self) -> str:
        if self.source_provider == AnimangaProvider.MAL:
            return Links.MAL_MANGA_URL.format(manga_id=self.manga_id)
        elif self.source_provider == AnimangaProvider.ANILIST:
            return Links.ANILIST_MANGA_URL.format(manga_id=self.manga_id)
        else:
            raise ValueError(f"Unknown source provider: {self.source_provider}")


class AnimeSearchResult:
    def __init__(self,
                 source_data: list[dict],
                 source_provider: str,  # AnimangaProvider
                 entries: list['AnimeSearchResultEntry'],
                 original_query: str):
        self.source_data: list[dict] = source_data
        self.source_provider: str = source_provider
        self.entries: list['AnimeSearchResultEntry'] = entries
        self.original_query: str = original_query

    @classmethod
    def from_mal_data(cls, search_results: list[dict], original_query: str) -> 'AnimeSearchResult':
        return cls(
            source_data=search_results,
            source_provider=AnimangaProvider.MAL,
            entries=[AnimeSearchResultEntry.from_mal_data(entry_data) for entry_data in search_results],
            original_query=original_query
        )

    @classmethod
    def from_anilist_data(cls, search_results: list[dict], original_query: str) -> 'AnimeSearchResult':
        return cls(
            source_data=search_results,
            source_provider=AnimangaProvider.ANILIST,
            entries=[AnimeSearchResultEntry.from_anilist_data(entry_data) for entry_data in search_results],
            original_query=original_query
        )


class AnimeSearchResultEntry:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 anime_id: int,
                 native_title: str,
                 english_title: str | None,
                 release_year: int | None,
                 air_dates: str | None,
                 image_url: str | None,
                 score: float | None,
                 media_type: str | None,  # AnimeMediaType
                 episode_count: int | None,
                 duration_in_minutes: int | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.anime_id: int = anime_id
        self.native_title: str = native_title
        self.english_title: str | None = english_title
        self.release_year: int | None = release_year
        self.air_dates: str | None = air_dates
        self.image_url: str | None = image_url
        self.score: float | None = score
        self.media_type: str | None = media_type
        self.episode_count: int | None = episode_count
        self.duration_in_minutes: int | None = duration_in_minutes

    @classmethod
    def from_mal_data(cls, entry_data: dict) -> 'AnimeSearchResultEntry':
        try:
            score = float(entry_data['payload'].get('score') or 0) or None
        except (ValueError, TypeError):
            score = None
        media_type = MAL_ANIME_MEDIA_TYPE_MAPPING.get(
                entry_data['payload'].get('media_type', '').lower(),
                entry_data['payload'].get('media_type').replace('_', ' ').title())
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.MAL,
            anime_id=entry_data['id'],
            native_title=entry_data['name'],
            english_title=None,
            release_year=entry_data['payload'].get('start_year'),
            air_dates=entry_data['payload'].get('aired'),
            image_url=entry_data.get('image_url'),
            score=score,
            media_type=media_type if media_type != '-' else None,
            episode_count=None,
            duration_in_minutes=None
        )

    @classmethod
    def from_anilist_data(cls, entry_data: dict) -> 'AnimeSearchResultEntry':
        parsed_start_date = parse_fuzzy_anilist_date_into_str(date=entry_data['startDate'])
        parsed_end_date = parse_fuzzy_anilist_date_into_str(date=entry_data['endDate'])
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            anime_id=entry_data['id'],
            native_title=entry_data['title'].get('romaji'),
            english_title=entry_data['title'].get('english'),
            release_year=entry_data['seasonYear'],
            air_dates=f"{parsed_start_date} - {parsed_end_date or '?'}" if parsed_start_date else None,
            image_url=entry_data['coverImage'].get('large') or entry_data['coverImage'].get('large'),
            score=round(entry_data.get('meanScore') / 10, 2) if entry_data.get('meanScore') else None,
            media_type=ANILIST_ANIME_MEDIA_TYPE_MAPPING.get(entry_data['format'].lower(),
                                                            entry_data['format'].replace('_', ' ').title())
            if entry_data.get('format') else None,
            episode_count=entry_data.get('episodes'),
            duration_in_minutes=entry_data.get('duration', 0) or None
        )


class MangaSearchResult:
    def __init__(self,
                 source_data: list[dict],
                 source_provider: str,  # AnimangaProvider
                 entries: list['MangaSearchResultEntry'],
                 original_query: str):
        self.source_data: list[dict] = source_data
        self.source_provider: str = source_provider
        self.entries: list['MangaSearchResultEntry'] = entries
        self.original_query: str = original_query

    @classmethod
    def from_mal_data(cls, search_results: list[dict], original_query: str) -> 'MangaSearchResult':
        return cls(
            source_data=search_results,
            source_provider=AnimangaProvider.MAL,
            entries=[MangaSearchResultEntry.from_mal_data(entry_data) for entry_data in search_results],
            original_query=original_query
        )

    @classmethod
    def from_anilist_data(cls, search_results: list[dict], original_query: str) -> 'MangaSearchResult':
        return cls(
            source_data=search_results,
            source_provider=AnimangaProvider.ANILIST,
            entries=[MangaSearchResultEntry.from_anilist_data(entry_data) for entry_data in search_results],
            original_query=original_query
        )


class MangaSearchResultEntry:
    def __init__(self,
                 source_data: dict,
                 source_provider: str,  # AnimangaProvider
                 manga_id: int,
                 native_title: str,
                 english_title: str | None,
                 release_year: int | None,
                 release_dates: str | None,
                 image_url: str | None,
                 score: float | None,
                 media_type: str | None,  # MangaMediaType
                 chapter_count: int | None,
                 volume_count: int | None):
        self.source_data: dict = source_data
        self.source_provider: str = source_provider
        self.manga_id: int = manga_id
        self.native_title: str = native_title
        self.english_title: str | None = english_title
        self.release_year: int | None = release_year
        self.release_dates: str | None = release_dates
        self.image_url: str | None = image_url
        self.score: float | None = score
        self.media_type: str | None = media_type
        self.chapter_count: int | None = chapter_count
        self.volume_count: int | None = volume_count

    @classmethod
    def from_mal_data(cls, entry_data: dict) -> 'MangaSearchResultEntry':
        try:
            score = float(entry_data['payload'].get('score') or 0) or None
        except (ValueError, TypeError):
            score = None
        media_type = MAL_MANGA_MEDIA_TYPE_MAPPING.get(
            entry_data['payload'].get('media_type', '').lower(),
            entry_data['payload'].get('media_type').replace('_', ' ').title())
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.MAL,
            manga_id=entry_data['id'],
            native_title=entry_data['name'],
            english_title=None,
            release_year=entry_data['payload'].get('start_year'),
            release_dates=entry_data['payload'].get('published'),
            image_url=entry_data.get('image_url'),
            score=score,
            media_type=media_type if media_type != '-' else None,
            chapter_count=None,
            volume_count=None
        )

    @classmethod
    def from_anilist_data(cls, entry_data: dict) -> 'MangaSearchResultEntry':
        parsed_start_date = parse_fuzzy_anilist_date_into_str(date=entry_data['startDate'])
        parsed_end_date = parse_fuzzy_anilist_date_into_str(date=entry_data['endDate'])
        return cls(
            source_data=entry_data,
            source_provider=AnimangaProvider.ANILIST,
            manga_id=entry_data['id'],
            native_title=entry_data['title'].get('romaji'),
            english_title=entry_data['title'].get('english'),
            release_year=entry_data['startDate'].get('year'),
            release_dates=f"{parsed_start_date} - {parsed_end_date or '?'}" if parsed_start_date else None,
            image_url=entry_data['coverImage'].get('large') or entry_data['coverImage'].get('large'),
            score=round(entry_data.get('meanScore') / 10, 2) if entry_data.get('meanScore') else None,
            media_type=ANILIST_MANGA_MEDIA_TYPE_MAPPING.get(entry_data['format'].lower(),
                                                            entry_data['format'].replace('_', ' ').title())
            if entry_data.get('format') else None,
            chapter_count=entry_data.get('chapters'),
            volume_count=entry_data.get('volumes')
        )


class UserAnimeAnalysis:
    def __init__(self,
                 amount_analysis: str | None,
                 score_analysis: str | None,
                 planning_analysis: str | None,
                 current_analysis: str | None,
                 dropped_analysis: str | None,
                 paused_analysis: str | None,
                 length_analysis: str | None,
                 release_years_analysis: str | None,
                 genres_analysis: str | None,
                 tags_analysis: str | None,
                 voice_actors_analysis: str | None,
                 studios_analysis: str | None):
        self.amount_analysis: str | None = amount_analysis
        self.score_analysis: str | None = score_analysis
        self.planning_analysis: str | None = planning_analysis
        self.current_analysis: str | None = current_analysis
        self.dropped_analysis: str | None = dropped_analysis
        self.paused_analysis: str | None = paused_analysis
        self.length_analysis: str | None = length_analysis
        self.release_years_analysis: str | None = release_years_analysis
        self.genres_analysis: str | None = genres_analysis
        self.tags_analysis: str | None = tags_analysis
        self.voice_actors_analysis: str | None = voice_actors_analysis
        self.studios_analysis: str | None = studios_analysis

    @classmethod
    def from_user_profile(cls, user_profile: UserAnimangaProfile) -> 'UserAnimeAnalysis':
        statistics = user_profile.source_data['statistics']['anime']
        status_stats_map = {
            status['status']: status['count'] for status in statistics['statuses']
        }
        planning_count = status_stats_map.get('PLANNING', 0)
        current_count = status_stats_map.get('CURRENT', 0)
        dropped_count = status_stats_map.get('DROPPED', 0)
        paused_count = status_stats_map.get('PAUSED', 0)
        total_count = user_profile.anime_stats.total_entries_count
        mean_score = round(user_profile.anime_stats.mean_score, 2)
        completed_days = user_profile.anime_stats.days_watched
        planned_percentage = round(planning_count / total_count * 100, 2) if total_count else 0

        if completed_days >= 100:
            amount_analysis = AnilistStrings.ANALYSIS_ANIME_DAYS_100P.format(completed_days=completed_days)
        elif completed_days >= 60:
            amount_analysis = AnilistStrings.ANALYSIS_ANIME_DAYS_60P.format(completed_days=completed_days)
        elif completed_days >= 30:
            amount_analysis = AnilistStrings.ANALYSIS_ANIME_DAYS_30P.format(completed_days=completed_days)
        elif completed_days > 0:
            amount_analysis = AnilistStrings.ANALYSIS_ANIME_DAYS_P0.format(completed_days=completed_days)
        else:
            amount_analysis = AnilistStrings.ANALYSIS_ANIME_DAYS_0

        if completed_days:
            if mean_score > 8.5:
                score_analysis = AnilistStrings.ANALYSIS_ANIME_SCORE_85P.format(mean_score=mean_score)
            elif mean_score >= 7.0:
                score_analysis = AnilistStrings.ANALYSIS_ANIME_SCORE_70P.format(mean_score=mean_score)
            elif total_count:
                score_analysis = AnilistStrings.ANALYSIS_ANIME_SCORE_0P.format(mean_score=mean_score)
            else:
                score_analysis = None
        else:
            score_analysis = None

        if planned_percentage >= 15 and total_count > 60:
            planning_analysis = AnilistStrings.ANALYSIS_ANIME_PLANNING_MAX.format(
                planned_percentage=planned_percentage
            )
        elif planned_percentage < 5 and total_count > 60:
            planning_analysis = AnilistStrings.ANALYSIS_ANIME_PLANNING_MIN.format(
                planned_percentage=planned_percentage
            )
        elif total_count > 60:
            planning_analysis = AnilistStrings.ANALYSIS_ANIME_PLANNING_BALANCED.format(
                planned_percentage=planned_percentage
            )
        elif total_count in range(30, 61) and planned_percentage > 50:
            planning_analysis = AnilistStrings.ANALYSIS_ANIME_PLANNING_NEW
        else:
            planning_analysis = None

        if current_count > 10:
            current_analysis = AnilistStrings.ANALYSIS_ANIME_CURRENT_MAX.format(current_count=current_count)
        elif current_count == 0 and completed_days > 0:
            current_analysis = AnilistStrings.ANALYSIS_ANIME_CURRENT_0
        else:
            current_analysis = None

        if dropped_count > 30:
            anime_dropped_analysis = AnilistStrings.ANALYSIS_ANIME_DROPPED_MAX.format(dropped_count=dropped_count)
        elif dropped_count + paused_count == 0 and completed_days:
            anime_dropped_analysis = AnilistStrings.ANALYSIS_ANIME_DROPPED_0
        else:
            anime_dropped_analysis = None

        if paused_count > 15:
            anime_paused_analysis = AnilistStrings.ANALYSIS_ANIME_PAUSED_MAX.format(paused_count=paused_count)
        else:
            anime_paused_analysis = None

        if total_count > 30 and completed_days:
            if statistics['lengths'][0]['length'] == "1":
                anime_length_analysis = AnilistStrings.ANALYSIS_ANIME_LENGTH_1
            elif statistics['lengths'][0]['length'] == "2-6":
                anime_length_analysis = AnilistStrings.ANALYSIS_ANIME_LENGTH_2_TO_6
            elif statistics['lengths'][0]['length'] in ["7-16", "17-28"]:
                anime_length_analysis = AnilistStrings.ANALYSIS_ANIME_LENGTH_7_TO_28
            elif statistics['lengths'][0]['length'] in ["29-55", "56-100"]:
                anime_length_analysis = AnilistStrings.ANALYSIS_ANIME_LENGTH_29_TO_100
            else:
                anime_length_analysis = None
        elif total_count and statistics['lengths'][0]['length'] == "101+":
            anime_length_analysis = AnilistStrings.ANALYSIS_ANIME_LENGTH_101P
        else:
            anime_length_analysis = None

        if total_count > 20 and completed_days:
            year_2000_minus = 0
            year_2001_2010 = 0
            year_2011_plus = 0
            for release_year, count in [(year_stat['releaseYear'], year_stat['count'])
                                        for year_stat in statistics['releaseYears']]:
                if release_year <= 2000:
                    year_2000_minus += count
                elif release_year in range(2001, 2011):
                    year_2001_2010 += count
                else:
                    year_2011_plus += count
            max_period = max(year_2011_plus, year_2001_2010, year_2000_minus)
            close_range = range(0, total_count // 8 + 2)
            if max_period == year_2011_plus \
                    and year_2011_plus - year_2001_2010 in close_range \
                    and year_2011_plus - year_2000_minus in close_range:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_ALL
            elif max_period == year_2011_plus and year_2011_plus - year_2001_2010 in close_range:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_2000P
            elif max_period == year_2011_plus and year_2011_plus - year_2000_minus in close_range:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_OLD_NEW
            elif max_period == year_2001_2010 and year_2001_2010 - year_2000_minus in close_range:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_OLD
            elif max_period == year_2011_plus:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_2010P
            elif max_period == year_2001_2010:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_2000_TO_2010
            elif max_period == year_2000_minus:
                release_years_analysis = AnilistStrings.ANALYSIS_ANIME_RELEASE_YEARS_PRE_2000
            else:
                release_years_analysis = None

            genres = statistics['genres']
            genres_names = [genre['genre'] for genre in genres]
            highest_rated_genre = max(genres, key=lambda genre: genre.get('meanScore', 0) or genre.get('count', 0),
                                      default=None)['genre'] if genres else None
            if len(genres) > 2:
                genres_analysis = AnilistStrings.ANALYSIS_ANIME_GENRES_3P.format(
                    genre_1=genres_names[0], genre_2=genres_names[1],
                    genre_3=genres_names[2], highest_rated_genre=highest_rated_genre
                )
            elif len(genres) > 1:
                genres_analysis = AnilistStrings.ANALYSIS_ANIME_GENRES_TWO.format(
                    genre_1=genres_names[0], genre_2=genres_names[1],
                    highest_rated_genre=highest_rated_genre
                )
            elif genres:
                genres_analysis = AnilistStrings.ANALYSIS_ANIME_GENRES_ONE.format(genre=genres_names[0])
            else:
                genres_analysis = None

            tags = [tag for tag in statistics['tags'] if tag['tag']['name'] not in ["Male Protagonist",
                                                                                    "Female Protagonist",
                                                                                    "Ensemble Cast",
                                                                                    "Primarily Female Cast",
                                                                                    "Primarily Male Cast",
                                                                                    "Primarily Teen Cast",
                                                                                    "Primarily Adult Cast",
                                                                                    "Heterosexual"]]
            tags_names = [tag['tag']['name'] for tag in tags]
            highest_rated_tag = max(tags, key=lambda tag: tag['meanScore'], default=None)['tag']['name'] \
                if tags else None
            if len(tags) > 2:
                tags_analysis = AnilistStrings.ANALYSIS_ANIME_TAGS_3P.format(tag_1=tags_names[0],
                                                                             tag_2=tags_names[1],
                                                                             tag_3=tags_names[2],
                                                                             highest_rated_tag=highest_rated_tag)
            elif len(tags) > 1:
                tags_analysis = AnilistStrings.ANALYSIS_ANIME_TAGS_TWO.format(tag_1=tags_names[0],
                                                                              tag_2=tags_names[1],
                                                                              highest_rated_tag=highest_rated_tag)
            elif tags:
                tags_analysis = AnilistStrings.ANALYSIS_ANIME_TAGS_ONE.format(tag=tags_names[0])
            else:
                tags_analysis = None
        else:
            release_years_analysis = genres_analysis = tags_analysis = None

        if total_count > 100:
            voice_actors_filtered = [va for va in statistics['voiceActors']
                                     if va['voiceActor'].get('languageV2') == "Japanese"]
            voice_actors_analysis = AnilistStrings.ANALYSIS_ANIME_VA.format(
                va_name=voice_actors_filtered[0]['voiceActor']['name']['full'],
                va_url=voice_actors_filtered[0]['voiceActor']['siteUrl']
            )
        else:
            voice_actors_analysis = None

        if total_count > 50:
            anime_studios_analysis = AnilistStrings.ANALYSIS_ANIME_STUDIO.format(
                studio_name=statistics['studios'][0]['studio']['name'],
                studio_url=statistics['studios'][0]['studio']['siteUrl']
            )
        else:
            anime_studios_analysis = None

        return cls(
            amount_analysis=amount_analysis,
            score_analysis=score_analysis,
            planning_analysis=planning_analysis,
            current_analysis=current_analysis,
            dropped_analysis=anime_dropped_analysis,
            paused_analysis=anime_paused_analysis,
            length_analysis=anime_length_analysis,
            release_years_analysis=release_years_analysis,
            genres_analysis=genres_analysis,
            tags_analysis=tags_analysis,
            voice_actors_analysis=voice_actors_analysis,
            studios_analysis=anime_studios_analysis
        )


class UserMangaAnalysis:
    def __init__(self,
                 amount_analysis: str | None,
                 score_analysis: str | None,
                 planning_analysis: str | None,
                 current_analysis: str | None,
                 paused_analysis: str | None,
                 genres_analysis: str | None,
                 tags_analysis: str | None,
                 staff_analysis: str | None):
        self.amount_analysis: str | None = amount_analysis
        self.score_analysis: str | None = score_analysis
        self.planning_analysis: str | None = planning_analysis
        self.current_analysis: str | None = current_analysis
        self.paused_analysis: str | None = paused_analysis
        self.genres_analysis: str | None = genres_analysis
        self.tags_analysis: str | None = tags_analysis
        self.staff_analysis: str | None = staff_analysis

    @classmethod
    def from_user_profile(cls, user_profile: UserAnimangaProfile) -> 'UserMangaAnalysis':
        statistics = user_profile.source_data['statistics']['manga']
        status_stats_map = {
            status['status']: status['count'] for status in statistics['statuses']
        }
        planning_count = status_stats_map.get('PLANNING', 0)
        current_count = status_stats_map.get('CURRENT', 0)
        dropped_count = status_stats_map.get('DROPPED', 0)
        paused_count = status_stats_map.get('PAUSED', 0)
        mean_score = round(user_profile.manga_stats.mean_score, 2)
        completed_chapters = user_profile.manga_stats.total_chapters
        total_count = user_profile.manga_stats.total_entries_count
        planned_percentage = round(planning_count / total_count * 100, 2) if total_count else 0

        if completed_chapters >= 5000:
            amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_5KP.format(
                completed_chapters=completed_chapters
            )
        elif completed_chapters >= 3000:
            amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_3KP.format(
                completed_chapters=completed_chapters
            )
        elif completed_chapters >= 1000:
            amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_1KP.format(
                completed_chapters=completed_chapters
            )
        elif completed_chapters > 0:
            amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_MIN.format(
                completed_chapters=completed_chapters
            )
        elif user_profile.anime_stats.days_watched > 30:
            if total_count:
                amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_0P_ANIME
            else:
                amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_0_ANIME
        else:
            if total_count:
                amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_0P
            else:
                amount_analysis = AnilistStrings.ANALYSIS_MANGA_CHAPTERS_0

        if completed_chapters:
            if mean_score > 8.5:
                score_analysis = AnilistStrings.ANALYSIS_MANGA_SCORE_85P.format(mean_score=mean_score)
            elif mean_score >= 7.0:
                score_analysis = AnilistStrings.ANALYSIS_MANGA_SCORE_70P.format(mean_score=mean_score)
            elif total_count:
                score_analysis = AnilistStrings.ANALYSIS_MANGA_SCORE_0P.format(mean_score=mean_score)
            else:
                score_analysis = None
        else:
            score_analysis = None

        if planned_percentage >= 15 and total_count > 60:
            planning_analysis = AnilistStrings.ANALYSIS_MANGA_PLANNING_MAX.format(
                planned_percentage=planned_percentage
            )
        elif planned_percentage < 5 and total_count > 60:
            planning_analysis = AnilistStrings.ANALYSIS_MANGA_PLANNING_MIN
        elif total_count >= 20 and planned_percentage > 50:
            if completed_chapters:
                planning_analysis = AnilistStrings.ANALYSIS_MANGA_PLANNING_MOST_WITH_COMPLETED
            else:
                planning_analysis = AnilistStrings.ANALYSIS_MANGA_PLANNING_MOST_WITHOUT_COMPLETED
        else:
            planning_analysis = None
        
        if current_count >= 50:
            current_analysis = AnilistStrings.ANALYSIS_MANGA_CURRENT_50P.format(current_count=current_count)
        elif current_count >= 15:
            current_analysis = AnilistStrings.ANALYSIS_MANGA_CURRENT_15P.format(current_count=current_count)
        elif current_count > 1:
            current_analysis = AnilistStrings.ANALYSIS_MANGA_CURRENT_1P.format(current_count=current_count)
        elif current_count == 0 and completed_chapters > 0:
            current_analysis = AnilistStrings.ANALYSIS_MANGA_CURRENT_0
        else:
            current_analysis = None

        if paused_count > dropped_count and paused_count > 3:
            paused_analysis = AnilistStrings.ANALYSIS_MANGA_PAUSED_DROPPED
        else:
            paused_analysis = None

        if total_count > 20 and completed_chapters:
            genres = statistics['genres']
            genres_names = [genre['genre'] for genre in genres]
            highest_rated_genre = max(genres, key=lambda genre: genre.get('meanScore', 0) or genre.get('count', 0),
                                      default=None)['genre'] if genres else None
            if len(genres) > 2:
                genres_analysis = AnilistStrings.ANALYSIS_MANGA_GENRES_3P.format(
                    genre_1=genres_names[0], genre_2=genres_names[1],
                    genre_3=genres_names[2], highest_rated_genre=highest_rated_genre
                )
            elif len(genres) > 1:
                genres_analysis = AnilistStrings.ANALYSIS_MANGA_GENRES_TWO.format(
                    genre_1=genres_names[0], genre_2=genres_names[1],
                    highest_rated_genre=highest_rated_genre
                )
            elif genres:
                genres_analysis = AnilistStrings.ANALYSIS_MANGA_GENRES_ONE.format(genre=genres_names[0])
            else:
                genres_analysis = None
            tags = [tag for tag in statistics['tags'] if tag['tag']['name'] not in ["Male Protagonist",
                                                                                    "Female Protagonist",
                                                                                    "Ensemble Cast",
                                                                                    "Primarily Female Cast",
                                                                                    "Primarily Male Cast",
                                                                                    "Primarily Teen Cast",
                                                                                    "Primarily Adult Cast",
                                                                                    "Heterosexual"]]
            tags_names = [tag['tag']['name'] for tag in tags]
            highest_rated_tag = max(tags, key=lambda tag: tag['meanScore'], default=None)['tag']['name'] \
                if tags else None
            if len(tags) > 2:
                tags_analysis = AnilistStrings.ANALYSIS_MANGA_TAGS_3P.format(tag_1=tags_names[0],
                                                                             tag_2=tags_names[1],
                                                                             tag_3=tags_names[2],
                                                                             highest_rated_tag=highest_rated_tag)
            elif len(tags) > 1:
                tags_analysis = AnilistStrings.ANALYSIS_MANGA_TAGS_TWO.format(tag_1=tags_names[0],
                                                                              tag_2=tags_names[1],
                                                                              highest_rated_tag=highest_rated_tag)
            elif tags:
                tags_analysis = AnilistStrings.ANALYSIS_MANGA_TAGS_ONE.format(tag=tags_names[0])
            else:
                tags_analysis = None
        else:
            genres_analysis = tags_analysis = None

        if total_count > 5 and statistics['staff'] and statistics['staff'][0]['count'] > 1:
            staff_analysis = AnilistStrings.ANALYSIS_MANGA_STAFF.format(
                staff_name=statistics['staff'][0]['staff']['name']['full'],
                staff_url=statistics['staff'][0]['staff']['siteUrl']
            )
        else:
            staff_analysis = None

        return cls(
            amount_analysis=amount_analysis,
            score_analysis=score_analysis,
            planning_analysis=planning_analysis,
            current_analysis=current_analysis,
            paused_analysis=paused_analysis,
            genres_analysis=genres_analysis,
            tags_analysis=tags_analysis,
            staff_analysis=staff_analysis
        )
