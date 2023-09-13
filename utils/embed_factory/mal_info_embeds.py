import discord
from globals_.constants import Colour, ANILIST_SCORING_SYSTEM_MAP, NUMBERS_EMOJI_CODES
import urllib.parse


def make_mal_anime_search_results_embed(query, results, author, thumbnail, num_of_results=5):
    embed = discord.Embed(colour=Colour.EXT_MAL,
                          url=f"https://myanimelist.net/anime.php?q={urllib.parse.quote(query)}&cat=anime",
                          description=f"_Query: '{query}'\n_")

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name="Showing MAL Search Results",
                     url=f"https://myanimelist.net/anime.php?q={urllib.parse.quote(query)}&cat=anime",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Search requested by {author}.",
                     icon_url=author.avatar.with_size(128).url if author.avatar else None)

    for i, result in enumerate(results[:num_of_results]):
        name = NUMBERS_EMOJI_CODES[i] + " " + result["title"]
        type_and_eps = "‎   [" + result["type"] + " - " + result["eps"] + "]"
        embed.add_field(name=name, value=type_and_eps, inline=False)

    return embed


def make_mal_manga_search_results_embed(query, results, author, thumbnail, num_of_results=5):
    embed = discord.Embed(colour=Colour.EXT_MAL,
                          url=f"https://myanimelist.net/manga.php?q={urllib.parse.quote(query)}&cat=manga",
                          description=f"_Query: '{query}'\n_")

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name="Showing MAL Search Results",
                     url=f"https://myanimelist.net/manga.php?q={urllib.parse.quote(query)}&cat=manga",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Search requested by {author}.",
                     icon_url=author.avatar.with_size(128).url if author.avatar else None)

    for i, result in enumerate(results[:num_of_results]):
        name = NUMBERS_EMOJI_CODES[i] + " " + result["title"]
        type_and_eps = "‎   [" + result["type"] + " - " + result["volumes"] + "]"
        embed.add_field(name=name, value=type_and_eps, inline=False)

    return embed


