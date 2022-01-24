import asyncio
from math import ceil
from globals_.clients import discord_client
from globals_ import constants
from actions import edit_message
from helpers import get_mal_al_profile_views, get_pagination_views, get_back_view, get_al_profile_views
from embed_factory import make_mal_profile_embed, make_mal_profile_anime_list_embed, make_mal_profile_manga_list_embed,\
    make_mal_profile_fav_list_embed, make_anilist_profile_anime_list_embed, make_anilist_profile_embed, \
    make_anilist_profile_manga_list_embed, make_anilist_profile_fav_list_embed, make_anilist_profile_analysis_embed


async def mal_profile_navigation(received_message, sent_message, embed_profile, profile_info, anime_list, manga_list):
    reacting_unlocked = False
    while True:
        view = get_mal_al_profile_views(add_unlock=not reacting_unlocked)
        edited_message = await edit_message(sent_message, None, embed=embed_profile, view=view)
        if edited_message is None:
            return

        def check_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            if interaction_.data.custom_id in ['close', 'unlock']\
                    and interaction_.user.id != received_message.author.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed_profile, view=None)
            return

        await interaction.response.defer()
        if interaction.data.custom_id == 'close':
            await interaction.edit_original_message(content="MAL profile closed.", embed=None, view=None)
            return

        elif interaction.data.custom_id == 'unlock':
            reacting_unlocked = True
            embed_profile = make_mal_profile_embed(profile_info, reacting_unlocked=reacting_unlocked)
            await interaction.edit_original_message(content=None, embed=embed_profile, view=view)

        elif interaction.data.custom_id == 'anime_list':
            i = 1
            total_pages = ceil(len(anime_list)/10)
            while True:
                anime_list_embed = make_mal_profile_anime_list_embed(profile_info["username"],
                                                                     profile_info["profile_avatar"],
                                                                     anime_list, i, total_pages)
                view = get_pagination_views(i, total_pages, add_close_button=False, add_back_button=True)
                await interaction.edit_original_message(content=None, embed=anime_list_embed, view=view)

                def check_interactions(interaction_):
                    if interaction_.message.id != sent_message.id:
                        return False
                    if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                        asyncio.get_event_loop().create_task(interaction_.response.defer())
                        return False
                    return True

                try:
                    interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                                check=check_interactions,
                                                                timeout=300)
                except asyncio.TimeoutError:
                    sent_message = sent_message.channel.get_partial_message(sent_message.id)
                    await edit_message(sent_message, None, embed=anime_list_embed, view=None)
                    return

                await interaction.response.defer()
                if interaction.data.custom_id == 'next':
                    if i < total_pages:
                        i += 1
                elif interaction.data.custom_id == 'previous':
                    if i > 1:
                        i -= 1
                elif interaction.data.custom_id == 'back':
                    break
        elif interaction.data.custom_id == 'manga_list':
            i = 1
            total_pages = ceil(len(anime_list)/10)
            while True:
                manga_list_embed = make_mal_profile_manga_list_embed(profile_info["username"],
                                                                     profile_info["profile_avatar"],
                                                                     manga_list, i, total_pages)
                view = get_pagination_views(i, total_pages, add_close_button=False, add_back_button=True)
                await interaction.edit_original_message(content=None, embed=manga_list_embed, view=view)

                def check_interactions(interaction_):
                    if interaction_.message.id != sent_message.id:
                        return False
                    if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                        asyncio.get_event_loop().create_task(interaction_.response.defer())
                        return False
                    return True

                try:
                    interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                                check=check_interactions,
                                                                timeout=300)
                except asyncio.TimeoutError:
                    sent_message = sent_message.channel.get_partial_message(sent_message.id)
                    await edit_message(sent_message, None, embed=manga_list_embed, view=None)
                    return

                await interaction.response.defer()
                if interaction.data.custom_id == 'next':
                    if i < total_pages:
                        i += 1
                elif interaction.data.custom_id == 'previous':
                    if i > 1:
                        i -= 1
                elif interaction.data.custom_id == 'back':
                    break
        elif interaction.data.custom_id == 'favorites':
            fav_list_embed = make_mal_profile_fav_list_embed(profile_info)
            view = get_back_view()
            await interaction.edit_original_message(content=None, embed=fav_list_embed, view=view)

            def check_interactions(interaction_):
                if interaction_.message.id != sent_message.id:
                    return False
                if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                    asyncio.get_event_loop().create_task(interaction_.response.defer())
                    return False
                return True

            try:
                interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                            check=check_interactions,
                                                            timeout=300)
            except asyncio.TimeoutError:
                sent_message = sent_message.channel.get_partial_message(sent_message.id)
                await edit_message(sent_message, None, embed=fav_list_embed, view=None)
                return
            await interaction.response.defer()


