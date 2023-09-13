from globals_.constants import CachingType
from services.third_party.base import ThirdPartyService
from utils.exceptions import AnilistNotFoundException, AnilistInternalErrorException, AnilistException
from internal.requests_manager import request


class AnilistService(ThirdPartyService):
    BASE_API_URL = "https://graphql.anilist.co"

    async def _handle_response(self, response):
        if response.status == 404:
            raise AnilistNotFoundException("Not found")
        elif response.status >= 500:
            raise AnilistInternalErrorException("Anilist is down")
        elif response.status != 200:
            self.error_logger.log(f"Received {response.status} while requesting {response.url}\n "
                                  f"Response: {response.content}")
            raise AnilistException("Something went wrong")

        return response.json

    async def get_anime_list(self, username):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.ANIME_LIST_QUERY,
                                        'variables': {
                                            "username": username
                                        }})
        return await self._handle_response(response)

    async def get_manga_list(self, username):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.MANGA_LIST_QUERY,
                                        'variables': {
                                            "username": username
                                        }})
        return await self._handle_response(response)

    async def get_anime_by_mal_id(self, mal_id):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.ANIME_BY_MAL_ID_QUERY,
                                        'variables': {
                                            "mal_id": mal_id
                                        }})
        return await self._handle_response(response)

    async def get_manga_by_mal_id(self, mal_id):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.MANGA_BY_MAL_ID_QUERY,
                                        'variables': {
                                            "mal_id": mal_id
                                        }})
        return await self._handle_response(response)

    async def get_user_stats_for_anime(self, anilist_id, username):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.ANIME_USER_STATS_QUERY,
                                        'variables': {
                                            "username": username,
                                            "media_id": anilist_id
                                        }})
        return await self._handle_response(response)

    async def get_user_stats_for_manga(self, anilist_id, username):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_LISTS,
                                 json_={'query': self.AnilistQueries.MANGA_USER_STATS_QUERY,
                                        'variables': {
                                            "username": username,
                                            "media_id": anilist_id
                                        }})
        return await self._handle_response(response)

    async def get_profile(self, username):
        response = await request(method="post",
                                 url=self.BASE_API_URL,
                                 type_of_request=CachingType.AL_PROFILE,
                                 json_={'query': self.AnilistQueries.PROFILE_QUERY,
                                        'variables': {
                                            "name": username
                                        }})
        return await self._handle_response(response)

    class AnilistQueries:
        ANIME_LIST_QUERY = '''
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
                }
            }
        '''
        MANGA_LIST_QUERY = '''
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
                }
            }
        '''

        ANIME_BY_MAL_ID_QUERY = '''
        query ($mal_id: Int) {

            Media(idMal: $mal_id, type: ANIME) {
                id
            }
        }
        '''
        MANGA_BY_MAL_ID_QUERY = '''
        query ($mal_id: Int) {

            Media(idMal: $mal_id, type: MANGA) {
                id
            }
        }
        '''

        ANIME_USER_STATS_QUERY = '''
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
        '''
        MANGA_USER_STATS_QUERY = '''
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
        '''

        PROFILE_QUERY = '''
            query ($name: String) {
            
                User (name: $name) {
                    id
                    name
                    about
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
                        medium
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
        '''
