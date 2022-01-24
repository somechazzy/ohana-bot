import json
from urllib.parse import quote
from internal.web_handler import request
from globals_ import constants


async def get_mal_anime_search_results(query):
    query = quote(query, safe='')
    url = f"https://myanimelist.net/search/prefix.json?type=anime&keyword={query}&v=1"
    response = await request("get", url, constants.CachingType.MAL_SEARCH_ANIME)
    if response.status != 200:
        raise Exception(f"Received {response.status} while grabbing anime search results.\n"
                        f" URL: {url}\n"
                        f"Response body: {response.content}\n"
                        f"Response json: {response.json}")
    results = json.loads(response.content)['categories'][0]['items']
    thumb = results[0]['image_url']
    to_return = []
    for result in results:
        title = result['name']
        url = result['url']
        anime_type = result['payload']['media_type']
        eps = result['payload']['aired']
        score = result['payload']['score']
        anime_id = result['id']
        result = {
            "title": title,
            "url": url,
            "type": anime_type,
            "eps": eps,
            "score": score,
            "id": anime_id
        }
        to_return.append(result)
    return to_return, thumb


async def get_mal_manga_search_results(query):
    query = quote(query, safe='')
    url = f"https://myanimelist.net/search/prefix.json?type=manga&keyword={query}&v=1"
    response = await request("get", url, constants.CachingType.MAL_SEARCH_MANGA)
    if response.status != 200:
        raise Exception(f"Received {response.status} while grabbing manga search results.\n"
                        f" URL: {url}\n"
                        f"Response body: {response.content}\n"
                        f"Response json: {response.json}")
    results = json.loads(response.content)['categories'][0]['items']
    thumb = results[0]['image_url']
    to_return = []
    for result in results:
        title = result['name']
        url = result['url']
        manga_type = result['payload']['media_type']
        volumes = result['payload']['published'].replace(" ??", "")
        score = result['payload']['score']
        manga_id = result['id']
        result = {
            "title": title,
            "url": url,
            "type": manga_type,
            "volumes": volumes,
            "score": score,
            "id": manga_id
        }
        to_return.append(result)
    return to_return, thumb
