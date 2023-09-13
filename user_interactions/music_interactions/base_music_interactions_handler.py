import asyncio

import discord

from components.music_components.library_music_component import LibraryMusicComponent
from components.music_components.music_logger_component import MusicLoggerComponent
from globals_ import shared_memory
from globals_.constants import MusicVCState, MusicServiceMode, MusicVCLoopMode
from utils.embed_factory import quick_embed
from utils.exceptions import MusicVoiceConnectionException
from services.background.music_service import GuildMusicService
from user_interactions.base_interactions_handler import BaseInteractionsHandler
from utils.helpers import quick_button_views


class MusicInteractionsHandler(BaseInteractionsHandler):

    def __init__(self, source_interaction):
        super().__init__(source_interaction=source_interaction)
        if self.__class__ == MusicInteractionsHandler:
            raise NotImplementedError("MusicInteractionsHandler is an abstract class and cannot be instantiated")
        self.guild = source_interaction.guild
        self.channel = source_interaction.channel
        self.music_channel = self.guild.get_channel(shared_memory.guilds_prefs[self.guild.id].music_channel) \
            if self.guild else None
        self.source_interaction_user = source_interaction.user
        self.source_interaction_member = self.guild.get_member(self.source_interaction_user.id) \
            if self.guild else None
        self.library_music_component = LibraryMusicComponent()
        self.music_logger_component = MusicLoggerComponent(guild_id=self.guild.id,
                                                           actor_id=self.source_interaction_user.id,
                                                           actor_name=self.source_interaction_user.name)

    async def on_timeout(self):
        try:
            await self.source_interaction.delete_original_response()
        except discord.NotFound:
            pass

    async def handle_play_playlist_from_view(self, playlist, music_service):
        tracks = playlist.tracks.copy()
        await music_service.add_track_to_queue(url=self.youtube_id_to_url(tracks[0].youtube_id),
                                               added_by=self.source_interaction_user.id,
                                               refresh_player=True)
        tracks = tracks[1:]
        if tracks:
            asyncio.get_event_loop() \
                .create_task(music_service.add_tracks_to_queue([self.youtube_id_to_url(track.youtube_id)
                                                                for track in tracks],
                                                               added_by=self.source_interaction_user.id,
                                                               channel=self.channel))

        await music_service.refresh_player()
        if music_service.state != MusicVCState.PLAYING:
            i = 0
            while not music_service.queue:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            asyncio.get_event_loop().create_task(music_service.start_worker())

    async def handle_play_track_from_view(self, track_url, voice_client=None):
        if not voice_client:
            voice_client = await self.check_playablity_and_connect(raise_=True)
        music_service = self.get_or_initiate_guild_music_service(voice_channel_id=voice_client.channel.id,
                                                                 voice_client=voice_client)
        track_info = await music_service.add_track_to_queue(url=track_url,
                                                            added_by=self.source_interaction_user.id,
                                                            refresh_player=True)
        if music_service.state != MusicVCState.PLAYING:
            i = 0
            while not music_service.queue:
                await asyncio.sleep(1)
                if i >= 5:
                    break
            asyncio.get_event_loop().create_task(music_service.start_worker())
        return track_info

    async def check_playablity_and_connect(self, edit=False, raise_=False):
        if raise_ and edit:
            raise Exception()
        delete_after = self.delete_after(longest=True)
        user_voice_channel = self.member_voice_channel
        if not user_voice_channel:
            message = "You must join a voice channel first."
            if edit:
                await self.source_interaction.edit_original_response(content=message)
            elif raise_:
                raise MusicVoiceConnectionException(message)
            else:
                await self.source_interaction.response.send_message(content=message, ephemeral=True)
            return False
        if self.guild.me.voice and self.guild.me.voice.channel != user_voice_channel:
            message = "Join my voice channel first."
            if edit:
                await self.source_interaction.edit_original_response(content=message)
            elif raise_:
                raise MusicVoiceConnectionException(message)
            else:
                await self.source_interaction.response.send_message(content=message, ephemeral=True)
            return False
        if not self.guild.me.voice:
            missing_permission = self.bot_can_connect_and_speak_in_vc()
            if missing_permission:
                message = f"I need the `{missing_permission}` permission on the voice channel for this command."
                if edit:
                    await self.source_interaction.edit_original_response(content=message)
                elif raise_:
                    raise MusicVoiceConnectionException(message)
                else:
                    await self.source_interaction.response.send_message(content=message, delete_after=delete_after)
                return False
            try:
                return await user_voice_channel.connect()
            except discord.ClientException as e:
                if "already connected" in str(e).lower():
                    await self.guild.voice_client.disconnect(force=True)
                    return await user_voice_channel.connect()
                else:
                    raise e
        return self.guild.voice_client

    def get_or_initiate_guild_music_service(self, voice_channel_id, voice_client) -> GuildMusicService:
        if self.guild.id not in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id] = GuildMusicService(guild_id=self.guild.id,
                                                                                  voice_channel_id=voice_channel_id,
                                                                                  voice_client=voice_client,
                                                                                  text_channel=self.channel)
            shared_memory.guild_music_services[self.guild.id].state = MusicVCState.CONNECTED
            asyncio.get_event_loop().create_task(
                shared_memory.guild_music_services[self.guild.id].initiate_dc_countdown()
            )
        return shared_memory.guild_music_services[self.guild.id]

    def delete_after(self, long=False, longest=False):
        if self.channel != \
                shared_memory.guild_music_services.get(self.guild.id,
                                                       GuildMusicService(self.guild.id, 0, None, None)).music_channel:
            return None
        return 15 if longest else 5 if long else 3

    def bot_can_connect_and_speak_in_vc(self):
        voice_channel = self.member_voice_channel
        bot_member = self.guild.me
        bot_permissions = voice_channel.permissions_for(bot_member)
        if bot_permissions.administrator:
            return
        if not bot_permissions.connect:
            return 'connect'
        if not bot_permissions.speak:
            return 'speak'
        if not bot_permissions.use_voice_activation:
            return 'use_voice_activation'

    @property
    def member_voice_channel(self):
        return self.source_interaction_member.voice.channel \
            if self.source_interaction_member and self.source_interaction_member.voice \
            else None

    @property
    def bot_voice_channel(self):
        return self.guild.me.voice.channel if self.guild.me.voice else None

    @staticmethod
    def youtube_id_to_url(id_):
        return f"https://www.youtube.com/watch?v={id_}"

    async def validate_music_channel(self, interaction):
        if not self.music_channel:
            await interaction.response.send_message("You need a music channel in order to play music."
                                                    " Use `/music channel-create` command to create it"
                                                    " or ask an admin to do it.",
                                                    ephemeral=True)
            return False
        if not self.music_channel.permissions_for(self.guild.me).send_messages \
                or not self.music_channel.permissions_for(self.guild.me).embed_links:
            await interaction.response.send_message(
                f"I need permissions to send messages and embed links in the"
                f" music channel ({self.music_channel.mention}).",
                ephemeral=True
            )
            return False
        return True

    async def ask_to_switch_to_player_mode(self, interaction):
        embed = quick_embed("In order to play something you need to switch to Music Player mode.",
                            bold=False)
        views = quick_button_views(button_callback_map={
            "Switch to Player mode": self._handle_prompt_to_switch_to_player_mode
        },
            styles=[discord.ButtonStyle.green],
            on_timeout=None,
            timeout=None
        )
        await interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    async def _handle_prompt_to_switch_to_player_mode(self, interaction: discord.Interaction):
        await interaction.response.defer()
        music_service = shared_memory.guild_music_services.get(self.guild.id)
        if not music_service:
            return
        await music_service.change_service_mode(service_mode=MusicServiceMode.PLAYER)
        await interaction.delete_original_response()
        await music_service.refresh_player()

    async def _check_for_voice_channels(self, interaction=None):
        """
        Checks if the bot is connected to a voice channel and if the user is in the same voice channel as the bot.
        MUST PASS interaction IF THE INTERACTION IS A FOLLOWUP (like a modal submission)
        :param interaction:
        :return:
        """
        if not interaction:
            interaction = self.source_interaction
        if not self.bot_voice_channel:
            await interaction.response.send_message("I'm not connected.",
                                                    ephemeral=True)
            return False
        elif not self.member_voice_channel or self.member_voice_channel != self.bot_voice_channel:
            await interaction.response.send_message("You must be in the same voice channel as me.",
                                                    ephemeral=True)
            return False
        return True

    async def _delete_guild_music_service(self):
        if self.guild.id in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id].queue = []
            shared_memory.guild_music_services[self.guild.id].currently_played_track_index = 0
            shared_memory.guild_music_services[self.guild.id].loop_mode = MusicVCLoopMode.NONE
            try:
                shared_memory.guild_music_services.pop(self.guild.id)
            except KeyError:
                pass
        self.music_service = None

    def _initiate_guild_music_service(self):
        if self.guild.id not in shared_memory.guild_music_services:
            shared_memory.guild_music_services[self.guild.id] = GuildMusicService(
                guild_id=self.guild.id,
                voice_channel_id=self.member_voice_channel.id,
                voice_client=self.guild.voice_client,
                text_channel=self.channel
            )
            shared_memory.guild_music_services[self.guild.id].state = MusicVCState.CONNECTED
            asyncio.get_event_loop().create_task(
                shared_memory.guild_music_services[self.guild.id].initiate_dc_countdown()
            )
        self.music_service = shared_memory.guild_music_services[self.guild.id]
        return self.music_service
