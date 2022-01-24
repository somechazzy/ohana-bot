from internal.web_handler import request
from bs4 import BeautifulSoup
import re
from globals_ import constants


async def get_mal_anime_info(anime_id):
    url = f"https://myanimelist.net/anime/{anime_id}"
    response = await request("get", url, constants.CachingType.MAL_INFO_ANIME)
    soup = BeautifulSoup(response.content, features="lxml")

    title_select = str(soup.select(".title-name")[0])
    title = re.sub("<[^>]*>", "", title_select).replace('&amp;', '&')  # title

    title_english_select = str(soup.select(".title-english"))
    title_english_select = title_english_select[0] \
        if (isinstance(title_english_select, list) and len(title_english_select) > 0) \
        else title_english_select
    title_english = re.sub("<[^>]*>", "", title_english_select)  # title english
    title_english = re.sub("[\[\]]", "", title_english).replace('&amp;', '&')

    poster_leading_keywords = "<meta property=\"og:image\" content=\""
    poster_starting_index = response.content.find(poster_leading_keywords) + len(poster_leading_keywords)
    poster_ending_index = response.content.find("\"", poster_starting_index)
    poster = response.content[poster_starting_index:poster_ending_index]  # poster

    score_select = str(soup.select(".score").pop())
    score = re.sub("<[^>]*>", "", score_select)  # score
    score_users = ""
    try:
        score_users = re.findall("[0-9, ]+ users", score_select)[0].split(" ")[0]  # number of scorers
    except:
        pass
    score_users = re.sub("[\[\]]", "", score_users)

    rank_select = str(soup.select(".ranked strong")[0])
    rank = re.sub("<[^>]*>", "", rank_select)  # rank

    popularity_select = str(soup.select(".popularity strong")[0])
    popularity = re.sub("<[^>]*>", "", popularity_select)  # popularity

    members_select = str(soup.select(".members strong")[0])
    members = re.sub("<[^>]*>", "", members_select)  # members

    description_select_arr = soup.select(".pb16~ p")
    if len(description_select_arr) == 0:
        description = "No synopsis."
    else:
        description_select = str(description_select_arr[0])
        description = re.sub("<[^>]*>", "", description_select)  # description

    anime_type, eps, source, airing, studios, genres = get_anime_information_tab_info(response.content)

    info = {
        "title": title,  #
        "title_english": title_english,  #
        "poster": poster,  #
        "score": score,  #
        "score_users": score_users,  #
        "rank": rank,  #
        "popularity": popularity,
        "members": members,
        "description": description,  # body
        "anime_type": anime_type,  # footer
        "eps": eps,  # footer
        "source": source,
        "airing": airing,  # footer
        "studios": studios,  # desc
        "genres": genres,  # desc
        "url": url
    }
    return info


def get_anime_information_tab_info(text):
    info_text = text[text.find("<h2>Information</h2>"):text.find("<h2>Statistics</h2>")]
    og_info_text = f"{info_text}"
    divs = []
    while True:
        starting_index = info_text.find("<div")
        ending_index = info_text.find("</div>") + 6
        div = info_text[starting_index:ending_index]
        divs.append(div)
        info_text = info_text[ending_index:]
        if not info_text.__contains__("<div"):
            break
    divs.append("?")
    anime_type_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Type")])
    anime_type = re.sub("Type:", "", anime_type_selection).strip()  # type

    eps_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Episodes")])
    eps = re.sub("Episodes:", "", eps_selection).strip()  # eps

    source_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Source")])
    source = re.sub("Source:", "", source_selection).strip()  # src

    airing_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Aired")])
    airing = re.sub("Aired:", "", airing_selection).strip()  # airing

    studios_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Studios")])
    studios = re.sub("Studios:", "", studios_selection).strip()  # studios
    studios = studios.replace("&#039;", "'")
    if studios == "None found, add some":
        studios = "Unknown Studio"

    genres_list = []
    for genre_attr in ['Genres:', 'Demographic:', 'Theme:', 'Themes:']:
        if genre_attr in og_info_text:
            genre_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, genre_attr)])
            genre_selection = re.sub(f"{genre_attr}", "", genre_selection).strip()  # demographic
            genres_list.extend(genre_selection.split(","))
            
    genres_list_final = []
    for genre in genres_list:
        genre = genre.strip()
        genres_list_final.append(genre[:int(len(genre) / 2)])
    genres = ', '.join(genres_list_final)

    return anime_type, eps, source, airing, studios, genres


