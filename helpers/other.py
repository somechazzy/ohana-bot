from globals_.constants import CachingType
from internal.web_handler import request


async def ensure_mal_exists(username):
    url = f"https://myanimelist.net/profile/{username}"
    response = await request("GET", url, CachingType.MAL_PROFILE)
    return response.status


async def ensure_anilist_exists(username):
    query = """
    query ($name: String) {

         User (name: $name) {
             id
             name
         }
    }
    """
    var = {
        'name': username
    }
    url = 'https://graphql.anilist.co'
    response = await request("post", url, CachingType.AL_PROFILE,
                             json={'query': query, 'variables': var})
    return response.status
