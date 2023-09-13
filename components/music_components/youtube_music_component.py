import json
import os
import traceback
from datetime import datetime, timedelta
from pathlib import Path

from components.music_components.base_music_component import MusicComponent
from globals_ import shared_memory
from globals_.constants import BackgroundWorker, BotLogLevel
from services.third_party.youtube import YoutubeService
from utils.decorators import periodic_worker
from utils.helpers import build_path


class YoutubeMusicComponent(MusicComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_service = YoutubeService()

    async def get_youtube_track_info(self, url: str):
        id_ = url.split('=')[1]
        track_info = None
        try:
            json_path = build_path(relative_path_params=('media', 'music', f'{id_}.json'))
            audio_path = build_path(relative_path_params=('media', 'music', f'{id_}.opus'))
            if not os.path.isfile(json_path) or not os.path.isfile(audio_path):
                raise FileNotFoundError
            with open(json_path, 'r') as file:
                info = json.load(file)
                track_info = info.get('title'), info.get('thumbnail_url'), \
                    info.get('tiny_thumbnail_url'), info.get('duration'), \
                    info.get('audio_url'), info.get('audio_expiry'), \
                    info.get('song_details')
            with open(json_path, 'w') as file:
                info['last_accessed'] = int(datetime.utcnow().timestamp())
                json.dump(info, file)
            print(f"Returning downloaded audio for \"{info.get('title')}\" ({url})")
        except FileNotFoundError:
            pass
        except Exception as e:
            self.error_logger.log(f"Error while reading/writing info for track local json ({url}): "
                                  f"{e}.\n{traceback.format_exc()}")
        if not track_info:
            info = await self.youtube_service.get_video_info(url_=url, process=True)
            if not info:
                return None
            track_info = self.get_track_info_fields_from_video_info(info)
            print(f"Downloaded audio for \"{info.get('title')}\" ({url})")
            if info['filesize'] / 1024 ** 2 < 55:
                await shared_memory.queues['youtube_download_queue'].put(url)

        return track_info

    def get_track_info_fields_from_video_info(self, info):
        title = info.get('title')
        thumbnail_url = info.get('thumbnail')
        if len(info.get('thumbnails')) > 1:
            tiny_thumbnail_url = info.get('thumbnails')[-2].get('url')
        else:
            tiny_thumbnail_url = thumbnail_url
        duration = info.get('duration')
        audio_url = self._get_best_audio_format_url(formats=info['formats'])
        audio_expiry = self._get_audio_expiry_from_url(audio_url)
        song_details = {
            "artist": info.get('artist', ''),
            "title": info.get('track', ''),
            "uploader": info.get('uploader', '-')
        }
        return title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details

    async def get_youtube_playlist_tracks(self, url):
        info = await self.youtube_service.get_video_info(url_=url, process=False)
        if not info:
            return []
        try:
            tracks = \
                info.get('entries').gi_frame.f_locals.get('tab').get('content').get('sectionListRenderer') \
                    .get('contents')[0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
        except Exception:
            tracks = info.get('entries').gi_frame.f_locals['entries'] \
                .gi_frame.f_locals['tab']['content']['sectionListRenderer'] \
                .get('contents')[0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
        tracks_info = []
        for track in tracks:
            if not track.get('continuationItemRenderer') and track.get('playlistVideoRenderer').get('isPlayable'):
                tracks_info.append({
                    "youtube_url": f"https://www.youtube.com/watch?v=" + track.get('playlistVideoRenderer').get(
                        'videoId'),
                    "title": track.get('playlistVideoRenderer').get('title').get('runs')[0].get('text'),
                    "duration_seconds": track.get('playlistVideoRenderer').get('lengthSeconds'),
                    "thumbnail_url": track.get('playlistVideoRenderer').get('thumbnail').get('thumbnails')[0].get('url')
                })
        return tracks_info

    @periodic_worker(name=BackgroundWorker.MUSIC_DOWNLOADER)
    async def music_download_worker(self):
        path = build_path(relative_path_params=('media', 'music'))
        Path(path).mkdir(parents=True, exist_ok=True)
        while not shared_memory.queues['youtube_download_queue'].empty():
            url = await shared_memory.queues['youtube_download_queue'].get()
            try:
                id_ = url.split('=')[1]
                json_path = build_path(relative_path_params=('media', 'music', f'{id_}.json'))
                audio_path = build_path(relative_path_params=('media', 'music', f'{id_}.opus'))
                if os.path.isfile(json_path) and os.path.isfile(audio_path):
                    try:
                        with open(json_path, 'r') as file:
                            _ = json.load(file)
                        continue
                    except Exception:
                        pass
                info = await self.youtube_service.get_video_info(url_=url,
                                                                 process=True,
                                                                 download=True, 
                                                                 file_name=f'{id_}')
                if not info:
                    continue
                title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details = \
                    self.get_track_info_fields_from_video_info(info=info)
                info_dict = dict(title=title,
                                 thumbnail_url=thumbnail_url,
                                 tiny_thumbnail_url=tiny_thumbnail_url,
                                 duration=duration,
                                 song_details=song_details,
                                 url=url,
                                 audio_url=audio_path,
                                 audio_expiry=1900000000,
                                 download_timestamp=int(datetime.utcnow().timestamp()),
                                 last_accessed=int(datetime.utcnow().timestamp()))
                json_path = build_path(relative_path_params=('media', 'music', f'{id_}.json'))
                with open(json_path, 'w+') as f:
                    json.dump(info_dict, f)
            except Exception as e:
                self.error_logger.log(f"Error while downloading audio for Youtube.\n"
                                      f"URL={url}\n"
                                      f"{e}: {traceback.format_exc()}",
                                      level=BotLogLevel.WARNING)
            shared_memory.queues['youtube_download_queue'].task_done()

    @staticmethod
    def _get_best_audio_format_url(formats):
        format_id_audio_url_map = {format_['format_id']: format_['url']
                                   for format_ in formats if format_['resolution'] == 'audio only'}
        for format_id in ['338', '258', '327', '141', '256', '251', '140', '250', '249', '139']:
            if format_id_audio_url_map.get(format_id):
                return format_id_audio_url_map[format_id]
        return list(format_id_audio_url_map.values())[0]

    @staticmethod
    def _get_audio_expiry_from_url(audio_url):
        start_i = audio_url.index("expire=")
        end_i = audio_url[start_i:].index("&") + start_i
        expiry_param_split = audio_url[start_i: end_i].split('=')
        if len(expiry_param_split) != 2 or not expiry_param_split[1].isdigit():
            expiry_timestamp = datetime.timestamp(datetime.utcnow() + timedelta(hours=3))
        else:
            expiry_timestamp = expiry_param_split[1]
        return int(expiry_timestamp)
