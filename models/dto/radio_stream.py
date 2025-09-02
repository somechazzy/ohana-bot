import random
from copy import deepcopy
import discord

from constants import MusicDefaults
from common.app_logger import AppLogger
from services.radio_stream_status_service import RadioStreamStatusService


class RadioStream:

    class StreamFormat:
        OPUS = "opus"
        MPEG = "mpeg"
        AAC = "aac"

    class StreamType:
        DEFAULT = "DEFAULT"
        CUSTOM = "CUSTOM"

    def __init__(self, code: str, category: str, name: str, description: str, genres: list, website_url: str,
                 stream_url: str, stream_format: str, dynamic_image: 'RadioStreamDynamicImage',
                 static_image_urls: list, image_refresh_rate: int, status_check: 'RadioStreamStatusCheck | None'):
        self.code: str = code
        self.category: str = category
        self.name: str = name
        self.description: str = description
        self.genres: list[str] = genres
        self.website_url: str = website_url

        self.stream_url: str = stream_url
        self.stream_format: str = stream_format

        self.dynamic_image: RadioStreamDynamicImage = dynamic_image
        self.static_image_urls: list = static_image_urls
        self.image_refresh_rate: int = image_refresh_rate

        self.status_check: RadioStreamStatusCheck | None = status_check

        self.audio_source = None

    @classmethod
    def from_dict(cls, info_dict: dict) -> 'RadioStream':
        if info_dict.get('images', None) or all(not info_dict['images'].get(key) for key in ['dynamic', 'static']):
            if info_dict['images'].get('dynamic'):
                dynamic_image = RadioStreamDynamicImage(
                    base_url=info_dict['images']['dynamic']['base_url'],
                    parameter_name=info_dict['images']['dynamic']['parameter']['name'],
                    parameter_substitution_type=info_dict['images']['dynamic']['parameter']['substitution_type'],
                    parameter_values=info_dict['images']['dynamic']['parameter']['values']
                )
            else:
                dynamic_image = None
            if info_dict['images'].get('static', {}).get('urls'):
                static_image_urls = info_dict['images'].get('static', {}).get('urls', [])
            elif not dynamic_image:
                static_image_urls = []
            else:
                static_image_urls = None
            image_refresh_rate = info_dict['image_refresh_rate']
        else:
            dynamic_image = None
            static_image_urls = []
            image_refresh_rate = 0

        if info_dict.get('status_check', {}).get('api', None):
            status_check = RadioStreamStatusCheck(
                url=info_dict['status_check']['api'],
                method=info_dict['status_check'].get('method', 'GET'),
                request_data=info_dict['status_check'].get('request_data', {}),
                currently_playing_path=info_dict['status_check']['currently_playing_path'],
                progress_path=info_dict['status_check'].get('progress_path', None),
                duration_path=info_dict['status_check'].get('duration_path', None),
                artwork_path=info_dict['status_check'].get('artwork_path', None),
                duration_time_format=info_dict['status_check'].get('duration_time_format',
                                                                   RadioStreamStatusCheck.TimeFormat.SECONDS)
            )
        else:
            status_check = None

        return cls(
            code=info_dict['code'],
            category=info_dict['category'],
            name=info_dict['name'],
            description=info_dict['description'],
            genres=info_dict['genres'],
            website_url=info_dict['website_url'],
            stream_url=info_dict['stream']['url'],
            stream_format=info_dict['stream']['format'],
            dynamic_image=dynamic_image,
            static_image_urls=static_image_urls,
            image_refresh_rate=image_refresh_rate,
            status_check=status_check
        )

    def get_image_url(self) -> str:
        if self.dynamic_image:
            return self.dynamic_image.get_image_url()
        elif self.static_image_urls:
            return random.choice(self.static_image_urls)
        else:
            return MusicDefaults.DEFAULT_STREAM_IMAGE

    async def get_stream_status(self) -> 'RadioStreamStatusCheck.StreamStatus | None':
        if self.status_check:
            return await self.status_check.get_current_stream_status()
        return None

    async def get_ffmpeg_audio_source(self) -> discord.AudioSource:
        ffmpeg_options = {'before_options': '-reconnect 1 ', 'options': '-vn'}
        if not self.stream_url.startswith("http"):
            ffmpeg_options.pop('before_options')
        if self.stream_format == self.StreamFormat.OPUS:
            return await discord.FFmpegOpusAudio.from_probe(source=self.stream_url, **ffmpeg_options)
        elif self.stream_format in [self.StreamFormat.MPEG, self.StreamFormat.AAC]:
            return discord.FFmpegPCMAudio(source=self.stream_url, **ffmpeg_options)
        else:
            raise ValueError(f"Unsupported stream format: {self.stream_format}. "
                             f"Supported formats are: {self.StreamFormat.OPUS}, {self.StreamFormat.MPEG}.")


