from datetime import datetime, timedelta
from typing import Union

import discord

from globals_ import shared_memory
from services.third_party.merriam_webster import MerriamDictionaryService
from services.third_party.urban import UrbanDictionaryService
from user_interactions.user_interactions.urban_interactions_handler import UrbanInteractionsHandler
from utils.embed_factory import quick_embed, make_server_info_embed, make_member_info_embed, \
    make_merriam_embed, make_snipe_embed
from globals_.clients import discord_client, reminder_service
from globals_.constants import Colour
from utils.helpers import get_duration_in_minutes_from_text, convert_minutes_to_time_string, \
    get_presentable_merriam_definition_data
from utils.decorators import slash_command
from slashes.user_slashes.base_user_slashes import UserSlashes


class UtilityUserSlashes(UserSlashes):

    @slash_command
    async def sticker(self, sticker_message_id: str):
        """
        /sticker
        Get link to a sticker
        """

        if not await self.preprocess_and_validate():
            return

        if not sticker_message_id.isdigit():
            await self.interaction.response.send_message(embed=quick_embed("Invalid message ID",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        try:
            message = await self.channel.fetch_message(int(sticker_message_id))
        except (discord.NotFound, discord.Forbidden):
            await self.interaction.response.send_message(embed=quick_embed("Message not found",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        if not message.stickers:
            await self.interaction.response.send_message(embed=quick_embed("Sticker not found",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.send_message(embed=quick_embed(f"Sticker URL: <{message.stickers[0].url}>",
                                                                       color=Colour.SUCCESS,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

    @slash_command
    async def avatar(self, user: Union[discord.Member, discord.User] = None, use_server_profile=False):
        """
        /avatar
        Get link to your or someone else's avatar
        """

        if not await self.preprocess_and_validate():
            return

        if use_server_profile and self.is_dm:
            use_server_profile = False

        user = user or self.user

        if isinstance(user, discord.Member) and use_server_profile and user.guild_avatar:
            avatar = user.guild_avatar
        else:
            avatar = user.avatar

        if not avatar:
            await self.interaction.response.send_message(embed=quick_embed("No avatar found...",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)

        await self.interaction.response.send_message(content=avatar.url, ephemeral=False)

    @slash_command
    async def banner(self, user: Union[discord.Member, discord.User] = None):
        """
        /banner
        Get link to your or someone else's banner
        """

        if not await self.preprocess_and_validate():
            return

        try:
            user = user or self.user
            user = await discord_client.fetch_user(user.id)
        except discord.NotFound:
            await self.interaction.response.send_message(embed=quick_embed("User not found",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        if not user.banner:
            await self.interaction.response.send_message(embed=quick_embed("No banner found...",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.send_message(content=user.banner.url, ephemeral=False)

    @slash_command
    async def server_info(self, make_visible: bool = False):
        """
        /server-info
        Get information about the server
        """

        if not await self.preprocess_and_validate():
            return

        embed = make_server_info_embed(self.guild)

        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command
    async def user_info(self, user: Union[discord.User, discord.Member], make_visible: bool = False):
        """
        /user-info
        Get information about yourself or someone else
        """

        if not await self.preprocess_and_validate():
            return

        member = user or self.member

        if not isinstance(member, discord.Member):
            await self.interaction.response.send_message(embed=quick_embed("Please select someone in the server.",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        try:
            user = await discord_client.fetch_user(member.id)
        except discord.NotFound:
            await self.interaction.response.send_message(embed=quick_embed("Cannot find the user.",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        embed = make_member_info_embed(member=member, user=user)

        await self.interaction.response.send_message(embed=embed,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command
    async def remind_me(self, when: str, what: str):
        """
        /remind-me
        Set a reminder for yourself
        """

        if not await self.preprocess_and_validate():
            return

        minutes = get_duration_in_minutes_from_text(when)

        if not minutes:
            await self.interaction.response.send_message(embed=quick_embed("Invalid time format. Valid examples:\n"
                                                                           "• 1d12h means 1 day and 12 hours\n"
                                                                           "• 1h30m means 1 hour and 30 minutes\n"
                                                                           "• 4h30m means 4 hours and 30 minutes",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        if minutes > 60 * 24 * 366:
            await self.interaction.response.send_message(embed=quick_embed("Maximum reminder time is 1 year.",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        await self.interaction.response.send_message(
            embed=quick_embed(f"Okie. I'll remind you about that in {convert_minutes_to_time_string(minutes)}",
                              emoji='',
                              color=Colour.SUCCESS,
                              bold=False),
            ephemeral=True
        )

        await reminder_service.add_reminder(timestamp=int((datetime.utcnow() + timedelta(minutes=minutes)).timestamp()),
                                            user_id=self.user.id,
                                            reason=what)

    @slash_command
    async def urban(self, term: str):
        """
        /urban
        Get a definition from Urban Dictionary
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(embed=quick_embed(f"Getting definitions {self.loading_emoji}",
                                                                       emoji='',
                                                                       color=Colour.EXT_URBAN,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            definitions = await UrbanDictionaryService().get_definitions(term=term)
        except NotImplementedError as e:
            await self.interaction.edit_original_response(embed=quick_embed(str(e),
                                                                            emoji='',
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return
        except Exception:
            await self.interaction.edit_original_response(embed=quick_embed("It seems like Urban Dictionary is down.",
                                                                            emoji='',
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return

        interactions_handler = UrbanInteractionsHandler(source_interaction=self.interaction,
                                                        definitions=definitions)

        embed, views = interactions_handler.get_embed_and_views()

        await self.interaction.edit_original_response(embed=embed, view=views)

    @slash_command
    async def define(self, term: str):
        """
        /define
        Get a definition from Merriam-Webster Dictionary
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(embed=quick_embed(f"Getting definitions {self.loading_emoji}",
                                                                       emoji='',
                                                                       color=Colour.EXT_MERRIAM,
                                                                       bold=False),
                                                     ephemeral=self.send_as_ephemeral())

        try:
            definitions = await MerriamDictionaryService().get_definitions(term=term)
        except NotImplementedError as e:
            await self.interaction.edit_original_response(embed=quick_embed(str(e),
                                                                            emoji='',
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return
        except Exception:
            await self.interaction.edit_original_response(embed=quick_embed("It seems like Merriam-Webster is down.",
                                                                            emoji='',
                                                                            color=Colour.ERROR,
                                                                            bold=False))
            return

        data, response_type = get_presentable_merriam_definition_data(definitions)

        embed = make_merriam_embed(term, data, response_type)

        await self.interaction.edit_original_response(embed=embed)

    @slash_command
    async def snipe(self):
        """
        /snipe
        Get the last deleted message in the channel
        """

        if not await self.preprocess_and_validate():
            return

        sniped_message = shared_memory.channel_id_sniped_message_map.get(self.channel.id)
        if not sniped_message or not (member := self.guild.get_member(sniped_message.get('author_id'))):
            await self.interaction.response.send_message(embed=quick_embed("Nothing to snipe.",
                                                                           emoji='',
                                                                           color=Colour.ERROR,
                                                                           bold=False),
                                                         ephemeral=True)
            return

        embed = make_snipe_embed(sniped_message=sniped_message, member=member)

        await self.interaction.response.send_message(embed=embed, ephemeral=False)

        shared_memory.channel_id_sniped_message_map[self.channel.id] = None
