import asyncio

from common.exceptions import ExternalServiceException, UserInputException
from components.integration_component import AnimangaProviderComponent
from constants import UserUsernameProvider, AnimangaProvider
from strings.integrations_strings import MALStrings
from models.dto.animanga import UserAnimangaProfile, AnimeSearchResult, MangaSearchResult, AnimeInfo, MangaInfo, \
    UserAnimeListEntry, UserMangaListEntry, UserAnimeList, UserMangaList
from services.mal_service import MyAnimeListService


class MALComponent(AnimangaProviderComponent):
    PROVIDER = AnimangaProvider.MAL
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mal_service = MyAnimeListService()

    async def validate_username(self, username: str, *args, **kwargs) -> None:
        """
        Validate the provided MyAnimeList username to check if it exists

        Args:
            username (str): MAL username

        Returns:
            None

        Raises:
            UserInputException: If the username does not exist
        """
        self.logger.debug(f"Validating MyAnimeList username: `{username}`")
        try:
            await self.mal_service.get_profile_webpage(username=username)
        except ExternalServiceException as e:
            if e.status_code == 404:
                self.logger.debug(f"Validating MyAnimeList username: `{username}` -> does not exist.")
                raise UserInputException(MALStrings.USERNAME_NOT_FOUND.format(username=username))
            raise e

    async def get_user_profile(self,
                               user_id: int | None = None,
                               username: str | None = None,
                               *args, **kwargs) -> UserAnimangaProfile:
        """
        Get the MyAnimeList user profile data. Must provide either user_id or username.

        Args:
            user_id (int | None): Discord user ID
            username (str | None): MAL username

        Returns:
            UserAnimangaProfile: User profile data

        Raises:
            UserInputException: If both user_id and username are None
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")

        self.logger.debug(f"Fetching MyAnimeList user profile for ID: {user_id}, Username: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.MAL)

        if not username:
            raise UserInputException(MALStrings.USERNAME_NOT_SET)

        profile_webpage = await self.mal_service.get_profile_webpage(username=username)
        user_profile = UserAnimangaProfile.from_mal_data(username=username, profile_webpage=profile_webpage)
        asyncio.get_event_loop().create_task(
            self.load_user_lists(user_profile=user_profile)  # lazyload the lists
        )
        return user_profile

    async def get_user_anime_list(self, username: str) -> UserAnimeList | None:
        """
        Get the user's anime list from MyAnimeList by username.

        Args:
            username (str): MyAnimeList username

        Returns:
            UserAnimeList: User's anime list
        """
        self.logger.debug(f"Fetching MyAnimeList user anime list for username: {username}")
        anime_list_entries = []
        offset = 0
        while True:
            try:
                batch = await self.mal_service.get_anime_list(username=username, offset=offset)
                if not batch:
                    break
                anime_list_entries.extend(batch)
                offset += len(batch)
            except ExternalServiceException as e:
                if e.alert_worthy:
                    self.logger.error(f"Failed to load anime list for MyAnimeList user: {username}. "
                                      f"Error: {e}. Debug: {e.debugging_info}")
                return None
        return UserAnimeList.from_mal_data(list_data=anime_list_entries, username=username)

    async def get_user_manga_list(self, username: str) -> UserMangaList | None:
        """
        Get the user's manga list from MyAnimeList by username.

        Args:
            username (str): MyAnimeList username

        Returns:
            UserMangaList: User's manga list
        """
        self.logger.debug(f"Fetching MyAnimeList user manga list for username: {username}")
        manga_list_entries = []
        offset = 0
        while True:
            try:
                batch = await self.mal_service.get_manga_list(username=username, offset=offset)
                if not batch:
                    break
                manga_list_entries.extend(batch)
                offset += len(batch)
            except ExternalServiceException as e:
                if e.alert_worthy:
                    self.logger.error(f"Failed to load manga list for MyAnimeList user: {username}. "
                                      f"Error: {e}. Debug: {e.debugging_info}")
                return None
        return UserMangaList.from_mal_data(list_data=manga_list_entries, username=username)

    async def get_user_stats_for_anime(self,
                                       anime_id: int,
                                       username: str | None = None,
                                       user_id: int | None = None,
                                       *args, **kwargs) -> UserAnimeListEntry | None:
        """
        Get the user's anime stats for a specific anime from MyAnimeList. Must provide either username or user_id.
        Args:
            anime_id (int): MyAnimeList anime ID
            username (str): MyAnimeList username
            user_id (int): Discord user ID

        Returns:
            UserAnimeListEntry: User's anime list entry for the specified anime
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")
        self.logger.debug(f"Fetching MyAnimeList user stats for anime ID: {anime_id} for user: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.MAL)
        if not username:
            return None
        user_anime_list = await self.get_user_anime_list(username=username)
        for entry in user_anime_list.entries:
            if entry.anime_id == anime_id:
                return entry
        return UserAnimeListEntry.as_empty_entry(anime_id=anime_id,
                                                 username=username,
                                                 provider=UserUsernameProvider.MAL)

    async def get_user_stats_for_manga(self,
                                       manga_id: int,
                                       username: str | None = None,
                                       user_id: int | None = None,
                                       *args, **kwargs) -> UserMangaListEntry | None:
        """
        Get the user's manga stats for a specific manga from MyAnimeList. Must provide either username or user_id.
        Args:
            manga_id (int): MyAnimeList manga ID
            username (str): MyAnimeList username
            user_id (int): Discord user ID

        Returns:
            UserAnimeListEntry: User's manga list entry for the specified manga
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided.")
        self.logger.debug(f"Fetching MyAnimeList user stats for manga ID: {manga_id} for user: {username}")

        if not username:
            from components.user_settings_components.user_username_component import UserUsernameComponent
            username = UserUsernameComponent().get_user_username(user_id=user_id, provider=UserUsernameProvider.MAL)
        if not username:
            return None
        user_manga_list = await self.get_user_manga_list(username=username)
        for entry in user_manga_list.entries:
            if entry.manga_id == manga_id:
                return entry
        return UserMangaListEntry.as_empty_entry(manga_id=manga_id,
                                                 username=username,
                                                 provider=UserUsernameProvider.MAL)

    async def get_anime_search_results(self, query: str, *args, **kwargs) -> AnimeSearchResult:
        """
        Search for anime on MyAnimeList.

        Args:
            query (str): Search query

        Returns:
            AnimeSearchResult: Search entries
        """
        self.logger.debug(f"Searching for anime on MyAnimeList with query: `{query}`")
        results = await self.mal_service.get_anime_search_results(query=query)
        return AnimeSearchResult.from_mal_data(search_results=results, original_query=query)

    async def get_manga_search_results(self, query: str, *args, **kwargs) -> MangaSearchResult:
        """
        Search for manga on MyAnimeList.

        Args:
            query (str): Search query

        Returns:
            MangaSearchResult: Search entries
        """
        self.logger.debug(f"Searching for manga on MyAnimeList with query: `{query}`")
        results = await self.mal_service.get_manga_search_results(query=query)
        return MangaSearchResult.from_mal_data(search_results=results, original_query=query)

    async def get_anime_info(self, anime_id: int, *args, **kwargs) -> AnimeInfo:
        """
        Get anime information from MyAnimeList by anime ID.

        Args:
            anime_id (int): MyAnimeList anime ID

        Returns:
            AnimeInfo: anime info object
        """
        self.logger.debug(f"Fetching detailed information for anime ID: {anime_id}")
        anime_info = await self.mal_service.get_anime_info(anime_id=anime_id)
        return AnimeInfo.from_mal_data(anime_data=anime_info)

    async def get_manga_info(self, manga_id: int, *args, **kwargs) -> MangaInfo:
        """
        Get manga information from MyAnimeList by manga ID.

        Args:
            manga_id (int): MyAnimeList manga ID

        Returns:
            MangaInfo: manga info object
        """
        self.logger.debug(f"Fetching detailed information for manga ID: {manga_id}")
        manga_info = await self.mal_service.get_manga_info(manga_id=manga_id)
        return MangaInfo.from_mal_data(manga_data=manga_info)
