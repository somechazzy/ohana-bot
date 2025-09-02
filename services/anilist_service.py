from common.exceptions import ExternalServiceException
from constants import CachingPolicyPresetName
from strings.integrations_strings import AnilistStrings
from services import ThirdPartyService


class AnilistService(ThirdPartyService):
    BASE_URL = "https://graphql.anilist.co"

    # noinspection PyMethodMayBeStatic
    def _process_response(self, response, raise_on_404: bool = True):
        if response.status == 404:
            if not raise_on_404:
                return None
            raise ExternalServiceException("Not found",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "status": response.status,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=AnilistStrings.NOT_FOUND_MESSAGE)
        elif response.status >= 500:
            raise ExternalServiceException("AniList is down",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "status": response.status,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=AnilistStrings.SERVICE_DOWN_MESSAGE)
        elif response.status != 200:
            raise ExternalServiceException("Unhandled response from Anilist",
                                           status_code=response.status,
                                           debugging_info={
                                               "url": response.url,
                                               "content": response.content,
                                               "headers": response.headers
                                           },
                                           user_message=AnilistStrings.CONNECTION_ERROR_MESSAGE,
                                           alert_worthy=True)

        return response.json

    async def get_user_profile(self, username: str, only_load_id: bool = False) -> dict:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_PROFILE
            if not only_load_id else CachingPolicyPresetName.NO_CACHE,
            json_={'query': self.Queries.PROFILE_QUERY if not only_load_id else self.Queries.PROFILE_CHECK_QUERY,
                   'variables': {
                       "name": username
                   }}
        )
        return self._process_response(response)['data']['User']

    async def get_anime_list(self, username: str) -> dict:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_LIST,
            json_={'query': self.Queries.ANIME_LIST_QUERY, 'variables': {"username": username}}
        )
        return self._process_response(response)['data']['MediaListCollection']

    async def get_manga_list(self, username: str) -> dict:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_LIST,
            json_={'query': self.Queries.MANGA_LIST_QUERY, 'variables': {"username": username}}
        )
        return self._process_response(response)['data']['MediaListCollection']

    async def get_anime_search_results(self, query: str) -> list:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_SEARCH,
            json_={'query': self.Queries.ANIME_SEARCH_QUERY, 'variables': {"search": query}}
        )
        return self._process_response(response)['data']['Page']['media']

    async def get_manga_search_results(self, query: str) -> list:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_SEARCH,
            json_={'query': self.Queries.MANGA_SEARCH_QUERY, 'variables': {"search": query}}
        )
        return self._process_response(response)['data']['Page']['media']

    async def get_anime_info(self, media_id: int) -> dict:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_INFO,
            json_={'query': self.Queries.ANIME_INFO_QUERY, 'variables': {"media_id": media_id}}
        )
        return self._process_response(response)['data']['Media']

    async def get_manga_info(self, media_id: int) -> dict:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_INFO,
            json_={'query': self.Queries.MANGA_INFO_QUERY, 'variables': {"media_id": media_id}}
        )
        return self._process_response(response)['data']['Media']

    async def get_user_anime_stats(self, username: str, media_id: int) -> dict | None:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_LIST,
            json_={'query': self.Queries.ANIME_USER_STATS_QUERY, 'variables': {"username": username,
                                                                               "media_id": media_id}},
        )
        data = self._process_response(response, raise_on_404=False)
        if data is None:
            return None
        else:
            return data['data']['MediaList']

    async def get_user_manga_stats(self, username: str, media_id: int) -> dict | None:
        response = await self._request(
            method="POST",
            url=self.BASE_URL,
            caching_policy=CachingPolicyPresetName.ANILIST_LIST,
            json_={'query': self.Queries.MANGA_USER_STATS_QUERY, 'variables': {"username": username,
                                                                               "media_id": media_id}}
        )
        data = self._process_response(response, raise_on_404=False)
        if data is None:
            return None
        else:
            return data['data']['MediaList']

    class Queries:
        PROFILE_QUERY = """
        query ($name: String) {
            User (name: $name) {
                id
                name
                statistics {
                    anime {
                        count
                        meanScore
                        minutesWatched
                        statuses {
                            count
                            status
                            minutesWatched
                        }
                        lengths(limit: 10, sort: COUNT_DESC) {
                            count
                            length
                            meanScore
                        }
                        releaseYears(limit: 10, sort: COUNT_DESC) {
                            count
                            releaseYear
                            meanScore
                        }
                        genres(limit: 10, sort: COUNT_DESC) {
                            count
                            genre
                            meanScore
                        }
                        tags(limit: 10, sort: COUNT_DESC) {
                            count
                            tag {
                                name
                            }
                            meanScore
                        }
                        voiceActors(limit: 10, sort: COUNT_DESC) {
                            count
                            voiceActor {
                                name {
                                    full
                                }
                                languageV2
                                siteUrl
                            }
                            meanScore
                        }
                        studios(limit: 10, sort: COUNT_DESC) {
                            count
                            studio {
                                name
                                siteUrl
                            }
                            meanScore
                        }
                    }
                    manga {
                        count
                        meanScore
                        chaptersRead
                        statuses {
                            count
                            status
                            chaptersRead
                        }
                        releaseYears(limit: 10, sort: COUNT_DESC) {
                            count
                            releaseYear
                            meanScore
                        }
                        genres(limit: 10, sort: COUNT_DESC) {
                            count
                            genre
                            meanScore
                        }
                        tags(limit: 10, sort: COUNT_DESC) {
                            count
                            tag {
                                name
                            }
                            meanScore
                        }
                        staff(limit: 10, sort: COUNT_DESC) {
                            count
                            staff {
                                name {
                                    full
                                }
                                siteUrl
                            }
                            meanScore
                        }
                    }
                }
                avatar {
                    large
                }
                bannerImage
                favourites {
                    anime {
                        nodes {
                            title {
                                romaji
                                english
                            }
                            siteUrl
                        }
                    }
                    manga {
                        nodes {
                            title {
                                romaji
                                english
                            }
                            siteUrl
                        }
                    }
                    characters {
                        nodes {
                            name {
                                full
                            }
                            siteUrl
                        }
                    }
                    staff {
                        nodes {
                            name {
                                full
                            }
                            siteUrl
                        }
                    }
                    studios {
                        nodes {
                            name
                            siteUrl
                        }
                    }

                }
                siteUrl
                createdAt
                updatedAt
            }
        }
        """

        PROFILE_CHECK_QUERY = """
        query ($name: String) {

            User (name: $name) {
                id
            }
        }
        """

        ANIME_LIST_QUERY = """
        query ($username: String) {
        
            MediaListCollection(userName: $username, type: ANIME) {
                user {
                    id
                    mediaListOptions {
                        scoreFormat
                    }
                }
                lists {
                    entries {
                        media {
                            title {
                                romaji
                                english
                            }
                            siteUrl
                            idMal
                            id
                        }
                        status
                        score
                        progress
                        repeat
                        startedAt {
                            year
                            month
                            day
                        }
                        completedAt {
                            year
                            month
                            day
                        }
                    }
                    status
                }
            }
        }
        """

        MANGA_LIST_QUERY = """
        query ($username: String) {

            MediaListCollection(userName: $username, type: MANGA) {
                user {
                    id
                    mediaListOptions {
                        scoreFormat
                    }
                }
                lists {
                    entries {
                        media {
                            title {
                                romaji
                                english
                            }
                            siteUrl
                            idMal
                            id
                        }
                        status
                        score
                        progress
                        repeat
                        startedAt {
                            year
                            month
                            day
                        }
                        completedAt {
                            year
                            month
                            day
                        }
                    }
                    status
                }
            }
        }
        """

        ANIME_SEARCH_QUERY = """
        query Media($search: String) {
            Page(perPage: 10) {
                media(search: $search, type: ANIME) {
                    id
                    title {
                        english
                        romaji
                    }
                    episodes
                    duration
                    format
                    meanScore
                    endDate {
                        year
                        month
                        day
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    seasonYear
                    coverImage {
                        large
                    }
                    bannerImage
                }
            }
        }
        """

        MANGA_SEARCH_QUERY = """
        query Media($search: String) {
            Page(perPage: 10) {
                media(search: $search, type: MANGA) {
                    id
                    title {
                        english
                        romaji
                    }
                    chapters
                    volumes
                    format
                    meanScore
                    endDate {
                        year
                        month
                        day
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    coverImage {
                        large
                    }
                    bannerImage
                }
            }
        }
        """

        ANIME_INFO_QUERY = """
        query Media($media_id: Int) {
            Media(id: $media_id, type: ANIME) {
                id
                title {
                    english
                    romaji
                }
                format
                meanScore
                endDate {
                    year
                    month
                    day
                }
                startDate {
                    year
                    month
                    day
                }
                coverImage {
                    large
                }
                bannerImage
                description
                duration
                episodes
                favourites
                genres
                popularity
                rankings {
                    allTime
                    rank
                    context
                    type
                }
                season
                seasonYear
                source
                studios(isMain: true) {
                    nodes {
                        name
                    }
                }
                tags {
                    name
                    rank
                    isGeneralSpoiler
                    isMediaSpoiler
                }
                type
                stats {
                    scoreDistribution {
                        score
                        amount
                    }
                }
                status
            }
        }
        """

        MANGA_INFO_QUERY = """
        query Media($media_id: Int) {
            Media(id: $media_id, type: MANGA) {
                id
                title {
                    english
                    romaji
                }
                format
                meanScore
                endDate {
                    year
                    month
                    day
                }
                startDate {
                    year
                    month
                    day
                }
                coverImage {
                    large
                }
                bannerImage
                description
                favourites
                genres
                popularity
                rankings {
                    allTime
                    rank
                    context
                    type
                }
                source
                tags {
                    name
                    rank
                    isGeneralSpoiler
                    isMediaSpoiler
                }
                type
                stats {
                    scoreDistribution {
                        score
                        amount
                    }
                }
                status
                chapters
                volumes
                staff(sort: RELEVANCE, perPage: 3) {
                    edges {
                        role
                        node {
                            name {
                                full
                            }
                        }
                    }
                }
            }
        }
        """

        ANIME_USER_STATS_QUERY = """
        query ($username: String, $media_id: Int) {

            MediaList(userName: $username, mediaId: $media_id, type: ANIME) {
                user {
                    id
                    mediaListOptions {
                        scoreFormat
                    }
                }
                media {
                    title {
                        romaji
                        english
                    }
                    siteUrl
                    idMal
                    id
                }
                status
                score
                progress
                repeat
                startedAt {
                    year
                    month
                    day
                }
                completedAt {
                    year
                    month
                    day
                }
            }
        }
        """

        MANGA_USER_STATS_QUERY = """
        query ($username: String, $media_id: Int) {

            MediaList(userName: $username, mediaId: $media_id, type: MANGA) {
                user {
                    id
                    mediaListOptions {
                        scoreFormat
                    }
                }
                media {
                    title {
                        romaji
                        english
                    }
                    siteUrl
                    idMal
                    id
                }
                status
                score
                progress
                repeat
                startedAt {
                    year
                    month
                    day
                }
                completedAt {
                    year
                    month
                    day
                }
            }
        }
        """