async def get_mal_manga_info(manga_id):
    url = f"https://myanimelist.net/manga/{manga_id}"
    response = await request("get", url, constants.CachingType.MAL_INFO_MANGA)
    soup = BeautifulSoup(response.content, features="lxml")

    title_select = soup.select(".h1-title span")
    title_select_0 = str(title_select[0])
    if title_select_0.__contains__("title-english"):
        title_select_0 = title_select_0[:title_select_0.find("<span class=\"title-english\"")]
    title = re.sub("<[^>]*>", "", title_select_0).replace('&amp;', '&')  # title
    title_english = ""
    if len(title_select) > 1:
        title_english = re.sub("<[^>]*>", "", str(title_select[1])).replace('&amp;', '&')  # title_english

    poster_leading_keywords = "<meta property=\"og:image\" content=\""
    poster_starting_index = response.content.find(poster_leading_keywords) + len(poster_leading_keywords)
    poster_ending_index = response.content.find("\"", poster_starting_index)
    poster = response.content[poster_starting_index:poster_ending_index]  # poster

    score_select = str(soup.select(".score").pop())
    score = re.sub("<[^>]*>", "", score_select)  # score
    score_users = ""
    try:
        score_users = re.findall("[0-9, ]+ users", score_select)[0].split(" ")[0]  # number of scorers
    except:
        pass
    score_users = re.sub("[\[\]]", "", score_users)

    rank_select = str(soup.select(".ranked strong")[0])
    rank = re.sub("<[^>]*>", "", rank_select)  # rank

    popularity_select = str(soup.select(".popularity strong")[0])
    popularity = re.sub("<[^>]*>", "", popularity_select)  # popularity

    members_select = str(soup.select(".members strong")[0])
    members = re.sub("<[^>]*>", "", members_select)  # members

    description_select_arr = soup.select("h2+ span")
    if len(description_select_arr) == 0:
        description = "No synopsis."
    else:
        description_select = str(description_select_arr[0])
        description = re.sub("<[^>]*>", "", description_select)  # description

    manga_type, volumes, chapters, published, authors, genres = get_manga_information_tab_info(response.content)

    info = {
        "title": title,  #
        "title_english": title_english,  #
        "poster": poster,  #
        "score": score,  #
        "score_users": score_users,  #
        "rank": rank,  #
        "popularity": popularity,
        "members": members,
        "description": description,  # body
        "manga_type": manga_type,  # footer
        "chapters": chapters,  # footer
        "volumes": volumes,  # footer
        "published": published,  # footer
        "authors": authors,  # desc
        "genres": genres,  # desc
        "url": url
    }
    return info


def get_manga_information_tab_info(text):
    info_text = text[text.find("<h2>Information</h2>"):text.find("<h2>Statistics</h2>")]
    og_info_text = f"{info_text}"
    divs = []
    while True:
        starting_index = info_text.find("<div")
        ending_index = info_text.find("</div>") + 6
        div = info_text[starting_index:ending_index]
        divs.append(div)
        info_text = info_text[ending_index:]
        if not info_text.__contains__("<div"):
            break
    divs.append("?")
    manga_type_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Type")])
    manga_type = re.sub("Type:", "", manga_type_selection).strip()  # type

    volumes_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Volumes")])
    volumes = re.sub("Volumes:", "", volumes_selection).strip()  # volumes

    chapters_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Chapters")])
    chapters = re.sub("Chapters:", "", chapters_selection).strip()  # eps

    published_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Published")])
    published = re.sub("Published:", "", published_selection).strip()  # published

    authors_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, "Authors")])
    authors = re.sub("Authors:", "", authors_selection).strip()  # authors
    authors = authors.replace("&#039;", "'")
    authors = authors.replace("&amp;", "&")
    if authors == "None found, add some":
        authors = "Unknown Authors"
    else:
        authors_list = authors.split(",")
        authors_list_final = []
        for author in authors_list:
            author = author.strip()
            authors_list_final.append(author)
        authors = ', '.join(authors_list_final)
    
    genres_list = []
    for genre_attr in ['Genres:', 'Demographic:', 'Theme:', 'Themes:']:
        if genre_attr in og_info_text:
            genre_selection = re.sub("<[^>]*>", "", divs[find_attribute_index(divs, genre_attr)])
            genre_selection = re.sub(f"{genre_attr}", "", genre_selection).strip()  # demographic
            genres_list.extend(genre_selection.split(","))
    
    genres_list_final = []
    for genre in genres_list:
        genre = genre.strip()
        genres_list_final.append(genre[:int(len(genre) / 2)].strip())
    genres = ', '.join(genres_list_final)

    return manga_type, volumes, chapters, published, authors, genres


def find_attribute_index(divs, attribute):
    for i in range(0, len(divs)):
        if divs[i].__contains__(attribute):
            return i
    return -1
