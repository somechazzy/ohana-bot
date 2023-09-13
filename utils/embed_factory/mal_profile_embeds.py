import discord

from globals_.constants import Colour, MAL_ANIME_STATUS_MAPPING, MAL_MANGA_STATUS_MAPPING


def make_mal_profile_embed(profile_info, reacting_unlocked=False):
    username = profile_info["username"]
    profile_url = f"https://myanimelist.net/profile/{username}"
    profile_avatar = profile_info["profile_avatar"]
    profile_banner = profile_info["profile_banner"]
    anime_days = profile_info["anime_days"]
    anime_avg_score = profile_info["anime_avg_score"]
    manga_days = profile_info["manga_days"]
    manga_avg_score = profile_info["manga_avg_score"]
    anime_watching = profile_info["anime_watching"]
    anime_completed = profile_info["anime_completed"]
    anime_entries = profile_info["anime_entries"]
    anime_rewatched = profile_info["anime_rewatched"]
    anime_episodes = profile_info["anime_episodes"]
    manga_reading = profile_info["manga_reading"]
    manga_completed = profile_info["manga_completed"]
    manga_entries = profile_info["manga_entries"]
    manga_reread = profile_info["manga_reread"]
    manga_chapters = profile_info["manga_chapters"]
    user_info = profile_info["user_info"]

    joined = user_info.get("Joined", "N/A")
    last_online = user_info.get("Last Online", "N/A")
    gender = user_info.get("Gender", "N/A")
    birthday = user_info.get("Birthday", "N/A")
    location = user_info.get("Location", "N/A")

    embed = discord.Embed(title=f"{username}", colour=Colour.EXT_MAL, url=f"{profile_url}")

    embed.set_thumbnail(url=profile_avatar or None)
    embed.set_image(url=profile_banner or None)
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Joined: {joined} | Last Online: {last_online}.")

    embed.add_field(name="User Info",
                    value=f"**Gender:** {gender}\n**Birthday:** {birthday}\n**Location:** {location}\n‎",
                    inline=False)
    embed.add_field(name="Anime Stats",
                    value=f"**Days**: {anime_days}\n**Avg Score**: {anime_avg_score}\n**Watching:** {anime_watching}"
                          f"\n**Completed:** {anime_completed}\n**Total Anime:** "
                          f"{anime_entries}\n**Rewatched:** {anime_rewatched}\n**Total Eps:** {anime_episodes}\n‎",
                    inline=True)
    embed.add_field(name="Manga Stats",
                    value=f"**Days**: {manga_days}\n**Avg Score**: {manga_avg_score}\n**Reading:** {manga_reading}"
                          f"\n**Completed:** {manga_completed}\n**Total Manga:**"
                          f" {manga_entries}\n**Reread:** {manga_reread}\n**Total Chapters:** {manga_chapters}\n‎",
                    inline=True)
    unlocked_navigating_str = "\n○ 🔓 Unlock navigating for everyone" if not reacting_unlocked else ""
    embed.add_field(name="React To Navigate", value="○ 📺 Anime List\n"
                                                    "○ 📚 Manga List\n"
                                                    f"○ ⭐ Favorites\n"
                                                    f"‎{unlocked_navigating_str}\n"
                                                    f"○ 🗑 Close embed\n‎",
                    inline=False)

    return embed


def make_mal_profile_anime_list_embed(username, profile_avatar, anime_list, page, total_pages):
    list_url = f"https://myanimelist.net/animelist/{username}?status=7"
    profile_url = f"https://myanimelist.net/profile/{username}"

    embed = discord.Embed(title=f"{username}'s anime list", colour=Colour.EXT_MAL, url=f"{list_url}")
    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")

    if not total_pages:
        embed.description = "‎\nThis list is empty!\n‎"
        starting_index = final_index = 0
    else:
        embed.set_footer(text=f"Page {page}/{total_pages} | Total of {len(anime_list)} anime entries")
        starting_index = (page - 1) * 10
        final_index = starting_index + 10

    for i, entry in enumerate(anime_list[starting_index:final_index], starting_index):
        anime_name = entry.anime_title
        anime_url = f"https://myanimelist.net/anime/{entry.anime_id}"
        anime_rating = f" - {entry.score}" if entry.score != 0 else ''
        anime_status = MAL_ANIME_STATUS_MAPPING[str(entry.status)]
        embed.add_field(name="‎",
                        value=f"{i + 1}. [{anime_name}]({anime_url}) [{anime_status}{anime_rating}]"
                              + ("\n‎" if i + 1 == final_index else ""),
                        inline=False)

    return embed


