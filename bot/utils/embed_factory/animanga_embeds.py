from datetime import datetime

import discord

from clients import emojis
from constants import Colour, AnimangaProvider, Links, UserAnimeStatus, DiscordTimestamp, UserMangaStatus, \
    AnimangaListLoadingStatus, AnimeMediaType
import urllib.parse

from models.dto.animanga import AnimeSearchResult, AnimeInfo, UserAnimeListEntry, MangaInfo, \
    UserMangaListEntry, UserAnimangaProfile, MangaSearchResult
from utils.helpers.text_manipulation_helpers import shorten_text, get_human_readable_number


def get_anime_search_results_embed(search_results: AnimeSearchResult, page_size: int) -> discord.Embed:
    """
    Create a Discord embed for anime search results.
    Args:
        search_results (AnimeSearchResult): The search results to display.
        page_size (int): The number of results to display per page.

    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if search_results.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        search_url = Links.MAL_ANIME_SEARCH_URL.format(query=urllib.parse.quote(search_results.original_query))
        logo = Links.Media.MAL_LOGO
    elif search_results.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        search_url = Links.ANILIST_ANIME_SEARCH_URL.format(query=urllib.parse.quote(search_results.original_query))
        logo = Links.Media.ANILIST_LOGO
    else:
        raise NotImplementedError(f"Unsupported source provider: {search_results.source_provider}")

    embed = discord.Embed(
        colour=embed_color,
        url=search_url,
        description=f"_Query: '{search_results.original_query}'\n_"
    )

    thumbnails = [search_result.image_url for search_result in search_results.entries]
    embed.set_thumbnail(url=thumbnails[0] if thumbnails else logo)

    embed.set_author(name="Showing anime search results",
                     url=search_url,
                     icon_url=logo)

    for i, result in enumerate(search_results.entries[:page_size], 1):
        title = shorten_text(result.native_title + (f" / {result.english_title}" if result.english_title else ''), 100)
        additional_info = []
        if result.release_year:
            additional_info.append(str(result.release_year))
        if result.media_type:
            additional_info.append(result.media_type)
        additional_info.append(f"Rated {result.score or '?'}")
        embed.add_field(name=f"{emojis.numbers[i]} ‎ {title}",
                        value=' • '.join(additional_info),
                        inline=False)

    return embed


def get_manga_search_results_embed(search_results: MangaSearchResult, page_size: int) -> discord.Embed:
    """
    Create a Discord embed for manga search results.
    Args:
        search_results (MangaSearchResult): The search results to display.
        page_size (int): The number of results to display per page.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if search_results.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        search_url = Links.MAL_MANGA_SEARCH_URL.format(query=urllib.parse.quote(search_results.original_query))
        logo = Links.Media.MAL_LOGO
    elif search_results.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        search_url = Links.ANILIST_MANGA_SEARCH_URL.format(query=urllib.parse.quote(search_results.original_query))
        logo = Links.Media.ANILIST_LOGO
    else:
        raise NotImplementedError(f"Unsupported source provider: {search_results.source_provider}")

    embed = discord.Embed(
        colour=embed_color,
        url=search_url,
        description=f"_Query: '{search_results.original_query}'\n_"
    )

    thumbnails = [search_result.image_url for search_result in search_results.entries]
    embed.set_thumbnail(url=thumbnails[0] if thumbnails else logo)

    embed.set_author(name="Showing manga search results",
                     url=search_url,
                     icon_url=logo)

    for i, result in enumerate(search_results.entries[:page_size], 1):
        title = shorten_text(result.native_title + (f" / {result.english_title}" if result.english_title else ''), 100)
        additional_info = []
        if result.release_year:
            additional_info.append(str(result.release_year))
        if result.media_type:
            additional_info.append(result.media_type)
        additional_info.append(f"Rated {result.score or '?'}")
        embed.add_field(name=f"{emojis.numbers[i]} ‎ {title}",
                        value=' • '.join(additional_info),
                        inline=False)

    return embed


