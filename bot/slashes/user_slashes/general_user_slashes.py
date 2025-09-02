import asyncio

import cache
from bot.interaction_handlers.user_interaction_handlers.help_menu_interaction_handler import HelpMenuInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.user_settings_interaction_handler import \
    UserSettingsInteractionHandler
from bot.slashes.user_slashes import UserSlashes
from bot.utils.bot_actions.basic_actions import send_message
from bot.utils.bot_actions.utility_actions import refresh_music_player_message
from bot.utils.embed_factory.general_embeds import get_success_embed, get_generic_embed
from clients import discord_client
from bot.utils.decorators import slash_command
from common.exceptions import UserInputException
from components.user_settings_components.user_settings_component import UserSettingsComponent
from settings import BOT_OWNER_ID
from constants import CommandCategory
from bot.guild_music_service import GuildMusicService
from strings.commands_strings import UserSlashCommandsStrings
from strings.music_strings import MusicStrings
from utils.helpers.context_helpers import create_isolated_task


class GeneralUserSlashes(UserSlashes):

    @slash_command()
    async def manage_user_settings(self):
        """
        /user-settings
        Manage your settings on Ohana.
        """

        user_settings = await UserSettingsComponent().get_user_settings(self.user.id,
                                                                        load_usernames=True)
        interaction_handler = UserSettingsInteractionHandler(source_interaction=self.interaction,
                                                             context=self.context,
                                                             guild_settings=self.guild_settings,
                                                             user_settings=user_settings)
        embed, view = interaction_handler.get_embed_and_view()
        await self.interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @slash_command()
    async def feedback(self, feedback: str):
        """
        /feedback
        Send feedback to the bot owner
        """

        await self.interaction.response.send_message(
            embed=get_success_embed(UserSlashCommandsStrings.FEEDBACK_REPLY),
            ephemeral=True
        )

        await send_message(channel=await discord_client.fetch_user(BOT_OWNER_ID),
                           embed=get_generic_embed(title="Received general feedback",
                                                   description=feedback,
                                                   field_value_map={
                                                       "User": f"**{self.user}** ({self.user.id})"
                                                   }))

    @slash_command()
    async def help(self, menu: CommandCategory.values_as_enum() | None, make_visible: bool):
        """
        /help
        Show the help menu
        """

        interactions_handler = HelpMenuInteractionHandler(source_interaction=self.interaction,
                                                          selected_menu=menu.value if menu else None,
                                                          context=self.context,
                                                          guild_settings=self.guild_settings)

        embed, view = interactions_handler.get_embed_and_view()

        await self.interaction.response.send_message(embed=embed,
                                                     view=view,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))

    @slash_command(guild_only=True,
                   bot_permissions=["send_messages", "embed_links", "manage_messages", "read_message_history"])
    async def music_fix(self):
        """
        /music-fix
        Fix Ohana music/radio by force resetting everything.
        """
        await self.interaction.response.defer(thinking=True, ephemeral=True)
        if not self.member.voice or not self.member.voice.channel:
            raise UserInputException(MusicStrings.JOIN_A_VC_ERROR_MESSAGE)
        current_voice_channel_id = self.guild.voice_client.channel.id if self.guild.voice_client else None  # noqa
        current_stream = None
        if self.guild.id in cache.MUSIC_SERVICES:
            current_stream = cache.MUSIC_SERVICES[self.guild.id].current_stream
            await cache.MUSIC_SERVICES[self.guild.id].kill()
        elif self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
            await refresh_music_player_message(guild=self.guild)
        else:
            await refresh_music_player_message(guild=self.guild)

        await asyncio.sleep(2)

        if current_voice_channel_id:
            gms = await GuildMusicService.instantiate_with_connection(guild_id=self.guild.id,
                                                                      voice_channel_id=current_voice_channel_id)
            if current_stream:
                gms.set_radio_stream(stream=current_stream)
                create_isolated_task(gms.start())
        await self.interaction.followup.send(
            embed=get_success_embed(MusicStrings.RESET_MUSIC_SUCCESS_MESSAGE),
            ephemeral=False
        )
