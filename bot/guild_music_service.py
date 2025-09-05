import asyncio
import traceback
import uuid
from datetime import datetime, UTC, timedelta

import discord

import cache
from bot.utils.bot_actions.utility_actions import refresh_music_player_message
from clients import discord_client
from common.app_logger import AppLogger
from common.exceptions import UserReadableException, ExternalServiceException
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import AppLogCategory
from models.dto.cachables import CachedGuildSettings
from models.dto.radio_stream import RadioStream
from utils.helpers.context_helpers import create_task


class GuildMusicService:
    """
    Service object meant to represent the state of a guild's Ohana Music connection.
    """

    def __init__(self,
                 guild_id: int,
                 voice_client: discord.VoiceClient,
                 guild_settings: CachedGuildSettings):
        self.guild_id: int = guild_id
        self.guild: discord.Guild = discord_client.get_guild(guild_id)
        self.voice_client: discord.VoiceClient = voice_client
        self.guild_settings: CachedGuildSettings = guild_settings

        self._voice_channel: discord.VoiceChannel = voice_client.channel
        self._last_refresh_time: datetime = datetime.now(UTC) - timedelta(seconds=30)

        self.current_stream: RadioStream | None = None
        self.is_running: bool = False
        self.idle_since: datetime | None = datetime.now(UTC)
        self.time_playing_seconds: int = 0
        self._current_stream_session_id = None  # set on start

        self._logger = AppLogger(component=self.__class__.__name__)

    @classmethod
    async def instantiate_with_connection(cls,
                                          guild_id: int,
                                          voice_channel_id: int,
                                          reconnect_on_already_connected: bool = True) -> "GuildMusicService":
        """
        Instantiates the music service for a guild and connects to the specified voice channel.
        Args:
            guild_id (int): The ID of the guild.
            voice_channel_id (int): The ID of the voice channel to connect to.
            reconnect_on_already_connected (bool): Whether to attempt to reconnect if already connected.
        Returns:
            GuildMusicService: The instantiated music service.
        Raises:
            UserReadableException: If there was an issue connecting to the voice channel.
            ExternalServiceException: If there was an unexpected error connecting to the voice channel.
        """
        voice_channel = discord_client.get_channel(voice_channel_id)
        try:
            voice_client = await voice_channel.connect(timeout=3,
                                                       reconnect=True)
        except asyncio.TimeoutError:
            raise UserReadableException("Couldn't connect to the voice channel - likely an issue on Discord's side. "
                                        "If this persists please let us know via `/feedback`.")
        except Exception as e:
            try:
                if isinstance(e, discord.ClientException) and reconnect_on_already_connected:
                    await voice_channel.guild.voice_client.disconnect(force=True)
                    return await cls.instantiate_with_connection(guild_id=guild_id,
                                                                 voice_channel_id=voice_channel_id,
                                                                 reconnect_on_already_connected=False)
                else:
                    raise e
            except Exception as e_:
                raise ExternalServiceException(message=f"Failed to connect to voice channel {voice_channel_id} "
                                                       f"for guild {guild_id}.",
                                               user_message="There was an issue while connecting to the voice channel. "
                                                            "Please try again!",
                                               status_code=500,
                                               debugging_info={
                                                   "error": str(e_),
                                                   "traceback": traceback.format_exc()
                                               },
                                               alert_worthy=True)
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        cache.MUSIC_SERVICES[guild_id] = cls(guild_id=guild_id,
                                             voice_client=voice_client,
                                             guild_settings=guild_settings)
        return cache.MUSIC_SERVICES[guild_id]

    def set_radio_stream(self, stream: RadioStream | None):
        """
        Sets the current radio stream and stops any currently playing audio.
        Args:
            stream (RadioStream | None): The radio stream to set. If None, stops playback.
        """
        self.current_stream = stream
        if self.voice_client:
            self.voice_client.stop()

    async def start(self):
        """
        Starts playing the current radio stream and keeps running until the stream ends or is stopped.
        """
        try:
            self.is_running = True
            self.idle_since = None
            self.time_playing_seconds = 0
            self._current_stream_session_id = uuid.uuid4().hex
            if not self.current_stream:
                raise Exception("Start called without a valid stream set.")
            if not self.voice_client:
                raise UserReadableException(user_message="There was an issue while connecting to the voice channel. "
                                                         "Please try disconnecting and reconnecting me.")
            audio_source = await self.current_stream.get_ffmpeg_audio_source()
            try:
                self.voice_client.play(source=audio_source, signal_type='music',
                                       after=self._on_playback_finished(self._current_stream_session_id))
            except discord.ClientException as e:
                if "already playing" in str(e).lower():
                    return
                elif "not connected" in str(e).lower():
                    self.voice_client = await self._voice_channel.connect()
                    self.voice_client.play(source=audio_source)
                else:
                    raise UserReadableException(
                        user_message="There was an issue while playing the audio source. "
                                     "Please try disconnecting and reconnecting me.",
                        status_code=500,
                        debugging_info={
                            "error": str(e),
                            "traceback": traceback.format_exc()
                        },
                        alert_worthy=True
                    )
            create_task(refresh_music_player_message(guild=self.guild))
            while self.voice_client and self.voice_client.is_playing() and self.current_stream:
                await asyncio.sleep(0.05)
                self.time_playing_seconds += 0.05
                self.is_running = True
                if self.time_playing_seconds % 30 == 0:
                    self.check_and_update_idle_status()
                if self.current_stream and self.current_stream.image_refresh_rate and \
                        self.time_playing_seconds % self.current_stream.image_refresh_rate == 0:
                    create_task(refresh_music_player_message(guild=self.guild))
        finally:
            self.idle_since = datetime.now(UTC)
            self.is_running = False
            self.time_playing_seconds = 0
            self._current_stream_session_id = None
            await refresh_music_player_message(guild=self.guild)

    def stop(self):
        """
        Stops playback and clears the current stream.
        """
        self.set_radio_stream(None)
        if self.voice_client.is_playing():
            self.voice_client.stop()

    async def kill(self, failure_ok=False):
        """
        Completely stops the music service, disconnects from the voice channel, and removes it from the cache.
        Args:
            failure_ok (bool): If True, suppresses exceptions during the kill process.
        """
        try:
            cache.MUSIC_SERVICES.pop(self.guild_id, None)
            self.stop()
            if self.guild.voice_client:
                try:
                    await self.guild.voice_client.disconnect(force=True)
                except:
                    pass
            await refresh_music_player_message(guild=self.guild)
        except Exception as e:
            if failure_ok:
                return
            else:
                raise e

    def _on_playback_finished(self, session_id: str):
        """
        Callback function called when playback finishes. Keeps track of current session ID to catch streams that existed
        but failed to set client's `is_playing` state correctly.
        Args:
            session_id (str): The session ID of the playback session at the time of calling this method.
        """
        async def wait_and_stop():
            await asyncio.sleep(1)
            if self._current_stream_session_id and self._current_stream_session_id == session_id:
                self._logger.debug(f"Playback finished callback called but client is still playing - force stopping.")
                self.stop()
                self.is_running = False
                await refresh_music_player_message(guild=self.guild)

        def callback(error):
            if error:
                self._logger.error(f"Error in playback finished callback: {error}",
                                   category=AppLogCategory.BOT_GENERAL)
            asyncio.run(wait_and_stop())

        return callback

    def check_and_update_idle_status(self):
        """
        Checks if the service should be marked as idle and updates the idle_since timestamp accordingly.
        """
        should_be_idle = not self.is_running or not self.voice_client.is_playing() or not self.current_stream or \
            not ([member for member in self.voice_client.channel.members if not member.bot])
        if should_be_idle and not self.idle_since:
            self.idle_since = datetime.now(UTC)
        elif not should_be_idle:
            self.idle_since = None