async def anilist_profile_navigation(received_message, sent_message, embed_profile, profile_info,
                                        anime_list, manga_list, scoring_system):
    scoring_system = constants.ANILIST_SCORING_SYSTEM[scoring_system]\
        if scoring_system in constants.ANILIST_SCORING_SYSTEM else scoring_system
    reacting_unlocked = False
    while True:
        view = get_al_profile_views(add_unlock=not reacting_unlocked)
        edited_message = await edit_message(sent_message, None, embed=embed_profile, view=view)
        if edited_message is None:
            return

        if len(embed_profile.fields) == 0:
            return

        def check_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            if interaction_.data.custom_id in ['close', 'unlock']\
                    and interaction_.user.id != received_message.author.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed_profile, view=None)
            return

        await interaction.response.defer()
        if interaction.data.custom_id == 'close':
            await interaction.edit_original_message(content="Anilist profile closed.", embed=None, view=None)
            return

        if interaction.data.custom_id == 'analysis':
            embed_analysis = make_anilist_profile_analysis_embed(profile_info)
            view = get_back_view()
            await interaction.edit_original_message(content=None, embed=embed_analysis, view=view)

            def check_interactions(interaction_):
                if interaction_.message.id != sent_message.id:
                    return False
                if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                    asyncio.get_event_loop().create_task(interaction_.response.defer())
                    return False
                return True

            try:
                interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                            check=check_interactions,
                                                            timeout=300)
            except asyncio.TimeoutError:
                sent_message = sent_message.channel.get_partial_message(sent_message.id)
                await edit_message(sent_message, None, embed=embed_analysis, view=None)
                return
            await interaction.response.defer()

        elif interaction.data.custom_id == 'unlock':
            reacting_unlocked = True
            embed_profile = make_anilist_profile_embed(profile_info, reacting_unlocked=reacting_unlocked)
            await interaction.edit_original_message(content=None, embed=embed_profile, view=view)

        elif interaction.data.custom_id == 'anime_list':
            i = 1
            total_pages = ceil(len(anime_list) / 10)
            while True:
                anime_list_embed = make_anilist_profile_anime_list_embed(profile_info.name,
                                                                         profile_info.avatar,
                                                                         anime_list, i, total_pages,
                                                                         scoring_system)
                view = get_pagination_views(i, total_pages, add_close_button=False, add_back_button=True)
                await interaction.edit_original_message(content=None, embed=anime_list_embed, view=view)

                def check_interactions(interaction_):
                    if interaction_.message.id != sent_message.id:
                        return False
                    if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                        asyncio.get_event_loop().create_task(interaction_.response.defer())
                        return False
                    return True

                try:
                    interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                                check=check_interactions,
                                                                timeout=300)
                except asyncio.TimeoutError:
                    sent_message = sent_message.channel.get_partial_message(sent_message.id)
                    await edit_message(sent_message, None, embed=anime_list_embed, view=None)
                    return

                await interaction.response.defer()
                if interaction.data.custom_id == 'next':
                    if i < total_pages:
                        i += 1
                elif interaction.data.custom_id == 'previous':
                    if i > 1:
                        i -= 1
                elif interaction.data.custom_id == 'back':
                    break
        elif interaction.data.custom_id == 'manga_list':
            i = 1
            total_pages = ceil(len(manga_list)/10)
            while True:
                manga_list_embed = make_anilist_profile_manga_list_embed(profile_info.name,
                                                                         profile_info.avatar,
                                                                         manga_list, i, total_pages,
                                                                         scoring_system)
                view = get_pagination_views(i, total_pages, add_close_button=False, add_back_button=True)
                await interaction.edit_original_message(content=None, embed=manga_list_embed, view=view)

                def check_interactions(interaction_):
                    if interaction_.message.id != sent_message.id:
                        return False
                    if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                        asyncio.get_event_loop().create_task(interaction_.response.defer())
                        return False
                    return True

                try:
                    interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                                check=check_interactions,
                                                                timeout=300)
                except asyncio.TimeoutError:
                    sent_message = sent_message.channel.get_partial_message(sent_message.id)
                    await edit_message(sent_message, None, embed=manga_list_embed, view=None)
                    return

                await interaction.response.defer()
                if interaction.data.custom_id == 'next':
                    if i < total_pages:
                        i += 1
                elif interaction.data.custom_id == 'previous':
                    if i > 1:
                        i -= 1
                elif interaction.data.custom_id == 'back':
                    break
        elif interaction.data.custom_id == 'favorites':
            fav_list_embed = make_anilist_profile_fav_list_embed(profile_info)
            view = get_back_view()
            await interaction.edit_original_message(content=None, embed=fav_list_embed, view=view)

            def check_interactions(interaction_):
                if interaction_.message.id != sent_message.id:
                    return False
                if not reacting_unlocked and interaction_.user.id != received_message.author.id:
                    asyncio.get_event_loop().create_task(interaction_.response.defer())
                    return False
                return True

            try:
                interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                            check=check_interactions,
                                                            timeout=300)
            except asyncio.TimeoutError:
                sent_message = sent_message.channel.get_partial_message(sent_message.id)
                await edit_message(sent_message, None, embed=fav_list_embed, view=None)
                return
            await interaction.response.defer()