def make_mal_anime_info_embed(anime_info, user_stats, synopsis_expanded=False):
    title = anime_info["title"]
    title_english = anime_info.get('alternative_titles', {}).get('en')
    url = f"https://myanimelist.net/anime/{anime_info['id']}"
    studios = ', '.join([studio['name'] for studio in anime_info.get('studios', [])]) or 'Unknown'
    genres = ', '.join([genre['name'] for genre in anime_info.get('genres', [])]) or 'Unknown'
    thumbnail = anime_info.get('main_picture', {}).get('medium', anime_info.get('main_picture', {}).get('large'))
    score = anime_info.get('mean', '-') or '-'
    score_users = anime_info.get('num_scoring_users', '-') or '-'
    if isinstance(score_users, int) or score_users.isdigit():
        score_users = f"{int(score_users):,}"
    rank = anime_info.get('rank', '-') or '-'
    anime_type = anime_info.get('media_type', 'Unknown').replace('_', ' ').upper()
    eps = anime_info.get('num_episodes', 'Unknown') or 'Unknown'
    source = anime_info.get('source', 'Unknown').replace('_', ' ').title()
    if anime_info.get('start_date'):
        airing = anime_info['start_date']
        if anime_info.get('end_date'):
            airing += f" to {anime_info['end_date']}"
        else:
            airing += " - N/A"
    else:
        airing = 'Unknown'
    description = anime_info.get('synopsis', 'No synopsis available.')
    description_shortened = False
    if len(description) > 600 and not synopsis_expanded:
        description = description[:600] + "... (📜 to expand)"
        description_shortened = True
    if synopsis_expanded:
        bigger_than_limit = len(description) > 1000
        description = description[:1000] + ("..." if bigger_than_limit else "")

    embed = discord.Embed(title=f"{title} {('/ ' + title_english) if title_english else ''}",
                          colour=Colour.EXT_MAL,
                          url=f"{url}",
                          description=f"**Studio:** {studios}\n"
                                      f"**Genres:** {genres}")

    embed.set_thumbnail(url=thumbnail or None)
    embed.set_author(name=f"Rated {score} by {score_users} users | Ranked #{rank}", url=f"{url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"{anime_type} | Source: {source} | Episodes: {eps}  | Aired: {airing}")

    embed.add_field(name="Synopsis", value=f"{description.strip()}\n‎", inline=False)

    if user_stats:
        username = user_stats["username"]
        status = user_stats.get("status")
        if not status:
            value = f"**Status:** Not in your list"
        else:
            watched_episodes = user_stats.get('progress', 0)
            score = user_stats.get('score', 'N/A')
            scoring_system = ANILIST_SCORING_SYSTEM_MAP.get(user_stats.get('scoring_system'), '')
            if scoring_system:
                scoring_system = f" ({scoring_system} rating system)"
            repeated_text = f" - rewatched {user_stats['rewatch_count']} times" \
                if user_stats.get("rewatch_count") else ""
            started_finished_date = user_stats.get('start_and_finish_dates', 'N/A')
            value = f"**Status:** {status} ({watched_episodes} eps){repeated_text}\n" \
                    f"**Rated:** {score}{scoring_system}\n" \
                    f"**Started/Finished:** {started_finished_date}\n‎"
        embed.add_field(name=f"Stats for {username}",
                        value=value,
                        inline=False)
    else:
        embed.add_field(name="Link your MAL or Anilist account to get your stats here",
                        value=f"Use `/link-myanimelist` or `link-anilist`\n‎",
                        inline=False)
    return embed, description_shortened


def make_mal_manga_info_embed(manga_info, user_stats, synopsis_expanded=False):
    title = manga_info["title"]
    title_english = manga_info.get('alternative_titles', {}).get('en')
    url = f"https://myanimelist.net/manga/{manga_info['id']}"
    authors = ', '.join([f"{author['node'].get('first_name', '-')} {author['node'].get('last_name', '')} "
                         f"({author['role']})"
                         for author in manga_info['authors']]) or 'Unknown'
    genres = ', '.join([genre['name'] for genre in manga_info.get('genres', [])]) or 'Unknown'
    thumbnail = manga_info.get('main_picture', {}).get('medium', manga_info.get('main_picture', {}).get('large'))
    score = manga_info.get('mean', '-') or '-'
    score_users = manga_info.get('num_scoring_users', '-') or '-'
    if isinstance(score_users, int) or score_users.isdigit():
        score_users = f"{int(score_users):,}"
    rank = manga_info.get('rank', '-') or '-'
    manga_type = manga_info.get('media_type', 'Unknown').replace('_', ' ').upper()
    chapters = manga_info.get('num_chapters', 'Unknown') or 'Unknown'
    if manga_info.get('start_date'):
        published = manga_info['start_date']
        if manga_info.get('end_date'):
            published += f" to {manga_info['end_date']}"
        else:
            published += " - N/A"
    else:
        published = 'Unknown'
    description = manga_info.get('synopsis', 'No synopsis available.')
    description_shortened = False
    if len(description) > 600 and not synopsis_expanded:
        description = description[:600] + "... (📜 to expand)"
        description_shortened = True
    if synopsis_expanded:
        bigger_than_limit = len(description) > 1018
        description = description[:1018] + ("..." if bigger_than_limit else "")

    embed = discord.Embed(title=f"{title} {('/ ' + title_english) if title_english else ''}",
                          colour=Colour.EXT_MAL,
                          url=f"{url}",
                          description=f"**Author:** {authors}\n"
                                      f"**Genres:** {genres}")

    embed.set_thumbnail(url=thumbnail or None)

    embed.set_author(name=f"Rated {score} by {score_users} users | Ranked #{rank}", url=f"{url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"{manga_type} | Chapters: {chapters} | Published: {published}")

    embed.add_field(name="Synopsis", value=f"{description.strip()}\n‎", inline=False)

    if user_stats:
        username = user_stats["username"]
        status = user_stats.get("status")
        if not status:
            value = f"**Status:** Not in your list"
        else:
            read_chapters = user_stats.get('progress', 0)
            score = user_stats.get('score', 'N/A')
            scoring_system = ANILIST_SCORING_SYSTEM_MAP.get(user_stats.get('scoring_system'), '')
            if scoring_system:
                scoring_system = f" ({scoring_system} rating system)"
            repeated_text = f" - reread {user_stats['reread_count']} times" if user_stats.get("reread_count") else ""
            started_finished_date = user_stats.get('start_and_finish_dates', 'N/A')
            value = f"**Status:** {status} ({read_chapters} chapters){repeated_text}\n" \
                    f"**Rated:** {score}{scoring_system}\n" \
                    f"**Started/Finished:** {started_finished_date}\n‎"
        embed.add_field(name=f"Stats for {username}",
                        value=value,
                        inline=False)
    else:
        embed.add_field(name="Link your MAL or Anilist account to get your stats here",
                        value=f"Use `/link-myanimelist` or `link-anilist`\n‎",
                        inline=False)

    return embed, description_shortened