def get_anime_info_embed(anime_info: AnimeInfo,
                         anime_user_entry: UserAnimeListEntry | None,
                         synopsis_expanded: bool = False) -> discord.Embed:
    """
    Create a Discord embed for anime information.
    Args:
        anime_info (AnimeInfo): The DTO containing anime information.
        anime_user_entry (UserAnimeListEntry | None): The user's list entry for this anime, if available.
        synopsis_expanded (bool): Whether to show the full synopsis or a shortened version.
    """
    if anime_info.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
    elif anime_info.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
    else:
        raise NotImplementedError(f"Unsupported source provider: {anime_info.source_provider}")

    title = anime_info.native_title + (f" / {anime_info.english_title}" if anime_info.english_title
                                       and anime_info.english_title != anime_info.native_title else "")
    if anime_info.year:
        if anime_info.season:
            airing_info = f"**{anime_info.season} {anime_info.year}**"
        else:
            airing_info = f"**{anime_info.year}**"
    else:
        airing_info = "**TBA**"
    airing_info += f" • **{anime_info.status}**"
    if anime_info.media_type == AnimeMediaType.MOVIE:
        airing_info += f" • **{anime_info.duration_in_minutes} minutes**\n"
    else:
        airing_info += f" • ** {anime_info.episode_count or "Unknown"} episodes**\n"
    embed = discord.Embed(
        title=title,
        colour=embed_color,
        url=anime_info.web_url,
        description=f"{airing_info}\n"
                    f"**Studios**: {', '.join(anime_info.studios[:3]) if anime_info.studios else '?'}\n"
                    f"**Genres**: {', '.join(anime_info.genres) if anime_info.genres else '?'}\n"
                    + (f"**Tags**: {', '.join(anime_info.themes[:5])}\n" if anime_info.themes else "") + "\n‎"
    )

    embed.set_thumbnail(url=anime_info.poster_url or logo)
    embed.set_image(url=anime_info.banner_url)
    embed.set_author(name=f"Rated {anime_info.score or '?'} "
                          f"by {get_human_readable_number(anime_info.score_count) or '?'} users "
                          f"| Ranked #{anime_info.rank or '?'}",
                     url=anime_info.web_url,
                     icon_url=logo)

    embed.set_footer(text=f"Type: {anime_info.media_type} "
                          f"| Source: {anime_info.media_source} "
                          f"| Aired: {anime_info.start_date or '?'} -> {anime_info.end_date or '?'}")

    if len(anime_info.synopsis) > 600 and not synopsis_expanded:
        synopsis = shorten_text(anime_info.synopsis, max_length=600)
    else:
        synopsis = shorten_text(anime_info.synopsis, max_length=1000)
    embed.add_field(name="Synopsis", value=(synopsis or "No synopsis available.") + "\n‎", inline=False)

    provider_config_upsell = "-# ‎"
    if anime_info.source_provider == AnimangaProvider.MAL:
        provider_config_upsell = ("-# ‎\n-# Want to get anime info from AniList instead?"
                                  " Use `/user-settings` to set your preferred provider.")

    if anime_user_entry:
        if anime_user_entry.status == UserAnimeStatus.NOT_ON_LIST:
            stats = "Not on list.\n‎"
        else:
            if anime_user_entry.started_at and isinstance(anime_user_entry.started_at, datetime):
                started_at = anime_user_entry.started_at.strftime("%b %d, %Y")
            else:
                started_at = anime_user_entry.started_at or "?"
            if anime_user_entry.finished_at and isinstance(anime_user_entry.finished_at, datetime):
                finished_at = anime_user_entry.finished_at.strftime("%b %d, %Y")
            else:
                finished_at = anime_user_entry.finished_at or "?"
            stats = (f"Status: {anime_user_entry.status}\n"
                     f"Score: {anime_user_entry.user_score or '?'}\n"
                     f"Progress: {anime_user_entry.watched_episodes_count or '?'} / {anime_info.episode_count or '?'}\n"
                     f"Started/finished: {started_at} - {finished_at}\n"
                     + (f"Rewatch count: {anime_user_entry.rewatch_count or 0}\n"
                        if anime_user_entry.rewatch_count else "")) + "\n‎"
        embed.add_field(name=f"Stats for {anime_user_entry.username}",
                        value=stats,
                        inline=False)
    else:
        embed.add_field(name="Link your MAL or AniList account to get your stats here",
                        value=f"Use `/link-myanimelist` or `link-anilist`\n{provider_config_upsell}", inline=False)

    return embed


