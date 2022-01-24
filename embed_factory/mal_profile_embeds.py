from globals_ import constants
import disnake as discord


def make_mal_profile_embed(info_dict, reacting_unlocked=False):
    username = info_dict["username"]
    profile_url = f"https://myanimelist.net/profile/{username}"
    profile_avatar = info_dict["profile_avatar"]
    joined = info_dict["joined"]
    last_online = info_dict["last_online"]
    gender = info_dict["gender"]
    birthday = info_dict["birthday"]
    location = info_dict["location"]
    anime_days = info_dict["anime_days"]
    anime_avg_score = info_dict["anime_avg_score"]
    manga_days = info_dict["manga_days"]
    manga_avg_score = info_dict["manga_avg_score"]
    anime_watching = info_dict["anime_watching"]
    anime_completed = info_dict["anime_completed"]
    anime_entries = info_dict["anime_entries"]
    anime_rewatched = info_dict["anime_rewatched"]
    anime_episodes = info_dict["anime_episodes"]
    manga_reading = info_dict["manga_reading"]
    manga_completed = info_dict["manga_completed"]
    manga_entries = info_dict["manga_entries"]
    manga_reread = info_dict["manga_reread"]
    manga_chapters = info_dict["manga_chapters"]

    embed = discord.Embed(title=f"{username}", colour=discord.Colour(0xe3cfaf), url=f"{profile_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Joined: {joined} | Last Online: {last_online}.")

    embed.add_field(name="User Info",
                    value=f"**Gender:** {gender}\n**Birthday:** {birthday}\n**Location:** {location}\n‎‎‎",
                    inline=False)
    embed.add_field(name="Anime Stats",
                    value=f"**Days**: {anime_days}\n**Avg Score**: {anime_avg_score}\n**Watching:** {anime_watching}"
                          f"\n**Completed:** {anime_completed}\n**Total Anime:** "
                          f"{anime_entries}\n**Rewatched:** {anime_rewatched}\n**Total Eps:** {anime_episodes}\n‎‎‎",
                    inline=True)
    embed.add_field(name="Manga Stats",
                    value=f"**Days**: {manga_days}\n**Avg Score**: {manga_avg_score}\n**Reading:** {manga_reading}"
                          f"\n**Completed:** {manga_completed}\n**Total Manga:**"
                          f" {manga_entries}\n**Reread:** {manga_reread}\n**Total Chapters:** {manga_chapters}\n‎‎‎",
                    inline=True)
    unlocked_navigating_str = "\n○ 🔓 Unlock navigating for everyone" if not reacting_unlocked else ""
    embed.add_field(name="React To Navigate", value="○ 📺 Anime List\n○ 📚 Manga List\n"
                                                    f"○ ⭐ Favorites\n‎{unlocked_navigating_str}\n○ 🗑 Close embed\n‎‎‎",
                    inline=False)

    return embed


def make_mal_profile_anime_list_embed(username, profile_avatar, anime_list, index, total_pages):
    list_url = f"https://myanimelist.net/animelist/{username}?status=7"
    profile_url = f"https://myanimelist.net/profile/{username}"
    if total_pages == 0:
        embed = discord.Embed(title=f"{username}'s anime list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}",
                              description="‎‎‎\nThis list is empty!\n‎‎‎")

        embed.set_thumbnail(url=f"{profile_avatar}")
        embed.set_author(name="MAL profile", url=f"{profile_url}",
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
        return embed
    embed = discord.Embed(title=f"{username}'s anime list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Page {index}/{total_pages} | Total of {len(anime_list)} anime entries")
    starting_index = 0 + (index - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(anime_list)) else len(anime_list)
    new_line = "‎‎‎\n‎‎‎"
    empty_string = " "
    for i in range(starting_index, final_index):
        anime_name = anime_list[i].anime_title
        anime_url = f"https://myanimelist.net/anime/{anime_list[i].anime_id}"
        anime_rating = f" - {anime_list[i].score}" if anime_list[i].score != 0 else ''
        anime_status = constants.MAL_ANIME_STATUS_MAPPING[str(anime_list[i].status)]
        embed.add_field(name="‎‎‎", value=f"{i + 1}. [{anime_name}]({anime_url}) [{anime_status}{anime_rating}]"
                                          f"{new_line if i + 1 == final_index else empty_string}", inline=False)
    return embed


def make_mal_profile_manga_list_embed(username, profile_avatar, manga_list, index, total_pages):
    list_url = f"https://myanimelist.net/mangalist/{username}?status=7"
    profile_url = f"https://myanimelist.net/profile/{username}"
    if total_pages == 0:
        embed = discord.Embed(title=f"{username}'s manga list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}",
                              description="‎‎‎\nThis list is empty!\n‎‎‎")

        embed.set_thumbnail(url=f"{profile_avatar}")
        embed.set_author(name="MAL profile", url=f"{profile_url}",
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
        return embed
    embed = discord.Embed(title=f"{username}'s manga list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")
    embed.set_footer(text=f"Page {index}/{total_pages} | Total of {len(manga_list)} manga entries")
    starting_index = 0 + (index - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(manga_list)) else len(manga_list)
    new_line = "‎‎‎\n‎‎‎"
    empty_string = " "
    for i in range(starting_index, final_index):
        manga_name = manga_list[i].manga_title
        manga_url = f"https://myanimelist.net/manga/{manga_list[i].manga_id}"
        manga_rating = f" - {manga_list[i].score}" if manga_list[i].score != 0 else ''
        manga_status = constants.MAL_MANGA_STATUS_MAPPING[str(manga_list[i].status)]
        embed.add_field(name="‎‎‎", value=f"{i + 1}. [{manga_name}]({manga_url}) [{manga_status}{manga_rating}]"
                                          f"{new_line if i + 1 == final_index else empty_string}", inline=False)
    return embed


def make_mal_profile_fav_list_embed(profile_info):
    username = profile_info["username"]
    profile_avatar = profile_info["profile_avatar"]
    profile_url = f"https://myanimelist.net/profile/{username}"
    anime_fav_list = profile_info["anime_fav_list"]
    manga_fav_list = profile_info["manga_fav_list"]
    characters_fav_list = profile_info["characters_fav_list"]
    people_fav_list = profile_info["people_fav_list"]

    exceeded_max_length = False
    if len(anime_fav_list) == 0:
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

    if len(manga_fav_list) == 0:
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

    if len(characters_fav_list) == 0:
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

    if len(people_fav_list) == 0:
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

    embed = discord.Embed(title=f"{username}'s favorites", colour=discord.Colour(0xe3cfaf), url=f"{profile_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="MAL profile", url=f"{profile_url}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png")

    embed.add_field(name="Anime", value=f"{anime_fav_string}")
    embed.add_field(name="Manga", value=f"{manga_fav_string}")
    embed.add_field(name="Characters", value=f"{characters_fav_string}")
    embed.add_field(name="People", value=f"{people_fav_string}")
    if exceeded_max_length:
        embed.add_field(name="Too many favorites!!", value=f"Not all your favorites are shown because they are too"
                                                           f" many.")
    return embed
