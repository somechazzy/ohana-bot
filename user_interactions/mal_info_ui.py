from globals_.clients import discord_client
from embed_factory import make_mal_anime_search_results_embed, make_mal_anime_info_embed, \
    make_mal_manga_search_results_embed, make_mal_manga_info_embed
import asyncio
import traceback
from internal.bot_logging import log
from actions import edit_message
from globals_.constants import BotLogType
from helpers import get_mal_username, get_numbered_list_views, get_mal_info_views, get_al_username
from web_parsers.anilist.anilist_api_handler import get_al_user_stats_for_show, get_al_user_stats_for_manga
from web_parsers.mal.mal_info_parser import get_mal_anime_info, get_mal_manga_info
from web_parsers.mal.mal_list_handler import get_mal_user_stats_for_anime, get_mal_user_stats_for_manga


async def mal_anime_search_navigation(received_message, sent_message, discord_id, not_author,
                                      query, results, thumbnail, prefix):
    go_back_to_search = await _mal_anime_info(0, received_message, results, sent_message, discord_id,
                                              not_author, prefix, allow_going_back_to_search=True)
    if not go_back_to_search:
        return
    num_of_results = 5
    embed = make_mal_anime_search_results_embed(query, results, received_message.author, thumbnail, num_of_results)
    view = get_numbered_list_views([result['title'] for result in results[:num_of_results]], add_close_button=True)
    sent_message = sent_message.channel.get_partial_message(sent_message.id)
    edited_message = await edit_message(sent_message, content=None, embed=embed, view=view,
                                        reason="Grabbed MAL search results")
    if edited_message is None:
        return

    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != received_message.author.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        await edit_message(sent_message, None, embed=embed, view=None)
        return

    await interaction.response.defer()
    if interaction.data.custom_id == 'close':
        await interaction.edit_original_message(content="Anime search closed.", embed=None, view=None)
        return

    if interaction.data.values and int(interaction.data.values[0]) in range(len(results)):
        index_chosen = int(interaction.data.values[0])
    else:
        return
    await _mal_anime_info(index_chosen, received_message, results, sent_message, discord_id,
                          not_author, prefix, interaction=interaction)


async def _mal_anime_info(index_chosen, received_message, results, sent_message, discord_id, not_author, prefix,
                          allow_going_back_to_search=False, interaction=None):
    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != received_message.author.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    anime_id = results[index_chosen]["id"]
    anime_title = results[index_chosen]["title"]
    if not allow_going_back_to_search:
        await interaction.edit_original_message(content=f"Loading \"{anime_title}\", please wait...",
                                                embed=None, view=None)

    mal_username, _ = get_mal_username(discord_id)
    al_username, _ = get_al_username(discord_id)
    list_username = mal_username
    user_stats = None
    if mal_username:
        user_stats = await get_mal_user_stats_for_anime(mal_username, anime_id)
    if (not mal_username or not user_stats) and al_username:
        try:
            user_stats = await get_al_user_stats_for_show(al_username, int(anime_id))
        except Exception as e:
            await log(f"Error while getting stats from anilist ({e}): {traceback.format_exc()}",
                      level=BotLogType.BOT_ERROR)
        if user_stats:
            list_username = al_username

    mal_anime_info = await get_mal_anime_info(anime_id)
    embed, shortened = make_mal_anime_info_embed(mal_anime_info, list_username, user_stats,
                                                 not_author, prefix)
    view = get_mal_info_views(add_expand_button=shortened, add_back_button=allow_going_back_to_search)
    if allow_going_back_to_search:
        await edit_message(sent_message, content="", embed=embed, view=view)
    else:
        await interaction.edit_original_message(content=None, embed=embed, view=view)

    async def expand_synopsis(interaction_):
        embed_, _ = make_mal_anime_info_embed(mal_anime_info, list_username,
                                              user_stats,
                                              not_author, prefix,
                                              synopsis_expand=True)
        view_ = get_mal_info_views(add_expand_button=False)
        await interaction_.edit_original_message(content=None, embed=embed_, view=view_)
        try:
            interaction_ = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                         check=check_interactions,
                                                         timeout=300)
        except asyncio.TimeoutError:
            sent_message_ = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message_, None, embed=embed, view=None)
            return

        await interaction_.response.defer()
        if interaction_.data.custom_id == 'close':
            await interaction_.edit_original_message(content="Anime info closed.", embed=None, view=None)
            return

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        await edit_message(sent_message, None, embed=embed, view=None)
        return False

    await interaction.response.defer()
    if interaction.data.custom_id == 'close':
        await interaction.edit_original_message(content="Anime info closed.", embed=None, view=None)
        return False
    elif interaction.data.custom_id == 'expand':
        await expand_synopsis(interaction)
        return False
    elif interaction.data.custom_id == 'back':
        return True


