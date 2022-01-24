import json
from datetime import datetime
from internal.web_handler import request
from globals_ import constants
from models import anilist_profile
from models.anilist_list import Status, AnilistList


async def get_anilist_profile(username):
    query = '''
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
    variables = {
        'name': username
    }
    url = 'https://graphql.anilist.co'

    response = await request("post", url, constants.CachingType.AL_PROFILE,
                             json={'query': query, 'variables': variables})
    if response.status != 200:
        return anilist_profile.DummyAnilistProfile(status=response.status)
    profile_json = str(response.content.encode()).replace("\\'", "'").replace("\\\\", "\\")
    if profile_json.startswith("b'") and profile_json.endswith("'"):
        profile_json = profile_json[2:len(profile_json) - 1]
    profile_json = json.loads(profile_json)
    anilist_profile_object = anilist_profile.AnilistProfile(profile_json)
    return anilist_profile_object


async def get_anilist_lists(username):
    query = '''
    query ($userName: String) {

        MediaListCollection(userName: $userName, type: ANIME){
            user {
              id
              mediaListOptions{
                scoreFormat
              }
            }
            lists{
              entries{
                media{
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
    variables = {
        'userName': username
    }
    url = 'https://graphql.anilist.co'

    response = await request("post", url, constants.CachingType.AL_LISTS, json={'query': query, 'variables': variables})
    scoring_system = "-"

    if response.status != 200:
        anime_list_object = None
    else:
        anime_list_json = str(response.content).replace("\\'", "'").replace("\\\\", "\\")
        if anime_list_json.startswith("b'") and anime_list_json.endswith("'"):
            anime_list_json = anime_list_json[2:len(anime_list_json) - 1]
        anime_list_object = anilist_list_from_dict(json.loads(anime_list_json))
        scoring_system = anime_list_object.data.media_list_collection.user.media_list_options.score_format

    query = query.replace("ANIME", "MANGA", 1)
    response = await request("post", url, constants.CachingType.AL_LISTS, json={'query': query, 'variables': variables})
    if response.status != 200:
        manga_list_object = None
    else:
        manga_list_json = str(response.content).replace("\\'", "'").replace("\\\\", "\\")
        if manga_list_json.startswith("b'") and manga_list_json.endswith("'"):
            manga_list_json = manga_list_json[2:len(manga_list_json) - 1]
        manga_list_object = anilist_list_from_dict(json.loads(manga_list_json))
        scoring_system = manga_list_object.data.media_list_collection.user.media_list_options.score_format

    anime_list_object = _order_and_append_list(anime_list_object)
    manga_list_object = _order_and_append_list(manga_list_object)

    return anime_list_object, manga_list_object, scoring_system


def anilist_list_from_dict(s) -> AnilistList:
    return AnilistList.from_dict(s)


class AnilistMediaUserStats:
    def __init__(self, status, start_date_string, finish_date_string, score,
                 days, repeat, rating_system, num_watched_episodes=None, num_read_chapters=None):
        self.status = status
        self.start_date_string = start_date_string
        self.finish_date_string = finish_date_string
        self.score = score
        self.days_string = days
        self.repeat = repeat
        self.num_watched_episodes = num_watched_episodes
        self.num_read_chapters = num_read_chapters
        self.rating_system = rating_system


async def get_al_user_stats_for_show(al_username, mal_anime_id):
    anime_list, _, scoring_system = await get_anilist_lists(username=al_username)
    anime_entry = [entry for entry in anime_list if entry.media.mal_id == mal_anime_id]
    if not anime_entry:
        return None
    anime_entry = anime_entry[0]
    status = anime_entry.status.value
    status = "Watching" if status == Status.CURRENT else status
    status = status.lower().capitalize()
    progress = anime_entry.progress
    score = anime_entry.score
    repeat = anime_entry.repeat
    start_date_string, start_date_parsed = _get_anilist_date(anime_entry.started_at)
    finish_date_string, end_date_parsed = _get_anilist_date(anime_entry.completed_at)
    if start_date_parsed and end_date_parsed:
        days = (end_date_parsed - start_date_parsed).days + 1
    else:
        days = None

    return AnilistMediaUserStats(status=status, start_date_string=start_date_string, repeat=repeat,
                                 num_watched_episodes=progress, finish_date_string=finish_date_string,
                                 score=score, days=days, rating_system=scoring_system)


async def get_al_user_stats_for_manga(al_username, mal_manga_id):
    _, manga_list, scoring_system = await get_anilist_lists(username=al_username)
    manga_entry = [entry for entry in manga_list if entry.media.mal_id == mal_manga_id]
    if not manga_entry:
        return None
    manga_entry = manga_entry[0]
    status = manga_entry.status.value
    status = "Reading" if status == Status.CURRENT else status
    status = status.lower().capitalize()
    progress = manga_entry.progress
    score = manga_entry.score
    repeat = manga_entry.repeat
    start_date_string, start_date_parsed = _get_anilist_date(manga_entry.started_at)
    finish_date_string, end_date_parsed = _get_anilist_date(manga_entry.completed_at)
    if start_date_parsed and end_date_parsed:
        days = (end_date_parsed - start_date_parsed).days + 1
    else:
        days = None

    return AnilistMediaUserStats(status=status, start_date_string=start_date_string, repeat=repeat,
                                 num_read_chapters=progress, finish_date_string=finish_date_string,
                                 score=score, days=days, rating_system=scoring_system)


def _get_anilist_date(fuzzy_date):
    date_string = ""
    date_parsed = None
    if not fuzzy_date:
        return date_string, date_parsed
    if fuzzy_date.get("year"):
        date_string += f"{fuzzy_date.get('year')}"
        if fuzzy_date.get("month"):
            date_string += f"-{fuzzy_date.get('month')}"
            if fuzzy_date.get("day"):
                date_string += f"-{fuzzy_date.get('day')}"
                date_parsed = datetime.strptime(date_string, "%Y-%m-%d")
    return date_string, date_parsed


def _order_and_append_list(list_object):
    lists = list_object.data.media_list_collection.lists
    planning_list = []
    current_list = []
    completed_list = []
    dropped_list = []
    paused_list = []
    repeating_list = []
    else_list = []
    master_list = []
    for list_ in lists:
        if not list_.entries[0].status:
            else_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "PLANNING":
            planning_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "CURRENT":
            current_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "COMPLETED":
            completed_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "DROPPED":
            dropped_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "PAUSED":
            paused_list.extend(list_.entries)
        elif str(list_.entries[0].status.name) == "REPEATING":
            repeating_list.extend(list_.entries)
        else:
            else_list.extend(list_.entries)
    for list_ in [current_list, repeating_list, completed_list, planning_list, paused_list, dropped_list, else_list]:
        master_list.extend(list_)
    return master_list
