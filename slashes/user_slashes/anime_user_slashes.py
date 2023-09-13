import traceback

import discord
from utils.embed_factory import quick_embed
from globals_.constants import Colour, BotLogLevel
from utils.helpers import mal_profile_exists, link_mal_username, link_al_username, \
    anilist_profile_exists, get_mal_username, unlink_mal_username, get_anilist_username, unlink_anilist_username
from utils.helpers import get_user_stats_for_anime, get_user_stats_for_manga
from utils.exceptions import MyAnimeListNotFoundException, MyAnimeListInternalErrorException, \
    MyAnimeListParseException, MyAnimeListException, AnilistNotFoundException, AnilistInternalErrorException, \
    AnilistParseException, AnilistException
from utils.decorators import slash_command
from slashes.user_slashes.base_user_slashes import UserSlashes
from user_interactions.user_interactions.anilist_profile_interactions_handler import AnilistProfileInteractionsHandler
from user_interactions.user_interactions.anime_info_interactions_handler import AnimeInfoInteractionsHandler
from user_interactions.user_interactions.manga_info_interactions_handler import MangaInfoInteractionsHandler
from user_interactions.user_interactions.myanimelist_profile_interactions_handler import \
    MyAnimeListProfileInteractionsHandler


class AnimeUserSlashes(UserSlashes):

    @slash_command
    async def link_myanimelist(self, username: str):
        """
        /link-myanimelist
        Link your MyAnimeList username for stats & profile
        """

        if not await self.preprocess_and_validate():
            return

        if username == get_mal_username(user_id=self.user.id):
            await unlink_mal_username(user_id=self.user.id)
            await self.interaction.response.send_message(content=None,
                                                         embed=quick_embed(text=f"Unlinked your MyAnimeList account. "
                                                                                f"If this was a mistake you can relink"
                                                                                f" it by using the same command.",
                                                                           color=Colour.SUCCESS,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.send_message(content=None,
                                                     embed=quick_embed(text=f"Checking username {self.loading_emoji}",
                                                                       color=Colour.EXT_MAL,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        profile_response = await mal_profile_exists(username)
        if profile_response == 404:
            await self.interaction.edit_original_response(content=None,
                                                          embed=quick_embed(text=f"Username **{username}**"
                                                                                 f" doesn't exist",
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return
        elif profile_response != 200:
            await self.interaction.edit_original_response(content=None,
                                                          embed=quick_embed(text=f"Error while connecting to MAL, "
                                                                                 f"please try again later.",
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return

        _, feedback_text = await link_mal_username(user=self.user, username=username)

        await self.interaction.edit_original_response(content=None,
                                                      embed=quick_embed(text=feedback_text,
                                                                        color=Colour.EXT_MAL,
                                                                        bold=False))

    @slash_command
    async def link_anilist(self, username: str):
        """
        /link-anilist
        Link your AniList username for stats & profile
        """

        if not await self.preprocess_and_validate():
            return

        if username == get_anilist_username(user_id=self.user.id):
            await unlink_anilist_username(user_id=self.user.id)
            await self.interaction.response.send_message(content=None,
                                                         embed=quick_embed(text=f"Unlinked your Anilist account. "
                                                                                f"If this was a mistake you can relink"
                                                                                f" it by using the same command.",
                                                                           color=Colour.SUCCESS,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.send_message(content=None,
                                                     embed=quick_embed(text=f"Checking username {self.loading_emoji}",
                                                                       color=Colour.EXT_ANILIST,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        profile_response = await anilist_profile_exists(username)
        if profile_response == 404:
            await self.interaction.edit_original_response(content=None,
                                                          embed=quick_embed(text=f"Username **{username}** doesn't "
                                                                                 f"exist",
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return
        elif profile_response != 200:
            await self.interaction.edit_original_response(content=None,
                                                          embed=quick_embed(text=f"Error while connecting to Anilist, "
                                                                                 f"please try again later.",
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return

        _, feedback_text = await link_al_username(user=self.user, username=username)

        await self.interaction.edit_original_response(content=None,
                                                      embed=quick_embed(text=feedback_text,
                                                                        color=Colour.EXT_ANILIST,
                                                                        bold=False))

    @slash_command
    async def myanimelist(self, username: str = None, member: discord.Member = None, unlock: bool = True):
        """
        /myanimelist
        Get your MyAnimeList profile
        """
        if not await self.preprocess_and_validate():
            return

        if username:
            selected_username = username
            username_not_linked_text = f""
        elif member:
            selected_username = get_mal_username(member.id)
            username_not_linked_text = f"**{member.mention}** doesn't have their MAL linked yet. " \
                                       f"You can ask them to use `/link-myanimelist` to link it."
        else:
            selected_username = get_mal_username(self.user.id)
            username_not_linked_text = f"You don't have your MAL linked yet. " \
                                       f"Use `/link-myanimelist` to link it."

        if not selected_username:
            return await self.interaction.response.send_message(embed=quick_embed(text=username_not_linked_text,
                                                                                  color=Colour.ERROR,
                                                                                  bold=False))

        await self.interaction.response.send_message(embed=quick_embed(text=f"Loading MAL profile {self.loading_emoji}",
                                                                       color=Colour.EXT_MAL,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            mal_profile_info = await self.get_mal_profile_info(username=selected_username)
            anime_list, manga_list = await self.get_mal_lists(username=selected_username)
        except MyAnimeListNotFoundException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Username **{selected_username}**"
                                       f" doesn't exist",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except MyAnimeListInternalErrorException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"MAL seems to be done at the moment. Please try again later.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except MyAnimeListParseException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while parsing MAL profile. We've been informed of this and will fix it "
                                       f"as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except MyAnimeListException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while connecting to MAL. We've been informed of this and will fix it "
                                       f"as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except Exception as e:
            self.error_logger.log(f"Error while getting MAL profile. Username = `{selected_username}`."
                                  f" User ID: {self.user.id}.\n"
                                  f"{e}: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR)
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"There was an error while getting your profile. "
                                       f"We've been informed of this and will fix it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )

        mal_profile_handler = MyAnimeListProfileInteractionsHandler(source_interaction=self.interaction,
                                                                    profile_info=mal_profile_info,
                                                                    username=selected_username,
                                                                    anime_list=anime_list,
                                                                    manga_list=manga_list,
                                                                    unlocked=unlock)

        embed, views = mal_profile_handler.get_embed_and_views()

        await self.interaction.edit_original_response(embed=embed, view=views)

    @slash_command
    async def anilist(self, username: str = None, member: discord.Member = None, unlock: bool = True):
        """
        /anilist
        Get your Anilist profile
        """
        if not await self.preprocess_and_validate():
            return

        if username:
            selected_username = username
            username_not_linked_text = f""
        elif member:
            selected_username = get_anilist_username(member.id)
            username_not_linked_text = f"**{member.mention}** doesn't have their Anilist linked yet. " \
                                       f"You can ask them to use `/link-anilist` to link it."
        else:
            selected_username = get_anilist_username(self.user.id)
            username_not_linked_text = f"You don't have your Anilist linked yet. " \
                                       f"Use `/link-anilist` to link it."

        if not selected_username:
            return await self.interaction.response.send_message(embed=quick_embed(text=username_not_linked_text,
                                                                                  color=Colour.ERROR,
                                                                                  bold=False))

        await self.interaction.response.send_message(embed=quick_embed(text=f"Loading Anilist profile"
                                                                            f" {self.loading_emoji}",
                                                                       color=Colour.EXT_ANILIST,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            anilist_profile_info = await self.get_anilist_profile_info(username=selected_username)
            anime_list, manga_list, anime_scoring_system, manga_scoring_system =\
                await self.get_anilist_lists(username=selected_username)
        except AnilistNotFoundException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Username **{selected_username}**"
                                       f" doesn't exist",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except AnilistInternalErrorException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Anilist seems to be done at the moment. Please try again later.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except AnilistParseException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while parsing Anilist profile. We've been informed of this and will fix "
                                       f"it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except AnilistException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while connecting to Anilist. We've been informed of this and will fix "
                                       f"it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except Exception as e:
            self.error_logger.log(f"Error while getting AL profile. Username = `{selected_username}`."
                                  f" User ID: {self.user.id}.\n"
                                  f"{e}: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR)
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"There was an error while getting your profile. "
                                       f"We've been informed of this and will fix it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )

        anilist_profile_handler = AnilistProfileInteractionsHandler(source_interaction=self.interaction,
                                                                    profile_info=anilist_profile_info,
                                                                    username=selected_username,
                                                                    anime_list=anime_list,
                                                                    manga_list=manga_list,
                                                                    anime_scoring_system=anime_scoring_system,
                                                                    manga_scoring_system=manga_scoring_system,
                                                                    unlocked=unlock)

        embed, views = anilist_profile_handler.get_embed_and_views()

        await self.interaction.edit_original_response(embed=embed, view=views)

    @slash_command
    async def anime(self, anime: str):
        """
        /anime
        Gets anime info from MAL
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(content=None,
                                                     embed=quick_embed(text=f"Loading anime {self.loading_emoji}",
                                                                       color=Colour.EXT_MAL,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            anime_info, search_result = await self.get_anime_by_name(anime_query=anime)
            user_stats = await get_user_stats_for_anime(anime_id=anime_info['id'], user_id=self.user.id)
        except MyAnimeListParseException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while parsing anime info. We've been informed of this and will fix it "
                                       f"as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except MyAnimeListException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while connecting to MAL. Their servers might be down at the moment.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except Exception as e:
            self.error_logger.log(f"Error while getting anime info. Anime = `{anime}`. User ID: {self.user.id}.\n"
                                  f"{e}: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR)
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"There was an error while getting anime info. "
                                       f"We've been informed of this and will fix it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )

        interactions_handler = AnimeInfoInteractionsHandler(source_interaction=self.interaction,
                                                            anime_info=anime_info,
                                                            search_result=search_result,
                                                            user_stats=user_stats,
                                                            query=anime)

        embed, views = interactions_handler.get_embed_and_views()

        await self.interaction.edit_original_response(embed=embed, view=views)

    @slash_command
    async def manga(self, manga: str):
        """
        /manga
        Gets manga info from MAL
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(content=None,
                                                     embed=quick_embed(text=f"Loading manga {self.loading_emoji}",
                                                                       color=Colour.EXT_MAL,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            manga_info, search_result = await self.get_manga_by_name(manga_query=manga)
            user_stats = await get_user_stats_for_manga(manga_id=manga_info['id'], user_id=self.user.id)
        except MyAnimeListParseException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while parsing manga info. We've been informed of this and will fix it "
                                       f"as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except MyAnimeListException:
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"Error while connecting to MAL. Their servers might be down at the moment.",
                                  color=Colour.ERROR,
                                  bold=False)
            )
        except Exception as e:
            self.error_logger.log(f"Error while getting manga info. Manga = `{manga}`. User ID: {self.user.id}.\n"
                                  f"{e}: {traceback.format_exc()}",
                                  level=BotLogLevel.ERROR)
            return await self.interaction.edit_original_response(
                embed=quick_embed(text=f"There was an error while getting manga info. "
                                       f"We've been informed of this and will fix it as soon as possible.",
                                  color=Colour.ERROR,
                                  bold=False)
            )

        interactions_handler = MangaInfoInteractionsHandler(source_interaction=self.interaction,
                                                            manga_info=manga_info,
                                                            search_result=search_result,
                                                            user_stats=user_stats,
                                                            query=manga)

        embed, views = interactions_handler.get_embed_and_views()

        await self.interaction.edit_original_response(embed=embed, view=views)
