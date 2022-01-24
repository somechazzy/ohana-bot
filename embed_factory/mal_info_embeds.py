from globals_ import constants
import disnake as discord


def make_mal_anime_search_results_embed(query, results, author, thumbnail, num_of_results):
    query_20p = str(query).replace(" ", "%20")
    embed = discord.Embed(colour=discord.Colour(0x364b92),
                          url=f"https://myanimelist.net/anime.php?q={query_20p}&cat=anime",
                          description=f"_Query: '{query}'\n_")

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name="Showing MAL Search Results",
                     url=f"https://myanimelist.net/anime.php?q={query_20p}&cat=anime",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Search requested by {author}.",
                     icon_url=author.avatar.with_size(32).url if author.avatar else discord.embeds.EmptyEmbed)

    max_range = num_of_results
    if len(results) < num_of_results:
        max_range = len(results)

    for i in range(0, max_range):
        name = constants.NUMBERS_EMOJI_CODES[i] + " " + results[i]["title"]
        type_and_eps = "\t   [" + results[i]["type"] + \
                       " - " + results[i]["eps"] + "]"
        embed.add_field(name=name, value=type_and_eps, inline=False)

    return embed


def make_mal_manga_search_results_embed(query, results, author, thumbnail, num_of_results):
    query_20p = str(query).replace(" ", "%20")
    embed = discord.Embed(colour=discord.Colour(0x364b92),
                          url=f"https://myanimelist.net/manga.php?q={query_20p}&cat=manga",
                          description=f"_Query: '{query}'\n_")

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name="Showing MAL Search Results",
                     url=f"https://myanimelist.net/manga.php?q={query_20p}&cat=manga",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Search requested by {author}.",
                     icon_url=author.avatar.with_size(32).url if author.avatar else discord.embeds.EmptyEmbed)

    max_range = num_of_results
    if len(results) < num_of_results:
        max_range = len(results)

    for i in range(0, max_range):
        name = constants.NUMBERS_EMOJI_CODES[i] + " " + results[i]["title"]
        type_and_eps = "\t   [" + results[i]["type"] + \
                       " - " + results[i]["volumes"] + "]"
        embed.add_field(name=name, value=type_and_eps, inline=False)

    return embed