def get_manga_info_embed(manga_info: MangaInfo,
                         manga_user_entry: UserMangaListEntry | None,
                         synopsis_expanded: bool = False) -> discord.Embed:
    """
    Create a Discord embed for manga information.
    Args:
        manga_info (MangaInfo): The DTO containing manga information.
        manga_user_entry (UserMangaListEntry | None): The user's list entry for this manga, if available.
        synopsis_expanded (bool): Whether to show the full synopsis or a shortened version.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if manga_info.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
    elif manga_info.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
    else:
        raise NotImplementedError(f"Unsupported source provider: {manga_info.source_provider}")

    title = manga_info.native_title + (f" / {manga_info.english_title}" if manga_info.english_title
                                       and manga_info.english_title != manga_info.native_title else "")
    if manga_info.year:
        publishing_info = f"**{manga_info.year}**"
    else:
        publishing_info = "**TBA**"
    publishing_info += f" • **{manga_info.status}** • ** {manga_info.chapter_count or "Unknown"} chapters**\n"
    embed = discord.Embed(
        title=title,
        colour=embed_color,
        url=manga_info.web_url,
        description=f"{publishing_info}\n"
                    f"**Authors**: {', '.join(manga_info.authors) if manga_info.authors else '?'}\n"
                    f"**Genres**: {', '.join(manga_info.genres) if manga_info.genres else '?'}\n"
                    + (f"**Tags**: {', '.join(manga_info.themes[:5])}\n" if manga_info.themes else "") + "\n‎"
    )

    embed.set_thumbnail(url=manga_info.poster_url or logo)
    embed.set_image(url=manga_info.banner_url)
    embed.set_author(name=f"Rated {manga_info.score or '?'} "
                          f"by{get_human_readable_number(manga_info.score_count) or '?'} users "
                          f"| Ranked #{manga_info.rank or '?'}",
                     url=manga_info.web_url,
                     icon_url=logo)

    embed.set_footer(text=f"Type: {manga_info.media_type} "
                          f"| Published: {manga_info.start_date or '?'} - {manga_info.end_date or '?'}")

    if len(manga_info.synopsis) > 600 and not synopsis_expanded:
        synopsis = shorten_text(manga_info.synopsis, max_length=600)
    else:
        synopsis = shorten_text(manga_info.synopsis, max_length=1000)
    embed.add_field(name="Synopsis", value=(synopsis or "No synopsis available.") + "\n‎", inline=False)

    provider_config_upsell = "-# ‎"
    if manga_info.source_provider == AnimangaProvider.MAL:
        provider_config_upsell = ("-# ‎\n-# Want to get manga info from AniList instead?"
                                  " Use `/user-settings` to set your preferred provider.")

    if manga_user_entry:
        if manga_user_entry.status == UserAnimeStatus.NOT_ON_LIST:
            stats = "Not on list.\n‎"
        else:
            if manga_user_entry.started_at and isinstance(manga_user_entry.started_at, datetime):
                started_at = manga_user_entry.started_at.strftime("%b %d, %Y")
            else:
                started_at = manga_user_entry.started_at or "?"
            if manga_user_entry.finished_at and isinstance(manga_user_entry.finished_at, datetime):
                finished_at = manga_user_entry.finished_at.strftime("%b %d, %Y")
            else:
                finished_at = manga_user_entry.finished_at or "?"
            stats = (
                f"Status: {manga_user_entry.status}\n"
                f"Score: {manga_user_entry.user_score or '?'}\n"
                f"Progress: {manga_user_entry.read_chapters_count or '?'} / {manga_info.chapter_count or '?'}\n"
                f"Started/finished: {started_at} - {finished_at}\n"
            ) + "\n‎"
        embed.add_field(name=f"Stats for {manga_user_entry.username}",
                        value=stats,
                        inline=False)
    else:
        embed.add_field(name="Link your MAL or AniList account to get your stats here",
                        value=f"Use `/link-myanimelist` or `link-anilist`\n{provider_config_upsell}", inline=False)

    return embed


def get_user_animanga_profile_embed(user_profile: UserAnimangaProfile, navigation_locked: bool = True) -> discord.Embed:
    """
    Create a Discord embed for a user's MAL/AniList profile.
    Args:
        user_profile (UserAnimangaProfile): The user's profile information.
        navigation_locked (bool): Whether the navigation is locked for everyone or not.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if user_profile.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
        author = "MyAnimeList profile"
    elif user_profile.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
        author = "AniList profile"
    else:
        raise NotImplementedError(f"Unsupported source provider: {user_profile.source_provider}")

    embed = discord.Embed(
        title=user_profile.username,
        colour=embed_color,
        url=user_profile.web_url,
    )
    embed.set_thumbnail(url=user_profile.avatar_image_url or logo)
    embed.set_image(url=user_profile.banner_image_url or None)
    embed.set_author(name=author, icon_url=logo)

    joined_at = DiscordTimestamp.LONG_DATE.format(timestamp=int(user_profile.created_at.timestamp())) \
        if isinstance(user_profile.created_at, datetime) else user_profile.created_at or None
    last_online = DiscordTimestamp.RELATIVE_TIME.format(timestamp=int(user_profile.updated_at.timestamp())) \
        if isinstance(user_profile.updated_at, datetime) else user_profile.updated_at or None
    user_info = ""
    if joined_at:
        user_info += f"**Joined**: {joined_at}\n"
    if last_online:
        user_info += f"**Last online**: {last_online}\n"
    if user_profile.location:
        user_info += f"**Location**: {user_profile.location}\n"
    if user_profile.birthday:
        user_info += f"**Birthday**: {user_profile.birthday}\n"
    if user_profile.gender:
        user_info += f"**Gender**: {user_profile.gender}\n"
    embed.add_field(name="User Info", value=user_info or "-", inline=False)

    anime_stats = user_profile.anime_stats
    embed.add_field(name="Anime stats",
                    value=f"**Days**: {anime_stats.days_watched}\n"
                          f"**Avg Score**: {anime_stats.mean_score}\n"
                          f"**Watching:** {anime_stats.watching_count}\n"
                          f"**Completed:** {anime_stats.completed_count}\n"
                          f"**Anime:** {anime_stats.total_entries_count}\n"
                          f"**Rewatched:** {anime_stats.rewatched_count}\n"
                          + (f"**Episodes:** {anime_stats.total_episodes}\n" if anime_stats.total_episodes else "") +
                          f"‎",
                    inline=True)

    manga_stats = user_profile.manga_stats
    embed.add_field(name="Manga stats",
                    value=f"**Days**: {manga_stats.days_read}\n"
                          f"**Avg Score**: {manga_stats.mean_score}\n"
                          f"**Reading:** {manga_stats.reading_count}\n"
                          f"**Completed:** {manga_stats.completed_count}\n"
                          f"**Manga:** {manga_stats.total_entries_count}\n"
                          f"**Reread:** {manga_stats.reread_count}\n"
                          f"**Chapters:** {manga_stats.total_chapters}\n"
                          f"‎",
                    inline=True)

    navigation_lock_info = "○ 🔓 Unlock navigating for everyone" if navigation_locked else "○ 🔓 Navigation unlocked"
    embed.add_field(name="Navigate",
                    value=f"○ 📺 Anime List\n"
                          f"○ 📚 Manga List\n"
                          f"○ ⭐ Favorites\n"
                          + (f"○ 🧮 Analyses\n" if user_profile.source_provider == AnimangaProvider.ANILIST else '') +
                          f"‎\n"
                          f"{navigation_lock_info}\n"
                          f"○ 🗑 Close embed\n‎",
                    inline=False)

    return embed


