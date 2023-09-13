import random
from copy import deepcopy
from typing import Union

import discord

from globals_.constants import DEFAULT_STREAM_IMAGE
from internal.bot_logger import ErrorLogger
from internal.requests_manager import request
from utils.exceptions import StreamStatusCheckException


class MusicStreamDynamicImage:

    class ParameterSubstitutionType:
        NUMERIC_RANGE = "numeric_range"

    def __init__(self, base_url: str, parameter_name: str, parameter_substitution_type: str, parameter_values: list):
        self.base_url: str = base_url
        self.parameter_name: str = parameter_name
        self.parameter_substitution_type: str = parameter_substitution_type
        self.parameter_values: list = parameter_values

    def get_image_url(self):
        """
        Returns a random image url using the base url and a random value from the parameter values list.
        """
        if self.parameter_substitution_type == self.ParameterSubstitutionType.NUMERIC_RANGE:
            return self.base_url.format(**{self.parameter_name: random.randint(self.parameter_values[0],
                                                                               self.parameter_values[1])})


class MusicStreamStatusCheck:

    class CurrentlyPlayingPathField:
        TITLE = "title"
        ARTIST = "artist"
        EXTRA = "extra"
        FULL = "full"

    class StreamStatus:
        def __init__(self, currently_playing: str, progress: int, duration: int, artwork_url: str):
            self.currently_playing: str = currently_playing
            self.progress: int = progress
            self.duration: int = duration
            self.artwork_url: str = artwork_url

    def __init__(self, url: str, currently_playing_path: dict, progress_path: list,
                 duration_path: list, artwork_path: list):
        self.url: str = url
        self.currently_playing_path: dict = currently_playing_path
        self.progress_path: list = progress_path
        self.duration_path: list = duration_path
        self.artwork_path: list = artwork_path

        self._error_logger = ErrorLogger(component=f"{self.__class__.__name__}")

    async def get_current_stream_status(self):
        if not self.url:
            return None
        try:
            stream_status_data = await self._get_stream_status_data()
        except StreamStatusCheckException as e:
            self._error_logger.log(message=f"Error while getting stream status data for {self.url}:\n{e}")
            return None

        if not stream_status_data:
            return None

        currently_playing = self._extract_currently_playing_full_text(stream_status_data)
        if not currently_playing:
            return None
        progress = self._extract_progress(stream_status_data)
        duration = self._extract_duration(stream_status_data)
        artwork_url = self._extract_artwork_url(stream_status_data)

        return self.StreamStatus(currently_playing=currently_playing, progress=progress, duration=duration,
                                 artwork_url=artwork_url)

    async def _get_stream_status_data(self):
        response = await request(method="GET", url=self.url)
        if not response or response.status != 200:
            raise StreamStatusCheckException("Error while getting stream status data")
        return response.json

    def _extract_currently_playing_full_text(self, stream_status_data):
        if not self.currently_playing_path:
            return None
        if self.currently_playing_path.get(self.CurrentlyPlayingPathField.FULL):
            currently_playing = self._get_value_from_path(
                data=stream_status_data,
                path=self.currently_playing_path.get(self.CurrentlyPlayingPathField.FULL)
            )
        elif self.currently_playing_path.get(self.CurrentlyPlayingPathField.TITLE):
            currently_playing = self._get_value_from_path(
                data=stream_status_data,
                path=self.currently_playing_path.get(self.CurrentlyPlayingPathField.TITLE)
            )
            if currently_playing and self.currently_playing_path.get(self.CurrentlyPlayingPathField.ARTIST):
                artist = self._get_value_from_path(
                    data=stream_status_data,
                    path=self.currently_playing_path.get(self.CurrentlyPlayingPathField.ARTIST)
                )
                currently_playing += f" - {artist}"
        else:
            return None
        if currently_playing and self.currently_playing_path.get(self.CurrentlyPlayingPathField.EXTRA):
            extra = self._get_value_from_path(
                data=stream_status_data,
                path=self.currently_playing_path.get(self.CurrentlyPlayingPathField.EXTRA)
            )
            if extra:
                currently_playing += f" ({extra})"

        return currently_playing.strip() if currently_playing else None

    def _extract_progress(self, stream_status_data):
        if not self.progress_path:
            return None
        progress = self._get_value_from_path(data=stream_status_data, path=self.progress_path)
        if not progress or not isinstance(progress, int):
            return None
        return progress

    def _extract_duration(self, stream_status_data):
        if not self.duration_path:
            return None
        duration = self._get_value_from_path(data=stream_status_data, path=self.duration_path)
        if not duration or not isinstance(duration, int):
            return None
        return duration

    def _extract_artwork_url(self, stream_status_data):
        if not self.artwork_path:
            return None
        return self._get_value_from_path(data=stream_status_data, path=self.artwork_path)

    @staticmethod
    def _get_value_from_path(data: dict, path: list) -> str:
        path = path.copy()
        data = deepcopy(data)
        while data:
            if not path:
                return data
            data = data.get(path.pop(0))


