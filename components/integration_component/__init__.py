from components import BaseComponent
from constants import AnimangaListLoadingStatus
from models.dto.animanga import UserAnimangaProfile, AnimeSearchResult, MangaSearchResult, AnimeInfo, MangaInfo, \
    UserAnimeListEntry, UserAnimeList, UserMangaList


class BaseIntegrationComponent(BaseComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is BaseIntegrationComponent:
            raise TypeError("BaseIntegrationComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)


class AnimangaProviderComponent(BaseIntegrationComponent):
    PROVIDER = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is AnimangaProviderComponent:
            raise TypeError("AnimangaProviderComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)

    async def validate_username(self, username: str, *args, **kwargs) -> None:
        raise NotImplementedError()

    async def get_user_profile(self,
                               user_id: int | None = None,
                               username: str | None = None,
                               *args, **kwargs) -> UserAnimangaProfile:
        raise NotImplementedError()

    async def get_user_anime_list(self, username: str) -> UserAnimeList | None:
        raise NotImplementedError()

    async def get_user_manga_list(self, username: str) -> UserMangaList | None:
        raise NotImplementedError()

    async def load_user_lists(self, user_profile: UserAnimangaProfile) -> None:
        """
        Load the user's anime and manga lists from provider into the user profile.
        Args:
            user_profile (UserAnimangaProfile): The user profile object.

        Returns:
            None
        """
        self.logger.debug(f"Loading user lists for {self.PROVIDER} user: {user_profile.username}")

        user_profile.anime_list_loading_status = AnimangaListLoadingStatus.LOADING
        user_profile.manga_list_loading_status = AnimangaListLoadingStatus.LOADING
        try:
            user_profile.anime_list = await self.get_user_anime_list(username=user_profile.username)
        except Exception as e:
            self.logger.error(f"Failed to load user anime list for {self.PROVIDER} user: {user_profile.username}. "
                              f"Error: {e}.")
            user_profile.anime_list_loading_status = AnimangaListLoadingStatus.FAILED
        else:
            user_profile.anime_list_loading_status = AnimangaListLoadingStatus.LOADED \
                if user_profile.anime_list else AnimangaListLoadingStatus.FAILED
        try:
            user_profile.manga_list = await self.get_user_manga_list(username=user_profile.username)
        except Exception as e:
            self.logger.error(f"Failed to load user manga list for {self.PROVIDER} user: {user_profile.username}. "
                              f"Error: {e}.")
            user_profile.manga_list_loading_status = AnimangaListLoadingStatus.FAILED
        else:
            user_profile.manga_list_loading_status = AnimangaListLoadingStatus.LOADED \
                if user_profile.manga_list else AnimangaListLoadingStatus.FAILED

        self.logger.debug(f"Finished loading user lists for {self.PROVIDER} user: {user_profile.username}. "
                          f"Anime list status: {user_profile.anime_list_loading_status}, "
                          f"Manga list status: {user_profile.manga_list_loading_status}")

    async def get_user_stats_for_anime(self, anime_id: int, username: str | None = None, user_id: int | None = None,
                                       *args, **kwargs) -> UserAnimeListEntry | None:
        raise NotImplementedError()

    async def get_user_stats_for_manga(self, manga_id: int, username: str | None = None, user_id: int | None = None,
                                       *args, **kwargs) -> UserAnimeListEntry | None:
        raise NotImplementedError()

    async def get_anime_search_results(self, query: str, *args, **kwargs) -> AnimeSearchResult:
        raise NotImplementedError()

    async def get_manga_search_results(self, query: str, *args, **kwargs) -> MangaSearchResult:
        raise NotImplementedError()

    async def get_anime_info(self, anime_id: int, *args, **kwargs) -> AnimeInfo:
        raise NotImplementedError()

    async def get_manga_info(self, manga_id: int, *args, **kwargs) -> MangaInfo:
        raise NotImplementedError()