class RadioStreamDynamicImage:

    class ParameterSubstitutionType:
        NUMERIC_RANGE = "numeric_range"

    def __init__(self, base_url: str, parameter_name: str, parameter_substitution_type: str, parameter_values: list):
        self.base_url: str = base_url
        self.parameter_name: str = parameter_name
        self.parameter_substitution_type: str = parameter_substitution_type
        self.parameter_values: list = parameter_values

    def get_image_url(self) -> str:
        """
        Returns a random image url using the base url and a random value from the parameter values list.
        """
        if self.parameter_substitution_type == self.ParameterSubstitutionType.NUMERIC_RANGE:
            return self.base_url.format(**{self.parameter_name: random.randint(self.parameter_values[0],
                                                                               self.parameter_values[1])})
        else:
            raise NotImplementedError(f"Parameter substitution type '{self.parameter_substitution_type}' "
                                      f"is not implemented for dynamic images.")


class RadioStreamStatusCheck:

    class CurrentlyPlayingPathField:
        TITLE = "title"
        ARTIST = "artist"
        EXTRA = "extra"
        FULL = "full"

    class TimeFormat:
        SECONDS = "seconds"
        MILLISECONDS = "milliseconds"
        STRING = "string"

    class StreamStatus:
        def __init__(self, currently_playing: str, progress: int, duration: int, artwork_url: str):
            self.currently_playing: str = currently_playing
            self.progress: int = progress
            self.duration: int = duration
            self.artwork_url: str = artwork_url

    def __init__(self, url: str, method: str, request_data: dict, currently_playing_path: dict,
                 progress_path: list, duration_path: list, artwork_path: list, duration_time_format: str):
        self.url: str = url
        self.method: str = method
        self.request_data: dict = request_data
        self.currently_playing_path: dict = currently_playing_path
        self.progress_path: list = progress_path
        self.duration_path: list = duration_path
        self.artwork_path: list = artwork_path
        self.duration_time_format: str = duration_time_format

        self._logger = AppLogger(component=f"{self.__class__.__name__}")

    async def get_current_stream_status(self) -> StreamStatus | None:
        if not self.url:
            return None
        stream_status_data = await RadioStreamStatusService(api_url=self.url)\
            .get_stream_status_data(method=self.method, data=self.request_data)

        if not stream_status_data \
                or not (currently_playing := self._generate_currently_playing_full_text(stream_status_data)):
            return None

        progress = self._extract_progress(stream_status_data)
        duration = self._extract_duration(stream_status_data)
        artwork_url = self._extract_artwork_url(stream_status_data)

        return self.StreamStatus(currently_playing=currently_playing, progress=progress, duration=duration,
                                 artwork_url=artwork_url)

    def _generate_currently_playing_full_text(self, stream_status_data: list | dict | str) -> str | None:
        if not self.currently_playing_path:
            return stream_status_data  # direct text
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

    def _extract_progress(self, stream_status_data) -> int | None:
        if not self.progress_path:
            return None
        progress = self._get_value_from_path(data=stream_status_data, path=self.progress_path)
        if not progress or not isinstance(progress, int):
            return None
        return progress

    def _extract_duration(self, stream_status_data) -> int | None:
        if not self.duration_path:
            return None
        duration = self._get_value_from_path(data=stream_status_data, path=self.duration_path)
        if not duration:
            return None
        if self.duration_time_format in [self.TimeFormat.SECONDS, self.TimeFormat.MILLISECONDS]\
                and not isinstance(duration, int):
            return None
        elif self.duration_time_format == self.TimeFormat.STRING and isinstance(duration, str):
            try:
                duration_parts = duration.split(":")
                if len(duration_parts) == 3:  # HH:MM:SS
                    duration = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
                elif len(duration_parts) == 2:  # MM:SS
                    duration = int(duration_parts[0]) * 60 + int(duration_parts[1])
                else:
                    return None
            except ValueError:
                return None
        elif self.duration_time_format == self.TimeFormat.MILLISECONDS and isinstance(duration, int):
            duration = int(duration / 1000)
        return duration

    def _extract_artwork_url(self, stream_status_data) -> str | None:
        if not self.artwork_path:
            return None
        return self._get_value_from_path(data=stream_status_data, path=self.artwork_path)

    @staticmethod
    def _get_value_from_path(data: dict, path: list) -> str:
        path = path.copy()
        data = deepcopy(data)
        while data:
            if not path:
                break
            key = path.pop(0)
            if isinstance(key, int) and isinstance(data, list) and key < len(data):
                data = data[key]
            else:
                data = data.get(key)
        return data
