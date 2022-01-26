import disnake as discord

from globals_.constants import AnilistStatus
from models.anilist_profile import AnilistProfile


def make_anilist_profile_embed(profile_info: AnilistProfile, reacting_unlocked=False):
    """
    Makes the main page of an Anilist profile.
    :param (AnilistProfile) profile_info:
    :param (bool) reacting_unlocked: whether or not navigation was unlocked for everyone
    :return: discord.Embed
    """
    if profile_info is None:
        embed = discord.Embed(title=f"Error getting profile", colour=discord.Colour(0xe3cfaf),
                              description="There was an error while requesting your profile from the Anilist API. "
                                          "Please make sure you have a correct working username linked.")
        return embed

    anilist_user = profile_info
    username = anilist_user.name
    profile_url = anilist_user.site_url
    profile_avatar = anilist_user.avatar
    anime_days = round(anilist_user.anime_stats.minutes_watched / (60 * 24), 1)
    anime_avg_score = anilist_user.anime_stats.mean_score
    anime_entries = anilist_user.anime_stats.count
    anime_completed = anilist_user.anime_stats.get_status_stats(status=AnilistStatus.COMPLETED).count
    anime_current = anilist_user.anime_stats.get_status_stats(status=AnilistStatus.CURRENT).count
    manga_chapters = anilist_user.manga_stats.chapters_read
    manga_avg_score = anilist_user.manga_stats.mean_score
    manga_entries = anilist_user.manga_stats.count
    manga_completed = anilist_user.manga_stats.get_status_stats(status=AnilistStatus.COMPLETED).count
    manga_current = anilist_user.manga_stats.get_status_stats(status=AnilistStatus.CURRENT).count

    embed = discord.Embed(title=f"{username}", colour=discord.Colour(0xe3cfaf), url=f"{profile_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="Anilist profile", url=f"{profile_url}",
                     icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")

    embed.add_field(name="User Info",
                    value=(f"Joined Anilist: <t:{int(anilist_user.created_at)}:D>\n" if anilist_user.created_at else "")
                    + f"Last updated their profile: <t:{int(anilist_user.updated_at)}:R>\n‎‎‎",
                    inline=False)
    embed.add_field(name="Anime Stats",
                    value=f"**Days**: {anime_days}\n**Mean Score**: {anime_avg_score}\n"
                          f"**Completed & rewatched**: {anime_completed}\n**Watching**: {anime_current}"
                          f"\n**Total Anime:** {anime_entries}\n‎‎‎",
                    inline=True)
    embed.add_field(name="Manga Stats",
                    value=f"**Total Chapters:** {manga_chapters}\n**Mean Score**: {manga_avg_score}\n"
                          f"**Completed & reread**: {manga_completed}\n**Reading**: {manga_current}"
                          f"\n**Total Manga:** {manga_entries}\n‎‎‎",
                    inline=True)

    unlocked_navigating_str = "\n○ 🔓 Unlock navigating for everyone" if not reacting_unlocked else ""
    embed.add_field(name="Navigate", value="○ 📺 Anime List\n○ 📚 Manga List\n"
                                           f"○ ⭐ Favorites\n○ 🧮 Analysis"
                                           f"\n‎{unlocked_navigating_str}\n○ 🗑 Close embed",
                    inline=False)
    if anilist_user.banner:
        embed.set_image(url=anilist_user.banner)
    return embed


def make_anilist_profile_anime_list_embed(username, profile_avatar, anime_list, index, total_pages, scoring_system):
    list_url = f"https://anilist.co/user/{username}/animelist"
    profile_url = f"https://anilist.co/user/{username}"
    if total_pages == 0:
        embed = discord.Embed(title=f"{username}'s anime list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}",
                              description="‎‎‎\nThis list is empty!\n‎‎‎")

        embed.set_thumbnail(url=f"{profile_avatar}")
        embed.set_author(name="Anilist profile", url=f"{profile_url}",
                         icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")
        return embed
    embed = discord.Embed(title=f"{username}'s anime list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="Anilist profile", url=f"{profile_url}",
                     icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")
    embed.set_footer(text=f"Page {index}/{total_pages} | Total of {len(anime_list)} anime entries | Scoring system:"
                          f" {scoring_system}")
    starting_index = 0 + (index - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(anime_list)) else len(anime_list)
    new_line = "‎‎‎\n‎‎‎"
    empty_string = " "
    for i in range(starting_index, final_index):
        anime_name = anime_list[i].media.title.romaji
        anime_url = anime_list[i].media.site_url
        anime_rating = f" - {anime_list[i].score}" if anime_list[i].score != 0 else ''
        anime_status = str(anime_list[i].status.name).lower().capitalize()
        embed.add_field(name="‎‎‎", value=f"{i + 1}. [{anime_name}]({anime_url}) [{anime_status}{anime_rating}]"
                                          f"{new_line if i + 1 == final_index else empty_string}", inline=False)
    return embed


def make_anilist_profile_manga_list_embed(username, profile_avatar, manga_list, index, total_pages, scoring_system):
    list_url = f"https://anilist.co/user/{username}/mangalist"
    profile_url = f"https://anilist.co/user/{username}"
    if total_pages == 0:
        embed = discord.Embed(title=f"{username}'s manga list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}",
                              description="‎‎‎\nThis list is empty!\n‎‎‎")

        embed.set_thumbnail(url=f"{profile_avatar}")
        embed.set_author(name="Anilist profile", url=f"{profile_url}",
                         icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")
        return embed
    embed = discord.Embed(title=f"{username}'s manga list", colour=discord.Colour(0xe3cfaf), url=f"{list_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="Anilist profile", url=f"{profile_url}",
                     icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")
    embed.set_footer(text=f"Page {index}/{total_pages} | Total of {len(manga_list)} manga entries | Scoring system:"
                          f" {scoring_system}")
    starting_index = 0 + (index - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(manga_list)) else len(manga_list)
    new_line = "‎‎‎\n‎‎‎"
    empty_string = " "
    for i in range(starting_index, final_index):
        manga_name = manga_list[i].media.title.romaji
        manga_url = manga_list[i].media.site_url
        manga_rating = f" - {manga_list[i].score}" if manga_list[i].score != 0 else ''
        manga_status = str(manga_list[i].status.name).lower().capitalize()
        embed.add_field(name="‎‎‎", value=f"{i + 1}. [{manga_name}]({manga_url}) [{manga_status}{manga_rating}]"
                                          f"{new_line if i + 1 == final_index else empty_string}", inline=False)
    return embed


def make_anilist_profile_fav_list_embed(profile_info):
    username = profile_info.name
    profile_avatar = profile_info.avatar
    profile_url = profile_info.site_url
    anime_fav_list = profile_info.favourites.anime
    manga_fav_list = profile_info.favourites.manga
    characters_fav_list = profile_info.favourites.characters
    people_fav_list = profile_info.favourites.staff
    studio_fav_list = profile_info.favourites.studios

    exceeded_max_length = False
    if len(anime_fav_list) == 0:
        anime_fav_string = "No anime favorites."
    else:
        anime_fav_string = ""
        i = 1
        for anime_fav in anime_fav_list:
            title = anime_fav.romaji_title
            url = anime_fav.site_url
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
            title = manga_fav.romaji_title
            url = manga_fav.site_url
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
            title = characters_fav.romaji_title
            url = characters_fav.site_url
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
            title = people_fav.romaji_title
            url = people_fav.site_url
            if len(people_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                people_fav_string += "..."
                exceeded_max_length = True
                break
            people_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    if len(studio_fav_list) == 0:
        studio_fav_string = "No studio favorites."
    else:
        studio_fav_string = ""
        i = 1
        for studio_fav in studio_fav_list:
            title = studio_fav.romaji_title
            url = studio_fav.site_url
            if len(studio_fav_string + f"{i}. [{title}]({url})\n") > 1020:
                studio_fav_string += "..."
                exceeded_max_length = True
                break
            studio_fav_string += f"{i}. [{title}]({url})\n"
            i += 1

    embed = discord.Embed(title=f"{username}'s favorites", colour=discord.Colour(0xe3cfaf), url=f"{profile_url}")

    embed.set_thumbnail(url=f"{profile_avatar}")
    embed.set_author(name="Anilist profile", url=f"{profile_url}",
                     icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")

    embed.add_field(name="Anime", value=f"{anime_fav_string}")
    embed.add_field(name="Manga", value=f"{manga_fav_string}")
    embed.add_field(name="Characters", value=f"{characters_fav_string}")
    embed.add_field(name="Staff", value=f"{people_fav_string}")
    embed.add_field(name="Studios", value=f"{studio_fav_string}")
    if exceeded_max_length:
        embed.add_field(name="Too many favorites!!", value=f"Not all your favorites are shown because they are too"
                                                           f" many.")
    return embed


def make_anilist_profile_analysis_embed(profile_info: AnilistProfile):
    embed = discord.Embed(title=f"{profile_info.name}'s profile analysis",
                          colour=discord.Colour(0xe3cfaf),
                          url=f"{profile_info.site_url}")

    embed.set_thumbnail(url=f"{profile_info.avatar}")
    embed.set_author(name="Anilist profile", url=f"{profile_info.site_url}",
                     icon_url="https://anilist.co/img/icons/android-chrome-512x512.png")

    anilysis_text_1 = ""
    anilysis_text_2 = ""
    mangalysis_text_1 = ""
    mangalysis_text_2 = ""
    anilysis = profile_info.anilysis
    mangalysis = profile_info.mangalysis
    for analysis_point in [anilysis.amount_analysis, anilysis.score_analysis, anilysis.planning_analysis,
                           anilysis.current_analysis, anilysis.dropped_analysis, anilysis.paused_analysis]:
        if analysis_point:
            anilysis_text_1 += f"\n• {analysis_point}"
    for analysis_point in [anilysis.length_analysis, anilysis.release_years_analysis, anilysis.genres_analysis,
                           anilysis.tags_analysis, anilysis.voice_actors_analysis, anilysis.studios_analysis]:
        if analysis_point:
            anilysis_text_2 += f"\n• {analysis_point}"
    for analysis_point in [mangalysis.amount_analysis, mangalysis.score_analysis, mangalysis.planning_analysis,
                           mangalysis.current_analysis, mangalysis.paused_analysis]:
        if analysis_point:
            mangalysis_text_1 += f"\n• {analysis_point}"
    for analysis_point in [mangalysis.genres_analysis, mangalysis.tags_analysis, mangalysis.staff_analysis]:
        if analysis_point:
            mangalysis_text_2 += f"\n• {analysis_point}"

    embed.add_field(name="Anime analysis",
                    value=anilysis_text_1.strip() + ("\n‎" if not anilysis_text_2 else ""),
                    inline=False)
    if anilysis_text_2:
        embed.add_field(name="‎",
                        value=anilysis_text_2.strip() + "\n‎",
                        inline=False)
    embed.add_field(name="Manga analysis",
                    value=mangalysis_text_1.strip() + ("\n‎" if not mangalysis_text_2 else ""),
                    inline=False)
    if mangalysis_text_2:
        embed.add_field(name="‎",
                        value=mangalysis_text_2.strip() + "\n‎",
                        inline=False)

    return embed
