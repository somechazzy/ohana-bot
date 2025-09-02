import asyncio
import random
import re

import discord

from bot.interaction_handlers.user_interaction_handlers.urban_dictionary_interaction_handler import \
    UrbanDictionaryInteractionHandler
from bot.slashes.user_slashes import UserSlashes
from bot.utils.embed_factory.definition_embeds import get_merriam_webster_definition_embed
from bot.utils.embed_factory.general_embeds import get_error_embed, get_generic_embed
from bot.utils.embed_factory.user_embeds import get_utility_image_embed, get_server_info_embed, get_member_info_embed
from bot.utils.helpers.client_helpers import force_fetch_member
from bot.utils.view_factory.general_views import get_external_url_view
from clients import discord_client, emojis
from bot.utils.decorators import slash_command
from common.exceptions import ExternalServiceException, UserInputException
from components.integration_component.merriam_webster_component import MerriamWebsterComponent
from components.integration_component.urban_dictionary_component import UrbanDictionaryComponent
from settings import RAPID_API_KEY, MERRIAM_API_KEY
from constants import Links, CommandContext
from strings.commands_strings import UserSlashCommandsStrings
from strings.integrations_strings import UrbanStrings, MerriamWebsterStrings


class UtilityUserSlashes(UserSlashes):

    @slash_command(bot_permissions=["read_message_history"])
    async def sticker(self, sticker_message_id: str):
        """
        /sticker
        Get link to a sticker
        """

        if not sticker_message_id.isdigit():
            sticker_message_id = sticker_message_id.split("/")[-1]  # if link
            if not sticker_message_id.isdigit():
                raise UserInputException(UserSlashCommandsStrings.STICKER_INVALID_MESSAGE_ID_ERROR_MESSAGE)

        try:
            message = await self.channel.fetch_message(int(sticker_message_id))
        except (discord.NotFound, discord.Forbidden):
            raise UserInputException(UserSlashCommandsStrings.STICKER_MESSAGE_NOT_FOUND_ERROR_MESSAGE)

        if not message.stickers:
            raise UserInputException(UserSlashCommandsStrings.STICKER_NOT_FOUND)

        sticker_url = Links.DISCORD_STICKER_URL.format(sticker_id=message.stickers[0].id,
                                                       extension=message.stickers[0].format.file_extension)
        await self.interaction.response.send_message(
            embed=get_utility_image_embed(
                image_url=sticker_url,
                title=UserSlashCommandsStrings.STICKER_TITLE,
                context_menu_command_instructions=UserSlashCommandsStrings.STICKER_CONTEXT_MENU_COMMAND_UPSELL
            ),
            view=get_external_url_view(external_url=sticker_url),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command()
    async def avatar(self, user: discord.Member | discord.User | None, use_server_profile: bool):
        """
        /avatar
        Get link to your or someone else's avatar
        """
        use_server_profile = use_server_profile and self.context == CommandContext.GUILD
        user = user or self.user
        if isinstance(user, discord.Member) and use_server_profile:
            avatar = user.guild_avatar
        elif isinstance(user, discord.Member):
            avatar = user.avatar
        else:
            user = await discord_client.fetch_user(user.id)
            avatar = user.avatar

        if not avatar:
            raise UserInputException(UserSlashCommandsStrings.AVATAR_NOT_FOUND)

        await self.interaction.response.send_message(
            embed=get_utility_image_embed(
                image_url=avatar.url,
                title=UserSlashCommandsStrings.AVATAR_TITLE.format(username=user.display_name),
                context_menu_command_instructions=UserSlashCommandsStrings.AVATAR_CONTEXT_MENU_COMMAND_UPSELL
            ),
            view=get_external_url_view(external_url=avatar.url),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command()
    async def banner(self, user: discord.Member | discord.User | None, use_server_profile: bool):
        """
        /banner
        Get link to your or someone else's banner
        """
        use_server_profile = use_server_profile and self.context == CommandContext.GUILD
        user = user or self.user
        if isinstance(user, discord.Member) \
                and use_server_profile \
                and (member := await self.guild.fetch_member(user.id)) \
                and member.guild_banner:
            banner = member.guild_banner
        else:
            user = await discord_client.fetch_user(user.id)
            banner = user.banner

        if not banner:
            raise UserInputException(UserSlashCommandsStrings.BANNER_NOT_FOUND)

        await self.interaction.response.send_message(
            embed=get_utility_image_embed(
                image_url=banner.url,
                title=UserSlashCommandsStrings.BANNER_TITLE.format(username=user.display_name),
                context_menu_command_instructions=UserSlashCommandsStrings.BANNER_CONTEXT_MENU_COMMAND_UPSELL
            ),
            view=get_external_url_view(external_url=banner.url),
            ephemeral=self.send_as_ephemeral()
        )

    @slash_command(guild_only=True)
    async def server_info(self, make_visible: bool):
        """
        /server_info
        Get information about the server
        """
        if not self.guild.chunked:
            await self.guild.chunk()
        embed = get_server_info_embed(guild=self.guild)
        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command(guild_only=True)
    async def user_info(self, user: discord.User | discord.Member, make_visible):
        """
        /user-info
        Get information about yourself or someone else
        """
        user = user or self.member
        if not isinstance(user, discord.Member):
            raise UserInputException(UserSlashCommandsStrings.USER_INFO_USER_NOT_FOUND_ERROR_MESSAGE)

        try:
            member = await force_fetch_member(user_id=user.id, guild=self.guild)
            user = await discord_client.fetch_user(user.id)
        except discord.NotFound:
            raise UserInputException(UserSlashCommandsStrings.USER_INFO_USER_NOT_FOUND_ERROR_MESSAGE)

        embed = get_member_info_embed(member=member, user=user)

        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command()
    async def urban(self, term: str):
        """
        /urban
        Get a definition from Urban Dictionary
        """
        if not RAPID_API_KEY:
            raise UserInputException(UrbanStrings.INTEGRATION_DISABLED)

        await self.interaction.response.send_message(
            embed=get_generic_embed(UrbanStrings.DEFINITION_LOADING.format(loading_emoji=self.loading_emoji)),
            ephemeral=self.send_as_ephemeral()
        )
        term = re.sub(r"[^a-zA-Z0-9-_\s]", "", term).strip()

        try:
            definitions = await UrbanDictionaryComponent().get_definitions(term=term)
        except ExternalServiceException as e:
            await self.interaction.edit_original_response(
                embed=get_error_embed(e.user_message or UrbanStrings.SERVICE_DOWN_MESSAGE)
            )
            return

        interactions_handler = UrbanDictionaryInteractionHandler(source_interaction=self.interaction,
                                                                 context=self.context,
                                                                 guild_settings=self.guild_settings,
                                                                 definitions=definitions)
        embed, view = interactions_handler.get_embed_and_view()

        await self.interaction.edit_original_response(embed=embed, view=view)

    @slash_command()
    async def define(self, term: str):
        """
        /define
        Get a definition from Merriam-Webster Dictionary
        """
        if not MERRIAM_API_KEY:
            raise UserInputException(MerriamWebsterStrings.INTEGRATION_DISABLED)

        await self.interaction.response.defer(thinking=True, ephemeral=self.send_as_ephemeral())
        term = re.sub(r"[^a-zA-Z0-9-_\s]", "", term).strip()

        definition = await MerriamWebsterComponent().get_definition(term=term)
        if not definition:
            raise UserInputException(MerriamWebsterStrings.NO_DEFINITION_FOUND)

        await self.interaction.edit_original_response(embed=get_merriam_webster_definition_embed(term=term,
                                                                                                 definition=definition))

    @slash_command()
    async def flip(self):
        """
        /flip
        Flip a coin
        """
        await self.interaction.response.send_message(
            UserSlashCommandsStrings.FLIP_FLIPPING.format(loading_emoji=self.loading_emoji),
            ephemeral=self.send_as_ephemeral()
        )

        await asyncio.sleep(1.5)  # suspense

        await self.interaction.edit_original_response(
            content=UserSlashCommandsStrings.FLIP_FLIPPED_RESULT.format(
                result=random.choice([UserSlashCommandsStrings.FLIP_HEADS, UserSlashCommandsStrings.FLIP_TAILS]),
                emoji=emojis.misc.yay
            )
        )