async def mal_manga_search_navigation(received_message, sent_message, discord_id, not_author,
                                      query, results, thumbnail, prefix):
    go_back_to_search = await _mal_manga_info(0, received_message, results, sent_message, discord_id,
                                              not_author, prefix, allow_going_back_to_search=True)
    if not go_back_to_search:
        return
    num_of_results = 5
    embed = make_mal_manga_search_results_embed(query, results, received_message.author, thumbnail, num_of_results)
    view = get_numbered_list_views([result['title'] for result in results[:num_of_results]], add_close_button=True)
    edited_message = await edit_message(sent_message, content=None, embed=embed, view=view,
                                        reason="Grabbed MAL search results")
    if edited_message is None:
        return

    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != received_message.author.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        await edit_message(sent_message, None, embed=embed, view=None)
        return

    await interaction.response.defer()
    if interaction.data.custom_id == 'close':
        await interaction.edit_original_message(content="Manga search closed.", embed=None, view=None)
        return

    if interaction.data.values and int(interaction.data.values[0]) in range(len(results)):
        index_chosen = int(interaction.data.values[0])
    else:
        return
    await _mal_manga_info(index_chosen, received_message, results, sent_message, discord_id,
                          not_author, prefix, interaction=interaction)


async def _mal_manga_info(index_chosen, received_message, results, sent_message, discord_id, not_author, prefix,
                          allow_going_back_to_search=False, interaction=None):
    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != received_message.author.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    manga_id = results[index_chosen]["id"]
    manga_title = results[index_chosen]["title"]
    if not allow_going_back_to_search:
        await interaction.edit_original_message(content=f"Loading \"{manga_title}\", please wait...",
                                                embed=None, view=None)

    mal_username, _ = get_mal_username(discord_id)
    al_username, _ = get_al_username(discord_id)
    list_username = mal_username
    user_stats = None
    if mal_username:
        user_stats = await get_mal_user_stats_for_manga(mal_username, manga_id)
    elif (not mal_username or not user_stats) and al_username:
        user_stats = await get_al_user_stats_for_manga(al_username, int(manga_id))
        if user_stats:
            list_username = al_username

    mal_manga_info = await get_mal_manga_info(manga_id)
    embed, shortened = make_mal_manga_info_embed(mal_manga_info, list_username, user_stats,
                                                 not_author, prefix)
    view = get_mal_info_views(add_expand_button=shortened, add_back_button=allow_going_back_to_search)
    if allow_going_back_to_search:
        await edit_message(sent_message, content="", embed=embed, view=view)
    else:
        await interaction.edit_original_message(content=None, embed=embed, view=view)

    async def expand_synopsis(interaction_):
        embed_, _ = make_mal_manga_info_embed(mal_manga_info, list_username,
                                              user_stats,
                                              not_author, prefix,
                                              synopsis_expand=True)
        view_ = get_mal_info_views(add_expand_button=False)
        await interaction_.edit_original_message(content=None, embed=embed_, view=view_)
        try:
            interaction_ = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                         check=check_interactions,
                                                         timeout=300)
        except asyncio.TimeoutError:
            sent_message_ = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message_, None, embed=embed, view=None)
            return

        await interaction_.response.defer()
        if interaction_.data.custom_id == 'close':
            await interaction_.edit_original_message(content="Manga info closed.", embed=None, view=None)
            return

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        await edit_message(sent_message, None, embed=embed, view=None)
        return False

    await interaction.response.defer()
    if interaction.data.custom_id == 'close':
        await interaction.edit_original_message(content="Manga info closed.", embed=None, view=None)
        return False
    elif interaction.data.custom_id == 'expand':
        await expand_synopsis(interaction)
        return False
    elif interaction.data.custom_id == 'back':
        return True
