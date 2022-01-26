from youtubesearchpython.__future__ import VideosSearch
import json
import os
from pathlib import Path
import traceback
import asyncio
import yt_dlp
from yt_dlp.utils import ExtractorError, DownloadError
from datetime import datetime, timedelta
from internal.bot_logging import log
from globals_ import variables
from globals_.constants import BotLogType
from helpers import build_path


async def get_youtube_track_info(url):
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
        print(f"returning downloaded audio for [{info.get('title')}]({url})")
    except FileNotFoundError:
        pass
    except Exception as e:
        await log(f"Error while reading/write info for track local json ({url}): {e}.\n{traceback.format_exc()}")
    if not track_info:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, extract_info, url, True)
        if not info:
            return None
        track_info = get_necessary_fields_from_track_info(info)
        if info['filesize'] / 1024**2 < 55:
            variables.youtube_download_queue.append(url)

    return track_info


def get_necessary_fields_from_track_info(info):
    title = info.get('title')
    thumbnail_url = info.get('thumbnail')
    if len(info.get('thumbnails')) > 1:
        tiny_thumbnail_url = info.get('thumbnails')[-2].get('url')
    else:
        tiny_thumbnail_url = thumbnail_url
    duration = info.get('duration')
    audio_url = _get_best_audio_format_url(formats=info['formats'])
    audio_expiry = _get_audio_expiry_from_url(audio_url)
    song_details = {
        "artist": info.get('artist', ''),
        "title": info.get('track', '')
    }
    return title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details


async def get_youtube_playlist_tracks(url):
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, extract_info, url, False)
    if not info:
        return []
    try:
        tracks = \
            info.get('entries').gi_frame.f_locals.get('tab').get('content').get('sectionListRenderer')\
            .get('contents')[0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
    except:
        tracks = \
            info.get('entries').gi_frame.f_locals['entries'].gi_frame.f_locals['tab']['content']['sectionListRenderer']\
            .get('contents')[0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
    tracks_info = []
    for track in tracks:
        if not track.get('continuationItemRenderer') and track.get('playlistVideoRenderer').get('isPlayable'):
            tracks_info.append({
                "youtube_url": f"https://www.youtube.com/watch?v=" + track.get('playlistVideoRenderer').get('videoId'),
                "title": track.get('playlistVideoRenderer').get('title').get('runs')[0].get('text'),
                "duration_seconds": track.get('playlistVideoRenderer').get('lengthSeconds'),
                "thumbnail_url": track.get('playlistVideoRenderer').get('thumbnail').get('thumbnails')[0].get('url')
            })
    return tracks_info


def extract_info(url_, process=True, download=False, file_name=None):
    params = {'format': 'bestaudio'}
    if download:
        params['postprocessors'] = [{'key': 'FFmpegExtractAudio'}]
        params['outtmpl'] = build_path(relative_path_params=('media', 'music', file_name))
    try:
        ydl = yt_dlp.YoutubeDL(params=params)
        return ydl.extract_info(url_, download=download, process=process)
    except (DownloadError, ExtractorError) as e:
        print(f"Couldn't extract info from a video/playlist: {e}: {traceback.format_exc()}")
        return None


async def search_on_youtube(search_term, limit=5):
    search_term = search_term.lower()
    search_results = variables.cached_youtube_search_results.get(search_term)
    if search_results and len(search_results) >= limit:
        search_results = variables.cached_youtube_search_results[search_term]
    else:
        video_search = VideosSearch(search_term, limit=limit)
        result = await video_search.next()
        if not result:
            return []
        search_results = [
            {
                "title": result_item['title'],
                "url": result_item['link'],
                "thumbnail_url": result_item['thumbnails'][0]['url'],
                "duration": result_item['duration']
            }
            for result_item in result['result']
        ]
        variables.cached_youtube_search_results[search_term] = search_results
    return search_results


def _get_best_audio_format_url(formats):
    format_id_audio_url_map = {format_['format_id']: format_['url']
                               for format_ in formats if format_['resolution'] == 'audio only'}
    for format_id in ['338', '258', '327', '141', '256', '251', '140', '250', '249', '139']:
        if format_id_audio_url_map.get(format_id):
            return format_id_audio_url_map[format_id]
    return list(format_id_audio_url_map.values())[0]


def _get_audio_expiry_from_url(audio_url):
    start_i = audio_url.index("expire=")
    end_i = audio_url[start_i:].index("&") + start_i
    expiry_param_split = audio_url[start_i: end_i].split('=')
    if len(expiry_param_split) != 2 or not expiry_param_split[1].isdigit():
        expiry_timestamp = datetime.timestamp(datetime.now() + timedelta(hours=3))
    else:
        expiry_timestamp = expiry_param_split[1]
    return int(expiry_timestamp)


async def start_download_queue_worker():
    path = build_path(relative_path_params=('media', 'music'))
    Path(path).mkdir(parents=True, exist_ok=True)
    while True:
        while not variables.youtube_download_queue:
            await asyncio.sleep(5)
        url = variables.youtube_download_queue.pop(0)
        try:
            id_ = url.split('=')[1]
            json_path = build_path(relative_path_params=('media', 'music', f'{id_}.json'))
            audio_path = build_path(relative_path_params=('media', 'music', f'{id_}.opus'))
            if os.path.isfile(json_path) and os.path.isfile(audio_path):
                try:
                    with open(json_path, 'r') as file:
                        _ = json.load(file)
                    continue
                except:
                    pass
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, extract_info, url, True, True, f'{id_}.opus')
            if not info:
                continue
            title, thumbnail_url, tiny_thumbnail_url, duration, audio_url, audio_expiry, song_details =\
                get_necessary_fields_from_track_info(info=info)
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
            variables.cached_youtube_info.pop(url)
        except Exception as e:
            await log(f"Error while downloading audio for Youtube.\nURL={url}\n{e}: {traceback.format_exc()}",
                      level=BotLogType.BOT_WARNING)