class MusicStream:

    class StreamFormat:
        OPUS = "opus"
        MPEG = "mpeg"

    def __init__(self, info_dict: dict):
        self.code: str = ...
        self.name: str = ...
        self.description: str = ...
        self.icon_url: str = ...
        self.icon_emoji_id: str = ...
        self.genres: list = ...
        self.website_url: str = ...

        self.stream_url: str = ...
        self.stream_format: str = ...

        self.dynamic_image: MusicStreamDynamicImage = ...
        self.static_image_urls: list = ...
        self.image_refresh_rate: int = ...

        self.status_check: MusicStreamStatusCheck = ...

        self.audio_source = None

        self._load_from_dict(info_dict)

    def _load_from_dict(self, info_dict: dict):
        self.code = info_dict['code']
        self.name = info_dict['name']
        self.description = info_dict['description']
        self.icon_url = info_dict['icon_url']
        self.icon_emoji_id = info_dict['icon_emoji_id']
        self.genres = info_dict['genres']
        self.website_url = info_dict.get('website_url', None)

        self.stream_url = info_dict['stream']['url']
        self.stream_format = info_dict['stream']['format']

        if info_dict.get('images', None) or all(not info_dict['images'].get(key) for key in ['dynamic', 'static']):
            if info_dict['images'].get('dynamic'):
                self.dynamic_image = MusicStreamDynamicImage(
                    base_url=info_dict['images']['dynamic']['base_url'],
                    parameter_name=info_dict['images']['dynamic']['parameter']['name'],
                    parameter_substitution_type=info_dict['images']['dynamic']['parameter']['substitution_type'],
                    parameter_values=info_dict['images']['dynamic']['parameter']['values']
                )
            else:
                self.dynamic_image = None
            if info_dict['images'].get('static', {}).get('urls'):
                self.static_image_urls = info_dict['images'].get('static', {}).get('urls', [])
            elif not self.dynamic_image:
                self.static_image_urls = []
            else:
                self.static_image_urls = None
            self.image_refresh_rate = info_dict['image_refresh_rate']
        else:
            self.dynamic_image = None
            self.static_image_urls = []
            self.image_refresh_rate = 0

        if info_dict.get('status_check', {}).get('api', None):
            self.status_check = MusicStreamStatusCheck(
                url=info_dict['status_check']['api'],
                currently_playing_path=info_dict['status_check']['currently_playing_path'],
                progress_path=info_dict['status_check'].get('progress_path', None),
                duration_path=info_dict['status_check'].get('duration_path', None),
                artwork_path=info_dict['status_check'].get('artwork_path', None)
            )
        else:
            self.status_check = None

    def get_image_url(self):
        if self.dynamic_image:
            return self.dynamic_image.get_image_url()
        elif self.static_image_urls:
            return random.choice(self.static_image_urls)
        else:
            return DEFAULT_STREAM_IMAGE

    async def get_stream_status(self) -> Union[MusicStreamStatusCheck.StreamStatus, None]:
        if self.status_check:
            return await self.status_check.get_current_stream_status()
        return None

    def get_genres_string(self):
        return ", ".join(self.genres)

    @property
    def emoji_string(self):
        if self.icon_emoji_id:
            from globals_.clients import discord_client
            return str(discord_client.get_emoji(int(self.icon_emoji_id)))
        return ""

    async def get_ffmpeg_audio_source(self):
        ffmpeg_options = {'before_options': '-reconnect 1 ', 'options': '-vn'}
        if not self.stream_url.startswith("http"):
            ffmpeg_options.pop('before_options')
        if self.stream_format == self.StreamFormat.OPUS:
            return await discord.FFmpegOpusAudio.from_probe(source=self.stream_url, **ffmpeg_options)
        elif self.stream_format == self.StreamFormat.MPEG:
            return discord.FFmpegPCMAudio(source=self.stream_url, **ffmpeg_options)
