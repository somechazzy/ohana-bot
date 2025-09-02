from bs4 import BeautifulSoup

from common.app_logger import AppLogger
from constants import Links


class MyAnimeListProfileParser:
    """
    A parser for extracting user profile information from a MyAnimeList HTML page.
    """

    def __init__(self, webpage_html: str):
        self.webpage_html: str = webpage_html
        self.soup = BeautifulSoup(webpage_html, features="lxml")
        self.username: str = self.soup.select(".di-ib.po-r")[0].text.strip().replace("'s Profile", '')
        self.logger = AppLogger(component=self.__class__.__name__)
        # reusable selections/extractions
        self._user_info_extractions: dict = {}

    def get_avatar_url(self) -> str | None:
        avatar_url = None
        try:
            avatar_selection = self.soup.select(".user-image")
            if avatar_selection and 'data-src' in avatar_selection[0].contents[1].attrs:
                avatar_url = avatar_selection[0].contents[1].attrs['data-src']
        except Exception as e:
            self.logger.debug(f"Failed at retrieving profile avatar for {self.username}. Error: {e}")
        return avatar_url

    def get_banner_url(self) -> str | None:
        banner_url = None
        try:
            banner_selection = self.soup.select(".l-mainvisual img")
            if banner_selection:
                banner_url = banner_selection[0].attrs['src']
        except Exception as e:
            self.logger.debug(f"Failed at retrieving profile banner for {self.username}. Error: {e}")
        return banner_url

    def _get_user_info_extractions(self) -> dict:
        if not self._user_info_extractions:
            try:
                user_info_selection = self.soup.select(".mb4 .clearfix")
                for subselection in user_info_selection:
                    self._user_info_extractions[subselection.contents[0].contents[0]] = \
                        subselection.contents[1].contents[0]
            except Exception as e:
                self.logger.debug(f"Failed at retrieving basic info for {self.username}. Error: {e}")
                return {}
        return self._user_info_extractions

    def get_joined_at(self) -> str | None:
        return self._get_user_info_extractions().get("Joined") or None

    def get_last_online_at(self) -> str | None:
        return self._get_user_info_extractions().get("Last Online") or None

    def get_location(self) -> str | None:
        return self._get_user_info_extractions().get("Location") or None

    def get_birthday(self) -> str | None:
        return self._get_user_info_extractions().get("Birthday") or None

    def get_gender(self) -> str | None:
        return self._get_user_info_extractions().get("Gender") or None

    def get_anime_total_entries_count(self) -> int:
        try:
            anime_stats_selection = self.soup.select(".anime .stats-data")
            return self._get_int(anime_stats_selection[0].contents[0].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime total entries for {self.username}. Error: {e}")
        return 0

    def get_anime_mean_score(self) -> float:
        try:
            anime_stats_selection = self.soup.select(".anime .fw-b")
            return self._get_float(anime_stats_selection[1].contents[3].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime mean score for {self.username}. Error: {e}")
        return 0.0

    def get_anime_days_watched(self) -> float:
        try:
            anime_stats_selection = self.soup.select(".anime .fw-b")
            return self._get_float(str(anime_stats_selection[0].contents[1]))
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime days watched for {self.username}. Error: {e}")
        return 0

    def get_anime_completed_count(self) -> int:
        try:
            anime_stats_selection = self.soup.select(".anime .stats-status")
            return self._get_int(anime_stats_selection[0].contents[1].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime completed count for {self.username}. Error: {e}")
        return 0

    def get_anime_watching_count(self) -> int:
        try:
            anime_stats_selection = self.soup.select(".anime .stats-status")
            return self._get_int(anime_stats_selection[0].contents[0].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime watching count for {self.username}. Error: {e}")
        return 0

    def get_anime_total_episodes(self) -> int:
        try:
            anime_stats_selection = self.soup.select(".anime .stats-data")
            return self._get_int(anime_stats_selection[0].contents[2].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime episode count for {self.username}. Error: {e}")
        return 0

    def get_anime_rewatched_count(self) -> int:
        try:
            anime_stats_selection = self.soup.select(".anime .stats-data")
            return self._get_int(anime_stats_selection[0].contents[1].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving anime rewatched count for {self.username}. Error: {e}")
        return 0

    def get_manga_total_entries_count(self) -> int:
        try:
            manga_stats_selection = self.soup.select(".manga .stats-data")
            return self._get_int(manga_stats_selection[0].contents[0].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga total entries for {self.username}. Error: {e}")
        return 0

    def get_manga_mean_score(self) -> float:
        try:
            manga_stats_selection = self.soup.select(".manga .fw-b")
            return self._get_float(manga_stats_selection[1].contents[3].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga mean score for {self.username}. Error: {e}")
        return 0.0

    def get_manga_days_read(self) -> float:
        try:
            manga_stats_selection = self.soup.select(".manga .fw-b")
            return self._get_float(str(manga_stats_selection[0].contents[1]))
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga days read for {self.username}. Error: {e}")
        return 0

    def get_manga_completed_count(self) -> int:
        try:
            manga_stats_selection = self.soup.select(".manga .stats-status")
            return self._get_int(manga_stats_selection[0].contents[1].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga completed count for {self.username}. Error: {e}")
        return 0

    def get_manga_reading_count(self) -> int:
        try:
            manga_stats_selection = self.soup.select(".manga .stats-status")
            return self._get_int(manga_stats_selection[0].contents[0].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga reading count for {self.username}. Error: {e}")
        return 0

    def get_manga_total_chapters(self) -> int:
        try:
            manga_stats_selection = self.soup.select(".manga .stats-data")
            return self._get_int(manga_stats_selection[0].contents[2].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga chapter count for {self.username}. Error: {e}")
        return 0

    def get_manga_reread_count(self) -> int:
        try:
            manga_stats_selection = self.soup.select(".manga .stats-data")
            return self._get_int(manga_stats_selection[0].contents[1].contents[1].contents[0])
        except Exception as e:
            self.logger.debug(f"Failed at retrieving manga reread count for {self.username}. Error: {e}")
        return 0

    def get_anime_favorites_urls_and_titles(self) -> list[tuple]:
        anime_favorites_selection = self.soup.select("#anime_favorites")
        if not anime_favorites_selection:
            return []
        return [
            (
                favorite_selection.attrs['title'],
                favorite_selection.contents[1].attrs['href']
            ) for favorite_selection in [inner_selection for inner_selection
                                         in anime_favorites_selection[0].contents[5].contents[1].contents
                                         if inner_selection != '\n']
        ]

    def get_manga_favorites_urls_and_titles(self) -> list[tuple]:
        manga_favorites_selection = self.soup.select("#manga_favorites")
        if not manga_favorites_selection:
            return []
        return [
            (
                favorite_selection.attrs['title'],
                favorite_selection.contents[1].attrs['href']
            ) for favorite_selection in [inner_selection for inner_selection
                                         in manga_favorites_selection[0].contents[5].contents[1].contents
                                         if inner_selection != '\n']
        ]

    def get_character_favorites_urls_and_titles(self) -> list[tuple]:
        character_favorites_selection = self.soup.select("#character_favorites")
        if not character_favorites_selection:
            return []
        return [
            (
                favorite_selection.attrs['title'],
                Links.MAL_BASE_URL + favorite_selection.contents[1].attrs['href']
            ) for favorite_selection in [inner_selection for inner_selection
                                         in character_favorites_selection[0].contents[5].contents[1].contents
                                         if inner_selection != '\n']
        ]

    def get_person_favorites_urls_and_titles(self) -> list[tuple]:
        person_favorites_selection = self.soup.select("#person_favorites")
        if not person_favorites_selection:
            return []
        return [
            (
                favorite_selection.attrs['title'],
                Links.MAL_BASE_URL + favorite_selection.contents[1].attrs['href']
            ) for favorite_selection in [inner_selection for inner_selection
                                         in person_favorites_selection[0].contents[5].contents[1].contents
                                         if inner_selection != '\n']
        ]

    def get_studio_favorites_urls_and_titles(self) -> list[tuple]:
        studio_favorites_selection = self.soup.select("#company_favorites")
        if not studio_favorites_selection:
            return []
        return [
            (
                favorite_selection.attrs['title'],
                Links.MAL_BASE_URL + favorite_selection.contents[1].attrs['href']
            ) for favorite_selection in [inner_selection for inner_selection
                                         in studio_favorites_selection[0].contents[5].contents[1].contents
                                         if inner_selection != '\n']
        ]

    @staticmethod
    def _get_int(field_value: str) -> int:
        try:
            return int(field_value.replace(',', ''))
        except ValueError:
            return 0

    @staticmethod
    def _get_float(field_value: str) -> float:
        try:
            return float(field_value.replace(',', ''))
        except ValueError:
            return 0.0