# noinspection DuplicatedCode
def get_user_anime_list_embed(user_profile: UserAnimangaProfile,
                              page: int,
                              page_count: int,
                              page_size: int) -> discord.Embed:
    """
    Create a Discord embed for a user's anime list.
    Args:
        user_profile (UserAnimangaProfile): The user's profile information.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of entries per page.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if user_profile.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
        author = "MyAnimeList profile"
    elif user_profile.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
        author = "AniList profile"
    else:
        raise NotImplementedError(f"Unsupported source provider: {user_profile.source_provider}")

    embed = discord.Embed(
        title=f"{user_profile.username}'s anime list",
        colour=embed_color,
        url=user_profile.anime_list.web_url if user_profile.anime_list else user_profile.web_url,
    )
    embed.set_thumbnail(url=user_profile.avatar_image_url or logo)
    embed.set_author(name=author,
                     icon_url=logo)

    if not user_profile.anime_list or not user_profile.anime_list.entries:
        if user_profile.anime_list_loading_status != AnimangaListLoadingStatus.LOADED:
            embed.description = "‎\n❌ There was an issue while loading this list. We're working on fixing it!\n‎"
        else:
            embed.description = "‎\nThis list is empty or the user has set it to private!\n‎"
        return embed

    list_offset = (page - 1) * page_size

    for i, entry in enumerate(user_profile.anime_list.entries[list_offset:list_offset + page_size], list_offset + 1):
        info = ""
        if entry.status == UserAnimeStatus.WATCHING:
            info += f"**Status**: {entry.status} ({entry.watched_episodes_count or '?'} episodes)"
        else:
            info += f"**Status**: {entry.status}"
        info += f" | **Score**: {entry.user_score or '?'}\n"
        embed.add_field(
            name="‎",
            value=f"{emojis.numbers[i]} ‎ [{entry.title}]({entry.anime_web_url})\n{info}",
            inline=False
        )
    embed.fields[-1].value += "\n‎"  # add some padding

    embed.set_footer(text=f"Page {page}/{page_count} | Total of {len(user_profile.anime_list.entries)} anime entries "
                          f"| Scoring system: {user_profile.anime_list.scoring_system}")

    return embed


# noinspection DuplicatedCode
def get_user_manga_list_embed(user_profile: UserAnimangaProfile,
                              page: int,
                              page_count: int,
                              page_size: int) -> discord.Embed:
    """
    Create a Discord embed for a user's manga list.
    Args:
        user_profile (UserAnimangaProfile): The user's profile information.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of entries per page.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if user_profile.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
        author = "MyAnimeList profile"
    elif user_profile.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
        author = "AniList profile"
    else:
        raise NotImplementedError(f"Unsupported source provider: {user_profile.source_provider}")

    embed = discord.Embed(
        title=f"{user_profile.username}'s manga list",
        colour=embed_color,
        url=user_profile.manga_list.web_url if user_profile.manga_list else user_profile.web_url,
    )
    embed.set_thumbnail(url=user_profile.avatar_image_url or logo)
    embed.set_author(name=author,
                     icon_url=logo)

    if not user_profile.manga_list or not user_profile.manga_list.entries:
        if user_profile.manga_list_loading_status == AnimangaListLoadingStatus.FAILED:
            embed.description = "‎\n❌ There was an issue while loading this list. We're working on fixing it!\n‎"
        else:
            embed.description = "‎\nThis list is empty or the user has set it to private!\n‎"
        return embed

    list_offset = (page - 1) * page_size

    for i, entry in enumerate(user_profile.manga_list.entries[list_offset:list_offset + page_size], list_offset + 1):
        info = ""
        if entry.status == UserMangaStatus.READING:
            info += f"**Status**: {entry.status} ({entry.read_chapters_count or '?'} chapters)"
        else:
            info += f"**Status**: {entry.status}"
        info += f" | **Score**: {entry.user_score or '?'}\n"
        embed.add_field(
            name="‎",
            value=f"{emojis.numbers[i]} ‎ [{entry.title}]({entry.manga_web_url})\n{info}",
            inline=False
        )
    embed.fields[-1].value += "\n‎"  # add some padding

    embed.set_footer(text=f"Page {page}/{page_count} | Total of {len(user_profile.manga_list.entries)} manga entries "
                          f"| Scoring system: {user_profile.manga_list.scoring_system}")

    return embed


