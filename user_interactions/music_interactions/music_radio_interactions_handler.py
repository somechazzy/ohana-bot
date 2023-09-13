import asyncio
import traceback

from actions import send_message
from globals_ import shared_memory

import discord

from globals_.clients import discord_client
from globals_.constants import BOT_OWNER_ID, MusicServiceMode, Colour, MusicLogAction
from services.background.music_service import GuildMusicService
from user_interactions.modals.music_player_modals import MusicPlayerReportModal
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler
from utils.decorators import interaction_handler
from utils.embed_factory import quick_embed, make_radio_currently_playing_embed
from utils.helpers import reset_music_player_message


class MusicRadioInteractionsHandler(MusicInteractionsHandler):

    def __init__(self, source_interaction: discord.Interaction):
        super().__init__(source_interaction=source_interaction)
        self.guild_prefs = shared_memory.guilds_prefs[self.guild.id]
        self.music_service: GuildMusicService = shared_memory.guild_music_services.get(self.guild.id)
        self.member = self.source_interaction.guild.get_member(self.source_interaction.user.id)
        self.voice_client = self.guild.voice_client

    async def handle_action(self, action: str):
        if not hasattr(self, f"_handle_{action.lower()}"):
            self.error_logger.log(f"Music radio action handler not found: {action}")
        action_handler = getattr(self, f"_handle_{action.lower()}")
        try:
            await action_handler(self.source_interaction)
        except Exception as e:
            self.error_logger.log(f"Error encountered while handling music radio interaction: {e}\n"
                                  f"{traceback.format_exc()}")
            try:
                await self._refresh_radio_embed_and_views()
                if not self.source_interaction.response.is_done():
                    self.source_interaction.response.send_message(f"I am facing an issue right now. "
                                                                  f"We've been notified and will fix it ASAP.",
                                                                  ephemeral=True)
            except Exception:
                pass
            if not self.source_interaction.response.is_done():
                await self.source_interaction.response.defer()
        if not self.source_interaction.response.is_done():
            self.error_logger.log(f"Music player handler did not respond to interaction: {action}\n"
                                  f"Interaction data: {self.source_interaction.data}")
            try:
                await self.source_interaction.response.defer()
            except (discord.ClientException, discord.HTTPException, discord.NotFound):
                pass

    @interaction_handler
    async def _handle_select_stream(self, _):
        if not await self._check_for_voice_channels():
            return

        stream_code = self.source_interaction.data["values"][0]
        stream = shared_memory.music_streams.get(stream_code)
        if not stream:
            return await self.source_interaction.response.send_message("Invalid stream.", ephemeral=True)

        if not self.voice_client:
            self.voice_client = self.check_playablity_and_connect()

        if not self.music_service:
            self.music_service = self._initiate_guild_music_service()

        if self.music_service.radio_stream and self.music_service.radio_stream.code == stream_code:
            return await self.source_interaction.response.send_message(
                embed=quick_embed("This radio is already playing."),
                ephemeral=True,
                delete_after=5
            )

        self.music_service.set_radio_stream(stream=stream)

        await self.source_interaction.response.send_message(
            embed=quick_embed(
                f"Playing Radio: **{stream.name}**"
            ),
            ephemeral=True,
            delete_after=5
        )

        if not self.voice_client.is_playing():
            asyncio.get_event_loop().create_task(self.music_service.start_radio())
        await self.music_logger_component.log_music_action(action=MusicLogAction.CHANGED_RADIO_STREAM,
                                                           context_value=stream.name)

    @interaction_handler
    async def _handle_stop(self, _):
        if not await self._check_for_voice_channels():
            return

        if not self.music_service or self.music_service.service_mode != MusicServiceMode.RADIO \
                or not self.music_service.radio_stream:
            await self.source_interaction.response.send_message(
                embed=quick_embed("Nothing is currently playing.", emoji='❌', color=Colour.RED),
                ephemeral=True,
                delete_after=5
            )
            return await self._refresh_radio_embed_and_views()

        self.music_service.set_radio_stream(stream=None, stop_current_radio=True)
        await self.source_interaction.response.defer()
        await self.music_logger_component.log_music_action(action=MusicLogAction.PAUSED_PLAYBACK)

    @interaction_handler
    async def _handle_disconnect(self, _):
        if not await self._check_for_voice_channels():
            return

        if self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
        else:
            channel = await self.member_voice_channel.connect()
            await channel.disconnect(force=True)

        if not self.source_interaction.response.is_done():
            await self.source_interaction.response.defer()

        await self._delete_guild_music_service()
        await self._refresh_radio_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.DISCONNECTED_BOT)

    @interaction_handler
    async def _handle_report(self, _):
        return await self.source_interaction.response.send_modal(MusicPlayerReportModal(interactions_handler=self))

    async def handle_report_modal_submit(self, inter, input_text):
        await inter.response.send_message(embed=quick_embed("Thank you for the feedback. "
                                                            "We'll work on fixing the issue ASAP and "
                                                            "will inform you once the issue is fixed."),
                                          ephemeral=True)

        await send_message(f"Received music radio feedback",
                           embed=quick_embed(input_text, bold=False, emoji=None,
                                             fields_values={
                                                 "User": f"**{inter.user}** ({inter.user.id})",
                                                 "Channel": f"**{self.channel}** ({self.channel.id})",
                                                 "Guild": f"**{self.guild}** ({self.guild.id})",
                                             }),
                           channel=discord_client.get_user(BOT_OWNER_ID))

    @interaction_handler
    async def _handle_show_currently_playing(self, _):
        if not await self._check_for_voice_channels():
            return
        if not self.music_service or self.music_service.service_mode != MusicServiceMode.RADIO \
                or not self.music_service.radio_stream:
            return await self.source_interaction.response.send_message(
                embed=quick_embed("Nothing is currently playing.", emoji='❌', color=Colour.RED),
                ephemeral=True,
                delete_after=5
            )

        await self.source_interaction.response.defer(thinking=True, ephemeral=True)

        await self.source_interaction.followup.send(
            embed=make_radio_currently_playing_embed(
                stream_status=await self.music_service.radio_stream.get_stream_status()
            ),
            ephemeral=True
        )

    @interaction_handler
    async def _handle_switch_to_player(self, _):
        if not await self._check_for_voice_channels(interaction=self.source_interaction):
            await self._refresh_radio_embed_and_views()
            return
        if not self.music_service:
            self._initiate_guild_music_service()
        if self.music_service.service_mode == MusicServiceMode.PLAYER:
            return await self.source_interaction.response.send_message(
                embed=quick_embed("You're already in player mode.", emoji='❌', color=Colour.RED),
                ephemeral=True,
                delete_after=5
            )
        await self.source_interaction.response.defer()
        await self.music_service.change_service_mode(service_mode=MusicServiceMode.PLAYER)
        await self._refresh_radio_embed_and_views()
        await self.music_logger_component.log_music_action(action=MusicLogAction.SWITCHED_TO_PLAYER)

    async def _refresh_radio_embed_and_views(self):
        if self.music_service:
            await self.music_service.refresh_player()
        else:
            await reset_music_player_message(self.guild)
