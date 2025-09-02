import discord

from bot.interaction_handlers.user_interaction_handlers.animanga_profile_interaction_handler import \
    AnimangaProfileInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.anime_info_interaction_handler import \
    AnimeInfoInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.manga_info_interaction_handler import \
    MangaInfoInteractionHandler
from bot.slashes.user_slashes import UserSlashes
from bot.utils.embed_factory.general_embeds import get_success_embed, get_info_embed, get_error_embed, get_generic_embed
from bot.utils.decorators import slash_command
from common.exceptions import UserReadableException, UserInputException
from components.integration_component.anilist_component import AnilistComponent
from components.integration_component.mal_component import MALComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from components.user_settings_components.user_username_component import UserUsernameComponent
from models.dto.animanga import UserAnimeListEntry
from settings import MYANIMELIST_CLIENT_ID
from constants import UserUsernameProvider, Colour, AnimangaProvider
from strings.integrations_strings import MALStrings, AnilistStrings
from utils.helpers.text_parsing_helpers import get_mal_username_from_url, get_anilist_username_from_url


class AnimangaUserSlashes(UserSlashes):

    @slash_command()
    async def link_myanimelist(self, username: str):
        """
        /link-myanimelist
        Link your MyAnimeList username for stats & profile
        """

        if not MYANIMELIST_CLIENT_ID:
            raise UserInputException(MALStrings.INTEGRATION_DISABLED)

        username_component = UserUsernameComponent()
        mal_component = MALComponent()

        username = get_mal_username_from_url(username)
        if (await username_component.get_user_username(user_id=self.user.id,
                                                       provider=UserUsernameProvider.MAL)) == username:
            await username_component.unset_user_username(user_id=self.user.id, provider=UserUsernameProvider.MAL)
            await self.interaction.response.send_message(
                embed=get_success_embed(message=MALStrings.USERNAME_UNSET),
                ephemeral=True
            )
            return

        await self.interaction.response.send_message(
            embed=get_info_embed(message=MALStrings.USERNAME_BEING_CHECKED.format(loading_emoji=self.loading_emoji)),
            ephemeral=self.send_as_ephemeral()
        )
        try:
            await mal_component.validate_username(username=username)
        except UserReadableException as e:
            await self.interaction.edit_original_response(embed=get_error_embed(message=e.user_message))
            return

        feedback_text = await username_component.set_user_username(user_id=self.user.id,
                                                                   new_username=username,
                                                                   provider=UserUsernameProvider.MAL,
                                                                   validate_with_provider=False)

        await self.interaction.edit_original_response(embed=get_success_embed(message=feedback_text))

    @slash_command()
    async def link_anilist(self, username: str):
        """
        /link-anilist
        Link your AniList username for stats & profile
        """

        username_component = UserUsernameComponent()
        anilist_component = AnilistComponent()

        username = get_anilist_username_from_url(username)
        if (await username_component.get_user_username(user_id=self.user.id,
                                                       provider=UserUsernameProvider.ANILIST)) == username:
            await username_component.unset_user_username(user_id=self.user.id, provider=UserUsernameProvider.ANILIST)
            await self.interaction.response.send_message(
                embed=get_success_embed(message=AnilistStrings.USERNAME_UNSET),
                ephemeral=True
            )
            return

        await self.interaction.response.send_message(
            embed=get_info_embed(
                message=AnilistStrings.USERNAME_BEING_CHECKED.format(loading_emoji=self.loading_emoji)
            ),
            ephemeral=self.send_as_ephemeral()
        )
        try:
            await anilist_component.validate_username(username=username)
        except UserReadableException as e:
            await self.interaction.edit_original_response(embed=get_error_embed(message=e.user_message))
            return

        feedback_text = await username_component.set_user_username(user_id=self.user.id,
                                                                   new_username=username,
                                                                   provider=UserUsernameProvider.ANILIST,
                                                                   validate_with_provider=False)

        await self.interaction.edit_original_response(embed=get_success_embed(message=feedback_text))

    @slash_command()
    async def myanimelist(self, username: str | None, member: discord.User | discord.Member | None):
        """
        /myanimelist
        Get your MyAnimeList profile
        """

        if not MYANIMELIST_CLIENT_ID:
            await self.interaction.response.send_message(
                embed=get_error_embed(message=MALStrings.INTEGRATION_DISABLED),
                ephemeral=True
            )
            return

        if not username and not member:
            username = await UserUsernameComponent().get_user_username(
                user_id=self.user.id, provider=UserUsernameProvider.MAL
            )
        elif member:
            username = await UserUsernameComponent().get_user_username(
                user_id=member.id, provider=UserUsernameProvider.MAL
            ) or username
        if not username:
            if member:
                raise UserInputException(MALStrings.OTHER_USERNAME_NOT_SET)
            raise UserInputException(MALStrings.USERNAME_NOT_SET)

        await self.interaction.response.send_message(
            embed=get_generic_embed(description=MALStrings.PROFILE_LOADING.format(loading_emoji=self.loading_emoji),
                                    color=Colour.EXT_MAL),
            ephemeral=self.send_as_ephemeral()
        )

        try:
            mal_profile = await MALComponent().get_user_profile(username=username)
        except UserReadableException as e:
            await self.interaction.edit_original_response(embed=get_error_embed(message=e.user_message))
            return

        interaction_handler = AnimangaProfileInteractionHandler(source_interaction=self.interaction,
                                                                user_profile=mal_profile,
                                                                context=self.context,
                                                                guild_settings=self.guild_settings)
        embed, view = interaction_handler.get_embed_and_view()
        await self.interaction.edit_original_response(embed=embed, view=view)

    @slash_command()
    async def anilist(self, username: str | None, member: discord.User | discord.Member | None):
        """
        /anilist
        Get your AniList profile
        """

        if not username and not member:
            username = await UserUsernameComponent().get_user_username(
                user_id=self.user.id, provider=UserUsernameProvider.ANILIST
            )
        elif member:
            username = await UserUsernameComponent().get_user_username(
                user_id=member.id, provider=UserUsernameProvider.ANILIST
            ) or username
        if not username:
            if member:
                raise UserInputException(AnilistStrings.OTHER_USERNAME_NOT_SET)
            raise UserInputException(AnilistStrings.USERNAME_NOT_SET)

        await self.interaction.response.send_message(
            embed=get_generic_embed(description=AnilistStrings.PROFILE_LOADING.format(loading_emoji=self.loading_emoji),
                                    color=Colour.EXT_ANILIST),
            ephemeral=self.send_as_ephemeral()
        )

        try:
            anilist_profile = await AnilistComponent().get_user_profile(username=username)
        except UserReadableException as e:
            await self.interaction.edit_original_response(embed=get_error_embed(message=e.user_message))
            return

        interaction_handler = AnimangaProfileInteractionHandler(source_interaction=self.interaction,
                                                                user_profile=anilist_profile,
                                                                context=self.context,
                                                                guild_settings=self.guild_settings)
        embed, view = interaction_handler.get_embed_and_view()
        await self.interaction.edit_original_response(embed=embed, view=view)

    @slash_command()
    async def anime(self, anime: str):
        """
        /anime
        Get anime info with your stats
        """

        await self.interaction.response.send_message(
            embed=get_generic_embed(
                description=MALStrings.ANIME_LOADING.format(loading_emoji=self.loading_emoji),
                color=Colour.EXT_ANILIST,
            ),
            ephemeral=self.send_as_ephemeral()
        )

        user_settings = await UserSettingsComponent().get_user_settings(self.user.id)
        username = await UserUsernameComponent().get_user_username(
            user_id=self.user.id, provider=user_settings.preferred_animanga_provider
        )

        if user_settings.preferred_animanga_provider == AnimangaProvider.MAL and MYANIMELIST_CLIENT_ID:
            component = MALComponent()
        else:
            component = AnilistComponent()

        search_result = await component.get_anime_search_results(query=anime)
        if not search_result.entries:
            await self.interaction.edit_original_response(
                embed=get_error_embed(message=MALStrings.ANIME_NOT_FOUND.format(title=anime)),
            )
            return

        anime_info = await component.get_anime_info(anime_id=search_result.entries[0].anime_id)
        try:
            user_stats = await component.get_user_stats_for_anime(anime_id=search_result.entries[0].anime_id,
                                                                  username=username) if username else None
        except Exception as e:
            if getattr(e, 'alert_worthy', True):
                self.logger.error(f"Error fetching user stats for anime `{anime}`: {e}")
            else:
                self.logger.debug(f"Error fetching user stats for anime `{anime}`: {e}")
            user_stats = UserAnimeListEntry.as_empty_entry(anime_id=search_result.entries[0].anime_id,
                                                           username=username,
                                                           provider=user_settings.preferred_animanga_provider)

        interaction_handler = AnimeInfoInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            guild_settings=self.guild_settings,
            anime_info=anime_info,
            user_stats=user_stats,
            search_result=search_result,
            user_username=username
        )
        embed, view = interaction_handler.get_embed_and_view()
        await self.interaction.edit_original_response(embed=embed, view=view)

    @slash_command()
    async def manga(self, manga: str):
        """
        /manga
        Get manga info with your stats
        """

        await self.interaction.response.send_message(
            embed=get_generic_embed(
                description=AnilistStrings.MANGA_LOADING.format(loading_emoji=self.loading_emoji),
                color=Colour.EXT_ANILIST,
            ),
            ephemeral=self.send_as_ephemeral()
        )

        user_settings = await UserSettingsComponent().get_user_settings(self.user.id)
        username = await UserUsernameComponent().get_user_username(
            user_id=self.user.id, provider=user_settings.preferred_animanga_provider
        )

        if user_settings.preferred_animanga_provider == AnimangaProvider.MAL and MYANIMELIST_CLIENT_ID:
            component = MALComponent()
        else:
            component = AnilistComponent()

        search_result = await component.get_manga_search_results(query=manga)
        if not search_result.entries:
            await self.interaction.edit_original_response(
                embed=get_error_embed(message=AnilistStrings.MANGA_NOT_FOUND.format(title=manga))
            )
            return

        manga_info = await component.get_manga_info(manga_id=search_result.entries[0].manga_id)
        try:
            user_stats = await component.get_user_stats_for_manga(manga_id=search_result.entries[0].manga_id,
                                                                  username=username) if username else None
        except Exception as e:
            if getattr(e, 'alert_worthy', True):
                self.logger.error(f"Error fetching user stats for manga `{manga}`: {e}")
            else:
                self.logger.debug(f"Error fetching user stats for manga `{manga}`: {e}")
            user_stats = None

        interaction_handler = MangaInfoInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            guild_settings=self.guild_settings,
            manga_info=manga_info,
            user_stats=user_stats,
            search_result=search_result,
            user_username=username
        )
        embed, view = interaction_handler.get_embed_and_view()
        await self.interaction.edit_original_response(embed=embed, view=view)
