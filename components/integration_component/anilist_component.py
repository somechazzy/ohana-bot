import asyncio

from common.exceptions import ExternalServiceException, UserInputException
from components.integration_component import AnimangaProviderComponent
from constants import UserUsernameProvider, AnimangaProvider
from strings.integrations_strings import AnilistStrings
from models.dto.animanga import UserAnimangaProfile, AnimeSearchResult, MangaSearchResult, MangaInfo, AnimeInfo, \
    UserAnimeListEntry, UserMangaListEntry, UserAnimeList, UserMangaList
from services.anilist_service import AnilistService


class AnilistComponent(AnimangaProviderComponent):
    PROVIDER = AnimangaProvider.ANILIST
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anilist_service = AnilistService()

    async def validate_username(self, username: str, *args, **kwargs) -> None:
        """
        Validate the provided AniList username to check if it exists

        Args:
            username (str): AniList username

        Returns:
            None

        Raises:
            UserInputException: If the username does not exist
        """
        self.logger.debug(f"Validating AniList username: `{username}`")
        try:
            await self.anilist_service.get_user_profile(username=username, only_load_id=True)
        except ExternalServiceException as e:
            if e.status_code == 404:
                self.logger.debug(f"Validating AniList username: `{username}` -> does not exist.")
                raise UserInputException(AnilistStrings.USERNAME_NOT_FOUND.format(username=username))
            raise e

    async def get_user_profile(self,
                               user_id: int | None = None,
                               username: str | None = None,
                               *args, **kwargs) -> UserAnimangaProfile:
        """
        Get the AniList user profile data. Must provide either user_id or username.

        Args:
            user_id (int | None): Discord user ID
            username (str | None): MAL username

        Returns:
            UserAnimangaProfile: User profile object

        Raises:
            UserInputException: If both user_id and username are None
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")

        self.logger.debug(f"Fetching AniList user profile for ID: {user_id}, Username: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.MAL)

        if not username:
            raise UserInputException(AnilistStrings.USERNAME_NOT_SET)

        profile_data = await self.anilist_service.get_user_profile(username=username)
        user_profile = UserAnimangaProfile.from_anilist_data(username=username, profile_data=profile_data)
        asyncio.get_event_loop().create_task(
            self.load_user_lists(user_profile=user_profile)  # lazyload the lists
        )
        return user_profile

    async def get_user_anime_list(self, username: str) -> UserAnimeList | None:
        """
        Get the user's anime list from AniList by username.

        Args:
            username (str): AniList username

        Returns:
            UserAnimeList: User's anime list
        """
        self.logger.debug(f"Fetching AniList user anime list for username: {username}")
        try:
            anime_list = await self.anilist_service.get_anime_list(username=username)
        except ExternalServiceException as e:
            if e.alert_worthy:
                self.logger.error(f"Failed to load anime list for AniList user: {username}. "
                                  f"Error: {e}. Debug: {e.debugging_info}")
            return None
        return UserAnimeList.from_anilist_data(list_data=anime_list, username=username)

    async def get_user_manga_list(self, username: str) -> UserMangaList | None:
        """
        Get the user's manga list from AniList by username.

        Args:
            username (str): AniList username

        Returns:
            UserMangaList: User's manga list
        """
        self.logger.debug(f"Fetching AniList user manga list for username: {username}")
        try:
            anime_list = await self.anilist_service.get_manga_list(username=username)
        except ExternalServiceException as e:
            if e.alert_worthy:
                self.logger.error(f"Failed to load manga list for AniList user: {username}. "
                                  f"Error: {e}. Debug: {e.debugging_info}")
            return None
        return UserMangaList.from_anilist_data(list_data=anime_list, username=username)

    async def get_user_stats_for_anime(self,
                                       anime_id: int,
                                       username: str | None = None,
                                       user_id: int | None = None,
                                       *args, **kwargs) -> UserAnimeListEntry | None:
        """
        Get the user's anime stats for a specific anime from AniList. Must provide either username or user_id.
        Args:
            anime_id (int): AniList anime ID
            username (str): AniList username
            user_id (int): Discord user ID

        Returns:
            UserAnimeListEntry: User's anime list entry for the specified anime
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")
        self.logger.debug(f"Fetching AniList user stats for anime ID: {anime_id} for user: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.ANILIST)
        if not username:
            return None
        user_anime_entry = await self.anilist_service.get_user_anime_stats(username=username, media_id=anime_id)
        if user_anime_entry:
            return UserAnimeListEntry.from_anilist_data(entry_data=user_anime_entry, username=username)
        return UserAnimeListEntry.as_empty_entry(anime_id=anime_id,
                                                 username=username,
                                                 provider=UserUsernameProvider.ANILIST)

    async def get_user_stats_for_manga(self,
                                       manga_id: int,
                                       username: str | None = None,
                                       user_id: int | None = None,
                                       *args, **kwargs) -> UserMangaListEntry | None:
        """
        Get the user's manga stats for a specific manga from AniList. Must provide either username or user_id.
        Args:
            manga_id (int): AniList manga ID
            username (str): AniList username
            user_id (int): Discord user ID

        Returns:
            UserAnimeListEntry: User's manga list entry for the specified manga
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")
        self.logger.debug(f"Fetching AniList user stats for manga ID: {manga_id} for user: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.ANILIST)
        if not username:
            return None
        user_manga_entry = await self.anilist_service.get_user_manga_stats(username=username, media_id=manga_id)
        if user_manga_entry:
            return UserMangaListEntry.from_anilist_data(entry_data=user_manga_entry, username=username)
        return UserMangaListEntry.as_empty_entry(manga_id=manga_id,
                                                 username=username,
                                                 provider=UserUsernameProvider.ANILIST)

    async def get_anime_search_results(self, query: str, *args, **kwargs) -> AnimeSearchResult:
        """
        Search for anime on AniList.

        Args:
            query (str): Search query

        Returns:
            AnimeSearchResult: Search entries
        """
        self.logger.debug(f"Searching for anime on AniList with query: `{query}`")
        results = await self.anilist_service.get_anime_search_results(query=query)
        return AnimeSearchResult.from_anilist_data(search_results=results, original_query=query)

    async def get_manga_search_results(self, query: str, *args, **kwargs) -> MangaSearchResult:
        """
        Search for manga on AniList.

        Args:
            query (str): Search query

        Returns:
            MangaSearchResult: Search entries
        """
        self.logger.debug(f"Searching for manga on AniList with query: `{query}`")
        results = await self.anilist_service.get_manga_search_results(query=query)
        return MangaSearchResult.from_anilist_data(search_results=results, original_query=query)

    async def get_anime_info(self, anime_id: int, *args, **kwargs) -> AnimeInfo:
        """
        Get anime information from AniList by anime ID.

        Args:
            anime_id (int): AniList anime ID

        Returns:
            AnimeInfo: anime info object
        """
        self.logger.debug(f"Fetching detailed information for anime ID: {anime_id}")
        anime_info = await self.anilist_service.get_anime_info(media_id=anime_id)
        return AnimeInfo.from_anilist_data(anime_data=anime_info)

    async def get_manga_info(self, manga_id: int, *args, **kwargs) -> MangaInfo:
        """
        Get manga information from AniList by manga ID.

        Args:
            manga_id (int): AniList manga ID

        Returns:
            MangaInfo: manga info object
        """
        self.logger.debug(f"Fetching detailed information for manga ID: {manga_id}")
        manga_info = await self.anilist_service.get_manga_info(media_id=manga_id)
        return MangaInfo.from_anilist_data(manga_data=manga_info)
