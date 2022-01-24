from math import ceil
import asyncio
from actions import edit_message, remove_reactions
from globals_.clients import discord_client
from globals_ import variables
from helpers import get_pagination_views, get_history_embed_views
from embed_factory import make_music_queue_embed, make_lyrics_embed, make_music_history_embed, make_now_playing_embed


async def handle_music_queue(sent_message, requested_by, page):
    music_service = variables.guild_music_services.get(sent_message.guild.id)
    if not music_service:
        return
    queue = music_service.queue
    embed = make_music_queue_embed(queue=queue, guild=requested_by.guild, page=page,
                                   currently_playing_index=music_service.currently_played_track_index)
    page_count = ceil(len(queue) / 10)
    if page > page_count:
        page = 1
    while True:
        page_count = ceil(len(queue) / 10)

        def check_queue_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if interaction_.data.custom_id == 'close' and interaction_.user.id != requested_by.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_queue_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed, view=None)
            return

        if interaction.data.custom_id == 'close':
            await interaction.response.defer()
            await interaction.edit_original_message(content="Queue closed.", embed=None, view=None)
            return
        elif interaction.data.custom_id == 'next':
            if page < page_count:
                page += 1
        elif interaction.data.custom_id == 'previous':
            if page > 1:
                page -= 1

        embed = make_music_queue_embed(queue=queue, guild=requested_by.guild, page=page,
                                       currently_playing_index=music_service.currently_played_track_index)
        view = get_pagination_views(page, page_count)
        await interaction.response.defer()
        await interaction.edit_original_message(content=None, embed=embed, view=view)


async def handle_lyrics(sent_message, lyrics_pages, requested_by, full_title, thumbnail, url):
    embed = make_lyrics_embed(lyrics_pages=lyrics_pages, requested_by=requested_by, full_title=full_title,
                              thumbnail=thumbnail, url=url, page_index=0)
    page_count = len(lyrics_pages)
    page_index = 0
    while True:
        def check_lyrics_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if interaction_.data.custom_id == 'close' and interaction_.user.id != requested_by.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_lyrics_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed, view=None)
            return

        if interaction.data.custom_id == 'close':
            await interaction.response.defer()
            await interaction.edit_original_message(content="Lyrics closed.", embed=None, view=None)
            return
        elif interaction.data.custom_id == 'next':
            if page_index + 1 < page_count:
                page_index += 1
        elif interaction.data.custom_id == 'previous':
            if page_index > 0:
                page_index -= 1

        embed = make_lyrics_embed(lyrics_pages=lyrics_pages,
                                  requested_by=requested_by,
                                  full_title=full_title,
                                  thumbnail=thumbnail,
                                  url=url,
                                  page_index=page_index)

        view = get_pagination_views(page_index + 1, page_count)
        await interaction.response.defer()
        await interaction.edit_original_message(content=None, embed=embed, view=view)


async def handle_music_search(sent_message, requested_by):
    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != requested_by.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        await edit_message(sent_message, content="Results timed out.", embed=None, view=None)
        return

    await interaction.response.defer()
    if interaction.data.custom_id == 'close':
        return None
    await interaction.edit_original_message(content="Youtube search closed.", embed=None, view=None)
    index_chosen = int(interaction.data.values[0])
    return index_chosen


async def handle_music_player(sent_message, requested_by):
    while True:
        await asyncio.sleep(3)
        await sent_message.add_reaction('🗑')
        await sent_message.add_reaction('♻')

        def check_react(reaction, user):
            if user.id == sent_message.author.id:
                return False
            if reaction.message.id != sent_message.id:
                return False
            if str(reaction.emoji) == "🗑":
                return user.id == requested_by.id
            if str(reaction.emoji) == "♻":
                return True
            return False

        try:
            reaction_received, _ = await discord_client.wait_for("REACTION_ADD",
                                                                 check=check_react,
                                                                 timeout=600)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            if sent_message:
                await remove_reactions(sent_message)
            return

        emoji = str(reaction_received.emoji)
        sent_message = sent_message.channel.get_partial_message(sent_message.id)
        if not sent_message:
            return
        if emoji == "🗑":
            await edit_message(sent_message, "Player closed.", reason=f"Closed player embed")
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await remove_reactions(sent_message)
            return
        elif emoji == "♻":
            embed = make_now_playing_embed(sent_message.guild)
            await edit_message(sent_message, "", embed=embed, reason=f"Refreshed player embed")
            await remove_reactions(sent_message)


async def handle_history(sent_message, requested_by, original_embed, history, page):
    embed = original_embed
    page_count = ceil(len(history) / 10)
    while True:

        def check_history_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if interaction_.data.custom_id == 'close' and interaction_.user.id != requested_by.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_history_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed, view=None)
            return None, None

        await interaction.response.defer()
        if interaction.data.custom_id == 'close':
            await interaction.edit_original_message(content="History closed.", embed=None, view=None)
            return None, None
        elif interaction.data.custom_id == 'next':
            if page < page_count:
                page += 1
        elif interaction.data.custom_id == 'previous':
            if page > 1:
                page -= 1
        elif interaction.data.values and \
                int(interaction.data.values[0]) in range(len(history[(page - 1) * 10:(page - 1) * 10 + 10])):
            index_chosen = int(interaction.data.values[0])
            return index_chosen, page

        embed = make_music_history_embed(guild=sent_message.guild, history=history, page=page)
        view = get_history_embed_views(page=page, page_count=ceil(len(history) / 10),
                                       list_items=history[(page - 1) * 10:(page - 1) * 10 + 10])
        await interaction.edit_original_message(content=None, embed=embed, view=view)
