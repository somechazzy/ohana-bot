import asyncio

import discord

import cache
from bot.utils.bot_actions.basic_actions import send_message
from bot.utils.modal_factory.music_modals import MusicPlayerReportModal
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.bot_actions.utility_actions import refresh_music_player_message
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.general_embeds import get_info_embed, get_generic_embed, get_success_embed
from bot.utils.embed_factory.music_embeds import get_radio_currently_playing_embed, get_radio_category_embed
from bot.utils.view_factory.music_views import get_radio_category_view
from clients import discord_client
from common.exceptions import UserInputException
from settings import BOT_OWNER_ID
from constants import MusicPlayerAction
from bot.guild_music_service import GuildMusicService
from utils.helpers.context_helpers import create_isolated_task


class RadioInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Radio player"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.music_service = cache.MUSIC_SERVICES.get(self.guild.id)
        self.user_voice_channel = self.original_member.voice.channel \
            if self.original_member and self.original_member.voice else None

    async def handle_action(self, action: str):
        match action:
            case MusicPlayerAction.CONNECT:
                await self.connect(self.source_interaction)
            case MusicPlayerAction.DISCONNECT:
                await self.disconnect(self.source_interaction)
            case MusicPlayerAction.SELECT_STREAM:
                await self.select_stream(self.source_interaction)
            case MusicPlayerAction.STOP:
                await self.stop(self.source_interaction)
            case MusicPlayerAction.REPORT_ISSUE:
                await self.report_issue(self.source_interaction)
            case MusicPlayerAction.FIX_PLAYER:
                await self.fix_player(self.source_interaction)
            case MusicPlayerAction.SHOW_CURRENTLY_PLAYING:
                await self.show_currently_playing(self.source_interaction)
            case _:
                await refresh_music_player_message(self.guild)
                raise UserInputException(f"Unknown action: {action}")

    @interaction_handler()
    async def connect(self, interaction: discord.Interaction):
        if not self.user_voice_channel:
            raise UserInputException("You must join a voice channel first.")
        elif self.guild.me.voice and self.guild.me.voice.channel != self.user_voice_channel:
            raise UserInputException("Join my voice channel first.")
        elif not self.guild.me.guild_permissions.administrator and \
                (not self.user_voice_channel.permissions_for(self.guild.me).connect or
                 not self.user_voice_channel.permissions_for(self.guild.me).speak):
            raise UserInputException("I need permission to connect and speak in your voice channel.")
        if not self.music_service:
            self.music_service = await GuildMusicService.instantiate_with_connection(
                guild_id=self.guild.id,
                voice_channel_id=self.user_voice_channel.id,
                reconnect_on_already_connected=True
            )
        await refresh_music_player_message(guild=self.guild)
        await interaction.response.defer()

    @interaction_handler()
    async def disconnect(self, interaction: discord.Interaction):
        await self.assert_author_and_bot_in_vc()
        if self.music_service:
            await self.music_service.kill(failure_ok=True)
            cache.MUSIC_SERVICES.pop(self.guild.id, None)
        else:
            await refresh_music_player_message(guild=self.guild)
        await interaction.response.defer()

    @interaction_handler()
    async def select_stream(self, interaction: discord.Interaction):
        stream_code = self.source_interaction.data["values"][0]
        if stream_code.startswith(MusicPlayerAction.subselect_qualifier()):
            category = stream_code.split(MusicPlayerAction.subselect_qualifier() + '-', 1)[-1]
            category_embed = get_radio_category_embed(guild=self.guild, category=category)
            category_view = get_radio_category_view(category=category)
            await interaction.response.send_message(embed=category_embed, view=category_view, ephemeral=True)
            return
        await self.assert_author_and_bot_in_vc()
        if not cache.RADIO_STREAMS.get(stream_code):
            self.logger.error(f"Received invalid stream code {stream_code}")
            raise UserInputException(f"Radio stream seems to be invalid. "
                                     f"This is a problem on our side and we're fixing it!")
        if not self.music_service:
            self.music_service = await GuildMusicService.instantiate_with_connection(
                guild_id=self.guild.id,
                voice_channel_id=self.user_voice_channel.id,
                reconnect_on_already_connected=True
            )
        self.music_service.set_radio_stream(cache.RADIO_STREAMS[stream_code])
        create_isolated_task(self.music_service.start())
        await interaction.response.defer()

    @interaction_handler()
    async def stop(self, interaction: discord.Interaction):
        await self.assert_author_and_bot_in_vc()
        if not self.music_service:
            await refresh_music_player_message(guild=self.guild)
            raise UserInputException("I'm not connected to a voice channel.")
        self.music_service.set_radio_stream(None)
        await interaction.response.defer()

    @interaction_handler()
    async def report_issue(self, interaction: discord.Interaction):
        return await interaction.response.send_modal(MusicPlayerReportModal(interactions_handler=self))

    @interaction_handler()
    async def on_report_modal_submit(self, interaction: discord.Interaction, report_text: str):
        await interaction.response.send_message(
            embed=get_info_embed("Thanks for the feedback! We're already reading it."), ephemeral=True
        )
        await send_message(channel=await discord_client.fetch_user(BOT_OWNER_ID),
                           embed=get_generic_embed(title="Received music feedback",
                                                   description=report_text,
                                                   field_value_map={
                                                       "User": f"**{interaction.user}** ({interaction.user.id})",
                                                       "Channel": f"**{self.channel}** ({self.channel.id})",
                                                       "Guild": f"**{self.guild}** ({self.guild.id})",
                                                   }))

    @interaction_handler()
    async def fix_player(self, interaction: discord.Interaction):
        await self.assert_author_and_bot_in_vc()
        await interaction.response.defer(thinking=True, ephemeral=True)
        current_voice_channel_id = self.guild.voice_client.channel.id if self.guild.voice_client else None  # noqa
        current_stream = None
        if self.guild.id in cache.MUSIC_SERVICES:
            current_stream = cache.MUSIC_SERVICES[self.guild.id].current_stream
            await cache.MUSIC_SERVICES[self.guild.id].kill()
        elif self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
            await refresh_music_player_message(guild=self.guild)
        await asyncio.sleep(2)
        if current_voice_channel_id:
            gms = await GuildMusicService.instantiate_with_connection(guild_id=self.guild.id,
                                                                      voice_channel_id=current_voice_channel_id)
            if current_stream:
                gms.set_radio_stream(stream=current_stream)
                create_isolated_task(gms.start())
        await interaction.followup.send(
            embed=get_success_embed(f"Music service reset successful. "
                                    f"Please let us know via the report button if any issue persists."),
            ephemeral=True
        )

    @interaction_handler()
    async def show_currently_playing(self, interaction: discord.Interaction):
        if not self.music_service or not self.music_service.current_stream:
            await refresh_music_player_message(guild=self.guild)
            raise UserInputException("Nothing is currently playing...")
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send(embed=get_radio_currently_playing_embed(
            stream_status=await self.music_service.current_stream.get_stream_status())
        )

    async def assert_author_and_bot_in_vc(self):
        feedback = None
        if not self.guild.me.voice:
            await refresh_music_player_message(guild=self.guild)
            feedback = "I'm not connected to a voice channel."
        elif not self.user_voice_channel:
            feedback = "You must join a voice channel first."
        elif self.guild.me.voice.channel != self.user_voice_channel:
            feedback = "You must be in the same voice channel as me."
        if feedback:
            raise UserInputException(message=feedback)