def get_user_animanga_favorites_embed(user_profile: UserAnimangaProfile) -> discord.Embed:
    """
    Create a Discord embed for a user's favorites on MAL/AniList.
    Args:
        user_profile (UserAnimangaProfile): The user's profile information.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if user_profile.source_provider == AnimangaProvider.MAL:
        embed_color = Colour.EXT_MAL
        logo = Links.Media.MAL_LOGO
        author = "MyAnimeList profile"
    elif user_profile.source_provider == AnimangaProvider.ANILIST:
        embed_color = Colour.EXT_ANILIST
        logo = Links.Media.ANILIST_LOGO
        author = "AniList profile"
    else:
        raise NotImplementedError(f"Unsupported source provider: {user_profile.source_provider}")

    embed = discord.Embed(
        title=f"{user_profile.username}'s favorites",
        colour=embed_color,
        url=user_profile.web_url,
    )
    embed.set_thumbnail(url=user_profile.avatar_image_url or logo)
    embed.set_author(name=author, icon_url=logo)

    for favorites, category in [
        (user_profile.favorites.anime, 'Anime'),
        (user_profile.favorites.manga, 'Manga'),
        (user_profile.favorites.characters, 'Characters'),
        (user_profile.favorites.people, 'Staff'),
        (user_profile.favorites.studios, 'Studios'),
    ]:
        list_str = ""
        for i, favorite in enumerate(favorites, 1):
            entry_str = f"{emojis.numbers[i]} ‎ [{favorite.title}]({favorite.item_url})"
            if len(list_str) + len(entry_str) > 1024:
                list_str += "\n..."
                break
            list_str += f"{entry_str}\n"
        list_str = list_str or f"No {category.lower()} favorites."
        embed.add_field(name=f"{category}", value=list_str, inline=True)

    return embed


def get_user_animanga_analyses_embed(user_profile: UserAnimangaProfile) -> discord.Embed:
    """
    Create a Discord embed for a user's analyses on AniList.
    Args:
        user_profile (UserAnimangaProfile): The user's profile information.
    Returns:
        discord.Embed: The constructed Discord embed.
    """
    if user_profile.source_provider != AnimangaProvider.ANILIST:
        raise NotImplementedError("Analyses are only available for AniList profiles.")

    embed = discord.Embed(
        title=f"{user_profile.username}'s analyses",
        colour=Colour.EXT_ANILIST,
        url=user_profile.web_url,
    )
    embed.set_thumbnail(url=user_profile.avatar_image_url or Links.Media.ANILIST_LOGO)
    embed.set_author(name="AniList profile", icon_url=Links.Media.ANILIST_LOGO)

    anime_analysis = user_profile.anime_analysis
    anime_analysis_part_1 = "• " + "\n• ".join(
        analysis_point for analysis_point in
        [anime_analysis.amount_analysis, anime_analysis.score_analysis, anime_analysis.planning_analysis,
         anime_analysis.current_analysis, anime_analysis.dropped_analysis, anime_analysis.paused_analysis]
        if analysis_point
    )
    anime_analysis_part_2 = "• " + "\n• ".join(
        analysis_point for analysis_point in
        [anime_analysis.length_analysis, anime_analysis.release_years_analysis, anime_analysis.genres_analysis,
         anime_analysis.tags_analysis, anime_analysis.voice_actors_analysis, anime_analysis.studios_analysis]
        if analysis_point
    )

    manga_analysis = user_profile.manga_analysis
    manga_analysis_part_1 = "• " + "\n• ".join(
        analysis_point for analysis_point in
        [manga_analysis.amount_analysis, manga_analysis.score_analysis, manga_analysis.planning_analysis,
         manga_analysis.current_analysis, manga_analysis.paused_analysis]
        if analysis_point
    )
    manga_analysis_part_2 = "• " + "\n• ".join(
        analysis_point for analysis_point in
        [manga_analysis.genres_analysis, manga_analysis.tags_analysis, manga_analysis.staff_analysis]
        if analysis_point
    )

    embed.add_field(name="Anime analysis", value=anime_analysis_part_1.strip(), inline=False)
    if anime_analysis_part_2.strip():
        embed.add_field(name="‎", value=anime_analysis_part_2.strip() + "\n‎", inline=False)
    else:
        embed.fields[-1].value += "\n‎"

    embed.add_field(name="Manga analysis", value=manga_analysis_part_1.strip(), inline=False)
    if manga_analysis_part_2.strip():
        embed.add_field(name="‎", value="‎" + manga_analysis_part_2.strip() + "‎", inline=False)
    else:
        embed.fields[-1].value += "‎"

    return embed