def make_mal_anime_info_embed(anime_info, username, user_stats, not_author, prefix, synopsis_expand=False):
    title = anime_info["title"]
    title_english = anime_info["title_english"]
    if title_english:
        title_english = f" / {title_english}"
    url = anime_info["url"]
    studios = anime_info["studios"]
    genres = anime_info["genres"]
    poster = anime_info["poster"]
    score = anime_info["score"]
    score_users = anime_info["score_users"]
    rank = anime_info["rank"]
    anime_type = anime_info["anime_type"]
    eps = anime_info["eps"]
    source = anime_info["source"]
    airing = anime_info["airing"]
    description = anime_info["description"]
    description_shortened = False
    if len(description) > 600 and not synopsis_expand:
        description = description[:600] + "... (📜 to expand)"
        description_shortened = True
    if synopsis_expand:
        bigger_than_limit = len(description) > 1018
        description = description[:1018] + ("..." if bigger_than_limit else "")

    embed = discord.Embed(title=f"{title}{title_english}", colour=discord.Colour(0x364b92), url=f"{url}",
                          description=f"{studios} | {genres}")

    embed.set_thumbnail(url=f"{poster}")
    if not score_users:
        score_users = 0
    embed.set_author(name=f"Rated {score} by {score_users} users | Ranked {rank}", url=f"{url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"{anime_type} | Source: {source} | Episodes: {eps}  | Aired: {airing}")

    embed.add_field(name="Synopsis", value=f"{description.strip()}\n‎", inline=False)
    if username is not None and username != "" and username != "None":
        value = "The requested user doesn't" if not_author else "You don't"
        value += " have this anime on " + ("their" if not_author else "your") + " list.\n‎‎‎"
        if user_stats is not None:
            if isinstance(user_stats.status, int):
                status = constants.MAL_ANIME_STATUS_MAPPING[str(user_stats.status)]
            else:
                status = user_stats.status
            watched_eps = user_stats.num_watched_episodes
            rating = user_stats.score
            if rating == "" or rating == "None" or not rating:
                rating = "?"
            starting_date = user_stats.start_date_string
            if starting_date == "" or starting_date == "None" or not starting_date:
                starting_date = "?"
            ending_date = user_stats.finish_date_string
            if ending_date == "" or ending_date == "None" or not ending_date:
                ending_date = "?"
            days = user_stats.days_string
            if days == "" or days == "None" or not days:
                days = "?"
            repeats_string = f" - rewatched {user_stats.repeat} time{'s' if user_stats.repeat > 1 else ''}" \
                if user_stats.repeat else ""
            rating_system_string = f" ({constants.ANILIST_SCORING_SYSTEM[user_stats.rating_system]} rating system)"\
                if user_stats.rating_system else ""
            value = f"**Status:** {status} ({watched_eps} eps){repeats_string}\n" \
                    f"**Rated:** {rating}{rating_system_string}\n" \
                    f"**Started/Finished:** {starting_date} - {ending_date} ({days} days)\n‎‎‎"
        embed.add_field(name=f"Stats for {username}",
                        value=value, inline=False)
    else:
        name = "Requested user hasn't linked their MAL or Anilist" if not_author \
            else "Add your MAL or Anilist to get your own stats here."
        embed.add_field(name=name,
                        value=f"Use `{prefix}linkmal [username]` or `{prefix}linkal [username]`\n‎‎‎", inline=False)
    return embed, description_shortened


def make_mal_manga_info_embed(manga_info, username, user_stats, not_author, prefix, synopsis_expand=False):
    title = manga_info["title"]
    title_english = manga_info["title_english"]
    if title_english:
        title_english = f" / {title_english}"
    url = manga_info["url"]
    authors = manga_info["authors"]
    genres = manga_info["genres"]
    poster = manga_info["poster"]
    score = manga_info["score"]
    score_users = manga_info["score_users"]
    rank = manga_info["rank"]
    manga_type = manga_info["manga_type"]
    chapters = manga_info["chapters"]
    published = manga_info["published"]
    description = manga_info["description"]
    description_shortened = False
    if len(description) > 600 and not synopsis_expand:
        description = description[:600] + "... (📜 to expand)"
        description_shortened = True
    if synopsis_expand:
        bigger_than_limit = len(description) > 1018
        description = description[:1018] + ("..." if bigger_than_limit else "")

    embed = discord.Embed(title=f"{title}{title_english}", colour=discord.Colour(0x364b92), url=f"{url}",
                          description=f"{authors} | {genres}")

    embed.set_thumbnail(url=f"{poster}")
    if not score_users:
        score_users = 0
    embed.set_author(name=f"Rated {score} by {score_users} users | Ranked {rank}", url=f"{url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"{manga_type} | Chapters: {chapters} | Published: {published}")

    embed.add_field(name="Synopsis", value=f"{description.strip()}\n‎", inline=False)
    if username is not None and username != "" and username != "None":
        value = "The requested user doesn't" if not_author else "You don't"
        value += " have this manga on " + ("their" if not_author else "your") + " list.\n‎‎‎"
        if user_stats is not None:
            if isinstance(user_stats.status, int):
                status = constants.MAL_MANGA_STATUS_MAPPING[str(user_stats.status)]
            else:
                status = user_stats.status
            read_chapters = user_stats.num_read_chapters
            rating = user_stats.score
            if rating == "" or rating == "None" or not rating:
                rating = "?"
            starting_date = user_stats.start_date_string
            if starting_date == "" or starting_date == "None" or not starting_date:
                starting_date = "?"
            ending_date = user_stats.finish_date_string
            if ending_date == "" or ending_date == "None" or not ending_date:
                ending_date = "?"
            days = user_stats.days_string
            if days == "" or days == "None" or not days:
                days = "?"
            repeats_string = f" - re-read {user_stats.repeat} time{'s' if user_stats.repeat > 1 else ''}" \
                if user_stats.repeat else ""
            rating_system_string = f" ({constants.ANILIST_SCORING_SYSTEM[user_stats.rating_system]} rating system)"\
                if user_stats.rating_system else ""
            value = f"**Status:** {status} ({read_chapters} chapters){repeats_string}\n" \
                    f"**Rated:** {rating}{rating_system_string}\n" \
                    f"**Started/Finished:** {starting_date} - {ending_date} ({days} days)\n‎‎‎"
        embed.add_field(name=f"Stats for {username}",
                        value=value, inline=False)
    else:
        name = "Requested user hasn't linked their MAL or Anilist" if not_author \
            else "Add your MAL or Anilist to get your own stats here."
        embed.add_field(name=name,
                        value=f"Use `{prefix}linkmal [username]` or `{prefix}linkal [username]`\n‎‎‎", inline=False)
    return embed, description_shortened