def make_mal_profile_manga_list_embed(username, profile_avatar, manga_list, page, total_pages):
    list_url = f"https://myanimelist.net/mangalist/{username}?status=7"
    profile_url = f"https://myanimelist.net/profile/{username}"

    embed = discord.Embed(title=f"{username}'s manga list", colour=Colour.EXT_MAL, url=f"{list_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")

    if not total_pages:
        embed.description = "‎\nThis list is empty!\n‎"
        starting_index = final_index = 0
    else:
        embed.set_footer(text=f"Page {page}/{total_pages} | Total of {len(manga_list)} manga entries")
        starting_index = (page - 1) * 10
        final_index = starting_index + 10

    for i, entry in enumerate(manga_list[starting_index:final_index], starting_index):
        manga_name = entry.manga_title
        manga_url = f"https://myanimelist.net/manga/{entry.manga_id}"
        manga_rating = f" - {entry.score}" if entry.score != 0 else ''
        manga_status = MAL_MANGA_STATUS_MAPPING[str(entry.status)]
        embed.add_field(name="‎",
                        value=f"{i + 1}. [{manga_name}]({manga_url}) [{manga_status}{manga_rating}]"
                              + ("\n‎" if i + 1 == final_index else ""),
                        inline=False)
    return embed


def make_mal_profile_favorites_embed(profile_info):
    username = profile_info["username"]
    profile_avatar = profile_info["profile_avatar"]
    profile_url = f"https://myanimelist.net/profile/{username}"
    anime_fav_list = profile_info["anime_fav_list"]
    manga_fav_list = profile_info["manga_fav_list"]
    characters_fav_list = profile_info["characters_fav_list"]
    people_fav_list = profile_info["people_fav_list"]
    company_fav_list = profile_info["company_fav_list"]

    exceeded_max_length = False
    if not anime_fav_list or anime_fav_list[0]["title"] == "[]":
        anime_fav_string = "No anime favorites."
    else:
        anime_fav_string = ""
        i = 1
        for anime_fav in anime_fav_list:
            title = anime_fav["title"]
            url = anime_fav["url"]
            if len(anime_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                anime_fav_string += "..."
                exceeded_max_length = True
                break
            anime_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    if not manga_fav_list or manga_fav_list[0]["title"] == "[]":
        manga_fav_string = "No manga favorites."
    else:
        manga_fav_string = ""
        i = 1
        for manga_fav in manga_fav_list:
            title = manga_fav["title"]
            url = manga_fav["url"]
            if len(manga_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                manga_fav_string += "..."
                exceeded_max_length = True
                break
            manga_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    if not characters_fav_list or characters_fav_list[0]["title"] == "[]":
        characters_fav_string = "No character favorites."
    else:
        characters_fav_string = ""
        i = 1
        for characters_fav in characters_fav_list:
            title = characters_fav["title"]
            url = characters_fav["url"]
            if len(characters_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                characters_fav_string += "..."
                exceeded_max_length = True
                break
            characters_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    if not people_fav_list or people_fav_list[0]["title"] == "[]":
        people_fav_string = "No people favorites."
    else:
        people_fav_string = ""
        i = 1
        for people_fav in people_fav_list:
            title = people_fav["title"]
            url = people_fav["url"]
            if len(people_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                people_fav_string += "..."
                exceeded_max_length = True
                break
            people_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    if not company_fav_list or company_fav_list[0]["title"] == "[]":
        company_fav_string = "No company favorites."
    else:
        company_fav_string = ""
        i = 1
        for company_fav in company_fav_list:
            title = company_fav["title"]
            url = company_fav["url"]
            if len(company_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                company_fav_string += "..."
                exceeded_max_length = True
                break
            company_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    embed = discord.Embed(title=f"{username}'s favorites", colour=Colour.EXT_MAL, url=f"{profile_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")

    embed.add_field(name="Anime", value=f"{anime_fav_string}")
    embed.add_field(name="Manga", value=f"{manga_fav_string}")
    embed.add_field(name="Characters", value=f"{characters_fav_string}")
    embed.add_field(name="People", value=f"{people_fav_string}")
    embed.add_field(name="Companies", value=f"{company_fav_string}")
    if exceeded_max_length:
        embed.add_field(name="Too many favorites!!",
                        value=f"We couldn't display all of your favorites because there are too many.")
    return embed
